# TrimMask trimmed-shell IGA companion data

This repository is the public companion material for the manuscript
**"TrimMask: a unified active-domain contract for severity-aware quadrature and
feature-aware resolution in CAD-native trimmed shell isogeometric analysis"**.

The repository has been reduced to the materials needed to inspect the numerical
evidence reported in the paper:

- tabulated TrimMask diagnostics exported from the IGAforCAD implementation;
- DWG and IGES geometry files for the paper examples;
- a packaged AutoCAD/ObjectARX plug-in build used to generate the diagnostics;
- documentation describing the runtime environment and reproducibility scope.

It is not a standalone reimplementation of the solver and it is not a Python
demo package. The complete research code is an AutoCAD/ObjectARX C++ plug-in
that depends on Autodesk CAD APIs and third-party numerical libraries.

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
  AutoCAD_2025_Debug_x64/
docs/
  reproducibility.md
  environment.md
DATA_SCHEMA.md
CITATION.cff
LICENSE
```

## What each folder contains

`data/trim_diagnostics/` contains the CSV files used to construct the diagnostic
tables and discussion in the manuscript. Each benchmark is divided into
quadrature-strategy subfolders, typically `fixed_subcell`, `fixed_triangle`, and
`severity_aware`.

`data/cad/dwg/` contains the native DWG input models. `data/cad/iges/` contains
IGES exports of the same benchmark geometries for geometry inspection and
cross-software viewing.

`plugin/AutoCAD_2025_Debug_x64/` contains the packaged AutoCAD plug-in binaries
and dependent runtime libraries. The `.pdb` debug-symbol files are intentionally
not included because they are not required for execution and exceed GitHub's
ordinary file-size limit.

## Can the plug-in run without installing an environment?

No. `IGAforCAD.arx` and `JYH_IGAEntity.dbx` are AutoCAD/ObjectARX runtime
extensions, not standalone Windows executables. They must be loaded inside a
compatible 64-bit AutoCAD installation. The supplied build was prepared against
the AutoCAD/ObjectARX 2025 environment.

At minimum, a reproduction machine needs:

1. Windows x64;
2. AutoCAD 2025 x64, or a binary-compatible AutoCAD release if rebuilt for that
   release;
3. the supplied files in `plugin/AutoCAD_2025_Debug_x64/` kept in one directory
   or available on the system `PATH`;
4. the Microsoft C++ runtime required by the build. Because this package is a
   Debug build, a machine without Visual Studio debug runtime components may not
   load it. For external reproduction, a Release x64 build is preferable;
5. AutoCAD security settings that allow loading the plug-in directory, for
   example by adding it to trusted paths or using the appropriate `SECURELOAD`
   setting.

See `docs/environment.md` for a more detailed environment note and
`docs/reproducibility.md` for the intended reproduction workflow.

## Reproducibility scope

The CSV diagnostics are the primary reproducibility data for the manuscript
tables and claims. They allow reviewers to inspect:

- cut-cell classification and retained-area metrics;
- strategy-level quadrature counts and runtimes;
- operator-domain consistency checks for loads and coupling;
- feature-aware analysis-resolution recommendations;
- severity-aware rule assignment and fallback events.

The packaged plug-in and CAD files are provided to support rerunning the same
workflow in a compatible AutoCAD environment. Because the implementation depends
on commercial CAD APIs and a local AutoCAD runtime, this repository should be
described in the manuscript as a data and executable companion package, not as a
fully environment-independent open-source solver.

## Citation

If you use this repository, please cite the associated manuscript and this
companion package. Citation metadata are provided in `CITATION.cff`.
