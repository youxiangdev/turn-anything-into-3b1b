---
name: scope
description: >-
  Turn a research dossier into a scope the user has confirmed, before anything is built: show on
  one short page what will be covered (everything, by default), what is proposed to be left out
  and why, and the few choices only the user can make (which things to compare in depth, the
  language, which output). Ask once, record the answers in scope.md, and lock it. Use after the
  research skill has produced a dossier, when the user says "confirm the scope", "show me what you
  will include", "给我看 scope", "是全部细节吗", "我们先 align", and as stage 2 of the deep-dive
  pipeline. Only for scoping something built from a research dossier; not for scoping code changes,
  tickets or project plans.
argument-hint: "<run folder>"
---

# Scope: one page, one round, then locked

A dossier holds everything that was learned. Before any of it is turned into an output, the
user gets to see what will be covered and to make the handful of choices that are really theirs.
This stage exists because skipping it is expensive in both directions: build without asking and
the result covers the wrong things at the wrong depth; ask in dribs and drabs across the build
and the user is interrupted four times for decisions that fit on one page.

So: **one page, one round of questions, then the scope is locked** and the build runs without
further stops.

## What the user has taught us about scope

These come from watching how such sessions actually went, and they set the defaults.

- **They want everything.** Offered a lighter option marked "recommended" against full coverage,
  they picked full coverage. Offered four optional sections, they took all four. So the default
  is that every group in the dossier is in, and the recommended answer is always the fuller one.
  Propose a cut only with a reason, and let them overrule it.
- **Depth needs a focus.** Full detail for every one of eleven systems cannot be taken in. What
  worked was full side-by-side depth on the two or three they care about most, with the others
  brought in where they do something notably different.
- **They decide the language of the output, and it is not always the language they chat in.**
- **They will not read a wall of text.** The scope page must be something they can take in at a
  glance: short lines, one table, numbers.

## Files

Paths are relative to this skill's folder.

| File | What it is |
|---|---|
| `references/scope-format.md` | The format of `scope.md`, and an example of the page shown to the user. Read it before writing either. |

## Steps

### 1. Check the dossier

The run folder must hold a dossier that passes its lint. The lint belongs to the research skill,
whose folder sits next to this one:

```bash
python3 ../research/scripts/dossier.py lint <run>
```

Read `dossier/inventory.md`, `dossier/overview.md` (including "Questions for the scope stage")
and `dossier/map.md`. If there is no dossier, run the research skill first.

### 2. Work out what is already decided

Read the user's original request and anything they have said since. A choice they have already
made is not a question: "an English video comparing A and B" settles the language, the output
and the focus. Preferences recorded from earlier sessions count too. Only what is still open
gets asked.

### 3. Show the scope page

Write it in the user's language, in the chat, following the example in
`references/scope-format.md`. It has five short blocks:

1. **What was read and checked.** One or two lines with the numbers from the "Verification"
   section of the inventory: how many statements were checked against a second source, and how
   many of the hinges. When most of it rests on the source alone, say so in plain words, and
   name any hinge that could not be checked and why.
2. **The map.** The parts, one line each, so the whole shape is visible.
3. **What will be covered.** One table: each group, its size, in or out. Everything is in unless
   you have a reason, and each proposed cut carries its reason.
4. **What was found along the way.** How many statements the primary sources corrected, with
   the two or three most striking, and how many questions no source answers.
5. **How it will be told.** The settings you will use unless told otherwise: who it is for, the
   order of telling, the focus, the language, the output. Close with the size of the build: the
   number of items the output owes (every item in an `in` group that is not a gap), and that
   once they confirm, all of it is built in one go. Above about 150 items the build is a long
   run that uses a large share of a usage allowance, so say that, and offer one chapter first
   as the way to see the form before paying for the rest. Record their choice under "Notes for
   the build".

Keep it to what fits on one screen. Details stay in the dossier.

### 4. Ask once

Ask only the open choices, at most four, in a single round. Use the question tool when there is
one (it lets the user click an answer); otherwise ask in the chat as a short numbered list with
your recommendation marked. Then wait. This is the one place the pipeline stops for the user.

The usual four, when they are still open:

| Choice | Options to offer | Recommend |
|---|---|---|
| Coverage | Everything; everything except the borderline groups you name; core parts only | Everything |
| Focus, when the source compares several things | The two or three covered most deeply or named by the user; all of them equally; one alone | Two or three in full depth, the others where they notably differ |
| Language of the output | The source's language; the user's own language | What they chose last time if known, otherwise their own language |
| Output | Each output skill that is installed, and the versions it offers | All the versions the output skill offers |

Phrase each option by what the user will get, not by what you will do. Say what a choice costs
when it costs something ("all eleven equally: each gets less depth").

If the user has asked not to be consulted, or nobody is there to answer, take the recommended
answers, record that in the sign-off, and say so in the final report.

### 5. Write scope.md and lock it

Write `<run>/scope.md` in the format given in `references/scope-format.md`: a decision for every
group, the settings, the user's answers word for word, and the sign-off line.

If an answer is ambiguous, take the more inclusive reading and say that you did. If they changed
something, apply it and show only what changed. Do not open a second round of questions unless
they ask one back.

Then confirm in two or three lines what is locked, and continue. When this skill was called by
the deep-dive pipeline, go straight on to the next stage.

## After the lock

The scope is a contract with the user. The build may not quietly drop anything that is in. If
something in scope turns out to be impossible or pointless to show, it is recorded as cut, with
its reason, in the coverage ledger and reported to the user at the end. Changing what is in or
out after the lock needs the user.
