# AutoCAD2025 CoreConsole cases

Use a compatible licensed AutoCAD2025 x64 CoreConsole host.

```powershell
python prepare_data.py --unpack --runtime
```

The runtime is extracted into `plugin/runtime_package/` and the five exact engineering models into `native_raw/<case>/input_model.dwg`. Set `RUNTIME_ROOT` to the extracted runtime package and `DATA_ROOT` to the repository root. Select exactly one entry from `PAPER_REPRODUCTION_CASES.json`, use fresh `RUN_WORK`/`RUN_OUT` directories and the exact case command, DWG, complete profile and physical environment flags. Use the model path specified by the selected case recipe.

Keep the eight runtime modules together. Retain the actual line-work, spectral/mapping and model-specific point-component settings and all carried inputs. The case recipes bind the required inputs and complete profiles. The source-default preimport scripts preserve the original profile check. KeepSECURELOAD=1 and trust the exact runtime directory.

The case recipes identify the actual runtime scope and complete physical inputs. Earlier experimental results are not relabeled as new executions. The demonstrated scope is the recorded CoreConsole workflow; the standalone archive is not an independent executable. Component licence notices remain with their modules.

The recorded study uses AutoCAD2025 x64 CoreConsole and Abaqus/Standard2024 for independent references. The release build uses the MSVC14.51.36231 toolset and WindowsSDK10.0.26100.0. Plotting package versions are listed in plotting/requirements-plotting.txt. Numerical results retain their recorded experiment family; a distribution rebuild does not relabel the original runs.

The rc4 release module passed an isolated AutoCAD2025 CoreConsole loading check with SECURELOAD=1. Numerical results retain the recorded experiment families described in the data tables.
