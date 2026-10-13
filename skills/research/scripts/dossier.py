#!/usr/bin/env python3
"""Scaffold and check a research dossier.

    dossier.py init RUN_DIR "Title of the source or topic"
    dossier.py part RUN_DIR 3 "Name of the part"
    dossier.py lint RUN_DIR

RUN_DIR holds sources/ (raw material plus index.md) and dossier/ (what was learned).
`lint` reads every ```facts block under dossier/ and the ```sources block in
sources/index.md, reports problems, and rewrites dossier/inventory.md.
Exit code 1 when there are errors; warnings do not fail the run.

The file formats are described in ../references/dossier-format.md.
"""
import argparse
import os
import re
import sys
from collections import Counter, OrderedDict, defaultdict

FENCE = re.compile(r"^\s*```+\s*([A-Za-z_-]*)\s*$")
ITEM_ID = re.compile(r"^(O|M|C|P\d+|SC\d+)\.(\d+)$")
GROUP_HEADING = re.compile(r"^#{1,3}\s+(O|M|C|P\d+|SC\d+)\s*[·:—–-]\s*(.+?)\s*$")
SOURCE_ID = re.compile(r"\bS(\d+)\b")
PAGE_CITE = re.compile(r"\bpp?\.?\s*(\d+)(?:\s*[-–]\s*(\d+))?")
QUESTION = re.compile(r"^\s*(?:[-*]\s*)?(?:\*\*)?Q[:：]")

STATUSES = ("source", "verified", "corrected", "external", "inferred", "gap")
KINDS = ("context", "part", "link", "step", "rule", "param", "failure", "diff", "claim")
FACT_KEYS = ("for", "show", "src", "status", "note", "hinge")
CHECKED = ("verified", "corrected")
SOURCE_TYPES = ("provided", "primary", "secondary")
PART_SECTIONS = ("in one sentence", "why it exists", "where it sits", "mechanism",
                 "worked example", "newcomer questions")
DEFAULT_TITLES = {"O": "Overview", "M": "Map", "C": "Claims"}


def fenced(path, name):
    """Yield (line_no, text) for the lines inside ```name fences of a file."""
    opened = None
    with open(path, encoding="utf-8") as f:
        for no, line in enumerate(f, 1):
            m = FENCE.match(line)
            if m:
                opened = m.group(1).lower() if opened is None else None
                continue
            if opened == name and line.strip() and not line.lstrip().startswith("#"):
                yield no, line.strip()


def split_fields(text):
    """Split a record on | characters; write \\| for a literal pipe inside a value."""
    return [part.replace("\\|", "|").strip() for part in re.split(r"(?<!\\)\|", text)]


def keyed(fields, where, problems, allowed):
    out = {}
    for field in fields:
        if not field:
            continue
        key, sep, value = field.partition(":")
        key = key.strip().lower()
        if not sep or " " in key:
            problems.append(f"{where}: '{field[:60]}' is not `key: value` "
                            "(a statement or title must not contain the | character)")
            continue
        if key not in allowed:
            problems.append(f"{where}: unknown key '{key}' (use one of: {', '.join(allowed)})")
            continue
        out[key] = value.strip()
    return out


def group_of(item_id):
    return item_id.rsplit(".", 1)[0]


def group_order(group):
    letter = re.match(r"[A-Z]+", group).group(0)
    number = int(re.search(r"\d+", group).group(0)) if re.search(r"\d+", group) else 0
    return (["O", "M", "P", "SC", "C"].index(letter), number)


def pages_in(text):
    pages = set()
    for a, b in PAGE_CITE.findall(text):
        lo, hi = int(a), int(b or a)
        if lo <= hi and hi - lo < 5000:
            pages.update(range(lo, hi + 1))
    return pages


def ranges(numbers):
    numbers = sorted(numbers)
    out, i = [], 0
    while i < len(numbers):
        j = i
        while j + 1 < len(numbers) and numbers[j + 1] == numbers[j] + 1:
            j += 1
        out.append(str(numbers[i]) if i == j else f"{numbers[i]}-{numbers[j]}")
        i = j + 1
    return ", ".join(out)


def rel(path, root):
    return os.path.relpath(path, root)


# ---------- reading the run folder ----------

def read_sources(run, errors, warnings):
    index = os.path.join(run, "sources", "index.md")
    sources = OrderedDict()
    if not os.path.isfile(index):
        errors.append("sources/index.md is missing: every source needs one line in a ```sources block")
        return sources
    for no, line in fenced(index, "sources"):
        where = f"sources/index.md:{no}"
        fields = split_fields(line)
        if len(fields) < 3 or not re.fullmatch(r"S\d+", fields[0]):
            errors.append(f"{where}: expected `S1 | type | title | key: value ...`")
            continue
        sid, stype, title = fields[0], fields[1].lower(), fields[2]
        if stype not in SOURCE_TYPES:
            errors.append(f"{where}: source type '{stype}' must be one of {', '.join(SOURCE_TYPES)}")
        if sid in sources:
            errors.append(f"{where}: {sid} is listed twice")
        extra = keyed(fields[3:], where, errors,
                      ("file", "url", "pages", "read", "retrieved", "version", "note"))
        if "file" in extra and not os.path.exists(os.path.join(run, extra["file"])):
            warnings.append(f"{where}: file '{extra['file']}' does not exist in the run folder")
        sources[sid] = {"type": stype, "title": title, **extra}
    if not sources:
        errors.append("sources/index.md has no ```sources block with at least one source")
    elif not any(s["type"] in ("provided", "primary") for s in sources.values()):
        errors.append("no provided or primary source is listed; secondary sources cannot carry a dossier")
    return sources


def read_dossier(run, errors, warnings):
    root = os.path.join(run, "dossier")
    facts, titles, files = OrderedDict(), {}, {}
    if not os.path.isdir(root):
        errors.append("dossier/ is missing")
        return facts, titles, files
    paths = []
    for base, _, names in os.walk(root):
        for name in sorted(names):
            if name.endswith(".md") and name != "inventory.md":
                paths.append(os.path.join(base, name))
    for path in sorted(paths):
        with open(path, encoding="utf-8") as f:
            for line in f:
                m = GROUP_HEADING.match(line)
                if m and m.group(1) not in titles:
                    titles[m.group(1)] = m.group(2)
        for no, line in fenced(path, "facts"):
            where = f"{rel(path, run)}:{no}"
            fields = split_fields(line)
            if len(fields) < 3 or not ITEM_ID.match(fields[0]):
                errors.append(f"{where}: expected `ID | kind | statement | key: value ...` "
                              "with an ID such as O.1, M.2, P3.4, SC1.2 or C.5")
                continue
            item, kind, text = fields[0], fields[1].lower(), fields[2]
            if item in facts:
                errors.append(f"{where}: {item} is already used at {facts[item]['where']}")
                continue
            if not text:
                errors.append(f"{where}: {item} has an empty statement")
            if kind not in KINDS:
                warnings.append(f"{where}: {item} has kind '{kind}' (usual kinds: {', '.join(KINDS)})")
            extra = keyed(fields[3:], where, errors, FACT_KEYS)
            status = extra.get("status", "").split()[0].lower() if extra.get("status") else ""
            if status not in STATUSES:
                errors.append(f"{where}: {item} needs `status:` set to one of {', '.join(STATUSES)}")
            show = [t.strip().strip("`").strip() for t in extra.get("show", "").split(";")]
            facts[item] = {"where": where, "file": path, "kind": kind, "text": text, "status": status,
                           "for": extra.get("for", ""), "src": extra.get("src", ""),
                           "note": extra.get("note", ""), "show": [t for t in show if t],
                           "hinge": extra.get("hinge", "").strip().lower() in ("yes", "y", "true", "1")}
            files.setdefault(group_of(item), path)
    for group, title in DEFAULT_TITLES.items():
        titles.setdefault(group, title)
    return facts, titles, files


# ---------- checks ----------

def check_facts(facts, sources, errors, warnings):
    cited_pages = defaultdict(set)
    for item, fact in facts.items():
        where, status = fact["where"], fact["status"]
        cited = ["S" + n for n in SOURCE_ID.findall(fact["src"])]
        for sid in cited:
            if sid not in sources:
                errors.append(f"{where}: {item} cites {sid}, which is not in sources/index.md")
        need = {"source": 1, "external": 1, "verified": 2, "corrected": 2}.get(status, 0)
        if len(set(cited)) < need:
            reason = {1: "needs `src:` naming the source it comes from",
                      2: "needs `src:` naming both the provided source and the one that confirms "
                         "or contradicts it"}[need]
            errors.append(f"{where}: {item} is `{status}` and {reason}")
        if status == "corrected" and not fact["note"]:
            errors.append(f"{where}: {item} is `corrected` and needs `note:` saying what the provided source claims")
        if status in ("source", "verified", "corrected") and not any(
                sources.get(sid, {}).get("type") == "provided" for sid in cited) and any(
                s["type"] == "provided" for s in sources.values()):
            warnings.append(f"{where}: {item} is `{status}` but does not cite the provided source; "
                            "use `external` for facts the provided source does not contain")
        for cite in fact["src"].split(";"):
            ids = SOURCE_ID.findall(cite)
            if ids:
                cited_pages["S" + ids[0]].update(pages_in(cite))
        if fact["kind"] == "param" and status not in ("gap", "") and not fact["show"]:
            warnings.append(f"{where}: {item} is a `param` without `show:`; give the name or number as it should "
                            "appear, so the coverage check can look for it")
    check_hinges(facts, errors, warnings)
    return cited_pages


def check_hinges(facts, errors, warnings):
    """The hinges are the few statements the whole explanation rests on. They are checked first."""
    hinges = [(i, f) for i, f in facts.items() if f["hinge"]]
    if facts and not hinges:
        warnings.append("no item is marked `hinge: yes`: mark the statements the explanation rests on "
                        "(usually five to fifteen), so that it is clear which of them were checked")
    for item, fact in hinges:
        if fact["status"] == "source" and not fact["note"]:
            warnings.append(f"{fact['where']}: {item} is a hinge and rests on one source alone; check it against "
                            "a primary source, or add `note:` saying why it cannot be checked")
        elif fact["status"] in ("inferred", "gap"):
            errors.append(f"{fact['where']}: {item} is a hinge but is `{fact['status']}`; the explanation cannot "
                          "rest on a statement no source makes")


def verification_summary(facts):
    """How much of the dossier was checked against a second source, as lines for the inventory."""
    checkable = [f for f in facts.values() if f["status"] in ("source",) + CHECKED]
    checked = [f for f in checkable if f["status"] in CHECKED]
    hinges = [(i, f) for i, f in facts.items() if f["hinge"]]
    hinges_checked = [i for i, f in hinges if f["status"] in CHECKED or f["status"] == "external"]
    lines = [f"- {len(checked)} of the {len(checkable)} statements taken from the source were checked against a "
             f"second source (corrected: {sum(f['status'] == 'corrected' for f in checked)}).",
             f"- {len(checkable) - len(checked)} rest on the source alone. That is not the same as confirmed."]
    if hinges:
        lines.append(f"- Hinges, the statements the explanation rests on: {len(hinges_checked)} of {len(hinges)} checked.")
        open_ = [f"{i}" + (f" ({f['note']})" if f["note"] else "") for i, f in hinges if i not in hinges_checked]
        if open_:
            lines.append("- Hinges not checked: " + "; ".join(open_))
    else:
        lines.append("- No hinges are marked, so it is not known whether the central statements were checked.")
    return lines


def check_structure(run, facts, titles, files, errors, warnings):
    groups = sorted({group_of(i) for i in facts}, key=group_order)
    if "O" not in groups:
        errors.append("no O facts: dossier/overview.md must say what the source is, who made it, and its caveats")
    map_facts = [f for i, f in facts.items() if group_of(i) == "M"]
    if not map_facts:
        errors.append("no M facts: dossier/map.md must list the parts and how they connect")
    elif not any(f["kind"] == "link" for f in map_facts):
        warnings.append("map.md has no `link` facts: say what flows between the parts, including loops")
    parts = [g for g in groups if g.startswith("P")]
    if not parts:
        errors.append("no parts: each part of the map needs its own file under dossier/parts/")
    if not any(g.startswith("SC") for g in groups):
        warnings.append("no scenarios (SC facts): trace at least one concrete situation end to end")
    if "C" not in groups:
        warnings.append("no C facts: record the source's own findings, results and limitations in claims.md")
    if not os.path.isfile(os.path.join(run, "dossier", "glossary.md")):
        warnings.append("dossier/glossary.md is missing: define every term a newcomer would not know")
    map_text = " ".join(f["text"] for f in map_facts)
    for part in parts:
        if not re.search(rf"\b{part}\b", map_text):
            warnings.append(f"{part} is not named in any M fact: the map should mention every part by its ID")
        if part not in titles:
            warnings.append(f"{part} has no title: start its file with `# {part} · Name`")
        path = files[part]
        headings, questions = [], 0
        with open(path, encoding="utf-8") as f:
            for line in f:
                if line.startswith("## "):
                    headings.append(line[3:].strip().lower())
                elif QUESTION.match(line):
                    questions += 1
        for section in PART_SECTIONS:
            if not any(h.startswith(section) for h in headings):
                errors.append(f"{rel(path, run)}: {part} has no `## {section.capitalize()}` section")
        kinds = Counter(f["kind"] for i, f in facts.items() if group_of(i) == part)
        if not (kinds["step"] or kinds["rule"]):
            warnings.append(f"{part} has no `step` or `rule` facts: the mechanism is not written down yet")
        if not kinds["failure"]:
            warnings.append(f"{part} has no `failure` facts: record what happens when it goes wrong, "
                            "or add a gap saying the source is silent")
        if questions < 3:
            warnings.append(f"{part} answers {questions} newcomer question(s); go through the question bank again")
    return groups


def check_reading(sources, cited_pages, errors, warnings):
    lines = []
    for sid, src in sources.items():
        span = re.fullmatch(r"(\d+)(?:\s*[-–]\s*(\d+))?", src.get("pages", "").strip())
        if not span:
            if src["type"] == "provided" and not src.get("read"):
                warnings.append(f"{sid}: add `read:` saying how much of the provided source was read")
            lines.append(f"- {sid} ({src['type']}): {src['title']} · read: {src.get('read', 'not stated')}")
            continue
        first, last = (1, int(span.group(1))) if not span.group(2) else (int(span.group(1)), int(span.group(2)))
        total = max(0, last - first + 1)
        every = set(range(first, last + 1))
        read = src.get("read", "").strip().lower()
        read_pages = every if read == "all" else pages_in("p" + read.replace(",", " p")) & every
        unread = every - read_pages
        uncited = every - cited_pages.get(sid, set())
        if unread and src["type"] == "provided":
            errors.append(f"{sid}: pages {ranges(unread)} of the provided source were not read "
                          f"(`read: {src.get('read', '')}`, `pages: {src['pages']}`)")
        line = f"- {sid} ({src['type']}): {src['title']} · {total} pages · read: {src.get('read', 'not stated')}"
        if uncited and src["type"] == "provided":
            line += f" · pages no fact cites: {ranges(uncited)}"
            warnings.append(f"{sid}: no fact cites pages {ranges(uncited)}; check that nothing on them was skipped")
        lines.append(line)
    return lines


# ---------- inventory ----------

def write_inventory(run, facts, titles, groups, reading):
    status = Counter(f["status"] for f in facts.values())
    out = ["# Inventory", "",
           "Generated by `dossier.py lint`. Do not edit; fix the dossier files and run the lint again.", "",
           f"{len(facts)} items in {len(groups)} groups · " +
           " · ".join(f"{status[s]} {s}" for s in STATUSES if status[s]), "",
           "| Group | Title | Items | Steps and rules | Params | Failures | Diffs | Verified | Corrected | Gaps |",
           "|---|---|---|---|---|---|---|---|---|---|"]
    for group in groups:
        mine = [f for i, f in facts.items() if group_of(i) == group]
        kinds, stats = Counter(f["kind"] for f in mine), Counter(f["status"] for f in mine)
        out.append(f"| {group} | {titles.get(group, '')} | {len(mine)} | {kinds['step'] + kinds['rule']} | "
                   f"{kinds['param']} | {kinds['failure']} | {kinds['diff']} | {stats['verified']} | "
                   f"{stats['corrected']} | {stats['gap']} |")
    sections = (("corrected", "Corrections", "The provided source is out of date or wrong here."),
                ("gap", "Gaps", "Questions that matter and that no source answers. Never fill these in."),
                ("inferred", "Inferred", "Reasoning of ours, not stated by any source. Label it as such."))
    for key, title, lead in sections:
        rows = [(i, f) for i, f in facts.items() if f["status"] == key]
        if rows:
            out += ["", f"## {title}", "", lead, ""]
            for i, f in rows:
                note = f" (the source says: {f['note']})" if key == "corrected" and f["note"] else ""
                out.append(f"- {i} · {f['text']}{note}")
    names = Counter()
    for f in facts.values():
        for name in re.split(r"[;,]", f["for"]):
            if name.strip():
                names[name.strip()] += 1
    if names:
        out += ["", "## Names used in `for:`", "",
                ", ".join(f"{n} ({c})" for n, c in names.most_common())]
    out += ["", "## Verification", ""] + verification_summary(facts)
    out += ["", "## Reading coverage", ""] + reading
    path = os.path.join(run, "dossier", "inventory.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")
    return path


def lint(run):
    errors, warnings = [], []
    sources = read_sources(run, errors, warnings)
    facts, titles, files = read_dossier(run, errors, warnings)
    cited_pages = check_facts(facts, sources, errors, warnings)
    groups = check_structure(run, facts, titles, files, errors, warnings) if facts else []
    reading = check_reading(sources, cited_pages, errors, warnings)
    if facts:
        path = write_inventory(run, facts, titles, groups, reading)
        print(f"inventory: {rel(path, run)}")
    status = Counter(f["status"] for f in facts.values())
    print(f"{len(facts)} items in {len(groups)} groups · {len(sources)} sources · " +
          " · ".join(f"{status[s]} {s}" for s in STATUSES if status[s]))
    for line in verification_summary(facts) if facts else []:
        print("  " + line.lstrip("- "))
    for label, items in (("ERROR", errors), ("warning", warnings)):
        for item in items:
            print(f"{label}: {item}")
    print(f"{len(errors)} error(s), {len(warnings)} warning(s)")
    return 1 if errors else 0


# ---------- scaffolding ----------

SOURCES_INDEX = """# Sources

One line per source inside the block below.
Types: `provided` (what the user gave), `primary` (official docs, source code, specs, original
papers, data), `secondary` (commentary; a lead to follow, never proof).

```sources
S1 | provided | {title} | file: sources/S1-source.txt | pages: 0 | read:
```
"""

OVERVIEW = """# Overview: {title}

## What this is

## Why it matters

## How the source is organised

## Who and what it covers

## Caveats and limits

## Questions for the scope stage
Choices only the user can make. They are asked once, later, by the scope stage.

```facts
O.1 | context |  | src: S1 | status: source
```
"""

MAP = """# Map

## The whole thing in one paragraph

## The running example
One concrete input that every part will handle in turn.

## Parts and connections
One `part` fact per part, naming it by ID and saying which problem it answers (for example
"P1 Intake exists because ..."). One `link` fact per hand-over between parts, loops included.

```facts
M.1 | part |  | src: S1 | status: source
M.2 | link |  | src: S1 | status: source
```
"""

SCENARIOS = """# Scenarios

Concrete situations traced end to end through the parts.

## SC1 · <situation>
Trigger:

```facts
SC1.1 | step |  | src: S1 | status: source
```
"""

CLAIMS = """# Claims

What the source itself concludes: findings, results with their numbers, recommendations,
and the limits its authors admit.

## C · Claims of the source

```facts
C.1 | claim |  | src: S1 | status: source
```
"""

GLOSSARY = """# Glossary

Every term a newcomer would not know, in one plain sentence each.

- **term**: meaning.
"""

PART = """# P{n} · {name}

## In one sentence

## Why it exists
The problem:

The obvious approaches, and why each one fails:

## Where it sits
Comes after:
Hands over to:
Not responsible for:

## Mechanism

```facts
P{n}.1 | step |  | src: S1 | status: source
```

## Worked example

## How implementations differ

## Newcomer questions

Q:
A:
"""


def write_new(path, text):
    if os.path.exists(path):
        print(f"kept    {path}")
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"created {path}")


def init(run, title):
    os.makedirs(os.path.join(run, "dossier", "parts"), exist_ok=True)
    write_new(os.path.join(run, "sources", "index.md"), SOURCES_INDEX.format(title=title))
    for name, text in (("overview.md", OVERVIEW.format(title=title)), ("map.md", MAP),
                       ("scenarios.md", SCENARIOS), ("claims.md", CLAIMS), ("glossary.md", GLOSSARY)):
        write_new(os.path.join(run, "dossier", name), text)
    return 0


def part(run, number, name):
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-") or "part"
    write_new(os.path.join(run, "dossier", "parts", f"P{number}-{slug}.md"), PART.format(n=number, name=name))
    return 0


def main():
    ap = argparse.ArgumentParser(description="Scaffold and check a research dossier.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("init", help="create the run folder skeleton")
    p.add_argument("run")
    p.add_argument("title")
    p = sub.add_parser("part", help="create one part file from the template")
    p.add_argument("run")
    p.add_argument("number", type=int)
    p.add_argument("name")
    p = sub.add_parser("lint", help="check the dossier and rewrite inventory.md")
    p.add_argument("run")
    args = ap.parse_args()
    run = os.path.abspath(os.path.expanduser(args.run))
    if args.cmd == "init":
        sys.exit(init(run, args.title))
    if args.cmd == "part":
        sys.exit(part(run, args.number, args.name))
    sys.exit(lint(run))


if __name__ == "__main__":
    main()
