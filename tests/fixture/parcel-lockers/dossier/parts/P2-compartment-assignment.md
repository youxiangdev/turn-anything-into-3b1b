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
Hands over to: the door, which opens.
Not responsible for: deciding whether this parcel may be delivered here at all (P1).

## Mechanism

```facts
P2.1 | step | The locker reads the parcel's size class, S, M or L, from the scan made in P1 | src: S1 p4 | status: source
P2.2 | rule | It picks the smallest free compartment that is at least the parcel's size class; an S parcel gets an M or L compartment only when no S is free | show: pickCompartment() | src: S1 p4 | status: source
P2.3 | step | The chosen compartment is marked held, so that no other courier can be given it | show: HELD | src: S1 p5 | status: source
P2.4 | param | A hold lasts 10 minutes; if the door has not been opened by then, the compartment is released | for: Lockr | show: HOLD_MINUTES = 10 | src: S1 p5; S2 | status: verified | hinge: yes
P2.5 | failure | When no compartment of a fitting size is free, the courier's handheld shows "Locker full" and the parcel goes back to the van | show: Locker full | src: S1 p6 | status: source
P2.6 | failure | When the door is opened but never closed, the compartment is marked faulty once the hold expires and stays out of service until a technician resets it | for: Lockr | show: FAULTY | src: S1 p6 | status: source
P2.7 | diff | BoxPost reserves the compartment when the shipping label is printed, not when the courier arrives, and keeps the reservation for 48 hours | for: BoxPost | show: 48 hours | src: S1 p7; S3 | status: corrected | hinge: yes | note: the paper says 24 hours; the operator's current developer guide says 48
P2.8 | diff | Because BoxPost reserves early, a parcel that never ships blocks a compartment for the whole reservation, while Lockr never blocks one for longer than a hold | for: Lockr; BoxPost | src: S1 p7 | status: inferred
P2.9 | failure | When two couriers scan in the same second, which of them gets the last free compartment? | src: S1 p5 | status: gap
```

## Worked example
A locker has two small, one medium and one large compartment free. Three parcels arrive in this
order: M, S, S. (The counts and the order are invented to show the rule.)

1. The M parcel gets the medium compartment, the smallest that fits. Free: 2 S, 0 M, 1 L.
2. The first S parcel gets a small one. Free: 1 S, 0 M, 1 L.
3. The second S parcel gets the other small one. Free: 0 S, 0 M, 1 L.

## How implementations differ

| | Lockr | BoxPost |
|---|---|---|
| When a compartment is chosen | When the courier scans at the locker | When the label is printed |
| How long it is kept | 10 minutes | 48 hours |

The question both are answering: is it worse to turn a courier away, or to keep a compartment
empty?

## Newcomer questions

Q: Who decides which compartment is used, the courier or the locker?
A: The locker (P2.2).

Q: Where is the 10-minute hold set, and who can change it?
A: In the locker's configuration, as `HOLD_MINUTES` (P2.4). No source says who may change it.

Q: What does the courier see when it fails?
A: "Locker full" on the handheld (P2.5).
