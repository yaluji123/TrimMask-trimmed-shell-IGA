# Scientific data and reference inputs

Use `python prepare_data.py --validation` to extract the topic archives. ZIP archives contain the named scientific files directly. Extraction does not execute a mechanics test.

| Data | Purpose |
| --- | --- |
| `geometry_mms_01.zip` | Retained-domain moments, polynomial/energy checks, independent references, manufactured fields and calibration |
| `interfaces_01.zip` | Matched support/reference comparisons, raw strong flux, physical work/Green ledgers and negative controls |
| `engineering_01.zip` | Saved refinement fields and engineering vector/tensor comparisons |
| `mapping_01.zip` | Actual mappings, accepted/final counts, model diagnostics and physical input records |
| `quadrature_*.zip` | Span moments, integration-order response, actual coefficients and original accuracy/work/timing data |
| `matched_reference_data.zip` | Actual0.25/0.125 reference stress captures, control nodes, IP/frame calibration, physical recovery kernel and Native16 data |
| `reference_*.zip` | Exact matched-reference, STRI65h1 and recovery-calibration input decks |

The existing engineeringSTRI65h2 decks are in the plotting data asD045.inp andD073.inp. The reference input archives add theirh1 counterparts and the matched three-patch0.25/0.125 decks without duplicating theh2 files. The standalone failedh3 identity record and nine-strategy gate results retain their original scientific status.

Current interface source tables include all16 graph/level cases and48 endpoint-vector records. `HISTORICAL_REFERENCE_` files are separately labeled old-reference controls. Raw strong-flux FAIL and open integration controls remain visible. Local bending and peak-stress limitations are not reclassified as passes. Numerical method references may require local path configuration; extraction does not execute any solver.
