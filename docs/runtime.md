# Running one recorded CoreConsole case

Use licensed AutoCAD 2025 x64 CoreConsole. These instructions describe the recorded workflow. The distribution module has a loading check; this distribution revision did not repeat the numerical cases.

First run `python prepare_data.py --unpack --runtime`. Choose exactly one case in `plugin/runtime_package/PAPER_REPRODUCTION_CASES.json`. Keep its exact model, complete profile, carried inputs and **all** environment flags together. The five recipes use these registered commands:

| Recipe | Command |
| --- | --- |
| `curve_latest_manual_default4x_ab_root_v2` | `IgaExportOEActualHullLinearStateV1Local` |
| `curve_latest_manual_uniform8x_root_v2` | `IgaExportOEAdmittedHullMeshStateV2Local` |
| `curve_latest_manual_local16x_root_v1` | `IgaExportOEAdmittedHullMeshStateV2Local` |
| `curve_latest_manual_gl4_root_v1` | `IgaExportOEActualHullLinearStateV1Local` |
| `new4af_panel4x_root_v1` | `IgaExportOEPanelMeshLinearStateV1Local` |

Use a fresh PowerShell session, fresh `RUN_WORK` and fresh empty `RUN_OUT`. The following preparation example expands every recipe flag; change only the four roots and the selected case name. It does not start the host.

```powershell
$DATA_ROOT = 'C:/TrimMask/data-package'
$RUNTIME_ROOT = "$DATA_ROOT/plugin/runtime_package"
$RUN_WORK = 'C:/TrimMask/run-one/work'
$RUN_OUT = 'C:/TrimMask/run-one/output'
$caseName = 'curve_latest_manual_default4x_ab_root_v2'
$recipes = Get-Content -Raw -LiteralPath "$RUNTIME_ROOT/PAPER_REPRODUCTION_CASES.json" | ConvertFrom-Json
$matches = @($recipes.cases | Where-Object case -eq $caseName)
if ($matches.Count -ne 1) { throw 'Select exactly one recipe' }
$case = $matches[0]
$roots = @{
    '${DATA_ROOT}' = $DATA_ROOT
    '${RUNTIME_ROOT}' = $RUNTIME_ROOT
    '${RUN_WORK}' = $RUN_WORK
    '${RUN_OUT}' = $RUN_OUT
}
$expand = {
    param([string]$value)
    foreach ($key in $roots.Keys) { $value = $value.Replace($key, $roots[$key]) }
    if ($value.Contains('${')) { throw 'Unexpanded recipe placeholder' }
    $value
}
if ((Test-Path -LiteralPath $RUN_WORK) -or (Test-Path -LiteralPath $RUN_OUT)) { throw 'Use fresh directories' }
New-Item -ItemType Directory -Path $RUN_WORK,$RUN_OUT | Out-Null
New-Item -ItemType Directory -Path "$RUN_OUT/module_identity","$RUN_WORK/profile_before_import" | Out-Null
$model = & $expand $case.input_model_member
if ((Get-FileHash -LiteralPath $model -Algorithm SHA256).Hash.ToLowerInvariant() -ne $case.exact_model_sha256) { throw 'Input model identity mismatch' }
Copy-Item -LiteralPath $model -Destination "$RUN_WORK/model.dwg"
Get-ChildItem Env:IGA_* | Remove-Item
foreach ($flag in $case.actual_environment_flags_with_public_relative_inputs.PSObject.Properties) {
    [Environment]::SetEnvironmentVariable($flag.Name, (& $expand ([string]$flag.Value)), 'Process')
}
if ((Get-FileHash -LiteralPath $env:IGA_ANALYSIS_PROFILE_JSON -Algorithm SHA256).Hash.ToLowerInvariant() -ne $case.full_profile_sha256) { throw 'Complete profile identity mismatch' }
foreach ($inputRef in $case.carried_input_file_refs) {
    $path = "$RUNTIME_ROOT/$($inputRef.member)"
    if ((Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant() -ne $inputRef.sha256) { throw 'Carried input identity mismatch' }
}
$baseline = "$RUNTIME_ROOT/profiles/source_default_baseline_mode3.json"
if ((Get-FileHash -LiteralPath $baseline -Algorithm SHA256).Hash.ToLowerInvariant() -ne '060882e17af8287183a73850cde94fcd1cbde16710068855e3939549c6100652') { throw 'Source-default baseline mismatch' }
$selectedProfileHash = (Get-Content -Raw -LiteralPath $env:IGA_ANALYSIS_PROFILE_JSON | ConvertFrom-Json).hash
$env:PATH = "$RUNTIME_ROOT/runtime;$env:PATH"
$env:OMP_NUM_THREADS = '1'; $env:MKL_NUM_THREADS = '1'; $env:OPENBLAS_NUM_THREADS = '1'
$env:OMP_DYNAMIC = 'FALSE'; $env:MKL_DYNAMIC = 'FALSE'
```

For `SECURELOAD=1`, keep the trusted scope to the exact runtime directory. Copy the two supplied profile helpers into that directory so they can be loaded from the same trusted location. This adds the two helper files and does not replace a runtime module:

```powershell
Copy-Item -LiteralPath "$RUNTIME_ROOT/profile_import/capture_original_profile.lsp" -Destination "$RUNTIME_ROOT/runtime/capture_original_profile.lsp"
Copy-Item -LiteralPath "$RUNTIME_ROOT/profile_import/engineering_profile_guard.lsp" -Destination "$RUNTIME_ROOT/runtime/engineering_profile_guard.lsp"
```

Write `RUN_WORK/run.scr` from the example below. Replace `<RUNTIME_ROOT>` and `<RUN_WORK>` with absolute forward-slash paths, `<SELECTED_PROFILE_HASH>` with `$selectedProfileHash`, and `<CASE_COMMAND>` with `$case.command`. The source-default hash is `6668325e2315a943`; the selected profile hash is `7311d61340e0fb12` for the default engineering profile or `0aade046dfb03030` for the manual GL4 profile.

The sequence is: load DBX, load CRX, capture actual loaded-module paths, check the original stored profile, explicitly import the complete selected profile, check the actual imported Xrecord hash, then execute the selected case command. The module capture sets `IGA_OE_MODULE_GATE_OK` from its actual checks; do not set that flag yourself.

```lisp
(setvar "SECURELOAD" 1)
(setvar "TRUSTEDPATHS" "<RUNTIME_ROOT>/runtime")
(vl-load-com)
(arxload "<RUNTIME_ROOT>/runtime/JYH_IGAEntity.dbx")
(arxload "<RUNTIME_ROOT>/runtime/IGAforCAD.crx")
IgaExportOELoadedModuleIdentity
(if (= (getenv "IGA_OE_MODULE_GATE_OK") "1")
  (progn
    (load "<RUNTIME_ROOT>/runtime/capture_original_profile.lsp")
    (load "<RUNTIME_ROOT>/runtime/engineering_profile_guard.lsp")
    (if (oe-engineering-preimport-allowed
          "<RUN_WORK>/profile_before_import"
          "<RUNTIME_ROOT>/profiles/source_default_baseline_mode3.json"
          "6668325e2315a943")
      (progn
        (command "IgaImportAnalysisProfileHeadless")
        (if (and
              (setq oe_selected_profile (dictsearch (namedobjdict) "IGA_NONLINEAR_ANALYSIS_PROFILE"))
              (= (cdr (nth 2 (vl-remove-if-not
                    (function (lambda (item) (member (car item) (quote (90 1)))))
                    oe_selected_profile))) "<SELECTED_PROFILE_HASH>"))
          (progn
            (oe-engineering-gate-status "<RUN_WORK>/profile_before_import" "IMPORT_HASH_MATCHED_NUMERIC_COMMAND_SELECTED" T T T)
            (command "<CASE_COMMAND>"))
          (oe-engineering-gate-status "<RUN_WORK>/profile_before_import" "IMPORT_HASH_REJECTED_NO_NUMERIC_COMMAND" T T nil)))))
  (princ "MODULE_GATE_REJECTED_NO_WORK"))
_.QUIT
_Y
```

After reviewing the selected inputs and script, start exactly that one case in the prepared PowerShell session:

```powershell
$core = 'C:/Program Files/Autodesk/AutoCAD 2025/accoreconsole.exe'
& $core /i "$RUN_WORK/model.dwg" /s "$RUN_WORK/run.scr" /l en-US
```

Stop on any load, module-path, original-profile or imported-profile mismatch. The original-profile helper admits only an absent stored profile or the exact complete source-default baseline; it does not replace an unknown stored profile silently. The imported hash is read from the actual DWG Xrecord. Keep the resulting module identity and profile gate outputs with the case outputs. The module path gate is not itself a SHA256 check of loaded binaries. The recorded numerical and source/runtime family boundaries still apply; a host exit code alone does not validate a numerical result.
