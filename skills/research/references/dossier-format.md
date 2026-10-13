# Dossier format

The dossier is read by three readers: the scope stage (to show the user what exists), the output
stage (to build from), and two scripts (the lint here, and the coverage check after the build).
The scripts are why the format is strict in a few places. Everything else is ordinary Markdown.

## Contents

- [Run folder](#run-folder)
- [Items](#items)
- [Sources index](#sources-index)
- [What goes in each file](#what-goes-in-each-file)
- [The lint](#the-lint)

## Run folder

```
<run>/
├── sources/
│   ├── index.md              every source, one line each
│   ├── S1-<name>.txt         full text with page or section markers
│   └── S1-<name>.pdf         the original, when there is one
└── dossier/
    ├── overview.md           O items    what the source is, who made it, what it covers, its caveats
    ├── map.md                M items    the parts, what flows between them, the running example
    ├── parts/P<n>-<slug>.md  P<n> items one file per part of the map
    ├── scenarios.md          SC<n> items  concrete situations traced end to end
    ├── claims.md             C items    what the source itself concludes
    ├── glossary.md
    └── inventory.md          written by the lint; never edit it
```

`scripts/dossier.py init <run> "<title>"` creates the skeleton, and
`scripts/dossier.py part <run> <n> "<name>"` creates one part file from the template.

## Items

An item is one checkable statement. Items are what the scope stage counts and what the coverage
check ticks off after the build, so anything that should reach the viewer has to be an item.
Prose around the items gives the reasoning and the story; the items carry the content.

Write one item per line inside a fenced block marked `facts`:

````
```facts
P2.4 | param | A hold lasts 10 minutes; if the door has not been opened by then, the compartment is released | for: Lockr | show: HOLD_MINUTES = 10 | src: S1 p5; S2 | status: verified
```
````

The fields are separated by `|`:

| Position | Field | Meaning |
|---|---|---|
| 1 | ID | Group, a dot, a number: `O.1`, `M.2`, `P2.4`, `SC1.2`, `C.7`. Numbers need not be contiguous. Never reuse or renumber an ID once the scope has been confirmed. |
| 2 | kind | What sort of statement it is (table below). |
| 3 | statement | One fact in a full sentence, with the real names and numbers. |
| 4+ | `key: value` | Any of `for`, `show`, `src`, `status`, `note`, `hinge`, in any order. `status` is required. |

To put a literal `|` inside a field (a shell pipe, for example), write `\|`.
A line that starts with `#` inside the block is a comment.

### Kinds

| Kind | Use it for |
|---|---|
| `context` | Background the reader needs: who, when, what was studied, a definition. |
| `part` | In the map: one part and the problem that makes it necessary. Name the part by its ID. |
| `link` | In the map: what one part hands to another, including loops back. |
| `step` | One step of a mechanism, in order. Write branches as "if ..., then ...; otherwise ...". |
| `rule` | Decision logic or a policy: what is allowed, chosen, ordered or preferred, and by what test. |
| `param` | A name, default, limit, threshold, size or timeout. |
| `failure` | What happens when something goes wrong or hits an edge case, including the exact error text when known. |
| `diff` | A difference between two implementations or approaches. |
| `claim` | A finding, result or recommendation of the source, with its numbers. |

### Keys

| Key | Meaning |
|---|---|
| `for:` | Which implementation, system or variant the statement is about, when the source compares several. Separate several names with `;`. Leave it out when the statement holds for all. Spell each name the same way everywhere; the lint lists the spellings it found. |
| `show:` | The exact strings a viewer should see when this item is shown: identifiers, file names, numbers with their units, error messages. Separate several with `;`. The coverage check searches the output for them, which is what keeps real names and numbers from being summarised away. An item without `show:` can only be checked by hand later, so give one whenever the statement has a name or a number; a `param` always has. Leave it out only when the statement has none. |
| `src:` | Where the statement comes from: a source ID and a locator, such as `S1 p5`, `S1 p5-7`, `S1 §3.2`, `S3 src/reserve.c`. Separate several citations with `;`. |
| `status:` | How far the statement can be trusted (table below). |
| `note:` | For `corrected`: what the provided source claims. For a hinge that could not be checked: why not. Otherwise any short remark. |
| `hinge:` | `hinge: yes` marks one of the few statements the whole explanation rests on: if it were wrong, the map would be wrong. Usually five to fifteen in a dossier. Hinges are what verification checks first, and the inventory reports how many of them were checked. |

### Status

| Status | Meaning | `src:` must name |
|---|---|---|
| `source` | The provided source says so, and nothing else was checked. | the provided source |
| `verified` | The provided source says so and an independent primary source agrees. | both |
| `corrected` | The provided source says something else, or is out of date. The statement gives what is true now; `note:` gives what the source claims. | both |
| `external` | The provided source does not cover it; a primary source does. | that primary source |
| `inferred` | No source states it; it is our reasoning from what the sources do state. | what it was reasoned from, if anything |
| `gap` | The question matters and no source answers it. The statement is the question. | nothing, or where the source falls silent |

When the user gave only a topic, there is no provided source. Then `source` means one primary
source states it, `verified` means two independent ones agree, and `corrected` means they
disagree (the statement gives the more authoritative or more recent version, `note:` the other).

Two rules matter more than the rest:

- **A gap stays a gap.** If no source answers a question, record the question as a `gap` item.
  Filling it with a plausible guess is the one mistake that cannot be caught later, because the
  guess will look exactly like a fact in the finished output.
- **Invented example values are not items.** Numbers and file names made up for a worked example
  belong in the "Worked example" prose, marked as illustrative, never in a `facts` block.

### Writing good statements

- One fact per item. If a sentence has "and" joining two things that could each be wrong
  separately, split it.
- Use the real name. "A timeout on the hold" is a summary; "`HOLD_MINUTES`, 10 by default,
  after which the compartment is released" is a fact.
- Give numbers with units and what they count: "a hold of 10 minutes", not "a short hold".
- Say who does it. "The locker picks the compartment", not "a compartment is picked".
- For steps, keep them in the order they happen and number the IDs in that order.

## Sources index

`sources/index.md` holds one line per source inside a fenced block marked `sources`:

````
```sources
S1 | provided | Two parcel-locker networks (the paper the user gave) | file: sources/S1-paper.txt | pages: 12 | read: 1-12
S2 | primary | Lockr operator manual | url: https://example.com/lockr/manual | retrieved: 2026-01-15 | read: chapter 3
S3 | primary | BoxPost locker firmware (source code) | url: https://example.com/boxpost/firmware | version: 4f2c9a1 | read: src/reserve.c
```
````

| Position | Field | Meaning |
|---|---|---|
| 1 | ID | `S1`, `S2`, ... |
| 2 | type | `provided` (what the user gave), `primary` (official docs, source code, specs, original papers, data) or `secondary` (commentary: a lead to follow, never proof). |
| 3 | title | What it is. |
| 4+ | `key: value` | `file` (path inside the run folder), `url`, `pages` (for paged sources: the page count, such as `83`, or the page range when the subject is part of a document, such as `35-38`), `read` (page ranges such as `1-40, 45-83`, or `all`, or the files and sections read), `retrieved` (date), `version` (commit, release or edition), `note`. |

`read:` is a promise about what was actually read. For a provided source with a page count the
lint fails when pages are unread, and lists the pages that no item cites so they can be checked.

## What goes in each file

**overview.md** (`O` items). What the source is and who wrote it, when, and from what evidence.
Why it matters. How it is organised. Who or what it covers (every system, method or case, with
its basic profile). Its caveats: weak evidence, self-reported numbers, things the authors admit,
and anything found out of date during verification.

**map.md** (`M` items). The whole subject in one paragraph. The running example: one concrete
input that every part will handle in turn. Then one `part` item per part, naming the part by ID
and the problem it answers, and one `link` item per hand-over between parts, loops included.
A newcomer should be able to redraw the whole flow from this file alone.

**parts/P&lt;n&gt;-&lt;slug&gt;.md** (`P<n>` items). One file per part, following
`part-template.md`. This is where the depth lives.

**scenarios.md** (`SC<n>` items). Concrete situations traced end to end across the parts: what
starts it, which parts it passes through in order, what each does, and where implementations
part ways. Start each scenario with a heading such as `## SC2 · The context window fills up`.

**claims.md** (`C` items). What the source itself concludes: thesis, numbered findings or
observations, results with their numbers and conditions, recommendations, and admitted limits.
Keep the source's own numbering in the statement ("Observation 7: ...") so nothing is lost.

**glossary.md**. Every term a newcomer would not know, one plain sentence each. Not items.

## The lint

```bash
python3 scripts/dossier.py lint <run>
```

It fails on: a malformed line, a reused ID, a missing or unknown status, a citation of a source
that is not in the index, a status whose required sources are missing, a `corrected` item
without `note:`, a part file without its required sections, no overview or map items, unread
pages of a provided source, and a hinge that is `inferred` or a `gap`.

It warns on: parts with no step, rule or failure items, parts with fewer than three newcomer
questions, parts the map never names, missing scenarios, claims or glossary, pages that no
item cites, a `param` without `show:`, a dossier with no hinge marked, and a hinge that rests on
one source and has no `note:` saying why it could not be checked.

It then writes `dossier/inventory.md`: counts per group, the corrections, the gaps, the inferred
items, the spellings used in `for:`, how much was checked against a second source (overall and
for the hinges), and the reading coverage. The scope stage reads that file.
