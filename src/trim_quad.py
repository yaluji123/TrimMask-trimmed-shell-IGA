"""Minimal TrimMask and cut-cell quadrature reference implementation.

The complete research code is an AutoCAD/ObjectARX C++ program for CAD-native
pre-processing, isogeometric shell analysis, and post-processing.  This Python
file intentionally keeps only the CAD-independent TrimMask/quadrature core.  A
TrimMask is the patch-level UV-domain object that stores the retained outer loop,
hole loops, and trimmed boundary chains, and then answers the geometric queries
needed by the two quadrature backends.
"""

from __future__ import annotations

import argparse
import json
import math
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


Point = tuple[float, float]
Rect = tuple[float, float, float, float]


GAUSS_1D: dict[int, list[tuple[float, float]]] = {
    1: [(0.0, 2.0)],
    2: [(-0.5773502691896257, 1.0), (0.5773502691896257, 1.0)],
    3: [
        (-0.7745966692414834, 0.5555555555555556),
        (0.0, 0.8888888888888888),
        (0.7745966692414834, 0.5555555555555556),
    ],
    4: [
        (-0.8611363115940526, 0.3478548451374538),
        (-0.3399810435848563, 0.6521451548625461),
        (0.3399810435848563, 0.6521451548625461),
        (0.8611363115940526, 0.3478548451374538),
    ],
    5: [
        (-0.9061798459386640, 0.2369268850561891),
        (-0.5384693101056831, 0.4786286704993665),
        (0.0, 0.5688888888888889),
        (0.5384693101056831, 0.4786286704993665),
        (0.9061798459386640, 0.2369268850561891),
    ],
    6: [
        (-0.9324695142031521, 0.1713244923791704),
        (-0.6612093864662645, 0.3607615730481386),
        (-0.2386191860831969, 0.4679139345726910),
        (0.2386191860831969, 0.4679139345726910),
        (0.6612093864662645, 0.3607615730481386),
        (0.9324695142031521, 0.1713244923791704),
    ],
}

TRI_GAUSS: dict[int, list[tuple[float, float, float, float]]] = {
    1: [(1.0 / 3.0, 1.0 / 3.0, 1.0 / 3.0, 1.0)],
    3: [
        (2.0 / 3.0, 1.0 / 6.0, 1.0 / 6.0, 1.0 / 3.0),
        (1.0 / 6.0, 2.0 / 3.0, 1.0 / 6.0, 1.0 / 3.0),
        (1.0 / 6.0, 1.0 / 6.0, 2.0 / 3.0, 1.0 / 3.0),
    ],
    7: [
        (1.0 / 3.0, 1.0 / 3.0, 1.0 / 3.0, 0.225000000000000),
        (0.059715871789770, 0.470142064105115, 0.470142064105115, 0.132394152788506),
        (0.470142064105115, 0.059715871789770, 0.470142064105115, 0.132394152788506),
        (0.470142064105115, 0.470142064105115, 0.059715871789770, 0.132394152788506),
        (0.797426985353087, 0.101286507323456, 0.101286507323456, 0.125939180544827),
        (0.101286507323456, 0.797426985353087, 0.101286507323456, 0.125939180544827),
        (0.101286507323456, 0.101286507323456, 0.797426985353087, 0.125939180544827),
    ],
}


@dataclass
class Stats:
    case_id: str
    backend: str
    element_total: int = 0
    inside: int = 0
    cut: int = 0
    outside: int = 0
    std_elem: int = 0
    std_gp: int = 0
    sub_cells: int = 0
    sub_test_gp: int = 0
    sub_accepted_gp: int = 0
    tri_outer: int = 0
    tri_hole: int = 0
    tri_gp: int = 0
    fallback: int = 0
    integrated_area: float = 0.0
    classify_ms: float = 0.0
    quad_ms: float = 0.0
    total_ms: float = 0.0


@dataclass(frozen=True)
class TrimMask:
    """Patch-level trimmed-domain oracle used by the quadrature routines.

    In the full C++ implementation, the same logical object is constructed from
    DWG B-Rep loops and then shared by element classification, loads, weak
    boundary conditions, coupling, and post-processing.  Here it is built from a
    JSON case file so that the CAD-independent behavior can be rerun without
    AutoCAD/ObjectARX.
    """

    outer_loop: list[Point] | None
    hole_loops: list[list[Point]]
    boundary_chains: list[list[Point]]

    @classmethod
    def from_case(cls, mask: dict) -> "TrimMask":
        outer_raw = mask.get("outer_loop")
        outer = ensure_ccw(clean_loop(outer_raw)) if outer_raw else None
        holes = [ensure_ccw(clean_loop(h)) for h in mask.get("hole_loops", []) if len(h) >= 3]
        chains = [
            clean_loop(chain.get("points", []))
            for chain in mask.get("boundary_chains", [])
            if len(chain.get("points", [])) >= 2
        ]
        return cls(outer_loop=outer, hole_loops=holes, boundary_chains=chains)

    def contains(self, point: Point) -> bool:
        return inside_trim(point, self.outer_loop, self.hole_loops)

    def classify_cell(self, rect: Rect) -> str:
        return classify_cell(rect, self.outer_loop, self.hole_loops)


def clean_loop(points: Iterable[Iterable[float]], eps: float = 1e-12) -> list[Point]:
    loop: list[Point] = [(float(p[0]), float(p[1])) for p in points]
    if not loop:
        return []
    compact: list[Point] = []
    for p in loop:
        if not compact or dist2(compact[-1], p) > eps * eps:
            compact.append(p)
    if len(compact) > 1 and dist2(compact[0], compact[-1]) <= eps * eps:
        compact.pop()
    return compact


def dist2(a: Point, b: Point) -> float:
    return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2


def cross(a: Point, b: Point, c: Point) -> float:
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def signed_area(poly: list[Point]) -> float:
    if len(poly) < 3:
        return 0.0
    return 0.5 * sum(
        poly[i][0] * poly[(i + 1) % len(poly)][1]
        - poly[(i + 1) % len(poly)][0] * poly[i][1]
        for i in range(len(poly))
    )


def ensure_ccw(poly: list[Point]) -> list[Point]:
    return list(reversed(poly)) if signed_area(poly) < 0 else poly


def bbox(poly: list[Point]) -> Rect:
    us = [p[0] for p in poly]
    vs = [p[1] for p in poly]
    return min(us), max(us), min(vs), max(vs)


def rects_overlap(a: Rect, b: Rect, eps: float = 1e-12) -> bool:
    return not (a[1] < b[0] - eps or a[0] > b[1] + eps or a[3] < b[2] - eps or a[2] > b[3] + eps)


def point_in_rect(p: Point, rect: Rect, eps: float = 1e-12) -> bool:
    return rect[0] - eps <= p[0] <= rect[1] + eps and rect[2] - eps <= p[1] <= rect[3] + eps


def point_on_segment(p: Point, a: Point, b: Point, eps: float = 1e-12) -> bool:
    if abs(cross(a, b, p)) > eps:
        return False
    return (
        min(a[0], b[0]) - eps <= p[0] <= max(a[0], b[0]) + eps
        and min(a[1], b[1]) - eps <= p[1] <= max(a[1], b[1]) + eps
    )


def point_in_poly(poly: list[Point], p: Point) -> bool:
    if len(poly) < 3:
        return False
    for i, a in enumerate(poly):
        b = poly[(i + 1) % len(poly)]
        if point_on_segment(p, a, b):
            return True
    inside = False
    u, v = p
    j = len(poly) - 1
    for i in range(len(poly)):
        ui, vi = poly[i]
        uj, vj = poly[j]
        if (vi > v) != (vj > v):
            u_hit = ui + (v - vi) * (uj - ui) / (vj - vi)
            if u <= u_hit:
                inside = not inside
        j = i
    return inside


def segment_intersects_rect(a: Point, b: Point, rect: Rect) -> bool:
    if point_in_rect(a, rect) or point_in_rect(b, rect):
        return True
    corners = [(rect[0], rect[2]), (rect[1], rect[2]), (rect[1], rect[3]), (rect[0], rect[3])]
    edges = list(zip(corners, corners[1:] + corners[:1]))
    return any(segments_intersect(a, b, c, d) for c, d in edges)


def segments_intersect(a: Point, b: Point, c: Point, d: Point, eps: float = 1e-12) -> bool:
    o1 = cross(a, b, c)
    o2 = cross(a, b, d)
    o3 = cross(c, d, a)
    o4 = cross(c, d, b)
    if (o1 > eps) != (o2 > eps) and (o3 > eps) != (o4 > eps):
        return True
    return (
        abs(o1) <= eps and point_on_segment(c, a, b, eps)
        or abs(o2) <= eps and point_on_segment(d, a, b, eps)
        or abs(o3) <= eps and point_on_segment(a, c, d, eps)
        or abs(o4) <= eps and point_on_segment(b, c, d, eps)
    )


def poly_intersects_rect(poly: list[Point], rect: Rect) -> bool:
    if len(poly) < 2 or not rects_overlap(bbox(poly), rect):
        return False
    if any(point_in_rect(p, rect) for p in poly):
        return True
    return any(segment_intersects_rect(poly[i], poly[(i + 1) % len(poly)], rect) for i in range(len(poly)))


def clip_polygon_to_rect(poly: list[Point], rect: Rect) -> list[Point]:
    umin, umax, vmin, vmax = rect
    out = poly[:]
    for inside, intersect in [
        (lambda p: p[0] >= umin, lambda a, b: (umin, a[1] + (umin - a[0]) * (b[1] - a[1]) / safe(b[0] - a[0]))),
        (lambda p: p[0] <= umax, lambda a, b: (umax, a[1] + (umax - a[0]) * (b[1] - a[1]) / safe(b[0] - a[0]))),
        (lambda p: p[1] >= vmin, lambda a, b: (a[0] + (vmin - a[1]) * (b[0] - a[0]) / safe(b[1] - a[1]), vmin)),
        (lambda p: p[1] <= vmax, lambda a, b: (a[0] + (vmax - a[1]) * (b[0] - a[0]) / safe(b[1] - a[1]), vmax)),
    ]:
        if not out:
            return []
        inp = out
        out = []
        s = inp[-1]
        s_in = inside(s)
        for e in inp:
            e_in = inside(e)
            if s_in and e_in:
                out.append(e)
            elif s_in and not e_in:
                out.append(intersect(s, e))
            elif not s_in and e_in:
                out.append(intersect(s, e))
                out.append(e)
            s, s_in = e, e_in
        out = clean_loop(out)
    return ensure_ccw(out)


def safe(x: float) -> float:
    return x if abs(x) > 1e-30 else math.copysign(1e-30, x if x else 1.0)


def triangulate_ear(poly: list[Point]) -> list[tuple[Point, Point, Point]]:
    poly = ensure_ccw(clean_loop(poly))
    if len(poly) < 3:
        return []
    if len(poly) == 3:
        return [(poly[0], poly[1], poly[2])]
    idx = list(range(len(poly)))
    tris: list[tuple[Point, Point, Point]] = []
    guard = 0
    while len(idx) > 3 and guard < 10000:
        guard += 1
        found = False
        n = len(idx)
        for k in range(n):
            i0, i1, i2 = idx[(k - 1) % n], idx[k], idx[(k + 1) % n]
            a, b, c = poly[i0], poly[i1], poly[i2]
            if cross(a, b, c) <= 1e-14:
                continue
            if any(
                point_in_triangle(poly[j], a, b, c)
                for j in idx
                if j not in {i0, i1, i2}
            ):
                continue
            tris.append((a, b, c))
            idx.pop(k)
            found = True
            break
        if not found:
            return []
    if len(idx) == 3:
        tris.append((poly[idx[0]], poly[idx[1]], poly[idx[2]]))
    return tris


def point_in_triangle(p: Point, a: Point, b: Point, c: Point) -> bool:
    c1, c2, c3 = cross(a, b, p), cross(b, c, p), cross(c, a, p)
    has_neg = c1 < -1e-12 or c2 < -1e-12 or c3 < -1e-12
    has_pos = c1 > 1e-12 or c2 > 1e-12 or c3 > 1e-12
    return not (has_neg and has_pos)


def tri_area(tri: tuple[Point, Point, Point]) -> float:
    return 0.5 * abs(cross(tri[0], tri[1], tri[2]))


def load_case(path: Path) -> dict:
    case = json.loads(path.read_text(encoding="utf-8"))
    if not case["knot_spans"]["u"] or not case["knot_spans"]["v"]:
        raise ValueError("knot_spans.u and knot_spans.v must be non-empty")
    return case


def inside_trim(p: Point, outer: list[Point] | None, holes: list[list[Point]]) -> bool:
    if outer is not None and not point_in_poly(outer, p):
        return False
    return not any(point_in_poly(h, p) for h in holes)


def classify_cell(rect: Rect, outer: list[Point] | None, holes: list[list[Point]]) -> str:
    corners = [(rect[0], rect[2]), (rect[1], rect[2]), (rect[0], rect[3]), (rect[1], rect[3])]
    inside = [inside_trim(c, outer, holes) for c in corners]
    loops = ([] if outer is None else [outer]) + holes
    cuts = any(poly_intersects_rect(loop, rect) for loop in loops)
    if all(inside) and not cuts:
        return "inside"
    if not any(inside) and not cuts:
        return "outside"
    return "cut"


def integrate_standard(rect: Rect, qn: int) -> tuple[int, float]:
    gp = GAUSS_1D[qn]
    area = 0.0
    for xi, wx in gp:
        for eta, wy in gp:
            area += 0.25 * (rect[1] - rect[0]) * (rect[3] - rect[2]) * wx * wy
    return len(gp) * len(gp), area


def integrate_masking(rect: Rect, outer: list[Point] | None, holes: list[list[Point]], qn: int, subdiv: int) -> tuple[int, int, int, float]:
    gp = GAUSS_1D[qn]
    sub_cells = subdiv * subdiv
    tested = 0
    accepted = 0
    area = 0.0
    du = (rect[1] - rect[0]) / subdiv
    dv = (rect[3] - rect[2]) / subdiv
    for su in range(subdiv):
        for sv in range(subdiv):
            u0 = rect[0] + su * du
            v0 = rect[2] + sv * dv
            for xi, wx in gp:
                u = u0 + 0.5 * (xi + 1.0) * du
                for eta, wy in gp:
                    tested += 1
                    v = v0 + 0.5 * (eta + 1.0) * dv
                    if inside_trim((u, v), outer, holes):
                        accepted += 1
                        area += 0.25 * du * dv * wx * wy
    return sub_cells, tested, accepted, area


def integrate_triangle(rect: Rect, outer: list[Point] | None, holes: list[list[Point]], tri_qn: int) -> tuple[int, int, int, int, float]:
    base = [(rect[0], rect[2]), (rect[1], rect[2]), (rect[1], rect[3]), (rect[0], rect[3])]
    if outer is not None:
        base = clip_polygon_to_rect(outer, rect)
    if len(base) < 3:
        return 0, 0, 0, 0, 0.0

    outer_tris = triangulate_ear(base)
    if not outer_tris:
        return 0, 0, 0, 1, 0.0
    area = sum(tri_area(t) for t in outer_tris)
    tri_outer = len(outer_tris)
    tri_hole = 0

    for hole in holes:
        if not rects_overlap(bbox(hole), rect):
            continue
        clipped_hole = clip_polygon_to_rect(hole, rect)
        if len(clipped_hole) < 3:
            continue
        hole_tris = triangulate_ear(clipped_hole)
        if not hole_tris:
            return tri_outer, tri_hole, tri_outer * len(TRI_GAUSS[tri_qn]), 1, area
        tri_hole += len(hole_tris)
        area -= sum(tri_area(t) for t in hole_tris)

    tri_gp = (tri_outer + tri_hole) * len(TRI_GAUSS[tri_qn])
    return tri_outer, tri_hole, tri_gp, 0, area


def run_case(case: dict, backend_override: str | None = None) -> Stats:
    settings = case.get("quadrature_settings", {})
    backend = backend_override or settings.get("backend", "triangle")
    qn = int(settings.get("quad_gauss_n", 3))
    subdiv = int(settings.get("sub_cell_div", 4))
    tri_qn = int(settings.get("tri_gauss_n", 7))
    if qn not in GAUSS_1D:
        raise ValueError(f"quad_gauss_n={qn} is unsupported; choose {sorted(GAUSS_1D)}")
    if tri_qn not in TRI_GAUSS:
        raise ValueError(f"tri_gauss_n={tri_qn} is unsupported; choose {sorted(TRI_GAUSS)}")
    if backend not in {"masking", "triangle"}:
        raise ValueError("backend must be 'masking' or 'triangle'")

    trim_mask = TrimMask.from_case(case.get("trim_mask", {}))
    u = [float(x) for x in case["knot_spans"]["u"]]
    v = [float(x) for x in case["knot_spans"]["v"]]

    stats = Stats(case_id=case.get("case_id", "unnamed"), backend=backend)
    t0 = time.perf_counter()
    cells: list[tuple[Rect, str]] = []
    t_class0 = time.perf_counter()
    for i in range(len(u) - 1):
        for j in range(len(v) - 1):
            rect = (u[i], u[i + 1], v[j], v[j + 1])
            cls = trim_mask.classify_cell(rect)
            cells.append((rect, cls))
    stats.classify_ms = 1000.0 * (time.perf_counter() - t_class0)
    stats.element_total = len(cells)
    stats.inside = sum(1 for _, cls in cells if cls == "inside")
    stats.outside = sum(1 for _, cls in cells if cls == "outside")
    stats.cut = sum(1 for _, cls in cells if cls == "cut")

    t_quad0 = time.perf_counter()
    for rect, cls in cells:
        if cls == "outside":
            continue
        if cls == "inside":
            gp_count, area = integrate_standard(rect, qn)
            stats.std_elem += 1
            stats.std_gp += gp_count
            stats.integrated_area += area
            continue
        if backend == "masking":
            sub_cells, tested, accepted, area = integrate_masking(
                rect,
                trim_mask.outer_loop,
                trim_mask.hole_loops,
                qn,
                subdiv,
            )
            stats.sub_cells += sub_cells
            stats.sub_test_gp += tested
            stats.sub_accepted_gp += accepted
            stats.integrated_area += area
        else:
            tri_outer, tri_hole, tri_gp, fallback, area = integrate_triangle(
                rect,
                trim_mask.outer_loop,
                trim_mask.hole_loops,
                tri_qn,
            )
            stats.tri_outer += tri_outer
            stats.tri_hole += tri_hole
            stats.tri_gp += tri_gp
            stats.fallback += fallback
            if fallback:
                sub_cells, tested, accepted, area = integrate_masking(
                    rect,
                    trim_mask.outer_loop,
                    trim_mask.hole_loops,
                    qn,
                    subdiv,
                )
                stats.sub_cells += sub_cells
                stats.sub_test_gp += tested
                stats.sub_accepted_gp += accepted
            stats.integrated_area += area
    stats.quad_ms = 1000.0 * (time.perf_counter() - t_quad0)
    stats.total_ms = 1000.0 * (time.perf_counter() - t0)
    return stats


def main() -> None:
    parser = argparse.ArgumentParser(description="Run minimal TrimMask/quadrature benchmark")
    parser.add_argument("--case", required=True, type=Path)
    parser.add_argument("--backend", choices=["masking", "triangle"])
    args = parser.parse_args()
    stats = run_case(load_case(args.case), args.backend)
    print(json.dumps(stats.__dict__, indent=2))


if __name__ == "__main__":
    main()
