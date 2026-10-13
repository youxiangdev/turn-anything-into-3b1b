---
name: visual-explainer
description: >-
  Builds an animated, visual explainer of how something works (a paper, a system, a protocol, an
  algorithm, a product, a process) as a web page with the feel of a 3Blue1Brown video. One story is
  written once and delivered in two versions: a video that plays everything by itself, including the
  moments a viewer would normally click, and a scroll-to-next-slide deck that stops and waits wherever
  the viewer should try something themselves. Each explanation inside the story uses whichever of five
  formats fits it: narrated animation, step-through simulator, sequence diagram, zoomable map, or tiny
  isometric world. Use this skill whenever the user wants to really understand or teach a mechanism end
  to end instead of reading a summary: "explain X visually", "make an explainer / animation / video of
  X", "deep dive this paper with me", "walk me through how X works", "I don't want a wall of text",
  "make slides I can scroll through", "做个讲解视频", "用动画解释", "可视化讲清楚", "像 3Blue1Brown 那样",
  "不要 summary", "做成可以滚动的 slides". Also use it to add a chapter to, or re-cut, an explainer that
  was made with it before. Do not use it for a one-page static summary, a data dashboard, or a deck of
  bullet points.
---

# Visual explainer

You are making something a person watches in order to understand a mechanism completely: what each part does, in what order, under which real names and numbers, and why it was built that way. The output is two web pages built from one story.

| | Video version | Slides version |
|---|---|---|
| How it moves | Plays from start to end by itself | One scroll gesture is one step |
| Moments where a viewer acts | A ghost cursor performs them. Every branch and every case is shown, one after another | The viewer performs them. The deck does not scroll further until they have |
| What it is for | Watching the whole thing once | Going at your own pace and trying things |

Both are produced by `scripts/build.py` from the same story file, on the kit in `assets/kit/`. Do not write the two versions separately: they drift apart within a day. Where a request or a scope names versions, `video` is the first and `scroll-slides` (or `slides`) is the second. Build both unless only one is asked for.

## The bar

Each of these names a way an earlier explainer was rejected by the person it was made for. Read them as the definition of done.

1. **The whole mechanism, not a summary.** A box labelled with a part's name explains nothing. For every part show what triggers it, what goes in, the steps in order, what comes out, what happens when it fails, and where a person configures it, with the real identifiers and numbers. If the viewer still has to ask "but what does it actually do?", the chapter is not finished.
2. **The picture explains, the text only narrates.** If understanding requires reading paragraphs, it has failed in the opposite direction. One line of narration per step, a few words on stage, and everything else is shown: things appear, move, split, queue, get refused.
3. **Someone who never read the source can follow it.** Assume no background. A term is never used before its picture has appeared. Every part is introduced by the problem that causes it, so the viewer always knows why they are being shown this now.
4. **The whole first, then zoom in.** Start from one picture of everything, then go into one part at a time and come back out. The viewer should always be able to say where they are.
5. **Real implementations, compared by name.** After the idea is clear, show how two real implementations built it, with their actual names, defaults and limits, and bring in a third only when it made a notably different choice. End each comparison by naming the one question on which they differ.
6. **True, and checked.** Verify every claim against a primary source: documentation and source code outrank papers, and papers outrank blog posts. Sources go stale, so note the version or date you checked. Example values are marked as examples. Where the sources are silent, say so on screen instead of guessing.
7. **No costume.** Do not wrap the whole story in a metaphor or theme unless the user asks for one. Use depth and 3D only where depth is the idea. The tiny-world format is one segment, never the frame for everything.
8. **Agree on the shape before building all of it.** These are large builds and a wrong format is expensive. Propose the outline, build one chapter completely in both versions, let the user judge it, then build the rest. Skip this only when the user has already approved the shape or tells you to go straight through.

## When the content and the scope are handed to you

This skill is often the last stage of a longer run. An earlier stage has researched the subject into a folder of notes, and the user has already confirmed what must be covered. You are then given a brief that says where those are and where to write. In that case:

- **Skip steps 1 and 2 of the workflow.** Audience, language, focus, versions and coverage are already decided. Do not ask the user again.
- **Build only from the content you were given.** Add no facts from memory. If something you need is missing or contradicts itself, report it back as a gap. Never fill it in.
- **The brief decides coverage, this skill decides form.** Everything marked as in scope must appear. Which format shows it, in what order of steps, and what moves, is decided here. An order of telling given in the brief will match the story shape in step 3. Follow it.
- **Write under the output folder you are given:** story files in `story/`, the copy of the kit in `kit/`, built pages in `dist/`.
- **Real names and numbers appear on screen exactly as the content writes them.** A later check reads the output files for those strings. Keep each identifier as one unbroken string in the story file, with no concatenation or escape inside it, and do not swap a figure for a friendlier paraphrase. Where you word something differently on purpose (a number spelled out, a name translated), record the wording you used wherever the brief asks you to record placements.
- **Say where each owed item is shown** when the brief keeps a ledger. Use the chapter title and `frame <n>`, the number printed by `scripts/outline.js`. After every build, save that listing as `outline.txt` in the output folder (`node scripts/outline.js --kit <output>/kit <output>/story/*.js > <output>/outline.txt`): a later check compares the ledger with it. Frame numbers shift when a frame is added earlier in the story, so take them from the current listing.
- **Carry the content's honesty labels onto the screen.** A corrected fact says that the source states otherwise. Reasoning is presented as reasoning. An example value is marked as an example. An open question is shown as open, or left out. Where the brief keeps a ledger, record for each corrected fact and each piece of reasoning the words on screen that mark it; a later check looks for those words.
- **Keep working files out of the output folder.** Notes and extracted facts go in the run's `work/` folder. Every text file under the output folder is read as output by the later check.
- **Build all of it before reporting,** unless a sample was asked for. With a confirmed scope, bar 8 has already been met.

## Workflow

### 1. Scope and align

Settle these before designing anything, from the conversation where possible and by asking where not:

- The subject, and the primary sources you will rely on.
- Who watches. Default: a curious person with no background in the subject.
- The language of the narration and of all text on stage. The user chooses it. It can differ from the language you chat in.
- Which implementations to compare. Usually the two the user cares most about.
- Depth. Default: the full mechanism.

Then propose an outline: the opening question, the parts on the map (five to nine), and the chapter list with the format you plan for each. Build one chapter first unless told otherwise (bar 8).

### 2. Research into a fact sheet

For each part of the mechanism collect: trigger and inputs; the steps in order; real identifiers (function, file, setting and flag names); defaults and limits, with units; outputs; failure paths; where it is configured; how the compared implementations differ, and the reason for each difference. Check each item against a primary source and keep a list of what the sources do not say. This fact sheet is working material. Keep it in the conversation unless the user asks for a file.

A useful test: write down the questions a sharp newcomer would ask about this part. "What is it? Is that really how it works? What is the default? Where do I write that rule? What is this for? How do the two differ?" Every one of them must be answered by something on screen. `references/storytelling.md` lists the eight that always apply.

### 3. Storyboard

The story has a fixed large shape:

1. **Why it exists.** From nothing, build the problem until the subject is the obvious answer.
2. **The map.** One picture of all the parts. Each part appears together with the problem that causes it.
3. **Zoom-ins.** One chapter per part. Each follows the same arc: the problem, the obvious fix, why the obvious fix fails, what is actually done, one concrete example traced through it, the real implementations side by side, and the one question on which they differ.
4. **Close.** Back on the map with every part visited, or one run of the whole thing from start to end.

Write each step as two things: what changes on the stage, and one narration line. `references/storytelling.md` has the full method, the narration rules and the visual language.

### 4. Choose a format for each explanation

The format follows the question the viewer has at that moment.

| The viewer is asking | Format | Read |
|---|---|---|
| "Why does this exist? What is the idea?" | Narrated animation: a stage where one thing changes per step | `references/format-narrated-animation.md` |
| "What does each part hold right now? What if I chose differently?" | Simulator: all the state in panels, pushed forward one step at a time | `references/format-simulator.md` |
| "Which rule decides this case?" | Simulator as an explore panel: controls, a pipeline of checks, a result | `references/format-simulator.md` |
| "Who talks to whom, in what order? How do A and B differ?" | Sequence diagram: one line per actor, time runs down, two lanes for a comparison | `references/format-sequence-diagram.md` |
| "Where does this sit? What are all the parts?" | Zoomable map: the overview that every chapter leaves from and returns to | `references/format-zoomable-map.md` |
| "What is the one picture to remember?" | Tiny world: a courier carries things between stations | `references/format-tiny-world.md` |

How they combine:

- The narrated animation is the spine. Every chapter opens with it, because it is the only format that fully controls where the viewer looks.
- The map is the table of contents. Show it after the opening, and return to it between chapters with finished parts ticked and the next part lit.
- Switch format when the question changes, never for variety. Do not show the same content in two formats unless the second view adds something the first could not: a simulator shows state step by step, and a sequence diagram of the same run then shows its whole shape on one screen.
- Use the tiny world at most once or twice, as a first intuition or a closing recap, and always alongside the real mechanism. It is the easiest format to remember and the easiest to be misled by.
- The simulator and the sequence diagram assume the viewer already has the basic picture. Never open a chapter with them.

### 5. Mark the viewer's turns

A turn is a moment where doing teaches more than watching. In the kit a turn is called a gate. There are three kinds:

| Gate | The moment | Video version | Slides version |
|---|---|---|---|
| **Predict** | Just before a reveal, especially where the obvious answer is wrong | Asks, pauses, presses a tempting wrong answer and shows why it fails, then presses the right one | Holds until the right answer is pressed. A wrong answer shows its consequence and lets the viewer try again |
| **Branch** | A real decision inside the flow that leads to different continuations | Plays one path, rewinds to the decision, plays the other. The main path goes last so the story continues from it | Holds until one option is pressed, then follows that path. The viewer can scroll back and take the other |
| **Explore** | A set of inputs where the interesting thing is which rule decides | Presses through a curated list of cases that covers every distinct outcome | Holds until the viewer has tried a set number of different settings |

Put a gate only where it teaches. One or two per chapter is typical. A step that needs nothing but "next" is not a gate: that is what scrolling is. `references/two-versions.md` has the full contract.

### 6. Build

```bash
cp -R "${CLAUDE_SKILL_DIR}/assets/kit" ./kit          # once per project; then never edit the copy's engine for one story's sake
python3 "${CLAUDE_SKILL_DIR}/scripts/build.py" --kit ./kit --title "Name of the Explainer" --name slug --out dist story/*.js
```

Add `--only video` or `--only slides` when one version is wanted.

If `${CLAUDE_SKILL_DIR}` is not replaced in your environment, use the absolute path of the folder that contains this file. Start the story from `assets/kit/demo-story.js`: it is a small neutral story that uses every format and every kind of gate once, and it is the fastest way to see the data shapes. Build it and open it before writing your own. `references/kit.md` documents everything the kit accepts.

Split a long story into one file per chapter, plus a last file that calls `Kit.story(...)`. Subject-specific drawing (a custom object kind, a recurring layout) belongs in the story files, registered with `Kit.kind(...)`. The kit itself stays free of any subject so it can be reused unchanged.

### 7. Check

Do all of these before showing anything. They take minutes and catch what reading the code cannot.

```bash
node "${CLAUDE_SKILL_DIR}/scripts/outline.js" --kit ./kit story/*.js
python3 "${CLAUDE_SKILL_DIR}/scripts/shoot.py" dist/preview-slug-video.html --lint
python3 "${CLAUDE_SKILL_DIR}/scripts/shoot.py" dist/preview-slug-video.html --frames 0,7,15,22 --out shots
python3 "${CLAUDE_SKILL_DIR}/scripts/shoot.py" dist/preview-slug-slides.html --slides 3,9 --out shots
```

- **Read the script.** `outline.js` prints every frame with its narration line. Read it once from the top as someone who knows nothing: every term must have been shown before it is used, and no line may only describe the picture. It also marks lines that are too long.
- **Lint** visits every frame at rest and reports overlapping text, text cut by the stage edge, labels wider than their box, panels too short for their content and text under about 16px. A frame where the camera is zoomed in will report cut text; that one is expected.
- **Look** at screenshots of at least the densest frame of every segment. The lint cannot see a label hidden behind a shape or an arrow that misses its target.
- **Play** the video version through each gate once and watch the cursor press the right things.
- **Click** through every gate in the slides version: confirm the deck holds, that a wrong answer explains itself, and that the deck releases.
- **Re-read** every name and number on stage against the fact sheet.

`shoot.py` needs Chrome or Chromium. Without it, open the `preview-*.html` files in any browser: add `?lint` to the video page to run the lint, `?f=12` to open on a frame, and `?unlock&s=12` to the slides page to open on a slide with the gates released.

### 8. Publish and report

Publish `dist/<name>-video.html` and `dist/<name>-slides.html` as two separate pages. They are complete page fragments with a `<title>`, a single dark theme chosen on purpose, no external scripts and fonts from Google Fonts only. Give them related titles so they sit together.

Report in the language the user chats in: both links, what is covered, what is deliberately left out, and anything you could not verify. Do not describe the design.

## Rules that hold in every format

- **State is a pure function of the step and the choices made.** Every format in the kit redraws from scratch for any step, which is what makes back, jump, scrub, rewind and deep links work. Never write a step that only looks right when reached from the step before it.
- **One new thing per step.** If a step needs two sentences about two different things, it is two steps.
- **Colour means role, and keeps meaning it.** Pick the roles once for the whole story (for example: the thing being explained, a request, a result, a refusal, the viewer's attention) and never reuse a colour for a second meaning.
- **Things persist.** An object that is on stage stays where it is and transforms. Do not clear the stage and redraw a similar picture: the viewer loses the thread.
- **Stage text is short and large.** A stage is 1600 by 900 units. Body labels are 20 to 26, nothing below 16, and a label is a few words. Sentences go in the narration line.
- **The narration line carries the idea, not a description of the picture.** One or two plain sentences, about 230 characters at most. Say what it means or why it happens.
- **Wide screen first.** The stage is 16:9. On an upright phone both pages still fit without sideways scrolling and show a line asking the viewer to turn the phone.

## Reference files

| File | Read it when |
|---|---|
| `references/storytelling.md` | Storyboarding: the arc of the whole story and of a zoom-in, the eight questions, narration and visual rules, how to compare implementations, what to avoid |
| `references/two-versions.md` | Deciding what becomes a gate, and making sure one story works both played and scrolled |
| `references/format-narrated-animation.md` | Writing a scene: objects, beats, phases, camera |
| `references/format-simulator.md` | Writing a simulator or an explore panel |
| `references/format-sequence-diagram.md` | Writing a sequence diagram, single or side by side |
| `references/format-zoomable-map.md` | Writing the map, the zoom, and the "you are here" inset |
| `references/format-tiny-world.md` | Writing an isometric world |
| `references/kit.md` | Any question about what the kit accepts: story structure, every object kind, gates, commands, deep links, extending it |
| `assets/kit/demo-story.js` | You want a working example of any of the above |
