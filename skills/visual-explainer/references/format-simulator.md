# Format B: simulator

Like a debugger. A few panels show everything the system holds right now, and each step pushes it forward by one change.

| | |
|---|---|
| The question it answers | "What does each part hold at this step? What happens if I choose differently?" and, as an explore panel, "Which rule decides this case?" |
| Strong at | Real data at every step, and decisions whose consequences the viewer can see |
| Weak at | First contact. It is dense and assumes the viewer already knows what the parts are |
| Use it for | Tracing the running example end to end, a flow with a real fork, a rule set the viewer can poke |
| Do not use it for | Introducing an idea, or anything with fewer than about five steps |

It has two shapes: the **trace** (several panels, many steps) and the **explore panel** (one panel, one step, several controls).

## The trace

### Anatomy

- **Panels**: one per actor or store in the running example, three to five, laid out left to right in the order things usually flow.
- **State**: one plain object. `init()` returns a fresh one.
- **Steps**: each has a narration line and a `do(S, ch)` that makes one change to the state. `hi` lists the panels to light. `move` shows something travelling from one panel to another before the change lands.
- **`draw(S, P, ch, info)`**: paints every panel from the state. It is called for every step, from a state rebuilt by replaying `do` from the start, so it must not remember anything itself.

### Designing one

1. Choose the panels. If two panels never exchange anything, one of them does not belong.
2. Write the state as the viewer would name it: what you hold, what the record says, what is on the shelf.
3. Write the steps so that each changes one thing in one panel, and give it a `move` when something crosses between panels. The travelling chip is what makes the simulator read as a flow.
4. Put the decision where it would really be made. A choice the user makes appears as buttons in the panel that asks, at the step where it asks.
5. Mark the steps that exist only on one side of the decision with `when`.

### Data shape

```js
const STN = ['Scan the card', 'Look up the book', 'Decide', 'Fetch the book', 'Update the record'];
const loan = Kit.sim({ title: 'One loan, step by step', head: 'One loan, step by step',
  panels: [{ id: 'you', title: 'You', x: 40, y: 110, w: 330, h: 640 },
           { id: 'desk', title: 'Desk', x: 400, y: 110, w: 430, h: 640, tone: 'teal' },
           { id: 'cat', title: 'Catalogue', x: 860, y: 110, w: 400, h: 640 }],
  init: () => ({ have: [], stn: -1, ask: 0, rec: { status: 'on the shelf' } }),
  steps: [
    { cap: 'You walk in with a library card and the name of a book.', hi: ['you'],
      do(S) { S.have = [{ t: 'library card #1042' }]; } },
    { cap: 'The desk scans the card.', move: ['you', 'desk', 'card #1042', 'ink'], hi: ['desk'], do(S) { S.stn = 0; } },
    { cap: 'Now the choice is yours.', hi: ['desk'], do(S) { S.stn = 2; S.ask = 1; },
      gate: { id: 'how', type: 'branch', options: ['here', 'home'], prompt: 'Your turn: read it here, or take it home?',
              say: { here: 'You read it here.', home: 'You take it home.' } } },
    { when: { how: 'home' }, cap: 'The desk writes the loan down first.', move: ['desk', 'cat', 'on loan · 2 Nov'], hi: ['cat'],
      do(S) { S.stn = 4; S.rec = { status: 'on loan' }; } }
  ],
  draw(S, P, ch, info) {
    P.you.list(S.have, info.prev ? info.prev.have.length : 0);     // items from that index on slide in as new
    P.desk.steps(STN, S.stn);
    if (S.ask) P.desk.buttons('how', [{ id: 'here', label: 'Read it here' }, { id: 'home', label: 'Take it home' }], ch, 'your choice');
    P.cat.kv([['status', S.rec.status, S.rec.status === 'on loan' ? 'yellow' : 'green']]);
  }});
```

Panels are positioned in stage units on the 1600 by 900 stage. `head` is an optional title above them.

### What a panel can show

`P.<panelId>` has these methods. Each adds to the panel and returns the panel, so they chain.

| Method | Shows |
|---|---|
| `count(text)` | A small note at the right of the panel title, such as "3 entries" |
| `status(text, tone)` | One large line: the state in a word |
| `text(str, tone)`, `note(str, tone)` | A paragraph. A `note` after a pipeline appears when the pipeline has finished lighting |
| `list(items, freshFrom)` | A list. Items are strings or `{t, tone, mono}`. Items from index `freshFrom` on animate in |
| `kv(pairs)` | Label and value rows: `[['status', 'on loan', 'yellow'], ...]` |
| `code(text)` | A monospace block, for real payloads or output |
| `steps(names, active)` | An ordered list of stations with one lit |
| `tags(items, active, label)` | A row of small code chips with one lit, for rules |
| `buttons(controlId, options, ch, label)` | The controls of a gate. The pressed one is filled |
| `pipeline(stages, result)` | See the explore panel below |
| `html(str)` | Anything else |

`info` holds `prev` (the state one step earlier, or null), `step`, `k` and `how`.

## The explore panel

One panel, one step, an explore gate. The viewer changes inputs and watches which stage of a pipeline decides.

```js
function check(v) {            // pure: the same inputs always give the same verdicts
  const st = [{ title: '1 · Card', sub: 'is it valid?' }, { title: '2 · Limit', sub: 'fewer than 5 out?' }];
  if (v.card === 'expired') { Object.assign(st[0], { verdict: 'expired', tone: 'red' });
    return { st, res: { title: 'Result', verdict: 'Refused', tone: 'red' }, note: 'The first check failed, so the second never ran.' }; }
  Object.assign(st[0], { verdict: 'valid', tone: 'green' });
  /* ... */
}
const checks = Kit.sim({ title: 'Three checks', head: 'Can this loan go ahead?',
  panels: [{ id: 'x', title: 'Change a setting, watch which check decides', x: 70, y: 200, w: 1460, h: 440 }],
  steps: [{ cap: 'Three checks run in a fixed order. The first one that fails ends the loan.',
    gate: { ids: ['card', 'out'], type: 'explore', init: { card: 'ok', out: '2' }, need: 2,
            prompt: 'Your turn: change a setting. Try two different ones.',
            demo: [{ card: 'expired' }, { card: 'ok', out: '5' }, { out: '2' }], say: ch => check(ch).note } }],
  draw(S, P, ch) { const r = check(ch);
    P.x.buttons('card', [{ id: 'ok', label: 'Valid' }, { id: 'expired', label: 'Expired' }], ch, 'Card')
       .buttons('out', [{ id: '2', label: '2 of 5' }, { id: '5', label: '5 of 5' }], ch, 'Books out')
       .pipeline(r.st, r.res).note(r.note); }});
```

A stage is `{title, sub, verdict, tone}`. A stage with no verdict shows "not reached". A stage with `off: true` shows as not used at all, for a stage that does not exist in the current mode. The stages light one after another, then the result, then the note: the order is the lesson.

Design rules: two or three controls with two or three settings each. Make every setting change the outcome somewhere. Make `demo` visit each distinct outcome once, simplest first. Let `say` return the reason for the outcome, so the narration line explains whatever the viewer just did.

## In the two versions

Video: steps play in order with the chip travelling between panels. At a branch the cursor presses an option, that path plays, the picture rewinds, and the other plays. On an explore panel the cursor presses through the demo cases. Slides: one step per scroll. The gate holds the deck until the viewer presses.

## Pitfalls

- A panel that is too short clips its content. The lint reports "panel too short". Cap long lists: show the last few and a count.
- State kept outside `S` (in a variable the steps close over) breaks jumping to a step. Everything a step changes must be in `S`.
- Hide the controls before the step that asks and they will seem to appear from nowhere when jumped to: guard them with a flag in the state (`S.ask`), set by the gate's step, so they are drawn on every later step too.
- Keep text short. A panel is read at a glance, many times.
