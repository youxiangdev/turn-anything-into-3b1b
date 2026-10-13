# turn-anything-into-3b1b

Give it a paper, a link, a repository or just a topic. It reads all of it, checks it, and gives you back an animated explainer in the style of a 3Blue1Brown video: one that shows how the thing really works, with the real names and numbers, instead of a summary.

A set of four agent skills for **Claude Code** and **Codex**. [中文说明](README.zh-CN.md)

## Install

**One line, for Claude Code and Codex** (macOS or Linux):

```bash
curl -fsSL https://raw.githubusercontent.com/youxiangdev/turn-anything-into-3b1b/main/install.sh | bash
```

It downloads the kit into `~/.turn-anything-into-3b1b` and links the four skills into `~/.claude/skills`, and into Codex's skills folder when Codex is installed. Nothing else is touched, and a skill of yours with the same name is never overwritten. Run the same line again to update.

**Or as a Claude Code plugin** (Claude Code 2.1.275 or later):

```
/plugin install turn-anything-into-3b1b --marketplace youxiangdev/turn-anything-into-3b1b
```

Use one way or the other. With both, every skill shows up twice.

## Use

Start a new session and type:

```
/deep-dive <path to a paper, a link, a repository, or a topic>
```

| Where | How to call it |
|---|---|
| Claude Code, installed with the one line | `/deep-dive ...` |
| Claude Code, installed as a plugin | `/turn-anything-into-3b1b:deep-dive ...` |
| Codex | `$deep-dive ...`, or pick it from `/skills` |

You can also just ask: "deep dive this paper", "help me really understand how X works".

## What happens

Three stages run one after another. It stops to ask you something exactly once, at stage 2.

| Stage | Skill | What it does | What it leaves |
|---|---|---|---|
| 1 | `research` | Reads the whole source, checks the key statements against primary sources (official documentation, source code, the original papers), and writes every part down at the depth of how it works | `dossier/`: every statement, each with its source and how far it can be trusted |
| 2 | `scope` | Shows you one page: what will be covered, what was found to be out of date, how big the build is. Asks at most four questions, once | `scope.md`: the scope you confirmed |
| 3 | `visual-explainer` | Builds the explainer as two web pages from one story: a video that plays by itself, and slides you scroll through and try things in | `output/`, and `coverage.md`: where each item is shown |

Each stage also works by itself: `/research <source>` for only the dossier, `/scope <run folder>` to scope an existing one, `/visual-explainer` to explain something you describe.

A run that is cut off (a usage limit, a closed session) loses nothing. Run `/deep-dive` on the same folder and it continues where it stopped.

## What keeps it honest

Two scripts check the work, so that "it covered everything" is not just the agent's word.

- **Every statement carries a label**: from the source, checked against a second source, corrected, our own reasoning, or an open question nobody answers. An open question is never filled in with a guess.
- **The dossier lint** fails when pages of the source were not read, and reports how many statements were checked against a second source, including the handful the whole explanation rests on.
- **The coverage check** fails when something in scope is missing from the output, when a real name or number was replaced by a vague phrase, when a correction or a piece of reasoning is not marked as one on screen, or when the ledger points at a frame that does not exist.
- **It says what it could not prove.** A statement with no name or number in it cannot be searched for. The check counts those separately, and the agent is told to open a sample of them and look.

## What it is good at, and what it is not

**Good at:** anything with a mechanism. A method from a paper, a system, an algorithm, a protocol, a product, a process. The source can be a PDF, a web page, a repository, pasted text, or a topic for which it finds the sources itself.

**Proven so far:** a full paper, end to end. The other kinds of source are supported by the instructions and have had less use.

**Not yet:**

- Subjects without a mechanism: a pure mathematics concept, a history, an essay or argument. The dossier format expects steps, failure paths and a worked example.
- Plots and formulas. The drawing kit has five formats (narrated animation, step-through simulator, sequence diagram, zoomable map, tiny isometric world) and no built-in graphs or equation layout yet.
- Video, audio and slide decks as sources.

A full run on a long paper is a large job: the example run behind this kit produced about 400 items and a 370-frame explainer. Stage 2 tells you the size before you commit, and you can ask for one chapter first.

## What you need

| | Needed for |
|---|---|
| Python 3 | All the scripts. Standard library only |
| A way to read PDFs | macOS has one built in. Elsewhere, any one of: poppler (`pdftotext`, `pdftoppm`), `pypdf`, `PyMuPDF`, `pdfminer.six` |
| Node | The script outline of an explainer, and a syntax check before building |
| Chrome or Chromium | Optional: screenshots and the layout check of the built pages |
| `git` and `gh` | Optional: reading source code during verification |

## What a run leaves behind

```
deep-dive-<name>/
├── sources/        the full text of the source material, and a list of every source
├── dossier/        the research: overview, map, one file per part, scenarios, claims, glossary
├── scope.md        the scope you confirmed
├── coverage.md     each item in scope, and where it is shown
└── output/         the explainer
```

The folder is created in the directory you are working in. The research and the output are kept apart, so the same dossier can be given to a different output skill later without researching again.

## Using a different output

Stage 3 is a slot. `visual-explainer` sits in it now. Any skill that builds from content it is given can replace it or sit beside it, for example one that makes a slide deck or a written report: see [skills/deep-dive/references/output-skills.md](skills/deep-dive/references/output-skills.md). From a checkout, `./install.sh --adopt <folder>` copies such a skill in and links it.

## Update and remove

| | One-line install | Plugin |
|---|---|---|
| Update | Run the install line again | `/plugin update turn-anything-into-3b1b` |
| Remove | `bash ~/.turn-anything-into-3b1b/install.sh --remove`, then delete `~/.turn-anything-into-3b1b` | `/plugin uninstall turn-anything-into-3b1b` |

`install.sh` has a few more options (`--no-codex`, `--codex`, `--list`); see the top of the file.

## Working on the skills

```bash
git clone https://github.com/youxiangdev/turn-anything-into-3b1b
cd turn-anything-into-3b1b
./install.sh              # links this checkout, so edits take effect at once
python3 tests/run_tests.py
```

The tests run every script against `tests/fixture/`, a small invented example that describes no real system.

```
skills/
├── deep-dive/           the entry point: runs the three stages; holds the coverage check
├── research/            stage 1: text extraction, page rendering, the dossier lint
├── scope/               stage 2
└── visual-explainer/    stage 3: the drawing kit, the build script, the layout check
tests/                   script tests, the fixture, prompts for trying the skills by hand
```

## Licence and name

MIT. See [LICENSE](LICENSE).

This project is not affiliated with or endorsed by 3Blue1Brown. The name describes the kind of explanation it aims for: show the idea moving instead of describing it.
