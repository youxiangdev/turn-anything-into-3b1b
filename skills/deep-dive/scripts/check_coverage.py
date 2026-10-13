#!/usr/bin/env python3
"""Check that everything in scope made it into the output.

    check_coverage.py plan  RUN_DIR
    check_coverage.py check RUN_DIR [--output PATH ...] [--outline FILE]

RUN_DIR holds dossier/ (facts), scope.md (what is in and out) and coverage.md
(where each in-scope item is shown).

`plan`  lists the items the output owes and adds any that are missing to
        coverage.md, so the ledger can be filled in while building.
`check` fails (exit code 1) when:
          - an in-scope item has no place in the ledger;
          - the real names and numbers it should show (`show:` in the dossier),
            or the wording given with `as:`, cannot be found in the output;
          - a corrected or inferred item has no `label:` saying how the output
            marks it, or that wording cannot be found in the output;
          - an outline of the output exists and a place in the ledger names a
            frame that is not in it, or that sits in another chapter.
        With no --output it reads every text file under RUN_DIR/output/,
        skipping folders that hold tooling or working files (kit, work, notes,
        tmp, node_modules, shots, .git). The outline is RUN_DIR/output/outline.txt
        unless --outline names another file.

What the check can and cannot prove is printed with the result: how many items
were matched by an exact string, and how many rest on the ledger alone.

The file formats are described in ../references/produce.md.
"""
import argparse
import html
import os
import re
import sys
from collections import Counter, OrderedDict

FENCE = re.compile(r"^\s*```+\s*([A-Za-z_-]*)\s*$")
ITEM_ID = re.compile(r"^(O|M|C|P\d+|SC\d+)\.(\d+)$")
GROUP_ID = re.compile(r"^(O|M|C|P\d+|SC\d+)$")
GROUP_HEADING = re.compile(r"^#{1,3}\s+(O|M|C|P\d+|SC\d+)\s*[·:—–-]\s*(.+?)\s*$")
TEXT_FILES = (".html", ".htm", ".js", ".mjs", ".json", ".md", ".txt", ".svg", ".css", ".vtt", ".srt", ".xml")
MIN_TOKEN = 3
SKIP_DIRS = {"kit", "work", "notes", "tmp", "node_modules", "shots", ".git"}
OUTLINE_NAME = "outline.txt"
PLACE_REF = re.compile(r"\b(?:frame|slide|scene|page)s?\s+#?(\d+(?:\s*[-–,]\s*\d+)*)", re.I)
# statuses whose items must be marked as such wherever they are shown
LABELLED = {"corrected": "the source says otherwise", "inferred": "our own reasoning"}
DEFAULT_TITLES = {"O": "Overview", "M": "Map", "C": "Claims"}


def fenced(path, name):
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
    return [part.replace("\\|", "|").strip() for part in re.split(r"(?<!\\)\|", text)]


def keyed(fields):
    out = {}
    for field in fields:
        key, sep, value = field.partition(":")
        if sep and " " not in key.strip():
            out[key.strip().lower()] = value.strip()
    return out


def group_of(item_id):
    return item_id.rsplit(".", 1)[0]


def group_order(group):
    letter = re.match(r"[A-Z]+", group).group(0)
    digits = re.search(r"\d+", group)
    return (["O", "M", "P", "SC", "C"].index(letter), int(digits.group(0)) if digits else 0)


def item_order(item_id):
    return group_order(group_of(item_id)) + (int(item_id.rsplit(".", 1)[1]),)


def read_facts(run):
    facts, titles = OrderedDict(), {}
    root = os.path.join(run, "dossier")
    for base, _, names in os.walk(root):
        for name in sorted(names):
            if not name.endswith(".md") or name == "inventory.md":
                continue
            path = os.path.join(base, name)
            with open(path, encoding="utf-8") as f:
                for line in f:
                    m = GROUP_HEADING.match(line)
                    if m:
                        titles.setdefault(m.group(1), m.group(2))
            for _, line in fenced(path, "facts"):
                fields = split_fields(line)
                if len(fields) < 3 or not ITEM_ID.match(fields[0]):
                    continue
                extra = keyed(fields[3:])
                show = [t.strip().strip("`").strip() for t in extra.get("show", "").split(";")]
                facts[fields[0]] = {"kind": fields[1].lower(), "text": fields[2],
                                    "status": (extra.get("status", "").split() or [""])[0].lower(),
                                    "show": [t for t in show if t]}
    for group, title in DEFAULT_TITLES.items():
        titles.setdefault(group, title)
    return facts, titles


def read_scope(run, facts, problems):
    path = os.path.join(run, "scope.md")
    groups, items = {}, {}
    if not os.path.isfile(path):
        problems.append("scope.md is missing: confirm the scope before building")
        return groups, items
    known_groups = {group_of(i) for i in facts}
    for no, line in fenced(path, "scope"):
        fields = split_fields(line)
        target = fields[0]
        decision = fields[1].lower() if len(fields) > 1 else ""
        extra = keyed(fields[2:])
        where = f"scope.md:{no}"
        if decision not in ("in", "out"):
            problems.append(f"{where}: `{target}` needs `in` or `out`")
            continue
        if decision == "out" and not extra.get("reason"):
            problems.append(f"{where}: `{target}` is out and needs `reason:`")
        if GROUP_ID.match(target):
            if target not in known_groups:
                problems.append(f"{where}: group {target} is not in the dossier")
            groups[target] = decision
        elif ITEM_ID.match(target):
            if target not in facts:
                problems.append(f"{where}: item {target} is not in the dossier")
            items[target] = decision
        else:
            problems.append(f"{where}: `{target}` is neither a group (P3) nor an item (P3.4)")
    for group in sorted(known_groups - set(groups), key=group_order):
        problems.append(f"scope.md: group {group} has no decision; every group must be `in` or `out`")
    settings = {}
    for _, line in fenced(path, "settings"):
        key, sep, value = line.partition(":")
        if sep:
            settings[key.strip().lower()] = value.strip()
    if not settings.get("signoff"):
        problems.append("scope.md: `signoff:` is empty; the scope has not been confirmed yet")
    return groups, items


def required_items(facts, groups, items):
    need = []
    for item, fact in facts.items():
        if fact["status"] == "gap":
            continue
        decision = items.get(item, groups.get(group_of(item)))
        if decision == "in":
            need.append(item)
    return sorted(need, key=item_order)


def read_ledger(run):
    path = os.path.join(run, "coverage.md")
    ledger = {}
    if os.path.isfile(path):
        for _, line in fenced(path, "coverage"):
            fields = split_fields(line)
            if ITEM_ID.match(fields[0]):
                ledger[fields[0]] = {"where": fields[1] if len(fields) > 1 else "", **keyed(fields[2:])}
    return path, ledger


def escape(text):
    return text.replace("|", "\\|")


def plan(run):
    problems = []
    facts, titles = read_facts(run)
    groups, items = read_scope(run, facts, problems)
    need = required_items(facts, groups, items)
    path, ledger = read_ledger(run)
    todo = [i for i in need if i not in ledger]
    for p in problems:
        print(f"ERROR: {p}")
    counts = Counter(group_of(i) for i in need)
    print(f"{len(need)} items owed by the output, in {len(counts)} groups:")
    for group in sorted(counts, key=group_order):
        print(f"  {group:<5} {counts[group]:>4}  {titles.get(group, '')}")
    if todo:
        lines = []
        if not os.path.isfile(path):
            lines += ["# Coverage", "",
                      "Where each in-scope item of the dossier is shown in the output.",
                      "Fill in the second field while building: the chapter or scene and the beat.",
                      "Write `cut` there, with `reason:`, for anything deliberately left out.", ""]
        lines += ["```coverage"]
        last = None
        for item in todo:
            if group_of(item) != last:
                last = group_of(item)
                lines.append(f"# {last} · {titles.get(last, '')}")
            lines.append(f"{item} |  | note: {escape(facts[item]['text'])}")
        lines += ["```", ""]
        with open(path, "a", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
        print(f"added {len(todo)} item(s) to {os.path.relpath(path, run)}")
    else:
        print("coverage.md already lists every owed item")
    return 1 if problems else 0


def variants(text):
    """The same text in the forms a token may take inside HTML or a JS string."""
    forms = [text, html.unescape(text)]
    forms.append(re.sub(r"\\(['\"`\\/])", r"\1", forms[1]))
    forms.append(re.sub(r"<[^>]+>", "", forms[1]))
    return [re.sub(r"\s+", " ", form).lower() for form in forms]


def squash(text):
    return re.sub(r"\s+", " ", text).strip().lower()


def read_outline(path):
    """An outline lists the places of the output: a line starting with `# ` opens a chapter,
    a line starting with a number is the place with that number."""
    places, chapters, chapter = {}, [], ""
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            if line.startswith("# "):
                chapter = squash(line[2:])
                chapters.append(chapter)
                continue
            m = re.match(r"\s*(\d+)\b", line)
            if m:
                places.setdefault(int(m.group(1)), chapter)
    return places, chapters


def place_problem(where, places, chapters):
    """Why a place in the ledger does not match the outline, or None when it does."""
    numbers = [int(n) for ref in PLACE_REF.findall(where) for n in re.findall(r"\d+", ref)]
    if not numbers:
        return "names no frame number"
    text = squash(where)
    named = {c for c in chapters if c and (c in text or c.split(" · ", 1)[-1] in text)}
    for n in numbers:
        if n not in places:
            return f"frame {n} is not in the outline"
        if named and places[n] and places[n] not in named:
            return f"frame {n} is in the chapter \"{places[n]}\""
    return None


def load_outputs(run, paths, outline=None):
    files = []
    for path in paths or [os.path.join(run, "output")]:
        path = os.path.abspath(os.path.expanduser(path))
        if os.path.isdir(path):
            for base, dirs, names in os.walk(path):
                dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
                files += [os.path.join(base, n) for n in sorted(names) if n.lower().endswith(TEXT_FILES)]
        elif os.path.isfile(path):
            files.append(path)
    files = [p for p in files if not (outline and os.path.abspath(p) == outline)]
    haystack = []
    for path in files:
        with open(path, encoding="utf-8", errors="replace") as f:
            haystack += variants(f.read())
    return files, haystack


def check(run, outputs, outline=None):
    problems = []
    facts, titles = read_facts(run)
    groups, items = read_scope(run, facts, problems)
    need = required_items(facts, groups, items)
    _, ledger = read_ledger(run)
    if outline:
        outline = os.path.abspath(os.path.expanduser(outline))
        if not os.path.isfile(outline):
            problems.append(f"the outline {outline} does not exist")
            outline = None
    else:
        default = os.path.join(run, "output", OUTLINE_NAME)
        outline = default if os.path.isfile(default) else None
    places, chapters = read_outline(outline) if outline else ({}, [])
    if outline and not places:
        problems.append(f"{os.path.relpath(outline, run)} lists no places: each place is a line starting with its number")
    files, haystack = load_outputs(run, outputs, outline)
    if not files:
        looked = ", ".join(outputs) if outputs else os.path.join(run, "output")
        problems.append(f"no output files found in {looked}: there is nothing to check the names and numbers against")

    def found(wording):
        needle = squash(wording)
        return any(needle in text for text in haystack)

    missing, cut, absent, unverified, covered = [], [], [], 0, 0
    by_string, misplaced, unlabelled, label_absent = 0, [], [], []
    for item in need:
        entry = ledger.get(item)
        where = (entry or {}).get("where", "").strip()
        if not where:
            missing.append(item)
            continue
        if where.lower() == "cut":
            if not entry.get("reason"):
                problems.append(f"coverage.md: {item} is cut and needs `reason:`")
            cut.append(item)
            continue
        covered += 1
        if places:
            wrong = place_problem(where, places, chapters)
            if wrong:
                misplaced.append((item, where, wrong))
        status = facts[item]["status"]
        if status in LABELLED and files:
            label = entry.get("label", "")
            if not label:
                unlabelled.append((item, status))
            elif not found(label):
                label_absent.append((item, label, where))
        lost, checked = [], False
        if entry.get("as"):
            wordings, shown_as = [entry["as"]], True
        else:
            wordings, shown_as = facts[item]["show"], False
        for token in wordings if files else []:
            if len(token) < MIN_TOKEN:
                unverified += 1
                continue
            checked = True
            if not found(token):
                lost.append(("as: " if shown_as else "") + token)
        by_string += 1 if checked and not lost else 0
        if lost:
            absent.append((item, lost, where))

    out_groups = sorted((g for g, d in groups.items() if d == "out"), key=group_order)
    gaps = [i for i, f in facts.items() if f["status"] == "gap" and groups.get(group_of(i)) == "in"]
    print(f"Scope: {sum(1 for d in groups.values() if d == 'in')} groups in, {len(out_groups)} out"
          + (f" ({', '.join(out_groups)})" if out_groups else ""))
    shown = [os.path.relpath(p, run) for p in files]
    print(f"Output files read: {len(files)}" + (": " + ", ".join(shown[:20]) if shown else "")
          + (f" and {len(shown) - 20} more" if len(shown) > 20 else ""))
    print(f"Owed: {len(need)} · covered: {covered} · cut on purpose: {len(cut)} · "
          f"missing: {len(missing)} · real names or numbers not found: {len(absent)}")
    print(f"Of the {covered} covered: {by_string} matched by an exact string in the output · "
          f"{covered - by_string - len(absent)} rest on the ledger alone")
    if places:
        print(f"Places checked against {os.path.basename(outline)} ({len(places)} places): "
              f"{covered - len(misplaced)} match · {len(misplaced)} do not")
    for p in problems:
        print(f"ERROR: {p}")
    if missing:
        print("\nMISSING: in scope, but coverage.md gives no place for them")
        for item in missing:
            print(f"  {item} · {facts[item]['text']}")
    if absent:
        print("\nNOT FOUND IN THE OUTPUT: the ledger says these are shown, but the exact strings are absent.")
        print("Show the real name or number, or add `as: <the wording used>` if it is shown another way.")
        for item, lost, where in absent:
            print(f"  {item} @ {where} · " + " · ".join(f"`{t}`" for t in lost))
    if misplaced:
        print("\nWRONG PLACE: the ledger names a place the outline does not have there.")
        print("Frame numbers shift when frames are added or moved; look the item up again and correct the ledger.")
        for item, where, wrong in misplaced:
            print(f"  {item} @ {where} · {wrong}")
    if unlabelled:
        print("\nNO LABEL: these are not plain statements of the source, and the ledger does not say how the")
        print("output marks them. Add `label: <the words on screen that mark it>` to each line.")
        for status in LABELLED:
            ids = [i for i, s in unlabelled if s == status]
            if ids:
                print(f"  {status} ({LABELLED[status]}): {', '.join(ids)}")
    if label_absent:
        print("\nLABEL NOT FOUND IN THE OUTPUT: the ledger gives these words as the label, but they are absent.")
        for item, label, where in label_absent:
            print(f"  {item} @ {where} · `{label}`")
    if cut:
        print("\nCUT ON PURPOSE: tell the user about these")
        for item in cut:
            print(f"  {item} · {ledger[item].get('reason', '(no reason given)')}")
    reminders = []
    for status, text in (("external", "not from the provided source: name where it comes from"),):
        ids = [i for i in need if facts[i]["status"] == status]
        if ids:
            reminders.append(f"  {len(ids)} {status} item(s), {text}: {', '.join(ids[:12])}"
                             + (" ..." if len(ids) > 12 else ""))
    if covered - by_string - len(absent) > 0:
        reminders.append(f"  {covered - by_string - len(absent)} covered item(s) have no exact string to search for, so only "
                         "the ledger says they are shown: look at a few of them in the output yourself")
    if not places:
        reminders.append(f"  no outline of the output was found (output/{OUTLINE_NAME}), so the places in the ledger "
                         "were not checked")
    if gaps:
        reminders.append(f"  {len(gaps)} gap(s) in scope: show them as open questions or leave them out, never fill them in")
    if unverified:
        reminders.append(f"  {unverified} `show:` string(s) shorter than {MIN_TOKEN} characters were not checked")
    if reminders:
        print("\nREMINDERS")
        print("\n".join(reminders))
    failed = bool(problems or missing or absent or misplaced or unlabelled or label_absent)
    print("\nFAILED" if failed else "\nOK: everything in scope has a place in the output")
    return 1 if failed else 0


def main():
    ap = argparse.ArgumentParser(description="Check that everything in scope made it into the output.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("plan", help="list what the output owes and extend coverage.md")
    p.add_argument("run")
    p = sub.add_parser("check", help="verify coverage.md and the output files")
    p.add_argument("run")
    p.add_argument("--output", nargs="*", default=[], help="output files or folders (default: RUN_DIR/output)")
    p.add_argument("--outline", help="a listing of the output's places (default: RUN_DIR/output/outline.txt, if present)")
    args = ap.parse_args()
    run = os.path.abspath(os.path.expanduser(args.run))
    sys.exit(plan(run) if args.cmd == "plan" else check(run, args.output, args.outline))


if __name__ == "__main__":
    main()
