# Format E: tiny world

A small isometric scene. The parts of the system are stations on a floor, and one courier carries labelled things between them.

| | |
|---|---|
| The question it answers | "What is the one picture to remember?" |
| Strong at | Intuition and memory. People recall "the little block walked to the cabinet twice" long after they forget a diagram |
| Weak at | Detail: there is room for a label, not for a payload. And a world invites the viewer to believe things the picture implies but the system does not do |
| Use it for | A first intuition before the real explanation, or a closing recap after it, of a flow in which something is carried between three to six places |
| Do not use it for | The only explanation of anything, a flow with more than about eight steps, or a subject where nothing is carried |

Use it at most once or twice in a whole explainer. Depth is the idea here, so this is also the place for it when the subject is physical: rooms, walls, layers.

## Keeping the world honest

- **Every station is a real part and every cargo is a real thing that is sent,** under its real name. No invented characters, no decoration that suggests a mechanism.
- **The courier is the part of the system that does the carrying.** Say in the first step what it stands for.
- **The number of trips is true.** If the real flow visits the store twice, the courier walks there twice. The count of trips is usually the thing viewers remember, so it must be right.
- **What the world cannot show, the narration does not claim.** Details go in the other formats.

## Designing one

1. Lay the floor as one row with one or two short spurs. The courier's home is where the row and a spur meet.
2. Place the stations at the ends. Choose the kind of each from what it does: a `stack` for a store that grows, a `gate` for a check that opens and closes, an `orb` for the thing that thinks, a `block` for a machine or a building, a `person` for a human.
3. Name the cargo. Give each cargo a colour that matches the role colours of the rest of the story.
4. Write five to eight steps. One trip, or one out-and-back, per step.

## Data shape

```js
const world = Kit.world({ title: 'One picture', origin: [640, 120], unit: 80,
  floor: [{ from: [0, 3], to: [10, 3] }, { from: [5, 0], to: [5, 2] }],
  cargo: { card: 'ink', question: 'yellow', answer: 'green', book: 'orange', record: 'yellow' },
  props: [{ id: 'cat', kind: 'stack', at: [5, -1], label: 'catalogue', state: { items: ['ink3', 'ink3', 'ink3'] } },
          { id: 'you', kind: 'person', at: [.6, 4.4], label: 'you' },
          { id: 'gate', kind: 'gate', at: [7.5, 3], label: 'three checks' },
          { id: 'shelf', kind: 'block', at: [11, 2.6], size: [1.1, 1.8, 1.7], col: '#3a4459', label: 'shelf' }],
  stops: { home: [5.5, 3.5], you: [1.2, 3.5], cat: [5.5, .7], gate: [7.1, 3.5], shelf: [10.6, 3.5] },
  courier: { home: 'home', col: 'teal' },
  steps: [
    { cap: 'The small block is the desk clerk. The whole job is carrying things between four places.' },
    { cap: 'A card and a request arrive.', legs: [{ to: 'you' }, { to: 'home', carry: 'card' }] },
    { cap: 'Two questions go up, two answers come back.', legs: [{ to: 'cat', carry: 'question' }, { to: 'home', carry: 'answer' }],
      set: { gate: { open: 1, sign: 'all pass' } } },
    { cap: 'The loan is written down before the book leaves.', legs: [{ to: 'cat', carry: 'record', set: { cat: { push: 'yellow' } } }, { to: 'home', carry: 'book' }] }
  ]});
```

Coordinates are grid cells: `x` runs down to the right, `y` down to the left. `origin` is where cell (0,0) sits on the 1600 by 900 stage and `unit` is the size of a cell. A `floor` entry tiles the rectangle between two cells. `stops` are the named points the courier walks between.

A step:

| Key | Effect |
|---|---|
| `legs: [{to, carry, set}]` | The courier walks to each stop in turn. `carry` changes what it holds from that leg on (`''` puts it down). `set` changes station states on arrival |
| `pre: {…}` | Station changes applied before the courier moves, such as a gate opening |
| `set: {…}` | Station changes applied after it arrives |
| `carry` | What the courier holds at the end of the step |
| `when` | As on any step |

Station kinds and their states:

| Kind | Looks like | State |
|---|---|---|
| `block` | A box of `size: [w, d, h]` | `flash: 1` to brighten it |
| `orb` | A ball with eyes on a pad | `glow: 1` shows a turning ring, for "working" |
| `gate` | Two posts and a bar across `span` cells | `open: 1` raises the bar and turns it green. `sign: 'text'` shows a word above it |
| `stack` | A pile of drawers | `push: 'tone'` adds a drawer. Start with `state: {items: [...]}` |
| `person` | A simple figure | `say: 'text'` shows a word above it |

Every station takes `label`, and `dx`, `dy` to nudge the label. `ltone` colours it.

## In the two versions

Video: the courier walks each leg, what it carries is written on a card above it, stations react on arrival. Slides: one step per scroll, and the courier walks when the step is entered from the one before. There are no gates in a world: it is for watching.

## Pitfalls

- Things further down the screen are drawn in front. Do not park the courier inside a block, and keep tall blocks at the edges so they hide nothing.
- Labels sit above or below their station by default and can land on the floor or on another label. Look at a screenshot and nudge with `dx`, `dy`.
- A cargo name longer than about twelve characters makes a card wider than the courier. Shorten the name.
- If the story needs the viewer to read a value, the world is the wrong format for that step.
