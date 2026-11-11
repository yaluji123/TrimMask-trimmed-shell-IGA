# Current finite element inputs

The previous coarseS4R decks are superseded by the actualSTRI65 h2 reference decks used for the current engineering comparisons:

| Model | Complete current input after `python prepare_data.py --unpack` |
| --- | --- |
| Perforated stiffened plate | `plotting/inputs/D045.inp` |
| Hull girder | `plotting/inputs/D073.inp` |

Both files are in the ordinary `data/plot_inputs_*.zip` archives, with their exact hashes in `PLOT_INPUT_CATALOG.json`. A second identical deck is not stored here. Loads, material, supports and reference discretization are defined by the actual decks and their paired field contracts, not inferred from filenames. Native engineering model inputs remain under `data/cad/` and `data/cad_models.zip`.
