# P1 · Check-in

## In one sentence
The courier scans the parcel's label, and the locker learns which parcel it is and how big it is.

## Why it exists
The problem: the locker cannot choose a compartment for something it knows nothing about.

The obvious approaches, and why each one fails:
- Have the courier type the size in. Couriers round up to be safe, and large compartments run out.

## Where it sits
Comes after: the courier arriving at the locker.
Hands over to: P2 Compartment assignment, with the size class.
Not responsible for: choosing a compartment (P2).

## Mechanism

```facts
P1.1 | step | The courier scans the barcode on the label with the locker's reader | src: S1 p3 | status: source
P1.2 | step | The locker looks the barcode up and receives the parcel's size class, S, M or L | show: sizeClass | src: S1 p3 | status: source
P1.3 | failure | When the barcode is unknown, the screen shows "Parcel not expected here" and nothing is assigned | show: Parcel not expected here | src: S1 p3 | status: source
```

## Worked example
The courier scans the medium parcel of the running example. The lookup returns size class M.
(The parcel is invented for the example.)

## Newcomer questions

Q: Who measures the parcel?
A: Nobody at the locker. The size class comes from the lookup (P1.2).

Q: What happens with a parcel meant for another locker?
A: The screen shows "Parcel not expected here" (P1.3).

Q: Does check-in pick the compartment?
A: No, that is P2.
