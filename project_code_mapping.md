# Mapping from the minimal package to the project code

The complete manuscript implementation is an AutoCAD/ObjectARX C++ application:
it reads and regularizes native DWG/B-Rep geometry, constructs TrimMask records,
assembles trimmed-shell IGA stiffness/load/coupling operators, solves the linear
system, and performs stress/post-processing inside the CAD workflow.  The Python
files in this release are not a replacement for that application.  They are a
minimal extraction of the CAD-independent TrimMask and quadrature logic so that
readers can rerun the geometric classification and backend comparison without
AutoCAD, ObjectARX, MKL, or the project-specific UI.

| Minimal package component | Project location | Purpose |
|---|---|---|
| TrimMask data layer | `IGAforCAD/IGAforCAD/TrimmedUV.h` | Stores outer loops, hole loops, curve trims, domain normalization, and point-in-domain tests.  A reference copy is included as `src/cpp_reference/TrimmedUV.h`.  In the runnable Python package, the same role is represented by `src/trim_quad.py::TrimMask` and the JSON `trim_mask` block. |
| Current-document registry | `IGAforCAD/IGAforCAD/DocData.h`, `IGAEntity/DocDataBridge.cpp` | Binds TrimMask records to the active DWG document.  This part is CAD-dependent and can be omitted in the standalone package. |
| Quadrature settings | `IGAforCAD/IGAforCAD/SolveConfig.h` | Defines `TrimQuadratureMode`, `QuadGaussN`, `SubCellDiv`, and `TriGaussN`. |
| Element classification | `IGAforCAD/IGAforCAD/Curves.cpp`, inside `BShellPatch::ComputeStiffness_safe` | Classifies background knot-span elements as inside, outside, or cut. |
| Masking backend | `IGAforCAD/IGAforCAD/Curves.cpp`, sub-cell masking branches | Subdivides cut elements and filters Gauss points with the TrimMask indicator. |
| Triangle backend | `IGAforCAD/IGAforCAD/Curves.cpp`, clipping/Clipper2/triangulation branches | Reconstructs visible cut-cell regions and integrates over triangles. |
| Scale statistics | `IGAforCAD/IGAforCAD/DocData.h`, `IGAforCAD/IGAforCAD/Curves.cpp`, `IGAforCAD/IGAforCAD/igaPaletteChildDlg.cpp` | Produces `[TRIM][...]` and `[IGA][Scale]` logs used in Table 8. |

## Recommended extraction boundary

For a public GitHub repository, extract only the UV-domain data structures and
quadrature routines.  Replace AutoCAD handles with integer patch IDs and replace
shell stiffness assembly with a generic scalar integrand, for example:

```cpp
double f(double u, double v) { return 1.0; }
```

This lets readers reproduce element classification, integration-point counts,
visible-region triangulation counts, and timing trends without requiring AutoCAD.

The included `src/cpp_reference/TrimmedUV.h` is therefore a traceability artifact,
not a standalone build target.  It shows the C++ data-layer interface used by the
complete AutoCAD/ObjectARX plug-in, while the Python implementation remains the
portable executable example for the public repository.
