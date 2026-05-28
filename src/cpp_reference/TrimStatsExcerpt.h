#pragma once
/*
 * Cleaned C++ excerpt of the trim/quadrature settings and statistics used by
 * the complete AutoCAD/ObjectARX implementation.
 *
 * This header is a documentation artifact for the public reproducibility
 * package. It is intentionally independent of AutoCAD/ObjectARX headers. The
 * full project stores these fields in SolveConfig.h and DocData.h, and prints
 * them through the [TRIM] and [IGA][Scale] log lines used to populate the
 * manuscript scale/backend-comparison tables.
 */

#include <cstdint>

namespace TrimMaskReference {

enum class TrimQuadratureMode : int {
    MaskingSubCell = 0,       // subdivide cut cells and filter Gauss points
    EarTriangle = 1,          // legacy ear-clipping triangle backend
    ClipperTriangle = 2       // Clipper2 visible-region triangle backend
};

struct TrimQuadratureSettings {
    TrimQuadratureMode mode = TrimQuadratureMode::EarTriangle;
    int quadGaussPerDirection = 3;  // tensor-product Gauss rule for full cells
    int subCellDivisions = 4;       // sub-cell divisions per parametric direction
    int triangleGaussPoints = 7;    // common values: 1, 3, or 7
};

struct TrimStatsExcerpt {
    // Patch-level TrimMask registration.
    std::int64_t registeredShellPatches = 0;
    std::int64_t nontrivialTrimShellPatches = 0;
    std::int64_t fullDomainOnlyShellPatches = 0;
    std::int64_t shellPatchesWithHoles = 0;

    // Background knot-span element classification.
    std::int64_t elementsTotal = 0;
    std::int64_t elementsInside = 0;
    std::int64_t elementsCut = 0;
    std::int64_t elementsOutside = 0;

    // Standard tensor-product quadrature for uncut inside cells.
    std::int64_t standardElements = 0;
    std::int64_t standardGaussPoints = 0;

    // Masking-based sub-cell quadrature for cut cells.
    std::int64_t subCells = 0;
    std::int64_t subCellGaussPointsTested = 0;
    std::int64_t subCellGaussPointsAccepted = 0;

    // Triangle-based visible-region quadrature for cut cells.
    std::int64_t outerVisibleTriangles = 0;
    std::int64_t holeTriangles = 0;
    std::int64_t triangleGaussPoints = 0;
    std::int64_t triangleFallbackToSubCell = 0;

    // Timing counters reported in the manuscript logs.
    std::int64_t classifyMicroseconds = 0;
    std::int64_t clipAndTriangulateMicroseconds = 0;
    std::int64_t trimTotalMicroseconds = 0;

    // Optional diagnostic integral over the active trimmed region.
    double integratedArea = 0.0;

    void clear() { *this = TrimStatsExcerpt{}; }
};

inline double millisecondsFromMicroseconds(std::int64_t microseconds)
{
    return static_cast<double>(microseconds) / 1000.0;
}

} // namespace TrimMaskReference
