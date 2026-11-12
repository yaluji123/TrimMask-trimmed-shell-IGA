# Data fields and provenance

Coordinates and displacement: mm. Angles: rad. Stress: MPa. Force: N, with line traction in N/mm where specified by the input. Energy: N mm. Relative quantities follow the explicit normalization in their source table/method.

`PLOT_INPUT_CATALOG.json` links the 81 input files to their original filenames and package-relative paths. `plotting/PLOT_INPUTS.json` maps them to specific panels. The full paired triangleNPZ retains525,825 fixed nodes, displacement vectors and reference connectivity. Native panel/hullCSV files retain all30,818/132,372 fixed samples, displacement components, SNEG/SPOS stress components and face vonMises values. Corresponding finite-reference files retain their full physical tensor/vector data and area/membership information. Actual geometryJSON and finite element input decks retain the distinct discretizations.

Cloud plots use the Euclidean displacement magnitude or the maximum vonMises value across the two physical faces. Maxima/minima are over the stated saved sample set. A sample maximum is not a certified continuum peak. The six-decimal legend formatting changes presentation only.

InterfaceCSV files preserve common-axis signs, owner/graph identifiers, all48 endpoint vectors and unselected pair jumps. Matched and historical reference controls are separately named. Engineering tables retain the actual refinement/source lineage and full error observations. Timing tables contain the original repetitions, rather than reconstructed averages.

The topic archives contain the scientific data directly. Archive extraction preserves the original numeric bytes. Historical method-source path descriptors identify provenance and may require local configuration.

Engineering displacement-vector and stress-tensor differences use original triangle areas as weights and the finite-reference norm as denominator. Tensor Frobenius norms count off-diagonal components twice. Membrane and bending stresses are the half-sum and half-difference of the two physical-face tensors, both in MPa. The opening mask retains the preselected original centroids within 20 mm of the selected opening corners.
