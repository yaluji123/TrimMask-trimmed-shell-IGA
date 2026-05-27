# Suggested manuscript text

## If a public GitHub/Zenodo package is created

Code availability: A minimal standalone Python TrimMask/quadrature implementation,
normalized UV benchmark cases, backend-comparison settings, and scale logs are
available at: `https://github.com/yaluji123/TrimMask-iga-EWC`.  If a Zenodo
archive is created later, the repository release can also be linked to the
reserved DOI.  The public package reproduces the
CAD-independent trimmed-domain data layer, element classification, masking-based
sub-cell quadrature, and triangle-based visible-region quadrature used in the
paper.  The full research implementation is an AutoCAD/ObjectARX C++ program
covering DWG/B-Rep pre-processing, trimmed-shell IGA assembly/solving, coupling,
stress recovery, and CAD-based post-processing; because it depends on
CAD-kernel-specific components and project software infrastructure, it is
available from the corresponding author upon reasonable request.

Data availability: Representative normalized UV trim-loop datasets and the
backend-comparison logs supporting Tables 2-8 are included in the public
repository.  The full DWG models can be provided by the corresponding author
upon reasonable request subject to CAD model and software-license constraints.

## If only a request-based package is possible before submission

Code availability: The full research implementation is an AutoCAD/ObjectARX C++
program containing CAD-kernel-dependent DWG/B-Rep pre-processing, trimmed-shell
IGA assembly/solving, coupling, stress recovery, and CAD-based post-processing
components.  A minimal standalone Python TrimMask/quadrature package, including
normalized UV trim-loop data, backend-comparison settings, and run logs, is
available from the corresponding author upon reasonable request.

Data availability: Representative trimming-loop data and benchmark settings can
be provided to reproduce the reported CAD-native trimmed-shell cases.  Full DWG
models are available from the corresponding author upon reasonable request
subject to software-license and model-ownership constraints.
