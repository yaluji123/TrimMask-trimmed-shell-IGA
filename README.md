# TrimMask revision data

Data, figures, current plotting programs and the AutoCAD2025 CoreConsole runtime for the revised trimmed-shell IGA study.

Version **2.0.0-oe-r1-rc4**. [Version downloads and DOI](https://github.com/yaluji123/TrimMask-trimmed-shell-IGA/releases/tag/v2.0.0-oe-r1-rc4). [All-version DOI](https://doi.org/10.5281/zenodo.20775314).

| Purpose | Files |
| --- | --- |
| Current separate figure panels | `current_figures/`, `FIGURE_TABLE_INDEX.json` |
| Numerical tables and source/runtime roles | `data/tables/`, `DATA_SCHEMA.md` |
| Full physical fields and actual meshes | `data/plot_inputs_*.zip`, `PLOT_INPUT_CATALOG.json` |
| Native input models and quadrature diagnostics | `data/cad/`, `data/cad_models.zip`, `data/trim_diagnostics/` |
| Current plotting programs and editable Figure1 | `plotting/`, `docs/plotting.md` |
| Scientific controls and independent reference inputs | `validation/`, `docs/validation.md` |
| Runtime and exact case profiles | `plugin/`, `docs/runtime.md` |

Download Source code (zip) from the release page, or the Zenodo version archive, for the complete package. The standalone runtime attachment is convenient when only the plugin is needed. The repository archive includes the data and runtime. The complete productionC++ solver is not distributed.

```powershell
python prepare_data.py
python prepare_data.py --unpack
python prepare_data.py --unpack --runtime
python prepare_data.py --validation
```

The first command displays the available extraction options. The options extract plotting inputs/models, the runtime, or scientific validation data into their documented relative locations. Existing changed files are not overwritten. Python3.10 or newer is required. The largest complete fieldCSV uses ZIP BZIP2 compression, supported by this unpacker. Individual ZIPs contain complete named files, not byte fragments.

Each experiment retains its actual source/runtime family. Current main-figure results, earlier valid refinement records and historical reference controls are identified by their table roles. All fixed physical samples and both stress faces are retained. Strong-flux, local-bending and stress-peak limitations remain in the results. No new simulation was performed for this distribution revision.

Project materials remain All rights reserved under `LICENSE`. Component notices accompany the runtime. AutoCAD, Abaqus, SDKs and fonts are not included.
