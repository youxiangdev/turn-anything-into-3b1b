# Map

## The whole thing in one paragraph
A courier scans a parcel at a locker. The locker learns the parcel's size, picks a compartment
for it, and holds that compartment until the door has been opened and closed.

## The running example
A medium parcel for a locker that has two small, one medium and one large compartment free.

## Parts and connections

```facts
M.1 | part | P1 Check-in exists because the locker knows nothing about a parcel until it is scanned | src: S1 p3 | status: source
M.2 | part | P2 Compartment assignment exists because compartments come in three sizes and parcels arrive in any order | src: S1 p4 | status: source
M.3 | link | P1 hands the parcel's size class to P2 | src: S1 p3 | status: source
M.4 | link | When P2 finds no fitting compartment, control returns to the courier, who may scan a different parcel in P1 | src: S1 p6 | status: source
```
