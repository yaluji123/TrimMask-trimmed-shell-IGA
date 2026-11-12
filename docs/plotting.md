# Plotting saved physical data

Run `python prepare_data.py --unpack`, then install the versions in `plotting/requirements-plotting.txt` in an isolated environment. The recorded plotting environment is Windows with Times New Roman available; fonts are not redistributed.

`plotting/EXACT_PANEL_RENDER_ROUTES.json` selects the current script for each panel. Use a fresh output directory under `plotting/`. Example:

```powershell
python plotting/export_six_decimal_no_foot_v5.py --panel F8e --out plotting/my_F8e --execute-render
```

The scripts use complete saved fields and genuine IGA/FEM discretizations. Every scalar plot has its own sampled minimum/maximum with six decimal places and the same Abaqus-style palette. Figures are separate panels. Captions are in `FIGURE_TABLE_INDEX.json`.

Figure1 has an editable Visio source in `plotting/F1_source/F1.vsdx`. Current numerical plotting entries are the four programs selected in the route table, with `true_mesh_helpers_v2.py` and `resource_guard.py` as required helpers.
