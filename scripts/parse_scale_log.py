from __future__ import annotations

import json
import re
import sys
from pathlib import Path


PATTERNS = {
    "patches": re.compile(r"patches: shell=(\d+), beam=(\d+), total=(\d+)"),
    "control_points": re.compile(
        r"control points: shell=(\d+), beam=(\d+), uniqueNodes=(\d+), totalDOF=(\d+)"
    ),
    "trim_loops": re.compile(
        r"trim loops: trimRegisteredShells=(\d+), nontrivialTrimShells=(\d+), "
        r"fullDomainOnlyShells=(\d+), holeShells=(\d+), outerLoops=(\d+), "
        r"holeLoops=(\d+), boundaryChains=(\d+)"
    ),
    "coupling": re.compile(r"coupling interfaces=(\d+), couplingAssembly=(\d+) ms"),
    "elements": re.compile(r"elements: total=(\d+), inside=(\d+), cut=(\d+), outside=(\d+)"),
    "quadrature": re.compile(
        r"quadrature: stdElem=(\d+), stdGP=(\d+), subCells=(\d+), "
        r"subTestGP=(\d+), subAcceptedGP=(\d+), triOuter=(\d+), "
        r"triHole=(\d+), triGP=(\d+), fallback=(\d+)"
    ),
    "timings": re.compile(
        r"timings: classify=([0-9.]+) ms, clipTri=([0-9.]+) ms, "
        r"trimTotal=([0-9.]+) ms, preSolve=(\d+) ms"
    ),
    "assembly_solver": re.compile(r"assemblySolver: assembly=(\d+) ms, solver=(\d+) ms"),
}

FIELDS = {
    "patches": ["shell", "beam", "total"],
    "control_points": ["shell", "beam", "unique_nodes", "total_dof"],
    "trim_loops": [
        "trim_registered_shells",
        "nontrivial_trim_shells",
        "full_domain_only_shells",
        "hole_shells",
        "outer_loops",
        "hole_loops",
        "boundary_chains",
    ],
    "coupling": ["interfaces", "assembly_ms"],
    "elements": ["total", "inside", "cut", "outside"],
    "quadrature": [
        "std_elem",
        "std_gp",
        "sub_cells",
        "sub_test_gp",
        "sub_accepted_gp",
        "tri_outer",
        "tri_hole",
        "tri_gp",
        "fallback",
    ],
    "timings": ["classify_ms", "clip_tri_ms", "trim_total_ms", "pre_solve_ms"],
    "assembly_solver": ["assembly_ms", "solver_ms"],
}


def coerce(value: str) -> int | float:
    return float(value) if "." in value else int(value)


def parse_log(path: Path) -> dict[str, object]:
    text = path.read_text(encoding="utf-8")
    result: dict[str, object] = {"source": path.name}
    for key, pattern in PATTERNS.items():
        match = pattern.search(text)
        if not match:
            continue
        result[key] = {
            field: coerce(value)
            for field, value in zip(FIELDS[key], match.groups())
        }
    return result


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit("usage: parse_scale_log.py <log> [<log> ...]")
    parsed = [parse_log(Path(arg)) for arg in sys.argv[1:]]
    print(json.dumps(parsed, indent=2))


if __name__ == "__main__":
    main()

