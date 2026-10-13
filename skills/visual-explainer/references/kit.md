# The kit: reference

Contents

1. Files and commands
2. Story structure
3. The segment interface
4. Scene objects: every kind and its properties
5. Phases
6. Gates
7. Colours, fonts and theme
8. Testing aids and deep links
9. Extending the kit
10. Known limits

## 1. Files and commands

```
assets/kit/
  engine.js       stage, scene engine, gate protocol, the two timelines, layout lint
  formats.js      simulator, sequence diagram, map, tiny world
  kit.css         every style both shells share
  video.html      the video shell
  slides.html     the slides shell
  demo-story.js   a neutral story that uses everything once
scripts/
  build.py        story files -> two publishable pages and two local previews
  shoot.py        screenshots and layout lint through headless Chrome
  outline.js      the story as a script: every frame with its narration line
```

```bash
# build: pages land in --out
python3 scripts/build.py --title "Name" --name slug --out dist [--kit ./kit] [--only video|slides] story/*.js
# read the narration in one go, with frame numbers
node scripts/outline.js [--kit ./kit] story/*.js
# layout problems on every frame
python3 scripts/shoot.py dist/preview-slug-video.html --lint
# look at chosen frames or slides
python3 scripts/shoot.py dist/preview-slug-video.html --frames 0,7,15 --out shots
python3 scripts/shoot.py dist/preview-slug-slides.html --slides 3,9 --out shots
```

`build.py` checks the syntax of the kit and the story with Node when it is available, then inlines everything. Each page is one self-contained file of about 75 KB plus the story. `<name>-video.html` and `<name>-slides.html` are page fragments that start with `<title>`, ready to publish. The `preview-*.html` twins are the same pages wrapped as complete documents for opening locally. Story files are concatenated in the order given, so a shell glob of numbered files works: `story/00-common.js story/10-why.js ... story/99-story.js`.

## 2. Story structure

```js
Kit.story({
  title: 'How a Library Lends a Book',
  credits: 'Sources and the date they were checked.',
  chapters: [
    { kicker: 'Part 1', title: 'Why a record exists', segs: [why] },
    { kicker: 'Part 2', title: 'The map', segs: [Kit.map(MAP)] },
    { kicker: 'Zoom-in', title: 'The desk', segs: [bridge, deskScene, deskSim, deskLog] }
  ]});
```

A chapter is a list of segments. A segment is one use of one format. `kicker` is the small label before the chapter title (default "Part n"). The call to `Kit.story` goes last, after every segment it names exists. Wrap each story file in `(function(){ ... })();` and share values between files through one global object of your own, such as `window.STORY_PARTS = {}`.

## 3. The segment interface

Every format returns an object with the same five members. A new format only needs to provide these.

| Member | Contract |
|---|---|
| `kind`, `title` | A name for the format and a title for outlines |
| `steps(ch)` | The list of steps on the path for the choices `ch`. A step is any object with `cap`, and optionally `gate` and `when` |
| `mount(layer)` | Build the picture into `layer.svg` (an SVG with a 1600 by 900 view box) and `layer.html` (a 1600 by 900 block that scales with the stage) |
| `unmount()` | Stop everything. The shell removes the layer |
| `render(path, k, ch, how)` | Show step `k` of `path` under choices `ch`. `how` is `'jump'` (draw it finished), `'enter'` (animate from step `k-1`) or `'pick'` (a choice was just made on this step: animate its outcome). Returns a promise of `true`, or `false` if a later call overtook it |

The state shown for `(path, k, ch)` must be the same however it was reached.

## 4. Scene objects: every kind and its properties

Declared as `[id, kind, init]`. Every kind has `x`, `y` (its centre unless noted), `s` (scale, 1), `o` (opacity, **0 by default**), and accepts `layer: 'ui'` (drawn above the camera's world and not moved by it) and `gate` + `pick` (make it a control).

| Kind | Properties (defaults) | Notes |
|---|---|---|
| `cam` | `x` 800, `y` 450, `s` 1 | The camera. Declare one as `['cam','cam']`. Tween it to zoom and pan |
| `box` | `w` 200, `h` 80, `r` 14, `fill`, `stroke`, `sw` 2.5, `draw` 1, `label`, `sub`, `tcol`, `fs` 26, `font`, `lw` 500, `subcol`, `subfs` 20, `subTop` false | A rounded box with a label and an optional second line. `fill: 'none'` with `draw` 0 to 1 draws a frame |
| `txt` | `str`, `fs` 30, `fill`, `anchor` 'middle', `font` 'f-sans', `weight` 500, `reveal` 1 | One line of text. `reveal` 0 to 1 types it out |
| `line` | `d`, `stroke`, `sw` 3, `draw` 1, `dashed`, `flow`, `head: [x, y, angle]` | Any path. `d`, `dashed`, `flow` and `head` are fixed at creation. `flow` makes a dashed line march |
| `actor` | `fill`, `px` 0, `py` 0, `think` 0, `lab` 1, `name` | A round character with eyes. `px`, `py` from -1 to 1 steer its gaze. `think` 1 shows a turning ring |
| `file` | `name`, `hl` 0 | A document icon. `hl` 0 to 1 lights it |
| `term` | `name` 'terminal', `hl` 0 | A terminal icon |
| `shape` | `d`, `fill`, `stroke`, `sw` | Any filled path, for beams, regions and arrows of your own |
| `bar` | `w` 0, `h` 28, `fill` | A horizontal bar growing from its left end. For meters and budgets |
| `brk` | `w` 200, `label`, `stroke`, `draw` 1 | A bracket under a group of things, with a label |
| `code` | `lines`, `w` 560, `fs` 20, `lh` 30, `hl` -1, `show` 99, `title` | A block of monospace lines. `hl` lights one line and dims the rest. `show` is how many lines are revealed |
| `btn` | `w` 240, `h` 66, `label`, `fs` 24, `tone` | A pill button. Needs `gate` and `pick`. Fills when its option is the current choice |
| `mrow` | `label`, `marks`, `note`, `lx` 560, `xs`, `nx` 1320 | One row of a comparison matrix. `marks` holds 2 (yes), 1 (partly) or 0 (no) for the columns at `xs` |
| `mini` | `map`, `cur`, `k` .13, `note` | A small inset of a map def with one node lit |
| `xmark`, `tick`, `lock` | none | A red cross, a green tick, a padlock |
| `veil` | `fill` | A full-stage cover. Fade it to dim everything under an overlay |

Fonts are the classes `f-sans`, `f-serif`, `f-mono` and `f-math` (serif italic, for a term being defined).

## 5. Phases

A beat's `ph` is a list of phases, run in order. A phase maps object ids to target properties.

- Numbers and `#rrggbb` colours tween over 850 ms with an ease in and out. Other values switch at the start.
- `_d` delays that object within the phase, `_t` sets its duration, `_fx: 1` pulses it, `_set: {...}` assigns instantly.
- `_: { wait: 600 }` holds after the phase.
- An id that does not exist logs "missing object" and is skipped.

`Kit.show(ids, gap)`, `Kit.hide(ids)` and `Kit.each(ids, (i, id) => ({...}))` build phases for lists. `Object.assign` merges them with hand-written entries.

## 6. Gates

See `references/two-versions.md` for the full description. In short, a step carries:

```js
gate: { id | ids, type: 'predict' | 'branch' | 'explore', options, answer, init, need, demo, say, prompt, rewind }
```

- A control is any element with `data-g` (control id) and `data-o` (option id). Scene objects get them from `gate` and `pick`, simulator panels from `P.x.buttons(controlId, options, ch, label)`, map nodes from a step's `pick`.
- Choices live in one object, `ch`, keyed by control id. Steps, `do` functions and `draw` functions all receive it.
- In a scene, a gate's beat can give each option its own phases: `opt: { optionId: [phase, ...] }`. They play when that option is pressed and stay applied afterwards.
- Gate ids must be unique across the whole story. A second gate with an id already used is treated as answered.

## 7. Colours, fonts and theme

`Kit.C` holds the palette, and `kit.css` holds the same values as CSS variables. Change both together to re-skin an explainer.

| Name | Default role |
|---|---|
| `bg`, `stage`, `panel` | Page, stage and panel grounds |
| `ink`, `ink2`, `dim`, `ink3`, `faint`, `line` | Text from strongest to weakest, then outlines |
| `blue` | The central actor |
| `teal` | The system around it |
| `yellow` | A request, or whatever is in focus |
| `green` | A result, a pass |
| `red` | A refusal, a failure |
| `orange` | Needs care, or needs a person |

Anywhere a `tone` is accepted, give one of these names or a `#rrggbb` value. `Kit.mix(a, b, t)` blends two colours. The design is a single dark theme on purpose: the stage is a video frame. Fonts load from Google Fonts with system fallbacks.

## 8. Testing aids and deep links

| On the local `preview-*.html` | Effect |
|---|---|
| video `?f=37` | Open on frame 37 |
| video `?still` | Draw without motion, for screenshots |
| video `?lint` | Visit every frame, then show a report at the bottom of the page |
| slides `?s=12` | Open on slide 12 (counting from 0) |
| slides `?unlock` | Settle every gate with the last case of its `demo`, so every slide is reachable |

| On a published page | Effect |
|---|---|
| video `#f37`, `#c3` | Open on frame 37, or on chapter 3 |
| slides `#s12` | Open on slide 12 (counting from 1), if it is within the unlocked part |

A format that clips part of its picture marks the clipped group with `data-clip="x,y,w,h"` in stage units, and the lint ignores text outside that box.

Lint messages: "overlap" (two texts collide), "cut by the stage edge", "label wider than its box", "panel too short for its content", "overflows its panel", "small text". The lint only sees text. Check shapes by looking.

## 9. Extending the kit

Add to the story files, not to the kit, unless the addition is free of any subject.

- **A new object kind:** `Kit.kind('name', defaults, (g, s0, ctx) => { /* build SVG into g once */ return s => { Kit.base(g, s); /* update from state s */ }; })`. `Kit.E(tag, attrs, parent, text)` creates SVG elements. The returned function runs on every animation frame for that object, so keep it to attribute updates.
- **A new panel content type** in a simulator: use `P.x.html(...)`, and put its styles in the story with a `<style>` you add from JavaScript, or propose it for `kit.css` if it is general.
- **A new format:** return an object with the five members in section 3, draw into the layer you are given, and mark any controls with `data-g` and `data-o`. Both shells will play it without changes.

## 10. Known limits

- The stage is fixed at 16:9. On an upright phone it is small, and both pages ask the viewer to turn the phone.
- There is no sound. The narration line is the voice.
- A gate inside a branch that is not the last one is not acted out by the video version.
- The video's total time is an estimate from line lengths.
- Scene text does not wrap, and a line's path cannot be tweened.
- `shoot.py` needs Chrome or Chromium on the machine.
