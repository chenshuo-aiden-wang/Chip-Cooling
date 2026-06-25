# K-16 Cold Plate

A cold plate design study on the ASME K-16 / IEEE ITherm Student Cold Plate Design Competition
problem. A fin plate is designed for a non uniform power map and evaluated in Ansys Icepak and
Fluent against the competition Figure of Merit.

See [`SPEC.md`](SPEC.md) for the problem data and the Figure of Merit.

## Structure

```
SPEC.md       problem data and Figure of Merit
model/        analytical model, used as a cross check on the CFD
cfd/          Icepak and Fluent cases                (coming)
report/       write up                               (coming)
resources/    competition guidance and CAD
```

## Tools

Ansys Icepak and Fluent for the CFD. Python (`model/`) for an analytical cross check.
