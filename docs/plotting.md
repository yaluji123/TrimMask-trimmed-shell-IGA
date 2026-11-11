# Plotting saved results

Run `python prepare_data.py --unpack` at the repository root. Install the packages in `plotting/requirements-plotting.txt` in an isolated environment. The recorded environment is Windows with Times New Roman available. Font files are not redistributed.

`plotting/EXACT_PANEL_RENDER_ROUTES.json` selects the proper script for each panel. The retained script versions correspond to different current panel routes; they are not alternative physical datasets. For example:

```powershell
python plotting/export_six_decimal_no_foot_v5.py --panel F8e --out plotting/my_F8e --execute-render
```

Use a fresh output directory under `plotting/`. The scripts verify input sizes/hashes and use the original resource guard. Figures are produced from all saved physical samples and actual IGA/FEM geometry, without a new solve. Each scalar panel has its own actual minimum/maximum and six-decimal labels. No extrema/location footer or model mesh inset is added. Independent inputs may produce visually close fields.

The distributedPDF/PNG panels are the final compact-canvas versions. Rendering generates the original native canvas. `CANVAS_TRIM_MANIFEST.json` records the white-only lower-margin reduction used for publication. The redundant intermediate masters and an obsolete master-dependent replay helper are omitted. The native render and final figure therefore need not have the same canvas height or binary hash.

Figure1 is an editable Visio source in `plotting/F1_source/`, with finalPDF/PNG in `current_figures/F1/`. Every multi-panel figure remains a set of separate panel files. Editable subcaption text is recorded in `FIGURE_TABLE_INDEX.json`.
