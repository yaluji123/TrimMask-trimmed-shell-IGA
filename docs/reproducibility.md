# Reproducibility notes

This repository supports two levels of reproducibility.

## Level 1: diagnostic data inspection

The primary public evidence consists of the exported CSV files in
`data/trim_diagnostics/`. These files are sufficient to inspect the numerical
diagnostics and strategy comparisons:

- retained-area consistency;
- candidate and accepted quadrature-point counts;
- fixed sub-cell, fixed triangle, and severity-aware rule comparisons;
- fallback counts and fallback reasons;
- load-domain and coupling-domain consistency checks;
- analysis-resolution advisor triggers and effective settings.

This level does not require AutoCAD. Any spreadsheet program or scripting
language can read the CSV files.

## Level 2: rerunning the CAD-native workflow

The DWG files in `data/cad/dwg/`, the IGES exports in `data/cad/iges/`, and the
plug-in binaries in `plugin/AutoCAD_2025_Release_x64/` support rerunning or
inspecting the CAD-native workflow.

This level requires a compatible AutoCAD/ObjectARX environment. The supplied
plug-in is not a standalone solver and cannot be loaded without AutoCAD. See
`docs/environment.md`.

## Benchmark folders

The four benchmark folders provide staged diagnostic evidence:

1. `trapezoid_pressure`: simple retained-domain surface-load verification.
2. `triangle_line`: sharp retained-domain line-load verification.
3. `Complex perforated plate`: controlled comparison for the severity-aware
   quadrature policy.
4. `Framework structure`: engineering-scale example for automatic
   analysis-resolution generation, automatic coupling consistency, and fallback
   diagnostics.

The repository intentionally excludes old standalone demonstration code that
does not generate the exported CAD-native diagnostics.
