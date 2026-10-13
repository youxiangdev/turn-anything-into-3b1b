# Format D: zoomable map

The overview. One picture of all the parts and what flows between them, which the story leaves from and returns to. Each step reveals more of it, lights one part, ticks the parts already covered, or zooms the camera into one.

| | |
|---|---|
| The question it answers | "Where does this part sit? What are all the parts? Where am I?" |
| Strong at | Keeping the overview and the detail in one picture, and keeping the viewer oriented across a long story |
| Weak at | Explaining anything by itself. A map with nobody guiding is a diagram to stare at, so in this kit the map is always stepped and narrated |
| Use it for | Part 2 of the story, the bridge between chapters, the closing recap |
| Do not use it for | The mechanism inside a part. Zoom, then switch to the format that fits |

## Designing one

1. **Nodes: five to nine parts.** Each has a short name and, optionally, one line under it that says what it is in plain words.
2. **Regions** draw the boundaries that matter: what is inside the system and what is outside. One or two.
3. **Edges** are what travels. Label them with the thing that moves, not with a verb.
4. **Reveal in the order of the problems,** not in reading order. Each step adds the parts that the narration is about to explain, and the narration says what problem brings them in.
5. **Lay it out so the main flow reads left to right or as a loop,** and keep that layout for the whole story. The map is a place, and places do not rearrange.

## Data shape

```js
const MAP = { id: 'lib', title: 'The map',
  regions: [{ id: 'lib', x: 470, y: 130, w: 870, h: 680, label: 'library' }],
  nodes: [{ id: 'you', x: 170, y: 450, label: 'You', tone: 'dim' },
          { id: 'desk', x: 640, y: 450, w: 290, label: 'Desk', sub: 'the only place you talk to' },
          { id: 'cat', x: 1080, y: 290, w: 240, label: 'Catalogue', sub: 'one record per book' }],
  edges: [{ id: 'in', d: 'M270,432 H492', head: [492, 432, 0], label: 'card + request', lx: 372, ly: 408 },
          { id: 'look', d: 'M785,425 C870,400 910,330 958,302', head: [958, 302, -28], label: 'look up, update', lx: 862, ly: 338, la: 'end' }],
  steps: [
    { cap: 'You stand outside, and you talk to exactly one place: the desk.', show: ['lib', 'you', 'desk', 'in'] },
    { cap: 'Behind the desk is the catalogue: one record for every book.', show: ['cat', 'look'] },
    { cap: 'So that is where we look next.', focus: 'desk', pick: 'desk',
      prompt: 'Your turn: click the desk to zoom in.', say: 'Inside the desk: one loan, one step at a time.' }
  ]};
const map = Kit.map(MAP);
```

Node `x`, `y` are the centre, with `w` and `h` defaulting to 200 by 88. An edge's `d` is an SVG path written by hand, `head` is `[x, y, angle in degrees]` for its arrowhead, and `lx`, `ly`, `la` place its label. Ids must be unique across regions, nodes and edges, because `show` mixes them.

What a step can do:

| Key | Effect |
|---|---|
| `show: [ids]` or `'all'` | Reveal those regions, nodes and edges. Earlier ones stay |
| `focus: id` or `[ids]` | Light those nodes in the focus colour. It applies to this step only |
| `done: [ids]` | Put a tick on those nodes. Ticks stay |
| `zoom: id` | Move the camera into that node. `zoom: null` returns to the whole map. `scale` sets how far (default 3) |
| `pick: id` | Make this step a gate: that node becomes a control, and pressing it zooms in. Give `prompt` and `say` |
| `also: {…}` | An extra phase of ordinary scene changes, for anything the keys above do not cover |
| `when` | As on any step |

`extra(A)` in the def lets you add ordinary scene objects to the map: a title, a legend, a travelling marker.

## The map as the table of contents

Declare the map def once and reuse it for short bridge segments between chapters. A helper keeps this to one line per bridge:

```js
const all = MAP.nodes.map(n => n.id).concat(MAP.edges.map(e => e.id), MAP.regions.map(r => r.id));
const bridge = (next, done, cap, say) => Kit.map(Object.assign({}, MAP, { id: 'to-' + next, steps: [
  { cap, show: all, done, focus: next, pick: next, prompt: 'Your turn: click “' + MAP.nodes.find(n => n.id === next).label + '” to zoom in.', say }] }));
// chapters: [..., { title: 'The desk', segs: [bridge('desk', ['cat'], 'One part down. Next, the desk.', 'Inside the desk.'), deskScene, deskSim] }]
```

Each bridge needs its own `id`, because the gate's id is derived from it and a gate that shares an id with an earlier one would already count as settled.

Inside a chapter, a small inset keeps the viewer oriented. It is an ordinary scene object:

```js
A('mini', 'mini', { map: MAP, cur: 'desk', x: 40, y: 40, o: 1, layer: 'ui' });
```

## In the two versions

Video: the map builds step by step. At a `pick` step the cursor travels to the node and presses it, and the camera goes in. Slides: the same, except that at a `pick` step the deck holds until the viewer clicks the node themselves. That click is cheap and it makes "zooming in" something the viewer did.

Use `pick` for the bridges into chapters. Use plain `zoom` when the zoom is only an illustration.

## Pitfalls

- The frame after a zoom reports "cut by the stage edge" in the lint. That one is expected.
- Edge labels sit near lines. Check that each label clears every edge and every region border, not only its own.
- A sub-line longer than its node is reported as "label wider than its box". Widen the node with `w`.
- A node's tick sits on its top right corner. Leave that corner clear of edge labels.
- Do not put the mechanism on the map. As soon as a node needs more than a name and one line, that is a zoom-in.
