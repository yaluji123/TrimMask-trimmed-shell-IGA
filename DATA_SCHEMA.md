# Data schema for minimal TrimMask/quadrature cases

Each JSON file describes one trimmed patch in the parametric domain.  Coordinates
may be given either in the true knot-span parameter domain or in the normalized
unit square.  The field `domain` tells the runner how to interpret them.

The `trim_mask` object is the JSON form of the TrimMask data layer used in the
manuscript.  In the full AutoCAD/ObjectARX C++ program, this data layer is built
from native DWG/B-Rep entities during pre-processing and then reused by shell
assembly, loads, weak boundary conditions, coupling, and post-processing.  In
this minimal Python package it is supplied directly as UV loops so that the
CAD-independent quadrature behavior can be reproduced without AutoCAD.

```json
{
  "case_id": "trapezoid_surface_load",
  "description": "One trimmed shell patch used for backend comparison.",
  "domain": {
    "umin": 0.0,
    "umax": 1.0,
    "vmin": 0.0,
    "vmax": 1.0
  },
  "knot_spans": {
    "u": [0.0, 0.1, 0.2, 0.3, 1.0],
    "v": [0.0, 0.1, 0.2, 0.3, 1.0]
  },
  "trim_mask": {
    "outer_loop": [[0.1, 0.1], [0.9, 0.1], [0.8, 0.8], [0.2, 0.9]],
    "hole_loops": [
      [[0.45, 0.45], [0.55, 0.45], [0.55, 0.55], [0.45, 0.55]]
    ],
    "boundary_chains": [
      {
        "tag": 1,
        "points": [[0.1, 0.1], [0.9, 0.1]]
      }
    ]
  },
  "quadrature_settings": {
    "quad_gauss_n": 3,
    "sub_cell_div": 4,
    "tri_gauss_n": 7,
    "backend": "triangle"
  },
  "expected_outputs": {
    "element_total": null,
    "inside": null,
    "cut": null,
    "outside": null,
    "std_gp": null,
    "sub_accepted_gp": null,
    "tri_gp": null,
    "fallback": null
  }
}
```

## Required fields

- `case_id`: stable identifier used in logs and scripts.
- `domain`: parameter rectangle for the patch.
- `knot_spans.u`, `knot_spans.v`: background knot-span grid.
- `trim_mask.outer_loop`: retained outer loop of the active trimmed patch.  Omit
  or set to `null` only for holes-only full-domain cases.
- `trim_mask.hole_loops`: inner loops removed from the retained domain.
- `trim_mask.boundary_chains`: optional trimmed-boundary segments used in the
  full program for line loads, weak boundary conditions, coupling, and
  post-processing.
- `quadrature_settings`: backend and integration parameters.
- `expected_outputs`: values filled after running the standalone code.

## Notes

For Table 8-scale evidence, the full box-girder geometry does not need to be
published if CAD/IP restrictions apply.  A scale log plus a small representative
trim-loop dataset is usually sufficient for a minimal public package; the complete
DWG/plug-in workflow can remain "available from the corresponding author upon
reasonable request".
