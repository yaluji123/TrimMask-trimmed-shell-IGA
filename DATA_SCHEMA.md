# Data fields and provenance

Coordinates and displacement: mm. Angles: rad. Stress: MPa. Force: N, with line traction in N/mm where specified by the input. Energy: N mm. Relative quantities follow the explicit normalization in their source table/method.

`PLOT_INPUT_CATALOG.json` links the83 byte-exact input files to their original filenames, hashes and operational package-relative paths. `plotting/PLOT_INPUTS.json` maps them to specific panels. The full paired triangleNPZ retains525,825 fixed nodes, displacement vectors and reference connectivity. Native panel/hullCSV files retain all30,818/132,372 fixed samples, displacement components, SNEG/SPOS stress components and face vonMises values. Corresponding finite-reference files retain their full physical tensor/vector data and area/membership information. Actual geometryJSON and finite element input decks retain the distinct discretizations.

Cloud plots use the Euclidean displacement magnitude or the maximum vonMises value across the two physical faces. Maxima/minima are over the stated saved sample set. A sample maximum is not a certified continuum peak. The six-decimal legend formatting changes presentation only.

InterfaceCSV files preserve common-axis signs, owner/graph identifiers, all48 endpoint vectors and unselected pair jumps. Matched and historical reference controls are separately named. Engineering tables retain the actual refinement/source lineage and full error observations. Timing tables contain the original repetitions, rather than reconstructed averages.

Each topicZIP contains its own member catalog. `DATA_INDEX.json` records distributed payload identities and selection purpose. `SHA256SUMS.txt` covers the final release tree. Archive extraction preserves the original numeric bytes. Historical method-source path descriptors identify provenance and may require local configuration.
