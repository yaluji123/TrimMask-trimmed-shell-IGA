# TrimMask minimal reproducibility package

This package is intended as the minimal public companion material for the manuscript
"A B-Rep-driven computational workflow for CAD-native trimmed shell isogeometric analysis".

## Scope of this public package

The research code used for the manuscript is a complete AutoCAD/ObjectARX C++
program.  It includes DWG/B-Rep pre-processing, TrimMask construction from native
CAD entities, isogeometric shell stiffness/load/coupling assembly, linear solving,
stress recovery, and CAD-based post-processing/visualization.

This public folder is not the complete AutoCAD/ObjectARX program.  It is a
minimal, CAD-independent Python reference package that shows the reproducible
TrimMask and cut-cell quadrature part of the implementation.  DWG entities,
AutoCAD handles, ObjectARX SDK calls, shell stiffness matrices, and post-processing
objects are intentionally replaced by small JSON trim-loop cases and the scalar
area integral `f(u,v)=1`.  The purpose is to let readers inspect and rerun the
geometric decision layer used by the full C++ code:

1. normalized UV trimming loops stored as a reusable TrimMask data layer;
2. background knot-span element classification;
3. masking-based sub-cell quadrature;
4. triangle-based visible-region quadrature;
5. benchmark logs for the backend comparison and the box-girder scale example.

## What TrimMask means here

In the full AutoCAD/ObjectARX C++ code, a TrimMask is the patch-level
trimmed-domain data layer built after CAD B-Rep extraction.  For each shell patch
it stores the retained outer UV loop, hole loops, trimmed boundary chains, and
domain-normalization information.  The rest of the solver does not repeatedly
query the CAD kernel; it queries this TrimMask object to answer the same geometric
questions everywhere: whether a UV point is active, whether a background knot-span
element is inside/outside/cut, which visible subregion should be integrated, and
which trimmed boundary chains are available for line loads, weak boundary
conditions, coupling, and post-processing.

In this Python package, the same concept is represented by the `TrimMask` data
class in `src/trim_quad.py` and by the `trim_mask` block in each JSON case file.
The implementation is deliberately small, but the data flow matches the manuscript:
JSON trim loops -> `TrimMask` -> element classification -> masking or triangle
quadrature -> statistics.

## Current runnable code

This folder now contains a CAD-independent reference implementation:

```text
src/trim_quad.py          # TrimMask, element classification, masking backend, triangle backend
src/cpp_reference/        # reference C++ TrimMask header from the full ObjectARX project
scripts/run_case.py       # command-line runner for one case/backend
scripts/run_all_examples.py
scripts/parse_scale_log.py
data/examples/*.json      # small UV-domain benchmark cases
data/logs/*.log           # Table 8 scale logs
docs/full_project_architecture.md
```

Run a single case:

```bash
python scripts/run_case.py --case data/examples/trapezoid_surface_load.json --backend triangle
python scripts/run_case.py --case data/examples/trapezoid_surface_load.json --backend masking
python scripts/run_case.py --case data/examples/triangular_line_load.json --backend triangle
python scripts/run_case.py --case data/examples/perforated_plate.json --backend masking
```

Run all examples:

```bash
python scripts/run_all_examples.py
```

Parse the Table 8 scale logs:

```bash
python scripts/parse_scale_log.py data/logs/table8_triangle_backend_scale.log data/logs/table8_masking_backend_scale.log
```

The runner reports element classes, integration-point counts, triangle/sub-cell
counts, fallback counts, timing, and a scalar area check.  It integrates
`f(u,v)=1` over the retained trimmed region, so `integrated_area` can be used to
compare the masking and triangle backends without requiring the full shell
stiffness assembly.

## Reference C++ header

The folder `src/cpp_reference/` contains `TrimmedUV.h`, the C++ header used in
the full AutoCAD/ObjectARX implementation to store and query patch-level TrimMask
records.  It is provided to show how the released Python `TrimMask` class maps to
the project code.  This header is not part of the standalone runner and is not
expected to compile without the original ObjectARX project, because it depends on
Autodesk's `adesk.h` and the current-document registry implementation.

## Recommended GitHub repository structure

```text
TrimMask-iga-EWC/
  README.md
  LICENSE
  CITATION.cff
  src/
    trim_quad.py
    cpp_reference/
      TrimmedUV.h
  data/
    trim_quad_case_template.json
    examples/
      trapezoid_surface_load.json
      triangular_line_load.json
      perforated_plate.json
    logs/
      table8_triangle_backend_scale.log
      table8_masking_backend_scale.log
  scripts/
    run_case.py
    parse_scale_log.py
  docs/
    DATA_SCHEMA.md
    project_code_mapping.md
```

## What to include from the current project

The following files/regions are the source of the minimal implementation:

- `IGAforCAD/IGAforCAD/TrimmedUV.h`: TrimMask registry, UV loops, hole loops,
  curve trims, coordinate-domain normalization, and point-in-trim tests.
- `IGAforCAD/IGAforCAD/Curves.cpp`: trimmed-element classification, sub-cell
  masking, triangle/Clipper2 visible-region construction, quadrature statistics.
- `IGAforCAD/IGAforCAD/SolveConfig.h`: public quadrature settings:
  `TrimQuadratureMode`, `QuadGaussN`, `SubCellDiv`, and `TriGaussN`.
- `IGAforCAD/IGAforCAD/DocData.h`: the fields used in `IGATrimStiffStats`.
- `IGAforCAD/IGAforCAD/igaPaletteChildDlg.cpp`: scale-report log lines used for
  Table 8.

Do not publish the complete plug-in unless all project, dependency, and CAD-kernel
licensing constraints have been checked.

## Minimal command-line behavior

The current Python implementation accepts one JSON case file and one backend.

The output should include at least:

```text
elements: total=..., inside=..., cut=..., outside=...
quadrature: stdElem=..., stdGP=..., subCells=..., subTestGP=..., subAcceptedGP=..., triOuter=..., triHole=..., triGP=..., fallback=...
timings: classify=... ms, clipTri=... ms, trimTotal=... ms
```

This is enough to support the manuscript's reproducibility claim without exposing
the full CAD plug-in.
