# Storytelling: how to plan the explainer

Contents

1. The shape of the whole story
2. The arc of one zoom-in
3. The eight questions every zoom-in answers on screen
4. Context for someone new
5. Writing the narration line
6. The visual language
7. Comparing real implementations
8. Honesty
9. What gets rejected

The examples below use a library lending a book, the same neutral subject as `assets/kit/demo-story.js`.

## 1. The shape of the whole story

| Part | Job | Typical format |
|---|---|---|
| Why it exists | Start from something the viewer already accepts. Add one difficulty at a time until the subject is the obvious answer. End on a one-line definition | Narrated animation |
| The map | One picture of every part. Each part arrives with the problem that causes it, in the order a newcomer would hit those problems | Narrated animation or zoomable map |
| Zoom-ins | One chapter per part, each following the arc in section 2 | Opens with narrated animation, then whatever fits |
| Close | The map with every part visited, or one complete run from start to end | Map, sequence diagram or tiny world |

Two decisions shape everything else, so make them early.

**The running example.** Pick one small, concrete case and carry it through the whole story: one request, one file, one customer, one packet. It should be small enough to draw and rich enough to pass through every part. Every chapter then shows what its part does to that same case, and the viewer never has to learn a new example.

**The parts on the map.** Five to nine. Fewer and the map says nothing. More and nobody holds it in their head. If the subject has twenty parts, group them: the map shows the groups and a zoom-in shows what is inside one.

## 2. The arc of one zoom-in

Each chapter makes the same seven moves. Skipping the first three is the most common way to end up with a chapter only experts can follow.

1. **The problem.** Show the difficulty with the running example, before any solution exists. "Two readers want the same book this week."
2. **The obvious fix.** Show what anyone would try first. "The librarian remembers who has it."
3. **Why the obvious fix fails.** Show it failing, concretely. "The shift ends. The memory goes home." This is the moment a predict gate belongs.
4. **What is actually done.** The real mechanism, built one piece at a time. "Every loan is one written record."
5. **One example, traced.** The running example goes through the mechanism step by step with real values, including one case where it is refused or fails.
6. **Real implementations.** How implementation A built it, then how B did, on the same picture, changing only what differs. Real names, defaults, limits.
7. **The axis.** One closing step that names the question on which they differ. "Where does the decision live: with the desk, or with the catalogue?" This is the line people remember.

A chapter is usually 10 to 20 steps. Under 8 it is probably a summary. Over 25 it is probably two chapters.

## 3. The eight questions every zoom-in answers on screen

Before calling a chapter finished, find the step that answers each of these. A question with no step is a hole a viewer will fall into.

1. What is this part, in one sentence?
2. Why does it exist? What goes wrong without it?
3. What triggers it, and what does it receive?
4. What exactly happens, in what order?
5. What are the real names, defaults and limits?
6. Where does a person configure or change it?
7. What happens when it fails or refuses, and where does that result go?
8. How do the compared implementations differ, and what is the reason?

## 4. Context for someone new

- **Picture before term.** Show the thing, then name it. "This form is called a record", said while the record is on screen, teaches the word. The word used three steps earlier teaches nothing.
- **Say why now.** Each new element enters as the answer to something the viewer just saw go wrong.
- **Cause before effect.** Draw the request before the response, the rule before the refusal, the overflow before the fix.
- **One new idea per step.** Two ideas in one step means the second is lost.
- **Return to the map.** At the start and end of each chapter, show where this part sits. A small "you are here" inset is enough inside a chapter.
- **Repeat on purpose.** Restating the previous chapter's conclusion in one line at the start of the next is not padding. A viewer who paused yesterday needs it.

## 5. Writing the narration line

The line under the stage is the voice of the video. It carries the idea. The stage carries the evidence.

- One or two sentences, about 230 characters at most. Longer lines mean the step is doing two things.
- Plain words. Spell out an abbreviation the first time. No term that has not been shown.
- Say what it means or why, not what is visible. The viewer can see that a box turned red.
- Present tense, active voice, and "you" where it is natural.
- Numbers and names are welcome when they are the point: "after three refusals in a row" beats "after several refusals".
- In a gate, write one line per choice: what happens and why. A wrong answer's line explains the failure without scolding.

| Weak | Better |
|---|---|
| "Now the record appears in the catalogue panel and turns yellow." | "Before the book leaves, the desk writes the loan down. If the record and the shelf ever disagree, the record is what people will believe." |
| "The system utilises a multi-stage validation pipeline." | "Three checks run in a fixed order, and the first one that fails ends the loan." |
| "Wrong! The correct answer is B." | "Memory works until the shift changes. Then the one person who knew has gone home." |

## 6. The visual language

- **Colour is a role.** Assign roles once and keep them for the whole story. A workable default on the kit's palette: blue for the central actor, teal for the system around it, yellow for a request or for the thing in focus, green for a result or a pass, red for a refusal, orange for something that needs care or a person's attention, grey for everything inert. Never give a colour a second meaning in a later chapter.
- **Persistence.** Keep objects on stage and transform them. When a chapter needs a clean stage, fade the old picture down rather than cutting.
- **Motion means cause.** A thing moves because something sent it. A line draws from its source to its target. Nothing moves for decoration.
- **Position means something.** Choose a layout rule and keep it: for example the past on the left, the actor in the middle, the outside world on the right. A recurring object always returns to the same place.
- **Text budget.** A label is a few words. A stage rarely needs more than about twelve labels visible at once. Real identifiers are shown in monospace so they read as the actual name.
- **Size.** On the 1600 by 900 stage: titles 48 to 76, labels 20 to 28, small notes 16 to 20. Text inside an object drawn at a reduced scale shrinks with it, so check the drawn size, not the font size.
- **Emphasis.** One thing is in focus per step. Dim or fade what is not being discussed rather than adding more highlight.
- **Loops are drawn as loops.** If something repeats, the picture shows the path closing on itself and something travelling round it, with a visible count of laps.

## 7. Comparing real implementations

- Explain the idea first with no product names. Names arrive in move 6, when the viewer can tell what they are looking at.
- Compare on the same picture. Keep the layout, change only the parts that differ, and let the difference be the only thing that moves.
- Put the real identifier on stage next to the plain-language name: the plain name is for understanding, the identifier is for finding it later.
- Use a sequence diagram with two lanes when the difference is in who talks to whom. Use a matrix (rows of implementations, columns of capabilities) when the difference is in which features exist. Keep a matrix for the final step of a chapter, after each cell has been explained.
- Be fair. State each design's reason, not just its cost. A viewer should finish able to argue for either.
- Add a third implementation only when it does something neither of the main two does. Give it one step, not a full tour.
- Date the facts. A line in the credits such as "checked against the documentation and source, October 2026" tells the viewer how far to trust it later.

## 8. Honesty

- An example value looks like an example: a made-up file name, a round number. Never dress an invented figure as a measurement.
- When the sources do not say how something works, a step says so: "The study does not say how ties are broken." Viewers trust the rest more for it.
- When a source is out of date, show the current behaviour and say in the credits what changed.
- A simplification is allowed when it is a true statement at lower resolution. A simplification that the next chapter would have to contradict is not.

## 9. What gets rejected

These are the failure modes that have actually sent explainers back to the start.

- **Summary cells.** A table or diagram whose cells are short labels. It looks complete and teaches nothing.
- **Walls of text.** Accurate paragraphs that must be read word by word. The fix is not shorter paragraphs. It is moving the content into the picture.
- **Boxes with names in them.** A flowchart node that says "cache" instead of showing what goes in, what comes out and what happens on a miss.
- **A format chosen for novelty.** A tiny world where a simulator was needed, because the world looked nicer.
- **A theme standing in for the mechanism.** A factory metaphor so elaborate that the viewer learns the factory and not the subject.
- **Gates as decoration.** A click that reveals the next sentence. It interrupts without teaching.
- **Thirty objects at once.** Everything shown from the first frame. Build the picture up.
- **Narration that reads the screen aloud.**
- **Claims from one secondary source.** A paper's description of software that has since changed.
