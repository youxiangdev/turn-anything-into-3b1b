#!/usr/bin/env python3
"""Run the kit's scripts against the invented fixture.

    python3 tests/run_tests.py

Each case copies the fixture, changes one thing, and checks that the script
notices. Exit code 1 if any case fails.
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIXTURE = os.path.join(ROOT, "tests", "fixture", "parcel-lockers")
DOSSIER = os.path.join(ROOT, "skills", "research", "scripts", "dossier.py")
PDF_PAGES = os.path.join(ROOT, "skills", "research", "scripts", "pdf_pages.py")
TO_TEXT = os.path.join(ROOT, "skills", "research", "scripts", "to_text.py")
COVERAGE = os.path.join(ROOT, "skills", "deep-dive", "scripts", "check_coverage.py")
EXPLAINER = os.path.join(ROOT, "skills", "visual-explainer")

results = []


def run(*args):
    proc = subprocess.run([sys.executable, *args], capture_output=True, text=True)
    return proc.returncode, proc.stdout + proc.stderr


def copy():
    tmp = tempfile.mkdtemp(prefix="kit-test-")
    dest = os.path.join(tmp, "run")
    shutil.copytree(FIXTURE, dest)
    return dest


def edit(path, old, new, count=1):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    assert old in text, f"fixture no longer contains {old!r}"
    with open(path, "w", encoding="utf-8") as f:
        f.write(text.replace(old, new, count))


def case(name, code, out, want_code, *want_text):
    ok = code == want_code and all(re.search(t, out) for t in want_text)
    results.append(ok)
    print(("PASS  " if ok else "FAIL  ") + name)
    if not ok:
        print(f"      exit {code}, wanted {want_code}; wanted text: {want_text}")
        print("      " + out.strip().replace("\n", "\n      ")[-1500:])


def lint_after(name, rel, old, new, *want):
    run_dir = copy()
    edit(os.path.join(run_dir, rel), old, new)
    code, out = run(DOSSIER, "lint", run_dir)
    case(name, code, out, 1, *want)
    shutil.rmtree(os.path.dirname(run_dir))


def coverage_after(name, rel, old, new, *want):
    run_dir = copy()
    edit(os.path.join(run_dir, rel), old, new)
    code, out = run(COVERAGE, "check", run_dir)
    case(name, code, out, 1, *want)
    shutil.rmtree(os.path.dirname(run_dir))


P2 = "dossier/parts/P2-compartment-assignment.md"

# ---- dossier lint ----
run_dir = copy()
code, out = run(DOSSIER, "lint", run_dir)
case("lint: the fixture is clean", code, out, 0, r"24 items in 6 groups", r"0 error\(s\), 0 warning\(s\)")
with open(os.path.join(run_dir, "dossier", "inventory.md"), encoding="utf-8") as f:
    inventory = f.read()
case("lint: inventory lists the correction, the gap and the inferred item", 0, inventory, 0,
     r"## Corrections\n[\s\S]*P2\.7", r"## Gaps\n[\s\S]*P2\.9", r"## Inferred\n[\s\S]*P2\.8", r"\| O \| Overview \|")
case("lint: inventory says how much was checked against a second source", 0, inventory, 0,
     r"## Verification\n[\s\S]*2 of the 22 statements", r"Hinges[^\n]*2 of 2 checked")
shutil.rmtree(os.path.dirname(run_dir))

lint_after("lint: a reused ID is an error", P2, "P2.3 | step", "P2.2 | step", r"P2\.2 is already used")
lint_after("lint: a missing status is an error", P2, "show: HELD | src: S1 p5 | status: source", "show: HELD | src: S1 p5",
           r"P2\.3 needs `status:`")
lint_after("lint: citing an unlisted source is an error", P2, "src: S1 p5; S2", "src: S1 p5; S9", r"cites S9")
lint_after("lint: `verified` needs two sources", P2, "src: S1 p5; S2 | status: verified", "src: S1 p5 | status: verified",
           r"P2\.4 is `verified` and needs")
lint_after("lint: `corrected` needs a note", P2, " | note: the paper says 24 hours; the operator's current developer guide says 48", "",
           r"P2\.7 is `corrected` and needs `note:`")
lint_after("lint: a part without its worked example is an error", P2, "## Worked example", "## An example",
           r"P2 has no `## Worked example` section")
lint_after("lint: unread pages of the provided source are an error", "sources/index.md", "read: 1-8", "read: 1-5",
           r"pages 6-8 of the provided source were not read")
lint_after("lint: a | inside a statement is caught", P2, "so that no other courier can be given it", "so that no | other courier",
           r"is not `key: value`")

run_dir = copy()
edit(os.path.join(run_dir, P2), " | status: verified | hinge: yes", " | status: verified")
edit(os.path.join(run_dir, P2), " | status: corrected | hinge: yes", " | status: corrected")
code, out = run(DOSSIER, "lint", run_dir)
case("lint: a dossier with no hinge marked is reported as a warning", code, out, 0, r"no item is marked `hinge: yes`")
shutil.rmtree(os.path.dirname(run_dir))

run_dir = copy()
edit(os.path.join(run_dir, P2), "show: pickCompartment() | src: S1 p4 | status: source",
     "show: pickCompartment() | src: S1 p4 | status: source | hinge: yes")
code, out = run(DOSSIER, "lint", run_dir)
case("lint: a hinge that rests on one source is reported as a warning", code, out, 0,
     r"P2\.2 is a hinge and rests on one source alone", r"Hinges not checked: P2\.2")
shutil.rmtree(os.path.dirname(run_dir))

lint_after("lint: a hinge cannot be our own reasoning", P2, "src: S1 p7 | status: inferred",
           "src: S1 p7 | status: inferred | hinge: yes", r"P2\.8 is a hinge but is `inferred`")

run_dir = copy()
edit(os.path.join(run_dir, P2), " | show: HOLD_MINUTES = 10", "")
code, out = run(DOSSIER, "lint", run_dir)
case("lint: a param without `show:` is reported as a warning", code, out, 0, r"P2\.4 is a `param` without `show:`")
shutil.rmtree(os.path.dirname(run_dir))

run_dir = copy()
edit(os.path.join(run_dir, "sources", "index.md"), "pages: 8 | read: 1-8", "pages: 3-8 | read: 3-8")
code, out = run(DOSSIER, "lint", run_dir)
case("lint: a page range for an excerpt is understood", code, out, 0, r"0 error\(s\), 0 warning\(s\)")
shutil.rmtree(os.path.dirname(run_dir))
lint_after("lint: unread pages inside an excerpt's range are an error", "sources/index.md",
           "pages: 8 | read: 1-8", "pages: 3-8 | read: 3-5", r"pages 6-8 of the provided source were not read")

run_dir = copy()
edit(os.path.join(run_dir, "dossier", "claims.md"), "src: S1 p8 | status: source", "src: S1 p7 | status: source", 2)
code, out = run(DOSSIER, "lint", run_dir)
case("lint: pages no fact cites are reported as a warning", code, out, 0, r"no fact cites pages 8")
shutil.rmtree(os.path.dirname(run_dir))

run_dir = copy()
edit(os.path.join(run_dir, P2), "show: Locker full", "show: scan \\| retry")
code, out = run(DOSSIER, "lint", run_dir)
case("lint: an escaped \\| is accepted", code, out, 0, r"0 error\(s\)")
shutil.rmtree(os.path.dirname(run_dir))

# ---- scaffolding ----
tmp = tempfile.mkdtemp(prefix="kit-test-")
run_dir = os.path.join(tmp, "new-run")
code, out = run(DOSSIER, "init", run_dir, "A new subject")
code2, out2 = run(DOSSIER, "part", run_dir, "1", "First part")
made = all(os.path.isfile(os.path.join(run_dir, p)) for p in (
    "sources/index.md", "dossier/overview.md", "dossier/map.md", "dossier/scenarios.md",
    "dossier/claims.md", "dossier/glossary.md", "dossier/parts/P1-first-part.md"))
case("init and part create the skeleton", code + code2 + (0 if made else 1), out + out2, 0)
code, out = run(DOSSIER, "lint", run_dir)
case("lint: an unfilled skeleton does not pass", code, out, 1, r"has an empty statement")
shutil.rmtree(tmp)

# ---- coverage ----
code, out = run(COVERAGE, "check", FIXTURE)
case("coverage: the fixture passes", code, out, 0, r"Owed: 22 · covered: 21 · cut on purpose: 1 · missing: 0",
     r"12 matched by an exact string in the output · 9 rest on the ledger alone",
     r"Places checked against outline\.txt \(20 places\): 21 match · 0 do not", r"\nOK:")

coverage_after("coverage: a real name dropped from the output is caught", "output/index.html",
               "<code>HOLD_MINUTES = 10</code>", "a short hold", r"NOT FOUND IN THE OUTPUT", r"P2\.4 @ .*`HOLD_MINUTES = 10`")
coverage_after("coverage: an item with no place in the ledger is caught", "coverage.md",
               "P1.3 | check-in · frame 7\n", "", r"MISSING", r"P1\.3 · ")
coverage_after("coverage: a frame the outline does not have is caught", "coverage.md",
               "C.2 | findings · frame 19", "C.2 | findings · frame 25", r"WRONG PLACE", r"C\.2 @ .*frame 25 is not in the outline")
coverage_after("coverage: a frame that sits in another chapter is caught", "coverage.md",
               "P1.2 | check-in · frame 6", "P1.2 | check-in · frame 9", r"WRONG PLACE", r"P1\.2 @ .*frame 9 is in the chapter")
coverage_after("coverage: a place without a frame number is caught when there is an outline", "coverage.md",
               "O.1 | intro · frame 0", "O.1 | the intro", r"O\.1 @ the intro · names no frame number")
coverage_after("coverage: a corrected item needs a label", "coverage.md", " | label: the paper says one", "",
               r"NO LABEL", r"corrected \(the source says otherwise\): P2\.7")
coverage_after("coverage: a label that is not in the output is caught", "coverage.md", "label: the paper says one",
               "label: the source is out of date", r"LABEL NOT FOUND IN THE OUTPUT", r"P2\.7 @ .*`the source is out of date`")
coverage_after("coverage: the wording given with `as:` must be in the output", "coverage.md", "as: two days", "as: a weekend",
               r"NOT FOUND IN THE OUTPUT", r"P2\.7 @ .*`as: a weekend`")
coverage_after("coverage: a group without a decision is caught", "scope.md", "SC1 | in\n", "",
               r"group SC1 has no decision")
coverage_after("coverage: an unsigned scope is caught", "scope.md", "signoff: 2026-01-15 · confirmed by the user", "signoff:",
               r"`signoff:` is empty")
coverage_after("coverage: a cut needs a reason", "coverage.md",
               "P2.8 | cut | reason: restates P2.7; showing both made the scene repeat itself", "P2.8 | cut",
               r"P2\.8 is cut and needs `reason:`")
coverage_after("coverage: `out` needs a reason", "scope.md",
               "O.2 | out | reason: fleet sizes do not affect how anything works; the user agreed", "O.2 | out",
               r"`O\.2` is out and needs `reason:`")

run_dir = copy()
os.makedirs(os.path.join(run_dir, "output", "kit"))
os.rename(os.path.join(run_dir, "output", "index.html"), os.path.join(run_dir, "output", "kit", "index.html"))
code, out = run(COVERAGE, "check", run_dir)
case("coverage: tooling folders are skipped, and no output at all is a failure", code, out, 1,
     r"Output files read: 0", r"no output files found")
shutil.rmtree(os.path.dirname(run_dir))

run_dir = copy()
os.remove(os.path.join(run_dir, "output", "outline.txt"))
code, out = run(COVERAGE, "check", run_dir)
case("coverage: without an outline the places are not checked, and the report says so", code, out, 0,
     r"no outline of the output was found", r"\nOK:")
shutil.rmtree(os.path.dirname(run_dir))

run_dir = copy()
edit(os.path.join(run_dir, "output", "index.html"), "<code>HOLD_MINUTES = 10</code>", "a short hold")
os.makedirs(os.path.join(run_dir, "output", "work"))
with open(os.path.join(run_dir, "output", "work", "facts.json"), "w", encoding="utf-8") as f:
    f.write('{"P2.4": "HOLD_MINUTES = 10"}')
code, out = run(COVERAGE, "check", run_dir)
case("coverage: a helper file in output/work does not count as output", code, out, 1,
     r"Output files read: 1: output/index\.html", r"P2\.4 @ .*`HOLD_MINUTES = 10`")
shutil.rmtree(os.path.dirname(run_dir))

run_dir = copy()
edit(os.path.join(run_dir, "scope.md"), "C   | in", "C   | out | reason: the user wants the findings later")
code, out = run(COVERAGE, "check", run_dir)
case("coverage: a group that is out is not owed", code, out, 0, r"Owed: 20 ", r"1 out \(C\)")
shutil.rmtree(os.path.dirname(run_dir))

run_dir = copy()
os.remove(os.path.join(run_dir, "coverage.md"))
code, out = run(COVERAGE, "plan", run_dir)
code2, out2 = run(COVERAGE, "plan", run_dir)
with open(os.path.join(run_dir, "coverage.md"), encoding="utf-8") as f:
    ledger = f.read()
case("plan: writes each owed item once and is safe to run twice",
     code + code2 + (0 if ledger.count("P2.4 |") == 1 else 1), out + out2, 0,
     r"added 22 item\(s\)", r"already lists every owed item")
shutil.rmtree(os.path.dirname(run_dir))

# ---- to_text ----
tmp = tempfile.mkdtemp(prefix="kit-test-")
page = os.path.join(tmp, "page.html")
with open(page, "w", encoding="utf-8") as f:
    f.write("<html><head><title>T</title><script>var no=1;</script></head><body><h1>One</h1>"
            "<p>Hello &amp; welcome</p><h2>Two</h2><p>" + "word " * 200 + "</p></body></html>")
code, out = run(TO_TEXT, page, "-o", os.path.join(tmp, "page.txt"))
with open(os.path.join(tmp, "page.txt"), encoding="utf-8") as f:
    text = f.read()
longest = max(len(line) for line in text.split("\n"))
case("to_text: HTML becomes sectioned text with long lines wrapped",
     code + (0 if longest <= 240 and "var no" not in text else 1), out + text[:300], 0,
     r"===== SECTION 1: One =====", r"Hello & welcome", r"===== SECTION 2: Two =====")
code, out = run(TO_TEXT, os.path.join(tmp, "missing.pdf"), "-o", os.path.join(tmp, "x.txt"))
case("to_text: a missing file is reported", code, out, 1, r"no such file")
sample = os.environ.get("KIT_TEST_PDF") or os.path.join(ROOT, "tests", "fixture", "sample.pdf")
code, out = run(TO_TEXT, sample, "-o", os.path.join(tmp, "sample.txt"))
if '"backend": null' in out:
    print("SKIP  PDF extraction (no PDF backend here: install pdftotext, pypdf or PyMuPDF)")
else:
    with open(os.path.join(tmp, "sample.txt"), encoding="utf-8") as f:
        text = f.read()
    case("to_text: a PDF is extracted with page markers", code, out + text[:200], 0, r'"kind": "pdf"', r'"pages": \d+',
         r"===== PAGE 1 =====")
code, out = run(PDF_PAGES, sample, os.path.join(tmp, "pages"), "1")
if "no way to render PDF pages here" in out:
    print("SKIP  PDF page rendering (needs pdftoppm, PyMuPDF, or macOS)")
else:
    made = os.path.isfile(os.path.join(tmp, "pages", "page-001.png"))
    case("pdf_pages: page 1 of a PDF is rendered as an image", code + (0 if made else 1), out, 0, r"page-001\.png")
shutil.rmtree(tmp)

# ---- visual-explainer: the kit builds, and its demo story has an outline ----
tmp = tempfile.mkdtemp(prefix="kit-test-")
demo = os.path.join(EXPLAINER, "assets", "kit", "demo-story.js")
dist = os.path.join(tmp, "dist")
code, out = run(os.path.join(EXPLAINER, "scripts", "build.py"), "--title", "Demo", "--name", "demo", "--out", dist, demo)
pages = [os.path.join(dist, n) for n in ("demo-video.html", "demo-slides.html", "preview-demo-video.html", "preview-demo-slides.html")]
left = ""
for page in pages:
    if os.path.isfile(page):
        with open(page, encoding="utf-8") as f:
            left += "".join(m for m in re.findall(r"\{\{[A-Z]+\}\}", f.read()))
case("build: the demo story becomes a video page and a slides page",
     code + (0 if all(os.path.isfile(p) for p in pages) and not left else 1), out + left, 0, r"demo-video\.html", r"demo-slides\.html")
if shutil.which("node"):
    proc = subprocess.run(["node", os.path.join(EXPLAINER, "scripts", "outline.js"), demo], capture_output=True, text=True)
    case("outline: every frame of the demo story is listed under its chapter", proc.returncode, proc.stdout + proc.stderr, 0,
         r"(?m)^# ", r"(?m)^\s+0\s+step\s+1\s", r"Total: \d+ frames")
    outline = os.path.join(tmp, "outline.txt")
    with open(outline, "w", encoding="utf-8") as f:
        f.write(proc.stdout)
    sys.path.insert(0, os.path.dirname(COVERAGE))
    import check_coverage
    places, chapters = check_coverage.read_outline(outline)
    total = re.search(r"Total: (\d+) frames", proc.stdout)
    case("outline: the coverage check reads the same number of places",
         0 if total and len(places) == int(total.group(1)) and chapters else 1, f"{len(places)} places, {len(chapters)} chapters", 0)
else:
    print("SKIP  outline of the demo story (needs Node)")
sys.path.insert(0, os.path.join(EXPLAINER, "scripts"))
try:
    import shoot
    shoot.chrome()
    have_chrome = True
except SystemExit:
    have_chrome = False
if have_chrome:
    code, out = run(os.path.join(EXPLAINER, "scripts", "shoot.py"), pages[2], "--lint")
    case("shoot: the layout lint visits every frame of the demo story", code, out, 0, r"\d+ frames, about")
else:
    print("SKIP  layout lint of the demo story (needs Chrome or Chromium)")
shutil.rmtree(tmp)

print(f"\n{sum(results)} of {len(results)} passed")
sys.exit(0 if all(results) else 1)
