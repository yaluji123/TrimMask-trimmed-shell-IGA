# AutoCAD2025 CoreConsole cases

Use a compatible licensed AutoCAD2025 x64 CoreConsole host.

```powershell
python prepare_data.py --unpack --runtime
```

The runtime is extracted into `plugin/runtime_package/` and the five exact engineering models into `native_raw/<case>/input_model.dwg`. Set `RUNTIME_ROOT` to the extracted runtime package and `DATA_ROOT` to the repository root. Select exactly one entry from `PAPER_REPRODUCTION_CASES.json`, use fresh `RUN_WORK`/`RUN_OUT` directories and the exact case command, DWG, complete profile and physical environment flags. Model hashes are listed in `data/CAD_MODELS.json`.

Keep the eight runtime modules together. Retain the actual line-work, spectral/mapping and model-specific point-component settings and all carried inputs. Their qualification files and full profiles are bound by the case recipes and supplied unchanged. The source-default preimport scripts preserve the original profile check. KeepSECURELOAD=1 and trust the exact runtime directory.

`RUNTIME_MANIFEST.json` identifies the actual mixed module family and supported case scope. Earlier experimental results are not relabeled as new executions. The demonstrated scope is the recorded CoreConsole workflow; the standalone archive is not an independent executable. Component licence notices remain with their modules.
