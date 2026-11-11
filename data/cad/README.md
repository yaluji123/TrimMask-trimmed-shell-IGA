# Native and exchange input models

TheDWG files are the actual revision-qualified input models. The triangle and hull baselineDWGs replace the corresponding previous snapshots. The unchanged exchangeIGES inputs retain their original byte identities. Geometry-only input reuse does not relabel historical numerical observations as new runs.

The five current engineering runtime recipes use the exact models in `data/cad_models.zip`, unpacked to `native_raw/<case>/input_model.dwg`. Their complete identity/recipe checks are independent of the convenient baseline1x input models here. `profiles/` preserves the exact profiles of the named baseline experiments, with their real runtime lineage.
