# Two versions from one story

Contents

1. Why two, and why from one story
2. The video version
3. The slides version
4. Gates in detail
5. Writing steps that work in both
6. Length and pacing
7. Publishing the pair

## 1. Why two, and why from one story

The two versions answer different needs of the same person. The video is for sitting back: it shows everything, in the best order, with nothing to operate. The slides are for leaning in: the viewer sets the pace and, at the moments that matter, has to act before the story continues.

They are built from one story because every format in the kit draws its picture purely from two inputs: which step, and which choices have been made. The video version walks all the steps and makes all the choices itself. The slides version walks only as far as the viewer has scrolled and uses the viewer's own choices. Nothing else differs, so a fact corrected in the story is corrected in both.

## 2. The video version

What the viewer experiences:

- Press play once. It runs to the end.
- The picture changes one step at a time, and the narration line under it changes with it.
- At a gate, a cursor appears on the stage, travels to a control and presses it. The outcome plays and the line changes with the outcome. The viewer never has to touch the picture, and clicking it does nothing.
- Every case is shown. At a branch, the first path plays, a "rewind" marker flashes, the picture returns to the moment of decision, and the next path plays.
- At a predict gate, the question stays up a little longer before the cursor moves, so the viewer can guess.

Controls: play and pause, previous and next step, a timeline cut into chapters that can be clicked to seek, elapsed and total time, speed (1×, 1.5×, 2×, 0.75×), full screen, and a chapter list with start times. Keys: space or k to play and pause, left and right arrows to step, f for full screen.

How frames are produced (`Kit.frames` in `engine.js`): each step is one frame. A step with a gate becomes several:

| Gate | Frames |
|---|---|
| Predict | The question (with a thinking pause), then one frame per option in `demo` order. Default order: the wrong options, then the answer |
| Explore | The panel at its initial settings, then one frame per case in `demo` |
| Branch | The decision. Then for each option in `demo` order: the press, and the steps that only exist on that path. Between options, a rewind frame. The last option is not rewound: the story continues from it |

Each frame stays for the time its animation takes plus a reading time computed from the length of its line (`Kit.dwell`). Write shorter lines and the video gets faster.

Before play is pressed the page shows the first frame, finished, with a play button over it, so a thumbnail or a shared link shows a real picture.

## 3. The slides version

What the viewer experiences:

- The picture is pinned in the middle of the screen. Each scroll gesture, swipe, or press of the down arrow, space or page-down moves exactly one step. Up goes back. A hard fling of a trackpad still moves one step.
- Arriving at a step from the one before plays its animation. Arriving any other way shows it finished.
- At a gate the deck holds. There is nothing below to scroll to. A yellow chip with a lock says what to do, the controls glow, and trying to scroll on makes the chip nudge.
- Once the gate is settled the chip is replaced by "Unlocked. Scroll to continue". The outcome stays on screen until the viewer moves on.
- Going back is always free. Returning to a branch and pressing the other option re-cuts everything after it.
- A rail on the right edge shows the chapters. Chapters already reached can be clicked.

When a gate counts as settled (`Kit.settled`):

| Gate | Settled when |
|---|---|
| Predict | The option named in `answer` has been pressed. Wrong options show their consequence and leave the gate open |
| Branch | Any option has been pressed |
| Explore | The viewer has tried `need` different combinations of settings. Default 1. `need:'all'` means as many as there are demo cases |

There is deliberately no skip button on a gate. The step exists so that the viewer does it. That puts an obligation on the author: the action must be small, obvious, and stated exactly in `prompt`.

## 4. Gates in detail

A gate is a property of a step. Controls are ordinary elements carrying two attributes, `data-g` (the control's id) and `data-o` (the option's id), and every format has a way to draw them: a `btn` object or any object with `gate` and `pick` in a scene, `P.x.buttons(...)` in a simulator, a node with `pick` on a map. The shells find controls by those attributes, so a new format only has to draw elements that carry them.

```js
gate: {
  id: 'how',                    // one control; or ids:['card','out','book'] for several
  type: 'branch',               // 'predict' | 'branch' | 'explore'
  options: ['here', 'home'],    // option ids; default demo order. For a branch the last one is the path the video continues on
  answer: 'write',              // predict only
  init: {card:'ok', out:'2'},   // explore only: the settings the panel starts with
  need: 2,                      // explore only: different settings the viewer must try in the slides version
  demo: ['here', 'home'],       // the cases the video acts out, in order. For explore: [{card:'expired'}, {card:'ok', out:'5'}]
                                // each case lists only the controls that change; add cap:'...' to give a case its own line
  say: {here:'...', home:'...'},// the narration line for each choice; or a function (ch) => string
  prompt: 'Your turn: read it here, or take it home?',   // the slides version's lock chip
  rewind: 'Back to the desk. This time, take it home.'   // optional line for the video's rewind frame
}
```

Steps that only exist after a particular choice carry `when:{how:'home'}`. Steps without `when` are on every path.

Choosing the kind:

- **Predict** when the viewer has enough to guess and the obvious guess is wrong or incomplete. It turns "the obvious fix fails" from something they are told into something they did.
- **Branch** when the real flow forks on a decision someone actually makes: allow or deny, retry or give up. Both continuations must be real.
- **Explore** when the lesson is "which rule fires for which input". Offer two or three controls with two or three settings each, and make `demo` cover each distinct outcome once.

## 5. Writing steps that work in both

- **Any step can be arrived at cold.** Do not rely on an animation having played. The picture a step ends on must be complete by itself.
- **Everything the story needs later is on the path every viewer takes.** The video shows every case. A slides viewer may press one option and move on. If a later chapter depends on something only one branch shows, restate it after the branch.
- **Steps after a branch are valid after either choice,** or carry `when`.
- **The main path goes last** in `demo`, so the video flows on from it.
- **Every option has a line** in `say`. For a wrong prediction the line explains the failure.
- **The control stays visible after it is pressed,** with the chosen option marked, so the following steps still show what was decided.
- **`prompt` says exactly what to do,** starting with "Your turn". "Your turn: click the desk to zoom in." not "Interact to continue."
- **No gate on the first step of the story,** and no two gates on consecutive steps.
- **A gate inside a branch that is not the last one is not acted out** by the video. Keep nested decisions on the main path.

## 6. Length and pacing

- A chapter of 10 to 25 steps plays for roughly one and a half to four minutes at normal speed. `shoot.py --lint` prints the frame count and the estimated minutes for the whole story.
- If one chapter passes about four minutes, it is two chapters.
- Start each chapter with a one-step title card (`Kit.card`) or a return to the map. It gives the video a breath and the slides a landmark.
- Do not pad. A step that neither changes the picture nor adds an idea should be deleted.

## 7. Publishing the pair

`build.py` writes `<name>-video.html` and `<name>-slides.html`. The video page carries the title as given and the slides page "Title in Slides", unless `--video-title` and `--slides-title` say otherwise. Publish each as its own page and give the user both links. Published pages only receive a plain `#token` from their link, so deep links are `#f120` or `#c3` on the video page and `#s12` on the slides page. Query strings such as `?lint` and `?unlock` work only on the local `preview-*.html` files, which is where they are needed.
