# TrimMask trimmed-shell IGA reproducibility package

This repository contains reproducibility materials for CAD-native trimmed-shell
isogeometric analysis with TrimMask diagnostics. It is organized as a data and
runtime package rather than as a standalone solver implementation.

The repository includes:

- exported TrimMask diagnostic CSV files;
- DWG and IGES geometry files for the benchmark models;
- a packaged AutoCAD/ObjectARX Release x64 plug-in build;
- documentation describing the runtime environment and data schema.

The complete implementation is an AutoCAD/ObjectARX C++ plug-in that depends on
Autodesk CAD APIs and third-party numerical libraries. The Python demonstration
code and obsolete example scripts previously stored here have been removed to
keep the repository focused on the reproducibility materials.

## Repository layout

```text
data/
  trim_diagnostics/
    trapezoid_pressure/
    triangle_line/
    Complex perforated plate/
    Framework structure/
  cad/
    dwg/
    iges/
plugin/
  AutoCAD_2025_Release_x64/
docs/
  reproducibility.md
  environment.md
DATA_SCHEMA.md
CITATION.cff
LICENSE
```

## Folder contents

`data/trim_diagnostics/` contains the exported CSV diagnostics. Each benchmark
is divided into strategy subfolders, typically `fixed_subcell`,
`fixed_triangle`, and `severity_aware`.

`data/cad/dwg/` contains the native DWG input models. `data/cad/iges/` contains
IGES exports of the same benchmark geometries for independent geometry
inspection and cross-software viewing.

`plugin/AutoCAD_2025_Release_x64/` contains the AutoCAD/ObjectARX plug-in
binaries and dependent runtime libraries. The `.pdb` symbol files are not
included because they are not required for execution and exceed ordinary
repository file-size limits.

## Runtime requirements

`IGAforCAD.arx` and `JYH_IGAEntity.dbx` are AutoCAD/ObjectARX runtime
extensions. They are not standalone Windows executables and must be loaded
inside a compatible 64-bit AutoCAD installation.

At minimum, a reproduction machine needs:

1. Windows x64;
2. AutoCAD 2025 x64, or a binary-compatible AutoCAD release if the plug-in is
   rebuilt for that release;
3. the supplied files in `plugin/AutoCAD_2025_Release_x64/` kept together in
   one directory or otherwise visible on the system `PATH`;
4. the Microsoft Visual C++ runtime components required by the Release build;
5. AutoCAD security settings that allow loading ARX/DBX files from the plug-in
   directory, for example a trusted path or appropriate `SECURELOAD` setting.

See `docs/environment.md` for the runtime notes and `docs/reproducibility.md`
for the intended inspection workflow.

## Reproducibility scope

The CSV diagnostics are the primary public data. They allow inspection of:

- cut-cell classification and retained-area metrics;
- strategy-level quadrature counts and runtimes;
- operator-domain consistency checks for loads and coupling;
- feature-aware analysis-resolution recommendations;
- severity-aware rule assignment and fallback events.

The packaged plug-in and CAD files support rerunning the workflow in a
compatible AutoCAD environment. Because the implementation depends on commercial
CAD APIs and local AutoCAD runtime state, this repository is not intended as an
environment-independent open-source solver.

## Citation

If you use this package, cite this repository. Citation metadata are provided in
`CITATION.cff`.
