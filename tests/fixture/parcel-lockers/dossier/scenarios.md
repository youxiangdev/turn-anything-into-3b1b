# Scenarios

## SC1 · A normal delivery
Trigger: a courier arrives with the medium parcel of the running example.

```facts
SC1.1 | step | The courier scans the parcel and P1 returns size class M | src: S1 p3 | status: source
SC1.2 | step | P2 picks the medium compartment and holds it | src: S1 p4-5 | status: source
SC1.3 | step | The door opens, the courier closes it, and the hold becomes an occupied compartment | show: OCCUPIED | src: S1 p5 | status: source
```
