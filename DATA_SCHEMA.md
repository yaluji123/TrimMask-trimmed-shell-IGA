# Data schema

This repository stores exported diagnostic CSV files from the TrimMask
implementation. The files are organized by benchmark and quadrature strategy:

```text
data/trim_diagnostics/<benchmark>/<strategy>/*.csv
```

Typical strategies are:

- `fixed_subcell`: all cut cells are treated by sub-cell masking;
- `fixed_triangle`: all cut cells are treated by ear-cut triangular integration,
  except where the implementation records an internal fallback;
- `severity_aware`: severity-aware rule assignment with explicit fallback
  checks.

Version 1.2.2 contains five CSV files for every benchmark/strategy combination,
for a total of 45 files across three benchmarks and three strategies.

## Common CSV files

The exact file set varies by benchmark, but the following files are commonly
exported.

### `trim_experiment_summary.csv`

Strategy-level summary for table-level comparisons. Typical fields include
candidate and active quadrature-point counts, retained-area consistency error,
line-load or operator-domain errors, runtime, and policy counts.

Runtime fields report operation-level timing emitted inside the analysis
workflow. They exclude external process startup, CAD file loading, and batch
orchestration time.

### `trim_cell_diagnostics.csv`

Cell-level evidence for rule assignment and fallback. Typical fields describe
the knot-span or element identifier, retained area, retained-area fraction, fill
ratio, crossing counts, hole-overlap information, selected rule, fallback
flag/reason, triangle counts, sub-cell counts, candidate points, active points,
and area-closure diagnostics.

### `trim_operator_consistency.csv`

Operator-domain consistency diagnostics for surface loads, line loads, and
coupling interfaces. These records are used to check whether stiffness, loads,
weak enforcement, and coupling query the same retained CAD domain.

### `trim_resolution_advisor.csv`

Feature-aware preprocessing recommendations. These records document the
geometric/operator triggers, recommended control counts, target sizes,
quadrature orders, sub-cell levels, triangular quadrature order, coupling
sampling settings, and the rationale used by the analysis-resolution advisor.

### `trim_summary.csv`

Compact run summary exported by the implementation. It is useful for quickly
checking total element counts, inside/cut/outside classification, generated
quadrature work, accepted quadrature points, fallback counts, and timing.

## Benchmarks

- `trapezoid_pressure`: simple trimmed patch under surface pressure, used for
  retained-domain integration verification and point-economy diagnostics.
- `triangle_line`: simple triangular retained patch under line loading, used for
  sharp-corner and line-load verification.
- `Complex perforated plate`: controlled complex perforated plate used for
  severity-aware quadrature comparisons.

## CAD files

The corresponding CAD geometries are provided in:

```text
data/cad/dwg/
data/cad/iges/
```

DWG files are the native inputs used by the AutoCAD/ObjectARX implementation.
IGES files are geometry exchange exports intended for inspection in external CAD
tools.

The version 1.2.2 engineering-validation DWG files are:

- `perforated_stiffened_plate_1x_displacement_controlled.dwg`: 1x IGA model
  with the prescribed end displacement stored in the DWG;
- `hull_girder_segment_1x.dwg`: 1x IGA model of the hull-girder segment under
  equal and opposite end rotations.

## Abaqus input decks

The matching finite-element inputs are provided in:

```text
data/fem/abaqus/
```

- `perforated_stiffened_plate_displacement_controlled.inp`: perforated
  stiffened plate with `U3 = -0.5 mm` prescribed at the loaded end;
- `hull_girder_segment_torsion.inp`: hull-girder segment with kinematic
  end-section coupling and reference-point rotations of `+0.0012 rad` and
  `-0.0012 rad`.
