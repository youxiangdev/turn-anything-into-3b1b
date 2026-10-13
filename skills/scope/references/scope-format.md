# Scope format

Two things are described here: the page shown to the user in the chat, and the `scope.md` file
written once they have answered.

## The page shown to the user

Write it in the user's language. This example is in English and uses an invented subject (a
paper comparing two parcel-locker networks). Yours will have the real numbers from
`dossier/inventory.md`.

````markdown
## Scope: Two parcel-locker networks

I read all 12 pages. The dossier holds 96 facts in 9 groups. 14 of them were checked against
the Lockr operator manual and the BoxPost firmware source, including 7 of the 8 the explanation
rests on. The eighth, how BoxPost picks a compartment, cannot be checked: that code is not
public. The other 76 are as the paper states them.

### The map
1. **Check-in**: the parcel is scanned and its size is known
2. **Compartment assignment**: the locker picks a compartment and holds it
3. **Door control**: the door opens, then confirms it was closed
4. **Notification**: the recipient gets a pickup code
5. **Pickup and expiry**: collection, or return after three days

### What will be covered

| Group | What it is | Facts | |
|---|---|---|---|
| Overview | What the paper is, who wrote it, its limits | 8 | in |
| Map | The five parts and what flows between them | 9 | in |
| P1 to P5 | The five parts, each in full | 61 | in |
| Scenarios | A normal delivery; a full locker; a door left open | 11 | in |
| Claims | The paper's four findings and its recommendation | 7 | in |

Nothing is left out. The one thing I would consider cutting is the appendix on locker hardware
suppliers (4 facts inside the overview), which does not affect how anything works. It stays in
unless you say otherwise.

### What I found along the way
- **3 statements in the paper are out of date.** The most important: BoxPost now holds a
  reservation for 48 hours, not 24.
- **6 questions have no answer in any source**, for example what happens when two couriers scan
  in the same second. These will be shown as open questions, not guessed.

### How it will be told
- **For**: someone who has not read the paper
- **Order**: the whole map first, then each part in turn, each one from the problem it solves
- **Compared in full**: Lockr and BoxPost
- **Language of the output**: to be decided
- **Output**: visual-explainer, as a video and as scroll-through slides

Once you confirm, I build all of it in one go: 90 items to show (the 96 minus the 6 open
questions). Tell me if you would rather see one chapter first.
````

Then the questions, at most four, only the ones still open.

What makes this page work:

- The numbers show that this is the full content and not a summary, and how much of it was
  checked rather than taken from the source.
- The size of the build is stated before the user commits to it.
- The map lets the user see the shape before deciding anything.
- Every proposed cut has its reason beside it, and the default is to keep it.
- Corrections and gaps are surfaced, since they are often what the user most wants to know.
- Settings that have a sensible default are stated, not asked. Only the open ones become questions.

## scope.md

````markdown
# Scope: Two parcel-locker networks

## What will be covered

```scope
O   | in
M   | in
P1  | in
P2  | in
P3  | in
P4  | in
P5  | in
SC1 | in
SC2 | in
SC3 | in
C   | in
O.7 | out | reason: hardware supplier list, the user agreed it does not affect how anything works
```

## How it will be told

```settings
audience: has not read the source
goal: understand how it works end to end, not a summary
order: the whole map first, then each part, each from the problem it solves
focus: Lockr; BoxPost
others: only where they do something notably different
language_chat: zh
language_output: en
output_skill: visual-explainer
versions: video; slides
deepen: close the gaps for the focus before building
signoff: 2026-01-15 · confirmed by the user
```

## The user's answers, word for word

- Coverage: "Everything"
- Language of the output: "English"

## Notes for the build

Anything the user said that the output must respect and that has no setting above.
````

### The `scope` block

One line per decision: `ID | in` or `ID | out | reason: ...`.

- Every group in the dossier needs a line (`O`, `M`, each `P<n>`, each `SC<n>`, `C`). The
  coverage check fails when a group has no decision, so that nothing is left out by forgetting.
- A line for a single item (`O.7`) overrides its group, in either direction.
- `out` always carries `reason:`.
- Items with status `gap` are never owed by the output, whatever their group says.

### The `settings` block

One `key: value` per line. `signoff` is required: the date and how the scope was confirmed. Use
`signoff: <date> · defaults taken, the user asked not to be consulted` when that was the case.
The other keys are read by the output stage; add more when the user asks for something that
needs one.

| Key | Meaning |
|---|---|
| `audience` | Who the output is for. Default: someone who has not read the source. |
| `goal` | What they should be able to do afterwards. |
| `order` | The order of telling. Default: map first, then each part from its problem. |
| `focus` | The things compared in full depth, separated by `;`. Use the spellings from the dossier. |
| `others` | How the remaining ones appear. |
| `language_chat` | The language used with the user. |
| `language_output` | The language of everything on screen and of any narration. |
| `output_skill` | The skill that builds the output. |
| `versions` | Which versions of the output to build, separated by `;`, in the output skill's own names for them. |
| `deepen` | Whether to close gaps for the focus from primary sources before building. |
| `signoff` | Date and how it was confirmed. |
