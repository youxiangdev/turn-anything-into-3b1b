# Format C: sequence diagram

Like a call log. Each actor gets a vertical line, time runs downward, and each message is an arrow from the sender's line to the receiver's. The diagram grows one message per step.

| | |
|---|---|
| The question it answers | "Who talks to whom, in what order?" and "How do A and B differ in what they say to each other?" |
| Strong at | Putting a whole exchange on one screen. The best format for two implementations side by side |
| Weak at | Internal state. It shows that a message was sent, not what the receiver now holds. It is also the most abstract of the five |
| Use it for | A recap of a run the viewer has already seen in detail, a protocol between three or more actors, a side-by-side comparison of two designs |
| Do not use it for | First contact with the subject, or anything where the interesting part happens inside one actor |

## Designing one

1. **Actors: three to five.** Order them so that most arrows connect neighbours. The one that talks to everyone goes in the middle.
2. **Messages: six to about twenty-four.** One arrow per thing actually sent. Label it with what is sent, in a few words: "is card #1042 valid?", not "validation request is transmitted".
3. **Group them** into phases or rounds with `grp`. Each group gets a frame and a small label, and the frame grows as its messages appear. A loop reads well as "LAP 1", "LAP 2".
4. **Colour by kind**, with the same roles as the rest of the story: a request in one colour, an answer in another, a refusal in a third.
5. **Work done alone** is a message from an actor to itself. It draws as a small block on that actor's line.
6. **Each message has its own narration line,** and the line says why the message is sent or what to notice, since the label already says what it is.

When the log is longer than the stage, the body scrolls by itself to keep the current message in view. The actor names stay fixed at the top.

## Data shape

```js
const log = Kit.seq({ title: 'The call log',
  actors: [{ id: 'y', name: 'You' }, { id: 'd', name: 'Desk', tone: 'teal' }, { id: 'c', name: 'Catalogue' }, { id: 's', name: 'Shelf' }],
  msgs: [
    { f: 'y', t: 'd', l: 'card + request', grp: 'CHECK', cap: 'Time runs downward. You hand over a card and a request.' },
    { f: 'd', t: 'c', l: 'is card #1042 valid?', tone: 'yellow', grp: 'CHECK', cap: 'The first question is about you.' },
    { f: 'c', t: 'd', l: 'valid, 2 of 5 out', tone: 'green', grp: 'CHECK', cap: 'Every arrow that comes back is an answer.' },
    { f: 'd', t: 'd', l: 'stamp the due date', tone: 'teal', grp: 'LEND', cap: 'A block on a line is work one actor does alone.' }
  ]});
```

`f` and `t` are actor ids, `l` is the label, `tone` is a colour name from the kit's palette or a `#rrggbb` value. A message can carry `when:{gateId:'option'}` like any other step.

## Two lanes: a side-by-side comparison

Give `lanes` instead of `actors`. Each lane is its own small diagram, and both share one grid of rows.

```js
Kit.seq({ title: 'Two ways to lend',
  lanes: [{ title: 'Riverside', actors: [{ id: 'd', name: 'Desk' }, { id: 'c', name: 'Catalogue' }] },
          { title: 'Hilltop',   actors: [{ id: 'd', name: 'Desk' }, { id: 'c', name: 'Catalogue' }] }],
  msgs: [
    { lane: 0, row: 0, f: 'd', t: 'c', l: 'is the card valid?', cap: 'Both desks start with the same question.' },
    { lane: 1, row: 0, f: 'd', t: 'c', l: 'is the card valid?', cap: 'Same row, same message.' },
    { lane: 0, row: 1, f: 'd', t: 'c', l: 'mark on loan',        cap: 'Riverside writes the record before fetching the book.' },
    { lane: 1, row: 2, f: 'd', t: 'c', l: 'mark on loan',        cap: 'Hilltop writes it afterwards. The empty row on the right is the whole difference.' }
  ]});
```

Rules for two lanes:

- Put the same logical step on the same `row` in both lanes. A step that one side does not have leaves an empty row there, and that gap is the point of the picture.
- Reveal in the order that makes the comparison: a pair at a time when the two match, one side then the other where they differ.
- Three or four actors per lane at most. Labels must be shorter, because each lane is half as wide.
- Group frames are not drawn in two-lane diagrams. Say the phase in the narration instead.

## In the two versions

Video: one message per frame. The arrow draws from sender to receiver, a band marks the current row, earlier messages dim slightly. Slides: one message per scroll. Scrolling back removes messages again, so the viewer can replay a confusing stretch.

Gates are rarely useful here. If the viewer should decide something, do it in a simulator and use the sequence diagram afterwards to show the shape of what happened.

## Pitfalls

- A label wider than the gap between its two actors overlaps a neighbour. Keep labels under about 28 characters between adjacent actors, less in two lanes. The lint reports overlaps.
- More than five actors makes every label too small. Split into two diagrams by phase.
- A sequence diagram of something the viewer has not yet understood is a wall of arrows. Explain first, summarise with this.
