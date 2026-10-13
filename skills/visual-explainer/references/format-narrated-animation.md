# Format A: narrated animation

A 16:9 stage that changes one beat at a time, with one line of narration under it. It plays like a video.

| | |
|---|---|
| The question it answers | "Why does this exist? What is the idea?" |
| Strong at | Leading someone who is seeing the subject for the first time. It controls exactly where they look |
| Weak at | Looking one detail up later. It is strictly linear |
| Use it for | The opening of the story and of every chapter, any idea built from nothing, the real implementations compared on one picture, a closing matrix |
| Do not use it for | Showing a lot of state at once (simulator) or a long exchange between actors (sequence diagram) |

## Anatomy

- **Objects** are declared once for the whole segment and persist: boxes, text, lines, a character, files, a code block, buttons. Each has a state (position, scale, opacity, colour, how much of it is drawn).
- **Beats** are the steps. A beat has one narration line and a list of phases.
- **Phases** run one after another inside a beat. Everything inside one phase moves together. Cause goes in one phase and effect in the next.
- **The camera** is an object too. Moving it zooms or pans the whole world. Objects on the `ui` layer ignore it.

## Designing a scene

1. Decide the picture the segment ends on. It should summarise the segment at a glance.
2. List every object that picture and the way to it needs, with final positions on the 1600 by 900 stage. Sketch the layout zones first: what lives on the left, in the middle, on the right.
3. Write the beats. One idea each. For each: what changes, then the line.
4. Split each beat into phases so the eye is led: the thing arrives, then it acts, then the result shows.
5. Remove objects from attention when they stop mattering: fade to 0.15 rather than deleting, so the layout stays familiar.

## Data shape

```js
const why = Kit.scene({ title: 'Why a record exists', make() {
  const o = [], A = (id, kind, init) => o.push([id, kind, init || {}]), C = Kit.C;
  A('cam', 'cam');
  A('ttl', 'txt', { x: 800, y: 390, str: 'How a library lends a book', fs: 68, font: 'f-serif', weight: 700 });
  A('shelf', 'line', { d: 'M470,412 H1130', stroke: C.dim, sw: 6, draw: 0, o: 1 });
  A('book', 'box', { x: 800, y: 300, w: 86, h: 210, r: 8, stroke: C.yellow });
  A('ada', 'actor', { x: 190, y: 570, s: .62, fill: C.teal, lab: 0 });
  A('want', 'line', { d: 'M245,548 L770,422', stroke: C.teal, draw: 0, o: 1, head: [770, 422, -13.5] });
  const beats = [
    { cap: 'A library owns one copy of most books.', ph: [{ ttl: { o: 1 } }] },
    { cap: 'Here is a shelf. Every book on it exists exactly once.',
      ph: [{ ttl: { o: 0 }, shelf: { draw: 1 } }, { book: { o: 1 } }] },
    { cap: 'A reader wants it.', ph: [{ ada: { o: 1 } }, { want: { draw: 1 }, book: { sw: 6, _d: 400 } }] }
  ];
  return { o, beats };
}});
```

Every object starts hidden (`o: 0`) unless its init says otherwise. A phase is a map from object id to the properties it should reach:

| In a phase | Meaning |
|---|---|
| `id: { x: 400, o: 1 }` | Tween those properties. Numbers and `#rrggbb` colours glide. Anything else switches at once |
| `_d: 300` | Start this object's change 300 ms into the phase |
| `_t: 1400` | Take 1400 ms instead of the default 850 |
| `_fx: 1` | A short pulse in place, to say "look here" |
| `_set: { label: 'new' }` | Change these instantly, before the tween |
| `_: { wait: 600 }` | Hold for 600 ms after the phase finishes |

Helpers: `Kit.show(ids, gap)` fades a list in with a stagger, `Kit.hide(ids)` fades a list out, `Kit.each(ids, (i, id) => ({...}))` builds a phase for a list.

## Patterns worth knowing

- **Draw a line or a frame:** create it with `draw: 0, o: 1`, then tween `draw: 1`. An arrowhead appears when the line is complete.
- **Type text out:** create a `txt` with `reveal: 0`, then tween `reveal: 1`.
- **Move a card along a route:** one phase per leg, each tweening `x` and `y`.
- **Zoom in:** `cam: { x: 600, y: 300, s: 2.4, _t: 1000 }`. Return with `cam: { x: 800, y: 450, s: 1 }`.
- **An overlay card:** a `veil` and the card's objects on `layer: 'ui'`, faded in over the scene.
- **Step through code:** a `code` object, tweening `hl` to the line being discussed and `show` to reveal lines.
- **A comparison matrix:** `mrow` objects revealed one row at a time on the last beat of a chapter.
- **Count laps of a loop:** a `txt` whose `str` is replaced with `_set` at the start of each lap.

## Gates in a scene

A predict gate fits best. Put `btn` objects on stage, show them in the gate's beat, and give each option its own phases in `opt`:

```js
A('bA', 'btn', { x: 520, y: 740, w: 440, label: 'Trust the librarian’s memory', gate: 'track', pick: 'mem' });
A('bB', 'btn', { x: 1080, y: 740, w: 440, label: 'Write every loan down', gate: 'track', pick: 'write' });
// ...
{ cap: 'How should the library keep track?', ph: [{ bA: { o: 1 }, bB: { o: 1, _d: 150 } }],
  gate: { id: 'track', type: 'predict', options: ['mem', 'write'], answer: 'write',
          prompt: 'Your turn: pick how the library should keep track.',
          say: { mem: 'Memory works until the shift changes.', write: 'Writing it down works whoever is at the desk.' } },
  opt: { mem: [{ xA: { o: 1 } }], write: [{ kB: { o: 1 } }, { rec: { o: 1 } }] } }
```

Any object becomes a control when its init has `gate` and `pick`, not only `btn`. A pressed `btn` fills with its colour by itself.

## In the two versions

Video: each beat plays, then waits for its line to be read. At a gate the cursor presses each option in turn. Slides: one beat per scroll. A beat entered from the previous one animates. A gate holds the deck.

## Pitfalls

- An object you forgot to show stays invisible. So does one whose id is misspelt in a phase: the console warns "missing object".
- These are fixed when an object is created and cannot be tweened: a line's `d`, `head`, `dashed` and `flow`; a file's `name`; a code block's `lines`; a matrix row's content. To change one, use two objects and cross-fade.
- Text does not wrap. Break a long label into two `txt` objects or shorten it.
- Text inside an object drawn at `s: .6` is 60% of its font size. The lint measures the drawn size.
- More than about twelve labels visible at once is a sign that the beat should be split or the old material dimmed.
