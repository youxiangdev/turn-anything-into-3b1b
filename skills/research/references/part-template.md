# Part template

One file per part of the map. The order of the sections is the order in which a person comes to
understand something: what it is, why anyone needed it, where it sits, how it works, one case
walked through, how others do it, and the questions that are still in the air. Keep that order.

## The template

````markdown
# P<n> · <Name of the part>

## In one sentence
What it does, in plain words, without the jargon the rest of the file will introduce.

## Why it exists
The problem: what goes wrong, or cannot be done, without this part.

The obvious approaches, and why each one fails:
- <the first thing anyone would try> ... <the concrete way it breaks>
- <the second> ... <how it breaks>

## Where it sits
Comes after: <part and what it receives>
Hands over to: <part and what it passes on>
Not responsible for: <the neighbouring jobs people confuse it with>

## Mechanism

```facts
P<n>.1 | step | ... | src: S1 p.. | status: source
P<n>.2 | rule | ... | show: ... | src: S1 p.. | status: source
P<n>.3 | param | ... | show: ... | src: S1 p..; S2 | status: verified
P<n>.4 | failure | ... | show: ... | src: S1 p.. | status: source
P<n>.5 | diff | ... | for: ... | src: S1 p.. | status: source
P<n>.6 | failure | <a question no source answers> | status: gap
```

## Worked example
One concrete input followed through the steps above, with the state before and after each step.
Say which values are invented for the example.

## How implementations differ
Only when the source compares several. A small table of the choices each one makes, then one
line naming the single question they are all answering differently.

## Newcomer questions

Q: ...
A: ... (P<n>.2)
````

## What each section is for

**In one sentence.** If this cannot be written without jargon, the part is not understood yet.

**Why it exists.** A mechanism is only memorable as the answer to a problem. Name the problem,
then the one or two things anyone would try first and the concrete way each of them breaks. The
real design then reads as the thing that survives those failures, and its odd details stop
looking arbitrary. Take the problem from the source when it states one; when it does not, reason
it out and say so.

**Where it sits.** Name the neighbours by part ID and say what this part does not do. Many
misunderstandings are boundary mistakes: choosing something is not the same job as checking
whether it is allowed, or as carrying it out.

**Mechanism.** The items. Steps in the order they happen, with every branch and loop back;
then rules, parameters, failure paths and differences. When the source describes several
implementations, write each one's steps with `for:` rather than blending them into one average
mechanism that no real system runs. End with the gaps: the questions a careful reader would ask
that no source answers.

**Worked example.** One input, traced through. Use the map's running example when it fits, so
the parts connect. Show the state changing, not a description of the state changing. Mark
invented values as invented; the names and numbers of the mechanism itself stay real.

**How implementations differ.** The table shows the choices. The line under it names the
question behind them ("is it worse to turn a courier away, or to keep a compartment empty?").
That question is what a person remembers a month later.

**Newcomer questions.** Go through `newcomer-questions.md` for this part. Each answer points to
the item that holds it. A question nobody can answer becomes a `gap` item.

## A filled-in example

The subject is invented, so that the example shows the depth and the format without teaching
anything about a real system. The "source" is an imaginary paper comparing two parcel-locker
networks.

````markdown
# P2 · Compartment assignment

## In one sentence
When a courier scans a parcel at the locker, the locker picks one free compartment for it and
keeps that compartment for this parcel until the door has been closed.

## Why it exists
The problem: a locker has compartments in three sizes and parcels arrive in any order. A parcel
in the wrong compartment either does not fit, or wastes a large compartment that a bigger parcel
will need an hour later.

The obvious approaches, and why each one fails:
- Let the courier choose a door. Couriers pick a large door because it always fits. By
  mid-morning every large compartment holds a small parcel and large parcels are turned away.
- Give each parcel the first free compartment. It is fast, but a small parcel lands in a large
  compartment about as often as not, with the same result.

## Where it sits
Comes after: P1 Check-in, which has scanned the parcel and knows its size class.
Hands over to: P3 Door control, which opens the chosen door.
Not responsible for: deciding whether this parcel may be delivered here at all (P1), or telling
the recipient (P4).

## Mechanism

```facts
P2.1 | step | The locker reads the parcel's size class, S, M or L, from the scan made in P1 | src: S1 p4 | status: source
P2.2 | rule | It picks the smallest free compartment that is at least the parcel's size class; an S parcel gets an M or L compartment only when no S is free | show: pickCompartment() | src: S1 p4 | status: source
P2.3 | step | The chosen compartment is marked held, so that no other courier can be given it | show: HELD | src: S1 p5 | status: source
P2.4 | param | A hold lasts 10 minutes; if the door has not been opened by then, the compartment is released | for: Lockr | show: HOLD_MINUTES = 10 | src: S1 p5; S2 | status: verified
P2.5 | failure | When no compartment of a fitting size is free, the courier's handheld shows "Locker full" and the parcel goes back to the van | show: Locker full | src: S1 p6 | status: source
P2.6 | failure | When the door is opened but never closed, the compartment is marked faulty once the hold expires and stays out of service until a technician resets it | for: Lockr | show: FAULTY | src: S1 p6 | status: source
P2.7 | diff | BoxPost reserves the compartment when the shipping label is printed, not when the courier arrives, and keeps the reservation for 48 hours | for: BoxPost | show: 48 hours | src: S1 p7; S3 | status: corrected | note: the paper says 24 hours; the operator's current developer guide says 48
P2.8 | diff | Because BoxPost reserves early, a parcel that never ships blocks a compartment for the whole reservation, while Lockr never blocks one for longer than a hold | for: Lockr; BoxPost | src: S1 p7 | status: inferred
P2.9 | failure | When two couriers scan in the same second, which of them gets the last free compartment? | src: S1 p5 | status: gap
```

## Worked example
A locker has two small, one medium and one large compartment free. Three parcels arrive in this
order: M, S, S. (The counts and the order are invented to show the rule.)

1. The M parcel gets the medium compartment, the smallest that fits. Free: 2 S, 0 M, 1 L.
2. The first S parcel gets a small one. Free: 1 S, 0 M, 1 L.
3. The second S parcel gets the other small one. Free: 0 S, 0 M, 1 L.

The large compartment is still free for a large parcel. Under "first free compartment" the M
parcel could have taken it, and the next large parcel would have been turned away.

## How implementations differ

| | Lockr | BoxPost |
|---|---|---|
| When a compartment is chosen | When the courier scans at the locker | When the label is printed |
| How long it is kept | 10 minutes | 48 hours |
| What that costs | A courier can arrive at a full locker | Compartments sit empty for parcels still in transit |

The question both are answering: is it worse to turn a courier away, or to keep a compartment
empty?

## Newcomer questions

Q: Who decides which compartment is used, the courier or the locker?
A: The locker. The courier only scans, and the door that opens is the locker's choice (P2.2).

Q: Where is the 10-minute hold set, and who can change it?
A: In the locker's configuration, as `HOLD_MINUTES` (P2.4). No source says who may change it.

Q: What does the courier see when it fails?
A: "Locker full" on the handheld, and the parcel returns to the van (P2.5).

Q: Does a small parcel ever get a large compartment?
A: Yes, but only when no small or medium one is free (P2.2).

Q: The paper says BoxPost holds a reservation for 24 hours. Is that still right?
A: No. The operator's current developer guide says 48 hours (P2.7).
````

What to notice in the example:

- The mechanism is a list of facts a person could check, each with its page, and the real
  identifiers sit in `show:` so the output cannot quietly drop them.
- One item was checked against a second source and agrees (`verified`), one disagrees
  (`corrected`, with what the paper said), one is our own reasoning (`inferred`), and one is a
  question nobody answers (`gap`). None of the four is dressed up as plain fact.
- The worked example shows the free compartments after every step, and says its numbers are
  invented.
- Every newcomer answer points at an item.
