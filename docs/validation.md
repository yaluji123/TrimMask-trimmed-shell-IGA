# Independent checks and saved scientific data

Use Python 3.10–3.12 with NumPy and SciPy for the checking entry points. NumPy 1.26.4 and SciPy 1.13.1 are the recorded analysis versions. Install dependencies in an isolated environment before extraction and checking.

```powershell
python prepare_data.py --unpack --validation
python validation/check_reported_fields.py
python validation/curve_inverse_regression/check_curve_inverse.py
python validation/spectral_calibration/check_saved_calibration.py
python validation/manufactured_field_inputs/check_saved_mms.py
python validation/weak_residual_checks/check_saved_weak_residual.py
python validation/green_verification_inputs/check_saved_green.py
python validation/quadrature_verification_inputs/check_saved_inputs.py
```

The field checker uses NumPy and reads the complete published arrays. It recomputes sampled displacement peaks, engineering displacement-vector and two-face tensor differences, membrane/bending stress components, the original opening-corner regions and the response-figure vector-difference maxima. It checks the original triangle area weights and retains every fixed sample. It does not solve a structural state or evaluate a new mesh.

The curve check uses the frozen 303 parameters and captured curve for the scalar Newton regression. The spectral check compares the saved 292 pencil results and 146 calibration groups with the recorded native parameters. Its default command checks the saved numerical results without repeating an eigensolve. Failed earlier spectral comparisons and the numerical controls accompany the successful saved results.

Topic archives include the complete reference geometries, physical fields, calibration captures, fixed samples, matrix/work data and numerical controls described in the paper. Examples retain the source/runtime families of their recorded executions.

The mathematical kernels include the affine stress recovery, bicubic Green calculation, exact cell polynomials, continuous manufactured fields, physical interface work and flat Kirchhoff–Love operators. The flat-shell basis and operator functions are standalone in `single_patch_readers_v7/math/flat_kl_operators.py` within the extracted scientific tree.

Other source files document the recorded analysis methods. In `single_patch_readers_v7/math/`, the `public_geometry.py`, `public_oracle.py` and `triangle_sparse.py` run adapters use the original execution context and captured matrices. The engineering readback adapters similarly require their case context. ODB extraction sources require the Abaqus Python environment. These are method references. The commands above are the supported entry points for checking the distributed saved results.

Additional scientific input tables remain in plotting/inputs/: D079.csv contains the four retained-area diagnostics, D080.csv the four-level weak/strong measures, D081.csv all nine quadrature configurations, D082.csv all nine timing observations and D083.csv the timing statistics. They retain their original numeric data independently of which illustrations appear in the manuscript or responses.

The manufactured-field checks use the saved actual Native matrices and manufactured-load solutions. The finite weak-residual check uses the original saved Riesz witnesses, and the Green check verifies the saved state and directed work ledgers. The quadrature checker reads the complete original control coefficients, rule literals, saved moment values and native quadrature records. None of these default checks launches CAD, factorizes a structural system, reruns a spectral solve or changes an original field. Intermediate OPEN input packets retain their recorded status; the final four-level weak norms and saved witnesses are identified in weak_residual_checks.

`data/tables/Triangle_operator_domain_identity.json` gives the recorded common-domain checks for bulk, loading and weak boundary evaluation. `Plate_feature_setting_example.json` gives one recorded feature-to-setting example. Initial-grid provenance is distinct from subsequent exact knot-insertion refinement.

`P2_reference_refinement.csv` gives all five saved triangular reference levels and their adjacent increments. `STRI65_reference_energy_refinement.csv` gives the two saved engineering reference energies. These are finite-reference changes. `validation/triangle_operator_records.zip` contains the actual registered-boundary and load-chain records for the common-domain check.
