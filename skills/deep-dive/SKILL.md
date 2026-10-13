---
name: deep-dive
description: >-
  One command from "here is a paper" (or a link, a repository, or just a topic) to a finished,
  fully detailed explainer: research the whole source, confirm the scope with the user once, then
  build the output with the installed output skill and check that nothing in scope was dropped.
  Use this whenever the user hands over a paper, PDF, arXiv link, article, repository or topic and
  wants it understood and presented in full, even if they do not name the skill: "deep dive this
  paper", "help me really understand X", "make an explainer for this paper", "和我一起 deep dive 这篇
  paper", "把这篇 paper 的全部重点做出来", "帮我把这个 topic 讲清楚". Also use it to continue a deep dive
  that already has a run folder. Not for a quick summary or a single question about a paper.
argument-hint: "<paper, link, repo or topic>"
---

# Deep dive: source in, finished explainer out

The user gives a source or a topic. They get back a finished output that covers all of it in
detail. In between there are three stages, each a skill of its own, and each hands the next one
a file:

| Stage | Skill | Hands over | Needs the user |
|---|---|---|---|
| 1. Research | `research` | `dossier/`: everything learned, each statement with its source and how far it can be trusted | no |
| 2. Scope | `scope` | `scope.md`: what is in, what is out, how it will be told, confirmed by the user | **once** |
| 3. Produce | the output skill named in the scope | `output/`, and `coverage.md` showing where each in-scope item appears | no |

The stages are separate so that each can be swapped or used alone: any source can go in, any
output skill can come out, and a finished dossier can be given to a different output skill later
without researching again.

## How to run the stages

Invoke each stage's skill by name (`research`, `scope`, and the output skill) with the skill
tool. If the kit was installed as a plugin, the names carry the plugin prefix, for example
`turn-anything-into-3b1b:research`. If a stage's skill cannot be invoked that way, read its `SKILL.md` in the
folder next to this one (`../research/SKILL.md`, `../scope/SKILL.md`) and follow it.

Paths below are relative to this skill's folder.

| File | What it is |
|---|---|
| `scripts/check_coverage.py` | `plan` lists what the output owes; `check` verifies that it was delivered. |
| `references/produce.md` | Stage 3 in full: the brief for the output skill, the coverage ledger, the final report. Read it when stage 3 starts. |
| `references/output-skills.md` | What makes a skill usable as the output stage, and how to add another one. |

## Before starting

**Find or create the run folder.** If the user points at an existing run folder, or one for
this source already exists in the working directory, continue it. Otherwise the research stage
creates `deep-dive-<short-slug>/` in the current working directory. If that directory is
temporary and will not outlive the session, say so in the final report so the user can keep the
files.

**See where the run stands** and start at the first stage that is not finished:

| What is in the run folder | Start at |
|---|---|
| No `dossier/`, or its lint fails | Stage 1 |
| A clean dossier, but no `scope.md` or an empty `signoff:` | Stage 2 |
| A signed-off scope, but the coverage check does not pass | Stage 3, continuing from what `coverage.md` shows as done |
| The coverage check passes | Nothing to build: report what exists and ask what they want next |

A run that was cut off partway (a usage limit, a lost connection, a closed session) loses
nothing: the files are on disk, and the table above says where to pick it up.

**Note what the user has already decided.** Anything in their request about what to cover, who
it is for, the language, the format, or which things to compare is a decision. Carry it into
stage 2 so that it is not asked again.

## Stage 1: research

Invoke the `research` skill with the source and the run folder. It reads the whole source,
checks it against primary sources, writes the dossier, and lints it. Do not stop for the user
when it finishes; give a two-line progress note and go on.

## Stage 2: scope

Invoke the `scope` skill with the run folder. It shows one short page, asks at most four
questions in a single round, and writes `scope.md`. **This is the only planned stop.** Wait for
the answer here and nowhere else.

## Stage 3: produce

Read `references/produce.md` and follow it. In short:

1. If the scope asks for it, close the gaps for the focus first (the `research` skill's
   deepening pass), then lint again.
2. Run `python3 scripts/check_coverage.py plan <run>` to list every item the output owes and
   start the ledger.
3. Invoke the output skill named in `scope.md` and give it the brief described in `produce.md`:
   the dossier is the content, the scope is the contract, the output goes in `<run>/output/`.
4. Build all of it. Fill in the ledger as each piece is built: the place of each item, and for
   corrected and inferred items the words on screen that mark them.
5. Run `python3 scripts/check_coverage.py check <run>` and fix what it reports until it passes.
   Then open the output at a sample of the items the check could not match by a string.
6. Give the final report.

Build everything that is in scope before reporting. A sample of two chapters is not the
deliverable unless the user asked for a sample.

## Talking to the user

- Use the language they are using. The output's language is whatever the scope says, which may
  be different.
- One planned stop, at the scope. Outside it, keep going; do not ask for permission to continue
  to the next stage or the next chapter.
- Progress notes are one or two lines at each stage boundary. The user does not want to read
  paragraphs; put detail in the files.
- If something truly blocks the run (the source cannot be read, a required tool is missing), say
  exactly what and what you tried, and continue with whatever does not depend on it.
- Do not present a guess as a finding. The dossier's labels (checked, corrected, our reasoning,
  unknown) carry through to what you tell the user and to what appears in the output.

## When there is no output skill

If the output skill named in the scope is not installed, say so in one line and build the output
directly from the brief in `references/produce.md`, as one self-contained page. The coverage
check applies all the same. Mention in the final report that the dedicated output skill was not
available, so the user knows the form can be improved by installing it.
