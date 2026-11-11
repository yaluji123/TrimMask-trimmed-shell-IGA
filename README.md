# TrimMask revision data

Current figures, numerical data, scientific validation evidence and the qualified AutoCAD2025 CoreConsole runtime for the revised trimmed-shell IGA study.

Version: **2.0.0-oe-r1-rc1**. Authors: Yuheng Ji, Chuntong Li, Zhijie Dai, Chun Fang, Pengyu Wei and Deyu Wang. [All-version DOI](https://doi.org/10.5281/zenodo.20775314).

## Start here

| Need | Files |
| --- | --- |
| Read or reuse the final figure panels | `current_figures/`, `FIGURE_TABLE_INDEX.json` |
| Inspect reported numerical observations | `data/tables/` |
| Inspect displacement, full face-stress components and genuine IGA/FEM geometry | `data/plot_inputs_*.zip`, `PLOT_INPUT_CATALOG.json` |
| Recreate a figure from the saved scientific data | `plotting/`, `docs/plotting.md` |
| Examine reviewer-relevant scientific checks | `validation/`, `docs/validation.md` |
| Run a recorded engineering case in the compatible licensed CAD host | `plugin/`, `data/cad_models.zip`, `docs/runtime.md` |

Download this version using **Code > Download ZIP**, or the release's source ZIP. The GitHub source tree includes the actual data and runtime, so the automatic Zenodo archive includes them too. Individual archives below100MiB keep the repository practical. They contain complete named files, not binary volume fragments.

With Python3.10 or newer, run:

```powershell
python prepare_data.py
python prepare_data.py --unpack
```

The first command verifies file identities. The second also extracts the83 plotting inputs, geometry caches and five native CAD models into their required relative locations. Neither performs a simulation. A changed local input is never overwritten. See `DATA_SCHEMA.md` for units and sample definitions.

Use the supplied Python unpacker for all data archives. The largest complete field file uses standardZIP BZIP2 compression, which some operating-system file browsers do not support. No numeric file is truncated or divided into byte volumes.

## Scientific scope

The files retain the actual source/runtime lineage of each experiment. Earlier benchmark results are not relabeled as new-runtime results. The matched-reference interface data include all16 graph/level cases and48 endpoints, including unselected comparisons. Strong force/moment residuals remain reported as approximately0.750/0.103. The local bending discrepancy and unconverged stress peaks remain visible in the engineering evidence. Finite-work/Green checks and finite-reference agreement answer their stated questions; they are not a replacement for those strong-flux or peak-convergence observations.

The package contains frozen numerical observations, reusable plots and method references. No additional simulation or full moved-root mathematical replay was performed during publication. Historical validation method sources may retain their original workspace conventions. The supported plotting routes and runtime profiles are described separately.

## Included and omitted

Selection follows the revised results and the scientific questions raised during review. Each distributed payload has a purpose andSHA256 in `DATA_INDEX.json`. Complete physical plotting samples, stress components, necessary negative/failed controls, actual model inputs and runtime dependencies are retained.

Redundant nativeODB containers, full solver/observer capture archives, the layered historical core, development/build records, duplicateTIFFs and pre-trim canvas masters are omitted. Previous published versions remain accessible through their original tags andDOIs. Manuscripts, reviewer comments and response letters are not part of this public dataset.

Project materials remain **All rights reserved** under `LICENSE`. Runtime component notices are preserved. See `THIRD_PARTY_NOTICES.md`.
