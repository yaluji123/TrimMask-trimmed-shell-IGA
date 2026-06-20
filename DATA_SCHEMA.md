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
- `severity_aware`: the proposed severity-aware rule assignment with explicit
  fallback checks.

## Common CSV files

The exact file set varies by benchmark, but the following files are used in the
manuscript.

### `trim_experiment_summary.csv`

Strategy-level summary used for table-level comparisons. Typical fields include
candidate and active quadrature-point counts, retained-area consistency error,
line-load or operator-domain errors, runtime, and policy counts.

### `trim_cell_diagnostics.csv`

Cell-level evidence for rule assignment and fallback. Typical fields describe
the knot-span or element identifier, retained area, retained-area fraction,
fill ratio, crossing counts, hole-overlap information, selected rule, fallback
flag/reason, triangle counts, sub-cell counts, candidate points, active points,
and area-closure diagnostics.

### `trim_operator_consistency.csv`

Operator-domain consistency diagnostics for surface loads, line loads, and
coupling interfaces. These data support the manuscript's claim that stiffness,
loads, weak enforcement, and coupling query the same retained CAD domain.

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
  sharp-corner/line-load verification.
- `Complex perforated plate`: controlled complex perforated plate used for the
  main severity-aware quadrature ablation.
- `Framework structure`: engineering-scale trimmed-shell structure used for
  feature-aware resolution, operator-domain consistency, and fallback evidence.

## CAD files

The corresponding CAD geometries are provided in:

```text
data/cad/dwg/
data/cad/iges/
```

DWG files are the native inputs used by the AutoCAD/ObjectARX implementation.
IGES files are geometry exchange exports intended for inspection in external CAD
tools.
