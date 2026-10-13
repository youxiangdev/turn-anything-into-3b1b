# Stage 3: produce

The dossier holds the content and the scope says what is owed. This stage turns them into the
finished output with an output skill, and proves at the end that nothing in scope was dropped.

## Contents

- [1. Close the gaps for the focus](#1-close-the-gaps-for-the-focus)
- [2. Plan the coverage](#2-plan-the-coverage)
- [3. Brief the output skill](#3-brief-the-output-skill)
- [4. Build, and keep the ledger](#4-build-and-keep-the-ledger)
- [5. Check](#5-check)
- [6. Final report](#6-final-report)

## 1. Close the gaps for the focus

Read the `settings` block of `scope.md`. If `deepen:` asks for it, invoke the `research` skill
again on the same run folder with the focus named in `focus:`. It works through the in-scope
`gap` items and unchecked items for those things, using primary sources, and lints again. Skip
this step when `deepen:` is absent or says no, or when the in-scope groups have no gaps.

Do not renumber anything. The scope refers to items by ID.

## 2. Plan the coverage

```bash
python3 scripts/check_coverage.py plan <run>
```

This prints how many items the output owes in each group and adds every one of them to
`<run>/coverage.md` with an empty place. An item is owed when its group (or the item itself) is
`in` in the scope and its status is not `gap`.

Read the list before designing anything. The number is the size of the job, and it is usually
larger than instinct suggests: that instinct is the pull towards summarising.

## 3. Brief the output skill

Invoke the skill named in `output_skill:`. Give it this brief, filled in from the run folder.
The brief says **what** must be conveyed; the output skill decides **how** it looks and moves.
Where the output skill has its own rules about structure, pacing or format, follow the output
skill.

> **What is already settled.** Research and scope are finished. If the output skill has steps
> of its own for scoping, researching, or agreeing an outline with the user, treat them as done:
> `scope.md` is the agreed scope and the dossier is the fact sheet. The user has confirmed the
> scope and expects the whole build without another stop, so do not pause to propose an outline
> or to show a sample chapter, unless the notes in `scope.md` say they want to see one first.
>
> **Content.** Build only from `<run>/dossier/`. Do not add facts from memory or from the
> original source; if something needed is not in the dossier, it goes back to the research
> stage, not straight into the output.
>
> **Contract.** `<run>/scope.md` says which groups and items are in. Everything in must appear.
> `<run>/coverage.md` lists each owed item; record where each one is shown.
>
> **Audience, language, focus, versions.** As given in the `settings` block of `scope.md`.
>
> **Where to write.** Put every output file under `<run>/output/`.
>
> **The order of telling.**
> 1. Begin with why the subject exists and the whole map (`map.md`), using the running example,
>    before any single part.
> 2. Then each in-scope part, in the map's order. Inside a part, follow the order of its file:
>    the problem; the obvious approaches and how each one breaks; the mechanism, step by step,
>    on the worked example; the real names and numbers, attached once the idea is clear; what
>    happens when it fails; how the implementations differ; the one question they are all
>    answering.
> 3. For the things named in `focus:`, show the difference in full. Bring in the others where
>    they do something notably different.
> 4. Show each in-scope scenario (`scenarios.md`) end to end at least once.
> 5. Give the source's own conclusions (`claims.md`) with their numbers.
> 6. By the end of a part, a viewer should be able to answer that part's "Newcomer questions".
>    Use them as the test of whether the part is clear.
> 7. Explain each glossary term the first time it appears.
>
> **Honesty on screen.**
> - A `corrected` item shows what is true now and says that the source states otherwise.
> - An `inferred` item is presented as our reasoning, not as what the source says.
> - Values invented for a worked example are marked as illustrative.
> - A `gap` is shown as an open question or left out. It is never filled in.
> - For every `corrected` and `inferred` item, record in the ledger the words on screen that mark
>   it (`label:`). The check looks for those words in the output.
>
> **A listing of places.** When the output has numbered places (frames, slides, pages), save a
> listing of them as `<run>/output/outline.txt` and refer to places in the ledger by those
> numbers. The check then confirms that each place exists.
>
> **Working files.** Notes, extracted facts and other helper files go in `<run>/work/`, never
> under `<run>/output/`: every text file under `output/` counts as output.
>
> **Depth.** The real identifiers, numbers and error messages in each item's `show:` appear on
> screen as written. A caption that says "a flag controls this" where the dossier names the flag
> is a summary, and the coverage check will report it.

## 4. Build, and keep the ledger

Follow the output skill's own process, including its checks in a real browser when it has them.

Build in the map's order and keep going until every in-scope group is built. As each piece is
finished, fill in the second field of its lines in `coverage.md`:

````
```coverage
P2.2 | assignment · frame 9
P2.4 | assignment · frame 11
P2.7 | assignment · frame 14 | as: two days | label: the paper says one
P2.8 | cut | reason: restates P2.7; showing both made the scene repeat itself
```
````

| Second field | Meaning |
|---|---|
| a place | Where the item is shown: the chapter, then `frame <n>` (or `slide`, `scene`, `page`) with the number from the outline. Several numbers are fine: `frames 9, 11`. |
| `cut` | Deliberately not shown. Needs `reason:`. Report every cut to the user. |
| empty | Not built yet. The check counts it as missing. |

Add `as: <the wording used>` when an item is shown without its exact `show:` strings on purpose
(a number written out in words, a name translated). The check then looks for that wording
instead of the `show:` strings, so write it exactly as it appears.

Add `label: <the words that mark it>` to every `corrected` and `inferred` item: the words on
screen that tell the viewer the source says otherwise, or that this is our reasoning and not the
source's. Give the words that are really there for that item. One stock phrase pasted onto every
line passes the check and proves nothing.

**Keep the outline current.** When the output skill can list its places, write the listing to
`<run>/output/outline.txt` after each build (for `visual-explainer`:
`node scripts/outline.js --kit <run>/output/kit <run>/output/story/*.js > <run>/output/outline.txt`).
A line that starts with `# ` opens a chapter, and a line that starts with a number is the place
with that number. Frame numbers shift whenever a frame is added or moved earlier in the story,
so fill in the ledger from the current outline, and run the check again after any change.

The ledger is also what makes a long build resumable: after an interruption, the lines that
still have an empty place are what remains.

## 5. Check

```bash
python3 scripts/check_coverage.py check <run>
```

It reads every text file under `<run>/output/` (or the paths given after `--output`), skipping
folders named `kit`, `work`, `notes`, `tmp`, `node_modules`, `shots` and `.git`, which hold
tooling and working files and not content. It prints the files it read: look at that list once,
because a stray helper file there would make every string look present.
It fails when:

- a group has no decision in the scope, or the scope is not signed off;
- an owed item has no place in the ledger;
- an item's `show:` strings, or the wording given with `as:`, cannot be found in the output;
- a `corrected` or `inferred` item has no `label:`, or its label is not in the output;
- there is an outline, and a place names a frame that is not in it or that sits in another
  chapter than the one the ledger names.

**What a pass proves, and what it does not.** The check prints how many covered items were
matched by an exact string and how many rest on the ledger alone. An item without `show:` has
nothing to search for, so for those the check only knows that you wrote down a place that
exists. Before reporting, open the output at ten or so of those places, spread across the
chapters, and confirm that each statement is really shown there. Say in the final report how
many you looked at.

Fix what it reports and run it again until it prints OK. Fixing means showing the item, not
editing the ledger to make the report quiet. Cut an item only when showing it would truly make
the output worse, and give the reason.

It also prints reminders: which items in scope are external, so that the output names where
they come from, and how many gaps the in-scope groups hold.

## 6. Final report

In the user's language, short enough to read at a glance:

1. **The output.** A link or path for each version.
2. **What it covers.** The numbers from the check: groups, items owed, items shown, and of
   those how many were matched by an exact string and how many rest on the ledger. Say how many
   of the second kind you opened and looked at.
3. **Cuts.** Each one with its reason, or "none".
4. **Corrections.** The places where the source is out of date, since the user will want to know.
5. **Open questions.** How many gaps remain, with the two or three that matter most.
6. **Anything not verified.** For example, a version that could not be opened in a browser.
7. **Where the files are**, and a note if that location is temporary.

Report what happened. If the check did not pass, say what is still missing; do not describe the
output as complete.
