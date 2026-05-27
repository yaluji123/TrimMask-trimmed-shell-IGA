#pragma once
/*
 * Reference C++ TrimMask header from the complete AutoCAD/ObjectARX
 * implementation used in the manuscript.
 *
 * This file is included for traceability between the public Python
 * reproducibility package and the full C++ CAD/CAE program. It is not part of
 * the standalone Python runner and is not expected to compile outside the
 * original ObjectARX project without the project registry implementation and
 * Autodesk headers. In the full program, Adesk::ULongPtr is the shell-patch
 * handle used to bind TrimMask records to native DWG/B-Rep entities.
 */
#include <cmath>
#include <algorithm>
#include <unordered_map>
#include <vector>
#include <functional>
#include <limits>
#include <utility>
#include "adesk.h" 

namespace TrimMask {

    struct UV { double u, v; };

    struct UVSeg {
        double u0 = 0, v0 = 0, u1 = 0, v1 = 0;   // segment endpoints
        inline void set(double a, double b, double c, double d) { u0 = a; v0 = b; u1 = c; v1 = d; }
        inline double du() const { return u1 - u0; }
        inline double dv() const { return v1 - v0; }
    };

    // ====== Triangular trimmed region ======
    struct TriUV {
        bool   enable = false;
        double u1 = 0, v1 = 0, u2 = 0, v2 = 0, u3 = 0, v3 = 0;
        UVSeg  E[3];                // E0:(1->2), E1:(2->3), E2:(3->1)
        double signed_area = 0;     

        inline void set(double U1, double V1, double U2, double V2, double U3, double V3) {
            enable = true; u1 = U1; v1 = V1; u2 = U2; v2 = V2; u3 = U3; v3 = V3;
            // Store the three directed edges of the triangular retained region.
            E[0].set(u1, v1, u2, v2);
            E[1].set(u2, v2, u3, v3);
            E[2].set(u3, v3, u1, v1);

            signed_area = 0.5 * ((u2 - u1) * (v3 - v1) - (v2 - v1) * (u3 - u1));
            if (signed_area < 0) {
                std::swap(u2, u3); std::swap(v2, v3);
                E[0].set(u1, v1, u2, v2);
                E[1].set(u2, v2, u3, v3);
                E[2].set(u3, v3, u1, v1);
                signed_area = -signed_area;
            }
        }
        inline void clear() { enable = false; }

        inline bool contains(double u, double v) const {
            if (!enable) return true; // no trim enabled -> treat as fully inside
            const double eps = 1e-12;
            const double v0x = u2 - u1, v0y = v2 - v1;
            const double v1x = u3 - u1, v1y = v3 - v1;
            const double v2x = u - u1, v2y = v - v1;
            const double d00 = v0x * v0x + v0y * v0y;
            const double d01 = v0x * v1x + v0y * v1y;
            const double d11 = v1x * v1x + v1y * v1y;
            const double d20 = v2x * v0x + v2y * v0y;
            const double d21 = v2x * v1x + v2y * v1y;
            const double denom = d00 * d11 - d01 * d01;
            if (std::abs(denom) < eps) return false;
            const double a = (d11 * d20 - d01 * d21) / denom;
            const double b = (d00 * d21 - d01 * d20) / denom;
            const double c = 1.0 - a - b;
            return (a >= -eps) && (b >= -eps) && (c >= -eps);
        }
    };

    struct PolyUV {
        std::vector<UV> pts;   // polygon vertices, CCW order, no repeated end point required
        double umin = +std::numeric_limits<double>::infinity();
        double umax = -std::numeric_limits<double>::infinity();
        double vmin = +std::numeric_limits<double>::infinity();
        double vmax = -std::numeric_limits<double>::infinity();
        inline void set(const std::vector<UV>& poly) {
            pts = poly;
            umin = +std::numeric_limits<double>::infinity();
            umax = -std::numeric_limits<double>::infinity();
            vmin = +std::numeric_limits<double>::infinity();
            vmax = -std::numeric_limits<double>::infinity();
            for (const auto& q : pts) {
                if (q.u < umin) umin = q.u; if (q.u > umax) umax = q.u;
                if (q.v < vmin) vmin = q.v; if (q.v > vmax) vmax = q.v;
            }
        }
    };

    struct CurveTrimUV {
        int boundaryTag = 0;
        std::vector<UV> pts;   // sampled UV polyline along one trim edge / chain
        double umin = +std::numeric_limits<double>::infinity();
        double umax = -std::numeric_limits<double>::infinity();
        double vmin = +std::numeric_limits<double>::infinity();
        double vmax = -std::numeric_limits<double>::infinity();
        double lengthUV = 0.0;

        inline void set(const std::vector<UV>& curvePts, int tag = 0) {
            boundaryTag = tag;
            pts = curvePts;
            umin = +std::numeric_limits<double>::infinity();
            umax = -std::numeric_limits<double>::infinity();
            vmin = +std::numeric_limits<double>::infinity();
            vmax = -std::numeric_limits<double>::infinity();
            lengthUV = 0.0;
            for (size_t i = 0; i < pts.size(); ++i) {
                const auto& q = pts[i];
                if (q.u < umin) umin = q.u; if (q.u > umax) umax = q.u;
                if (q.v < vmin) vmin = q.v; if (q.v > vmax) vmax = q.v;
                if (i > 0) {
                    const double du = pts[i].u - pts[i - 1].u;
                    const double dv = pts[i].v - pts[i - 1].v;
                    lengthUV += std::sqrt(du * du + dv * dv);
                }
            }
        }
    };

    class Registry {
    public:
        std::unordered_map<Adesk::ULongPtr, TriUV>& triMap() { return triMap_; }
        const std::unordered_map<Adesk::ULongPtr, TriUV>& triMap() const { return triMap_; }

        std::unordered_map<Adesk::ULongPtr, PolyUV>& polyMap() { return polyMap_; }
        const std::unordered_map<Adesk::ULongPtr, PolyUV>& polyMap() const { return polyMap_; }

        std::unordered_map<Adesk::ULongPtr, std::vector<PolyUV>>& holesMap() { return holesMap_; }
        const std::unordered_map<Adesk::ULongPtr, std::vector<PolyUV>>& holesMap() const { return holesMap_; }

        std::unordered_map<Adesk::ULongPtr, std::vector<CurveTrimUV>>& curveMap() { return curveMap_; }
        const std::unordered_map<Adesk::ULongPtr, std::vector<CurveTrimUV>>& curveMap() const { return curveMap_; }

    private:
        std::unordered_map<Adesk::ULongPtr, TriUV> triMap_;
        std::unordered_map<Adesk::ULongPtr, PolyUV> polyMap_;
        std::unordered_map<Adesk::ULongPtr, std::vector<PolyUV>> holesMap_;
        std::unordered_map<Adesk::ULongPtr, std::vector<CurveTrimUV>> curveMap_;
    };

    Registry& RegistryForCurrentDocument();

    inline std::unordered_map<Adesk::ULongPtr, TriUV>& _triMap() { return RegistryForCurrentDocument().triMap(); }
    inline std::unordered_map<Adesk::ULongPtr, PolyUV>& _polyMap() { return RegistryForCurrentDocument().polyMap(); }
    inline std::unordered_map<Adesk::ULongPtr, std::vector<PolyUV>>& _holesMap() { return RegistryForCurrentDocument().holesMap(); }
    inline std::unordered_map<Adesk::ULongPtr, std::vector<CurveTrimUV>>& _curveMap() { return RegistryForCurrentDocument().curveMap(); }

    inline bool _near_uv_pt(const UV& a, const UV& b, double tol = 1e-8) {
        return (std::abs(a.u - b.u) <= tol) && (std::abs(a.v - b.v) <= tol);
    }

    inline void _compact_curve_pts(std::vector<UV>& pts, double tol = 1e-8) {
        if (pts.size() < 2) return;
        std::vector<UV> compact;
        compact.reserve(pts.size());
        for (const auto& p : pts) {
            if (compact.empty() || !_near_uv_pt(compact.back(), p, tol))
                compact.push_back(p);
        }
        pts.swap(compact);
    }

    inline bool _curve_trim_same_endpoints(const CurveTrimUV& a, const CurveTrimUV& b, double tol = 1e-8) {
        if (a.pts.size() < 2 || b.pts.size() < 2) return false;
        const bool sameForward = _near_uv_pt(a.pts.front(), b.pts.front(), tol)
            && _near_uv_pt(a.pts.back(), b.pts.back(), tol);
        const bool sameReverse = _near_uv_pt(a.pts.front(), b.pts.back(), tol)
            && _near_uv_pt(a.pts.back(), b.pts.front(), tol);
        return sameForward || sameReverse;
    }

    inline bool _point_in_poly_evenodd(const PolyUV& P, double u, double v) {
        if (P.pts.size() < 3) return true; // empty polygon -> treat as fully inside
        const double eps = 1e-12 * (std::max(std::abs(P.umax - P.umin),std::abs(P.vmax - P.vmin)) + 1.0);
        if (u < P.umin - eps || u > P.umax + eps || v < P.vmin - eps || v > P.vmax + eps)
            return false;
        bool inside = false;
        const size_t n = P.pts.size();
        for (size_t i = 0, j = n - 1; i < n; j = i++) {
            const double xi = P.pts[i].u, yi = P.pts[i].v;
            const double xj = P.pts[j].u, yj = P.pts[j].v;
            const bool cross = ((yi > v) != (yj > v));
            if (cross) {
                const double denom = (yj - yi);
                const double t = (std::abs(denom) > 1e-300) ? ((v - yi) / denom) : 0.0;
                const double xhit = xi + t * (xj - xi);
                if (u <= xhit + eps) inside = !inside;
            }
        }
        return inside;
    }

    inline bool TryGetTriFor(Adesk::ULongPtr sh, TriUV& out) {
        auto& M = _triMap();
        auto it = M.find(sh);
        if (it == M.end() || !it->second.enable || it->second.signed_area <= 1e-16) return false;
        out = it->second;
        return true;
    }

    inline bool TryGetPolyFor(Adesk::ULongPtr sh, std::vector<UV>& out) {
        auto& P = _polyMap();
        auto it = P.find(sh);
        if (it == P.end() || it->second.pts.size() < 3) return false;
        out = it->second.pts;
        return true;
    }

    // Read hole loops as UV point sequences; each returned hole has at least three points.
    inline bool TryGetHolesFor(Adesk::ULongPtr sh, std::vector<std::vector<UV>>& out) {
        auto& H = _holesMap();
        auto it = H.find(sh);
        if (it == H.end() || it->second.empty()) return false;
        out.clear();
        out.reserve(it->second.size());
        for (const auto& hp : it->second) {
            if (hp.pts.size() >= 3) out.push_back(hp.pts);
        }
        return !out.empty();
    }

    inline bool HasHolesFor(Adesk::ULongPtr sh) {
        auto& H = _holesMap();
        auto it = H.find(sh);
        return (it != H.end() && !it->second.empty());
    }

    inline bool TryGetCurveTrimsFor(Adesk::ULongPtr sh, std::vector<CurveTrimUV>& out) {
        auto& C = _curveMap();
        auto it = C.find(sh);
        if (it == C.end() || it->second.empty()) return false;
        out = it->second;
        return !out.empty();
    }

    inline bool HasCurveTrimsFor(Adesk::ULongPtr sh) {
        auto& C = _curveMap();
        auto it = C.find(sh);
        return (it != C.end() && !it->second.empty());
    }

    struct UVRect {
        double umin = 0.0, umax = 1.0, vmin = 0.0, vmax = 1.0;
    };

    struct NormalizedTrimData {
        bool hasPoly = false;
        bool hasTri = false;
        std::vector<UV> poly;
        TriUV tri;
        std::vector<std::vector<UV>> holes;

        inline bool hasOuter() const { return hasPoly || hasTri; }
        inline bool hasHoles() const { return !holes.empty(); }

        inline bool outerAsPoly(std::vector<UV>& out) const {
            out.clear();
            if (hasPoly && poly.size() >= 3) {
                out = poly;
                return true;
            }
            if (hasTri && tri.enable && tri.signed_area > 1e-16) {
                out.resize(3);
                out[0] = { tri.u1, tri.v1 };
                out[1] = { tri.u2, tri.v2 };
                out[2] = { tri.u3, tri.v3 };
                return true;
            }
            return false;
        }
    };

    inline bool RectIsUnit01(const UVRect& r, double eps = 1e-6) {
        return std::abs(r.umin) <= eps &&
            std::abs(r.vmin) <= eps &&
            std::abs(r.umax - 1.0) <= eps &&
            std::abs(r.vmax - 1.0) <= eps;
    }

    inline bool LoopInUnit01(const std::vector<UV>& loop, double eps = 1e-6) {
        if (loop.empty()) return false;
        for (const auto& p : loop) {
            if (p.u < -eps || p.u > 1.0 + eps ||
                p.v < -eps || p.v > 1.0 + eps)
                return false;
        }
        return true;
    }

    inline bool TriInUnit01(const TriUV& tri, double eps = 1e-6) {
        if (!tri.enable) return false;
        auto in01 = [&](double x)->bool { return x >= -eps && x <= 1.0 + eps; };
        return in01(tri.u1) && in01(tri.v1) &&
            in01(tri.u2) && in01(tri.v2) &&
            in01(tri.u3) && in01(tri.v3);
    }

    inline UVRect LoopBBox(const std::vector<UV>& loop) {
        UVRect r{};
        if (loop.empty()) return r;
        r.umin = r.umax = loop[0].u;
        r.vmin = r.vmax = loop[0].v;
        for (const auto& p : loop) {
            r.umin = std::min(r.umin, p.u);
            r.umax = std::max(r.umax, p.u);
            r.vmin = std::min(r.vmin, p.v);
            r.vmax = std::max(r.vmax, p.v);
        }
        return r;
    }

    inline UVRect TriBBox(const TriUV& tri) {
        UVRect r{};
        r.umin = std::min(tri.u1, std::min(tri.u2, tri.u3));
        r.umax = std::max(tri.u1, std::max(tri.u2, tri.u3));
        r.vmin = std::min(tri.v1, std::min(tri.v2, tri.v3));
        r.vmax = std::max(tri.v1, std::max(tri.v2, tri.v3));
        return r;
    }

    inline bool RectHasArea(const UVRect& r, double eps = 1e-14) {
        return (std::abs(r.umax - r.umin) > eps) && (std::abs(r.vmax - r.vmin) > eps);
    }

    inline void MapLoop01ToRect(std::vector<UV>& loop, const UVRect& dst) {
        const double du = dst.umax - dst.umin;
        const double dv = dst.vmax - dst.vmin;
        for (auto& p : loop) {
            p.u = dst.umin + p.u * du;
            p.v = dst.vmin + p.v * dv;
        }
    }

    inline void MapLoopRectTo01(std::vector<UV>& loop, const UVRect& src) {
        const double du = src.umax - src.umin;
        const double dv = src.vmax - src.vmin;
        if (std::abs(du) <= 1e-14 || std::abs(dv) <= 1e-14) return;
        for (auto& p : loop) {
            p.u = (p.u - src.umin) / du;
            p.v = (p.v - src.vmin) / dv;
        }
    }

    inline void ClampLoopToRect(std::vector<UV>& loop, const UVRect& r) {
        for (auto& p : loop) {
            p.u = std::min(std::max(p.u, r.umin), r.umax);
            p.v = std::min(std::max(p.v, r.vmin), r.vmax);
        }
    }

    inline void ResetTri(TriUV& tri, const UV& a, const UV& b, const UV& c) {
        tri.set(a.u, a.v, b.u, b.v, c.u, c.v);
    }

    inline void MapTri01ToRect(TriUV& tri, const UVRect& dst) {
        std::vector<UV> loop = { { tri.u1, tri.v1 }, { tri.u2, tri.v2 }, { tri.u3, tri.v3 } };
        MapLoop01ToRect(loop, dst);
        ResetTri(tri, loop[0], loop[1], loop[2]);
    }

    inline void MapTriRectTo01(TriUV& tri, const UVRect& src) {
        std::vector<UV> loop = { { tri.u1, tri.v1 }, { tri.u2, tri.v2 }, { tri.u3, tri.v3 } };
        MapLoopRectTo01(loop, src);
        ResetTri(tri, loop[0], loop[1], loop[2]);
    }

    inline void ClampTriToRect(TriUV& tri, const UVRect& r) {
        std::vector<UV> loop = { { tri.u1, tri.v1 }, { tri.u2, tri.v2 }, { tri.u3, tri.v3 } };
        ClampLoopToRect(loop, r);
        ResetTri(tri, loop[0], loop[1], loop[2]);
    }

    inline void NormalizeLoopToDomain(std::vector<UV>& loop,
        const UVRect& domain,
        bool domainIsUnit,
        bool useSharedSrcBBox,
        const UVRect& sharedSrcBBox,
        bool clampToDomain = false)
    {
        if (loop.size() < 3) return;
        const bool loopIsUnit = LoopInUnit01(loop);
        if (domainIsUnit && !loopIsUnit) {
            if (useSharedSrcBBox) MapLoopRectTo01(loop, sharedSrcBBox);
        }
        else if (!domainIsUnit && loopIsUnit) {
            MapLoop01ToRect(loop, domain);
        }
        if (clampToDomain) ClampLoopToRect(loop, domain);
    }

    inline void NormalizeTriToDomain(TriUV& tri,
        const UVRect& domain,
        bool domainIsUnit,
        bool useSharedSrcBBox,
        const UVRect& sharedSrcBBox,
        bool clampToDomain = false)
    {
        if (!tri.enable) return;
        const bool triIsUnit = TriInUnit01(tri);
        if (domainIsUnit && !triIsUnit) {
            if (useSharedSrcBBox) MapTriRectTo01(tri, sharedSrcBBox);
        }
        else if (!domainIsUnit && triIsUnit) {
            MapTri01ToRect(tri, domain);
        }
        if (clampToDomain) ClampTriToRect(tri, domain);
    }

    inline bool NormalizeTrimDataForDomain(bool& hasPoly,
        std::vector<UV>& poly,
        bool& hasTri,
        TriUV& tri,
        std::vector<std::vector<UV>>& holes,
        const UVRect& domain,
        bool clampToDomain = false)
    {
        hasPoly = hasPoly && poly.size() >= 3;
        hasTri = hasTri && tri.enable && tri.signed_area > 1e-16;

        const bool domainIsUnit = RectIsUnit01(domain);
        UVRect sharedSrcBBox{};
        bool useSharedSrcBBox = false;

        if (domainIsUnit) {
            if (hasPoly && !LoopInUnit01(poly)) {
                sharedSrcBBox = LoopBBox(poly);
                useSharedSrcBBox = RectHasArea(sharedSrcBBox);
            }
            else if (!hasPoly && hasTri && !TriInUnit01(tri)) {
                sharedSrcBBox = TriBBox(tri);
                useSharedSrcBBox = RectHasArea(sharedSrcBBox);
            }
        }

        if (hasPoly) NormalizeLoopToDomain(poly, domain, domainIsUnit, useSharedSrcBBox, sharedSrcBBox, clampToDomain);
        if (hasTri) NormalizeTriToDomain(tri, domain, domainIsUnit, useSharedSrcBBox, sharedSrcBBox, clampToDomain);

        std::vector<std::vector<UV>> normalizedHoles;
        normalizedHoles.reserve(holes.size());
        for (auto& hole : holes) {
            if (hole.size() < 3) continue;
            NormalizeLoopToDomain(hole, domain, domainIsUnit, useSharedSrcBBox, sharedSrcBBox, clampToDomain);
            if (hole.size() >= 3) normalizedHoles.push_back(std::move(hole));
        }
        holes.swap(normalizedHoles);

        return hasPoly || hasTri || !holes.empty();
    }

    inline bool GetTrimDataForDomain(Adesk::ULongPtr shellH,
        const UVRect& domain,
        NormalizedTrimData& out,
        bool clampToDomain = false)
    {
        out = NormalizedTrimData{};

        bool hasPoly = TryGetPolyFor(shellH, out.poly);
        bool hasTri = false;
        if (!hasPoly) {
            hasTri = TryGetTriFor(shellH, out.tri);
        }
        TryGetHolesFor(shellH, out.holes);

        if (!hasPoly && !hasTri && out.holes.empty()) return false;
        if (!NormalizeTrimDataForDomain(hasPoly, out.poly, hasTri, out.tri, out.holes, domain, clampToDomain))
            return false;

        out.hasPoly = hasPoly;
        out.hasTri = hasTri;
        return true;
    }

    inline void SetTrimTriFor(Adesk::ULongPtr shellH,
        double u1, double v1, double u2, double v2, double u3, double v3) {
        TriUV t; t.set(u1, v1, u2, v2, u3, v3);
        _triMap()[shellH] = t;
    }

    inline double _signed_area(const std::vector<UV>& poly) {
        if (poly.size() < 3) return 0.0;
        double a = 0.0;
        const size_t n = poly.size();
        for (size_t i = 0, j = n - 1; i < n; j = i++) {
            a += poly[j].u * poly[i].v - poly[i].u * poly[j].v;
        }
        return 0.5 * a;   // >0: CCW, <0: CW
    }

    inline void SetTrimPolyFor(Adesk::ULongPtr shellH, const std::vector<UV>& polyIn) {
        if (polyIn.size() < 3) { _polyMap().erase(shellH); return; }

        std::vector<UV> poly = polyIn;          
        if (_signed_area(poly) < 0.0) {        
            std::reverse(poly.begin(), poly.end());
        }

        PolyUV P;
        P.set(poly);                           
        _polyMap()[shellH] = std::move(P);
    }
    // Set internal hole loops. An empty holesIn list clears all holes for this patch.
    inline void SetTrimHolesFor(Adesk::ULongPtr shellH, const std::vector<std::vector<UV>>& holesIn) {
        if (holesIn.empty()) { _holesMap().erase(shellH); return; }
        std::vector<PolyUV> holes;
        holes.reserve(holesIn.size());
        for (const auto& h : holesIn) {
            if (h.size() < 3) continue;
            std::vector<UV> poly = h;
            if (_signed_area(poly) < 0.0) {
                std::reverse(poly.begin(), poly.end());
            }
            PolyUV P; P.set(poly);
            if (P.pts.size() >= 3) holes.push_back(std::move(P));
        }
        if (holes.empty()) { _holesMap().erase(shellH); return; }
        _holesMap()[shellH] = std::move(holes);
    }

    inline bool AppendCurveTrimFor(Adesk::ULongPtr shellH, const std::vector<UV>& curvePtsIn, int boundaryTag = 0) {
        std::vector<UV> curvePts = curvePtsIn;
        _compact_curve_pts(curvePts);
        if (curvePts.size() < 2) return false;

        CurveTrimUV curve;
        curve.set(curvePts, boundaryTag);
        if (!(curve.lengthUV > 0.0)) return false;

        auto& dst = _curveMap()[shellH];
        for (auto& oldCurve : dst) {
            if (_curve_trim_same_endpoints(oldCurve, curve)) {
                oldCurve = std::move(curve);
                return true;
            }
        }
        dst.push_back(std::move(curve));
        return true;
    }

    inline void SetCurveTrimsFor(Adesk::ULongPtr shellH, const std::vector<CurveTrimUV>& curvesIn) {
        if (curvesIn.empty()) { _curveMap().erase(shellH); return; }
        std::vector<CurveTrimUV> curves;
        curves.reserve(curvesIn.size());
        for (const auto& c : curvesIn) {
            std::vector<UV> pts = c.pts;
            _compact_curve_pts(pts);
            if (pts.size() < 2) continue;
            CurveTrimUV curve;
            curve.set(pts, c.boundaryTag);
            if (curve.lengthUV > 0.0)
                curves.push_back(std::move(curve));
        }
        if (curves.empty()) { _curveMap().erase(shellH); return; }
        _curveMap()[shellH] = std::move(curves);
    }

    inline void ClearCurveTrimsFor(Adesk::ULongPtr shellH) {
        _curveMap().erase(shellH);
    }

    inline void ClearFor(Adesk::ULongPtr shellH) {
        _triMap().erase(shellH);
        _polyMap().erase(shellH);
        _holesMap().erase(shellH);
        _curveMap().erase(shellH);
    }

    // Trimming is enabled when an outer polygon/triangle or at least one hole loop exists.
    inline bool EnabledFor(Adesk::ULongPtr shellH) {
        auto ip = _polyMap().find(shellH);
        if (ip != _polyMap().end() && ip->second.pts.size() >= 3) return true;
        auto ih = _holesMap().find(shellH);
        if (ih != _holesMap().end() && !ih->second.empty()) return true;
        auto it = _triMap().find(shellH);
        return (it != _triMap().end()) && it->second.enable && it->second.signed_area > 1e-16;
    }

    inline const TriUV& GTriFor(Adesk::ULongPtr shellH) { return _triMap().at(shellH); }
    inline const UVSeg& EdgeFor(Adesk::ULongPtr shellH, int k) { return _triMap().at(shellH).E[k % 3]; }

    // With an outer polygon/triangle, inside = inOuter && !inAnyHole.
    // Without an outer loop, the full parameter domain is active except for holes.
    inline bool ContainsUVFor(Adesk::ULongPtr shellH, double u, double v) {
        bool inOuter = true;

        auto ip = _polyMap().find(shellH);
        if (ip != _polyMap().end() && ip->second.pts.size() >= 3) {
            inOuter = _point_in_poly_evenodd(ip->second, u, v);
        }
        else {
            auto it = _triMap().find(shellH);
            if (it != _triMap().end() && it->second.enable && it->second.signed_area > 1e-16) {
                inOuter = it->second.contains(u, v);
            }
        }
        if (!inOuter) return false;

        auto ih = _holesMap().find(shellH);
        if (ih != _holesMap().end()) {
            for (const auto& hole : ih->second) {
                if (hole.pts.size() >= 3 && _point_in_poly_evenodd(hole, u, v)) {
                    return false;
                }
            }
        }
        return true;
    }

    inline double _cross(const UV& O, const UV& A, const UV& B) {
        return (A.u - O.u) * (B.v - O.v) - (A.v - O.v) * (B.u - O.u);
    }

    inline std::vector<UV> _convex_hull(std::vector<UV> pts) {
        // Andrew monotone-chain convex hull.
        if (pts.size() < 3) return pts;
        std::sort(pts.begin(), pts.end(), [](const UV& a, const UV& b) {
            return (a.u < b.u) || (a.u == b.u && a.v < b.v);
            });
        std::vector<UV> H(pts.size() * 2);
        int k = 0;
        // Lower hull.
        for (size_t i = 0; i < pts.size(); ++i) {
            while (k >= 2 && _cross(H[k - 2], H[k - 1], pts[i]) <= 0) k--;
            H[k++] = pts[i];
        }
        for (int i = int(pts.size()) - 2, t = k + 1; i >= 0; --i) {
            while (k >= t && _cross(H[k - 2], H[k - 1], pts[i]) <= 0) k--;
            H[k++] = pts[i];
        }
        H.resize(std::max(0, k - 1));
        return H;
    }

    inline double _dist_point_seg(const UV& P, const UV& A, const UV& B) {
        const double vx = B.u - A.u, vy = B.v - A.v;
        const double wx = P.u - A.u, wy = P.v - A.v;
        const double L2 = vx * vx + vy * vy;
        if (L2 <= 1e-30) return std::hypot(P.u - A.u, P.v - A.v);
        double t = (vx * wx + vy * wy) / L2;
        t = std::max(0.0, std::min(1.0, t));
        const double px = A.u + t * vx, py = A.v + t * vy;
        return std::hypot(P.u - px, P.v - py);
    }

    inline bool TryGetEdgeTangentFor(Adesk::ULongPtr shellH,
        double u, double v,
        double& tu, double& tv)
    {
        UV  P{ u, v };
        double bestDist = std::numeric_limits<double>::infinity();
        bool found = false;

        {
            auto ip = _polyMap().find(shellH);
            if (ip != _polyMap().end() && ip->second.pts.size() >= 2) {
                const auto& poly = ip->second.pts;
                const size_t n = poly.size();
                for (size_t i = 0; i < n; ++i) {
                    const UV& A = poly[i];
                    const UV& B = poly[(i + 1) % n];
                    double d = _dist_point_seg(P, A, B);
                    if (d < bestDist) {
                        bestDist = d;
                        tu = B.u - A.u;
                        tv = B.v - A.v;
                        found = true;
                    }
                }
            }
        }

        {
            auto ih = _holesMap().find(shellH);
            if (ih != _holesMap().end()) {
                for (const auto& hp : ih->second) {
                    if (hp.pts.size() < 2) continue;
                    const auto& poly = hp.pts;
                    const size_t n = poly.size();
                    for (size_t i = 0; i < n; ++i) {
                        const UV& A = poly[i];
                    const UV& B = poly[(i + 1) % n];    // closed loop
                        double d = _dist_point_seg(P, A, B);
                        if (d < bestDist) {
                            bestDist = d;
                            tu = B.u - A.u;
                            tv = B.v - A.v;
                            found = true;
                        }
                    }
                }
            }
        }

        if (!found) {
            TriUV tri;
            if (TryGetTriFor(shellH, tri)) {
                for (int k = 0; k < 3; ++k) {
                    UV A{ tri.E[k].u0, tri.E[k].v0 };
                    UV B{ tri.E[k].u1, tri.E[k].v1 };
                    double d = _dist_point_seg(P, A, B);
                    if (d < bestDist) {
                        bestDist = d;
                        tu = B.u - A.u;
                        tv = B.v - A.v;
                        found = true;
                    }
                }
            }
        }

        if (!found)
            return false;

        double len = std::sqrt(tu * tu + tv * tv);
        if (len < 1e-14)
            return false;
        tu /= len;
        tv /= len;
        return true;
    }
 
    inline void _rdp_rec(const std::vector<UV>& poly, int s, int e, double eps, std::vector<char>& keep) {
        if (e <= s + 1) return;
        double dmax = 0; int idx = -1;
        for (int i = s + 1; i < e; ++i) {
            double d = _dist_point_seg(poly[i], poly[s], poly[e]);
            if (d > dmax) { dmax = d; idx = i; }
        }
        if (dmax > eps) {
            keep[idx] = 1;
            _rdp_rec(poly, s, idx, eps, keep);
            _rdp_rec(poly, idx, e, eps, keep);
        }
    }
    inline std::vector<UV> _rdp(const std::vector<UV>& poly, double eps) {
        if (poly.size() <= 3) return poly;
        std::vector<char> keep(poly.size(), 0);
        keep.front() = keep.back() = 1;
        _rdp_rec(poly, 0, int(poly.size()) - 1, eps, keep);
        std::vector<UV> out; out.reserve(poly.size());
        for (size_t i = 0; i < poly.size(); ++i) if (keep[i]) out.push_back(poly[i]);
        return out;
    }

    inline double _tri_area(const UV& A, const UV& B, const UV& C) {
        return std::abs(0.5 * _cross(A, B, C));
    }

    struct UVBox { double umin, umax, vmin, vmax; };

    inline bool AutoDetectTrimTriFor(
        Adesk::ULongPtr shellH,
        const std::function<void(double, double, double&, double&, double&)>& eval3D,
        const std::function<bool(double, double, double)>& isOnSurf,
        const UVBox& box,
        int grid = 56,                  
        double rdp_eps_ratio = 0.02     
    ) {
        const double du = (box.umax - box.umin) / grid;
        const double dv = (box.vmax - box.vmin) / grid;
        if (du <= 0 || dv <= 0) return false;
         
        std::vector<UV> inPts; inPts.reserve(size_t(grid * grid * 0.6));
        double x, y, z;
        for (int j = 0; j <= grid; ++j) {
            const double v = box.vmin + j * dv;
            for (int i = 0; i <= grid; ++i) {
                const double u = box.umin + i * du;
                eval3D(u, v, x, y, z);
                if (isOnSurf(x, y, z)) {
                    inPts.push_back({ u,v });
                }
            }
        }
        if (inPts.size() < 16) return false; 
        auto hull = _convex_hull(inPts);
        if (hull.size() < 3) return false;

        const double diag = std::hypot(box.umax - box.umin, box.vmax - box.vmin);
        auto simple = _rdp(hull, rdp_eps_ratio * diag);

        if (simple.front().u != simple.back().u || simple.front().v != simple.back().v) {
            simple.push_back(simple.front());
        }

        if (simple.size() < 4) return false; 
        double bestA = -1.0; UV A, B, C;
        for (size_t i = 0; i + 2 < simple.size(); ++i) {
            for (size_t j = i + 1; j + 1 < simple.size(); ++j) {
                for (size_t k = j + 1; k < simple.size(); ++k) {
                    double a = _tri_area(simple[i], simple[j], simple[k]);
                    if (a > bestA) { bestA = a; A = simple[i]; B = simple[j]; C = simple[k]; }
                }
            }
        }
        if (bestA <= 0) return false;

        SetTrimTriFor(shellH, A.u, A.v, B.u, B.v, C.u, C.v);
        return true;
    }
} 
