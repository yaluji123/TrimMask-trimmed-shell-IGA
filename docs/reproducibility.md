# Reproducibility notes

This repository supports two levels of reproducibility.

## Level 1: table and claim inspection

The primary public evidence consists of the exported CSV files in
`data/trim_diagnostics/`. These files are sufficient to inspect the numerical
values used in the manuscript tables and the diagnostic reasoning behind the
main claims:

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
plug-in binaries in `plugin/AutoCAD_2025_Debug_x64/` are provided for reviewers
who want to rerun or inspect the CAD-native workflow.

This level requires a compatible AutoCAD/ObjectARX environment. The supplied
plug-in is not a standalone solver and cannot be loaded without AutoCAD. See
`docs/environment.md`.

## Relation to the manuscript

The four benchmark folders correspond to the staged numerical evidence in the
paper:

1. `trapezoid_pressure`: simple retained-domain surface-load verification.
2. `triangle_line`: sharp retained-domain line-load verification.
3. `Complex perforated plate`: main controlled ablation for the severity-aware
   quadrature policy.
4. `Framework structure`: engineering-scale example for automatic
   analysis-resolution generation, automatic coupling consistency, and fallback
   diagnostics.

The repository intentionally excludes old standalone demonstration code that
does not generate the paper's reported CAD-native diagnostics.
