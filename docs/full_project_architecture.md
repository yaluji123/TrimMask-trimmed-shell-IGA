# Full project architecture

The public repository contains a minimal reproducibility package, not the full
AutoCAD/ObjectARX plug-in.  The complete research implementation used for the
manuscript is a C++ CAD/CAE application with the following high-level structure.
This architecture map is included to document how the released TrimMask and
quadrature code relates to the full project without publishing Autodesk SDK
files, build artifacts, DWG models, or project-specific binaries.

```text
IGAforCAD/
  IGAforCAD.sln
  IGAforCAD/                         # Main AutoCAD/ObjectARX application module
    TrimmedUV.h                      # TrimMask registry and UV-domain queries
    SolveConfig.h/.cpp               # Solver, quadrature, coupling and post settings
    DocData.h/.cpp                   # Per-document state, TrimMask registry, timing/statistics
    Curves.h/.cpp                    # NURBS/B-spline geometry, shell patches, trimmed-cell assembly
    Solver.h/.cpp                    # Linear algebra and solver wrappers
    CigaShell_nitscheType.h/.cpp     # Shell/Nitsche operator variants
    dbReactor.h/.cpp                 # CAD database reactors and coupling preparation
    Function.h/.cpp                  # Common numerical helper routines
    igaPalette*.h/.cpp               # AutoCAD palette UI and analysis commands
    igaShellOPM.* / igaBeamOPM.*     # Object property managers
    acrxEntryPoint.cpp               # ObjectARX application entry point
    resource.h                       # UI/resource identifiers
    *.vcxproj, *.filters             # Visual Studio project files

  IGAEntity/                         # Custom CAD entity and COM bridge module
    BackMesh.h/.cpp                  # Background mesh, visualization, stress recovery
    DocDataBridge.cpp                # Bridge to the active document TrimMask registry
    Couple.h/.cpp                    # Non-matching shell/beam coupling entity
    lineforceShell.h/.cpp            # Trimmed shell line-load entity
    surfaceforceShell.h/.cpp         # Shell surface-load entity
    surfaceBoundaryShell.h/.cpp      # Shell boundary-condition entity
    liftPointLoad.h/.cpp             # Lifting-point load entity
    bBoundaryEnt.* / sBoundaryEnt.*  # Beam/shell boundary entities
    *COM.h/.cpp                      # COM wrapper interfaces for CAD entities
    acrxEntryPoint.cpp               # ObjectARX entity module entry point
    resource.h                       # UI/resource identifiers
    *.vcxproj, *.filters             # Visual Studio project files

  x64/, .vs/                         # Local build/cache directories, not released
```

## Manuscript-related execution path

```text
DWG/B-Rep shell faces and trim curves
  -> TrimMask construction in TrimmedUV.h and CAD extraction commands
  -> Domain normalization and patch-level retained UV loops
  -> Background knot-span element classification in Curves.cpp
  -> Cut-cell quadrature backend:
       1. masking-based sub-cell quadrature, or
       2. triangle-based visible-region quadrature
  -> Shell stiffness/load/Nitsche/coupling assembly
  -> Linear solver
  -> Stress recovery and CAD post-processing
  -> Scale and quadrature logs used in the manuscript tables
```

## Public release boundary

The following parts are appropriate for a public reproducibility package:

- `src/trim_quad.py`: portable Python implementation of the TrimMask, element
  classification, masking backend, and triangle backend.
- `src/cpp_reference/TrimmedUV.h`: reference C++ header showing the TrimMask data
  layer used by the complete ObjectARX project.
- `data/examples/*.json`: normalized UV trim-loop benchmark cases.
- `data/logs/*.log`: scale and backend-comparison logs used to populate the
  manuscript tables.
- `scripts/*.py`: runners and log parsers.

The following parts are intentionally not published in full:

- Autodesk ObjectARX SDK headers, libraries, generated `.tlh/.tli` files, and
  Visual Studio build artifacts.
- `.arx`, `.dbx`, `.dll`, `.pdb`, `.obj`, `.pch`, `.vs/`, `x64/`, `Debug/`, and
  `Release/` outputs.
- Full DWG engineering models and local CAD workflow files.
- Large project source files that are dominated by AutoCAD UI, entity
  serialization, COM wrappers, or project-specific engineering workflows rather
  than the CAD-independent TrimMask/quadrature logic.

## Source files that can be cited in correspondence

When explaining the implementation to readers or reviewers, the most relevant
full-project source locations are:

| Project file | Role in the full implementation |
|---|---|
| `IGAforCAD/TrimmedUV.h` | TrimMask data layer, retained loops, hole loops, boundary chains, normalization, and point-in-trim tests. |
| `IGAforCAD/SolveConfig.h` | Runtime settings for quadrature mode, Gauss rules, sub-cell density, line-load integration, and coupling integration. |
| `IGAforCAD/DocData.h` | Per-document TrimMask registry and quadrature/statistics counters used by the manuscript tables. |
| `IGAforCAD/Curves.cpp` | Background element classification, shell stiffness assembly, masking quadrature, triangle quadrature, and trim statistics. |
| `IGAEntity/BackMesh.cpp` | Post-processing, visible-region handling, Clipper2 triangulation path, and stress recovery support. |
| `IGAEntity/DocDataBridge.cpp` | Bridge from CAD entity module to the active-document TrimMask registry. |
| `IGAEntity/lineforceShell.cpp` | Trimmed-boundary line-load entity used in the manuscript line-load examples. |
| `IGAEntity/Couple.cpp` | CAD entity representation of non-matching coupling interfaces. |

