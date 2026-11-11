# Qualified runtime and native inputs

This is the recorded AutoCAD2025 x64 **CoreConsole paper workflow**. It requires a compatible licensed CAD host. It is not a standalone executable or a claim that ordinary empty-flag GUI defaults use the same physics.

```powershell
python prepare_data.py --unpack --runtime
```

This extracts the exact original runtime into `plugin/runtime_package/` and the five byte-exact models into `native_raw/<case>/input_model.dwg`. The large solver-captureZIPs mentioned in the original runtimeREADME are not required: their necessary model files are supplied separately here. `data/CAD_MODELS.json` verifies every model against `PAPER_REPRODUCTION_CASES.json`.

Set `RUNTIME_ROOT` to the extracted runtime package and `DATA_ROOT` to the repository root. Select exactly one entry from `PAPER_REPRODUCTION_CASES.json`. Use a fresh `RUN_WORK` and `RUN_OUT`, the byte-exact input model, complete per-case environment map, actual profile and physics flags. All carried point/input qualification files are present and hash-checked against the recipes.

Retain the actual line-work, checked spectral/mapping and case-specific point-component flags. KeepSECURELOAD=1 and trust only the exact runtime directory. Follow the included profile preimport/module/input gates. Do not substitute another model's endpoint plan or silently replace an unknown stored profile.

The runtime retains its qualified mixed component identity and separate third-party notices. Current default, uniform8x, local16x and integration-order studies have their own source/input identities. Manual4 is the recorded observed-enrichment study and carries its stated quadrature limitation. No new host or other-machine execution is certified by repackaging.
