# GitHub/Zenodo release checklist

Release this folder as a minimal reproducibility package, not as the complete
project code.  The complete project is the AutoCAD/ObjectARX C++ pre-processing,
solver, coupling, stress-recovery, and post-processing program used for the
manuscript; this repository should expose only the CAD-independent Python
TrimMask/quadrature demonstration and supporting logs/data.

1. Create a new public repository named `TrimMask-iga-EWC`.
2. Add a clear license.  Use MIT/BSD-3-Clause for the standalone code if your
   advisor/lab permits it; otherwise use "all rights reserved" and keep only the
   data package public.
3. Add `README.md`, `DATA_SCHEMA.md`, and `project_code_mapping.md`.
4. Add only CAD-independent source code.  Do not add ObjectARX SDK files,
   AutoCAD headers, generated `.tlh/.tli`, `.pdb`, `.obj`, `.dll`, `.arx`,
   `.dbx`, `.pch`, or local `.vs` files.
5. Add small JSON cases for:
   - trapezoidal surface-load backend comparison;
   - triangular line-load backend comparison;
   - perforated plate with circular and triangular holes;
   - optional anonymized box-girder trim-loop sample or scale logs only.
6. Add logs generated with the exact settings used in the manuscript:
   `TrimQuadratureMode`, `QuadGaussN`, `SubCellDiv`, `TriGaussN`, CPU/compiler,
   and Clipper2 version.
7. Add `CITATION.cff` with the manuscript title and authors.
8. Create a GitHub release, upload the same package to Zenodo, and reserve a DOI.
9. Replace the placeholder URL/DOI in the manuscript Code availability section.
