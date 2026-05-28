# C++ reference headers

`TrimmedUV.h` is a reference header copied from the complete AutoCAD/ObjectARX
C++ implementation used in the manuscript.  It defines the TrimMask data layer
used by the project code to store retained UV outer loops, hole loops, trimmed
boundary chains, domain-normalization utilities, and point-in-trim queries for
each shell patch.

This file is included for traceability only.  It is not part of the standalone
Python runner and is not intended to compile by itself, because the full project
binds TrimMask records to DWG/B-Rep shell patches through Autodesk ObjectARX
types such as `Adesk::ULongPtr` and a current-document registry implemented in
the main plug-in.

`TrimStatsExcerpt.h` is a cleaned, AutoCAD-independent excerpt of the quadrature
settings and statistics counters used by the complete project.  It documents the
fields behind the `[TRIM]` and `[IGA][Scale]` logs that support the manuscript
tables, including element classes, standard Gauss points, sub-cell quadrature
counts, triangle quadrature counts, fallback counts, and trim-related timings.

For a portable executable example, use `../trim_quad.py`, which reimplements the
CAD-independent TrimMask, element-classification, masking-quadrature, and
triangle-quadrature logic using JSON trim-loop data.
