"""Check saved physical fields; requires NumPy. Run after prepare_data.py.
Place in validation/: ROOT defaults to the distribution root. No solver is run.
"""
from pathlib import Path
import csv
import json
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
COMPONENTS = ("sxx", "syy", "szz", "sxy", "sxz", "syz")
TENSOR_WEIGHTS = np.array([1, 1, 1, 2, 2, 2])


def checked_path(root, entry):
    path = (root / "plotting" / entry["path"]).resolve()
    path.relative_to(root.resolve())
    if not path.is_file():
        raise FileNotFoundError(f"Missing {path}; run prepare_data.py first")
    return path


def numeric_csv(path, fields):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        missing = set(fields) - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Missing columns in {path}: {sorted(missing)}")
        data = np.array([[float(row[key]) for key in fields] for row in reader])
    if data.ndim != 2 or not len(data) or not np.isfinite(data).all():
        raise ValueError(f"Empty or nonfinite numeric data: {path}")
    return data


def tensor_square(values):
    return (values * values * TENSOR_WEIGHTS).sum(axis=1)


def relative_percent(numerator, denominator):
    if denominator <= 0:
        return None
    return float(100 * np.sqrt(numerator / denominator))


def mises(t):
    normal = (t[:, 0]-t[:, 1])**2 + (t[:, 1]-t[:, 2])**2 + (t[:, 2]-t[:, 0])**2
    return np.sqrt(np.maximum(0, .5 * normal + 3 * (t[:, 3:]**2).sum(axis=1)))


def check_engineering(root, cfg):
    fields = ["element_1x", "owner", "ux_mm", "uy_mm", "uz_mm", "U_magnitude_mm"]
    fields += [f"{face}_{axis}_MPa" for face in ("SNEG", "SPOS") for axis in COMPONENTS]
    native = numeric_csv(checked_path(root, cfg["native_fields"]), fields)
    reference = numeric_csv(checked_path(root, cfg["reference_fields"]), fields + ["area_mm2", "near_opening20mm"])
    triangle_fields = ["element_1x"] + [f"{axis}{i}_mm" for i in (1, 2, 3) for axis in "xyz"] + ["area_mm2"]
    triangles = numeric_csv(checked_path(root, cfg["triangles"]), triangle_fields)
    if len(native) != len(reference) or len(native) != len(triangles):
        raise ValueError("Native, reference and triangle row counts differ")
    if not np.array_equal(native[:, :2], reference[:, :2]) or not np.array_equal(native[:, 0], triangles[:, 0]):
        raise ValueError("Element/owner identities or order differ")
    if len(np.unique(native[:, 0])) != len(native):
        raise ValueError("Repeated fixed-sample element identifiers")
    xyz = triangles[:, 1:10].reshape(-1, 3, 3)
    area = .5 * np.linalg.norm(np.cross(xyz[:, 1]-xyz[:, 0], xyz[:, 2]-xyz[:, 0]), axis=1)
    if (area <= 0).any() or not np.allclose(area, reference[:, -2], rtol=1e-12, atol=1e-10):
        raise ValueError("Nonpositive or inconsistent physical triangle area")
    if not np.allclose(area, triangles[:, -1], rtol=1e-12, atol=1e-10):
        raise ValueError("Saved triangle areas disagree with coordinates")
    if not np.isin(reference[:, -1], [0, 1]).all():
        raise ValueError("Invalid frozen opening-region membership")
    delta = native[:, 2:5] - reference[:, 2:5]
    nneg, npos = native[:, 6:12], native[:, 12:18]
    rneg, rpos = reference[:, 6:12], reference[:, 12:18]
    regions = {}
    for name, mask in (("all", np.ones(len(native), dtype=bool)), ("opening20mm", reference[:, -1].astype(bool))):
        weights = area[mask]
        metrics = {"points": int(mask.sum()), "area_mm2": float(weights.sum())}
        metrics["U_percent"] = relative_percent((weights * (delta[mask]**2).sum(axis=1)).sum(), (weights * (reference[mask, 2:5]**2).sum(axis=1)).sum())
        pairs = (("SNEG", nneg, rneg), ("SPOS", npos, rpos), ("membrane", (nneg+npos)/2, (rneg+rpos)/2), ("bending", (npos-nneg)/2, (rpos-rneg)/2))
        for quantity, current, finite in pairs:
            metrics[quantity + "_percent"] = relative_percent((weights * tensor_square((current-finite)[mask])).sum(), (weights * tensor_square(finite[mask])).sum())
        regions[name] = metrics
    return {"regions": regions, "sources": {key: cfg[key]["path"] for key in ("native_fields", "reference_fields", "triangles")},
            "ROI_membership": "Frozen centroids within 20 mm of the preselected opening corners; near_opening20mm membership unchanged",
            "pointwise_U_vector_difference_max_mm": float(np.linalg.norm(delta, axis=1).max()),
            "native_sampled_U_max_mm": float(np.linalg.norm(native[:, 2:5], axis=1).max()),
            "reference_sampled_U_max_mm": float(np.linalg.norm(reference[:, 2:5], axis=1).max()),
            "native_sampled_max_faces_Mises_MPa": float(np.maximum(mises(nneg), mises(npos)).max()),
            "reference_sampled_max_faces_Mises_MPa": float(np.maximum(mises(rneg), mises(rpos)).max()),
            "native_saved_U_magnitude_max_difference_mm": float(np.abs(native[:, 5]-np.linalg.norm(native[:, 2:5], axis=1)).max()),
            "area_max_difference_from_saved_mm2": float(np.abs(area-reference[:, -2]).max())}


def main(root=ROOT):
    root = Path(root).resolve()
    cfg = json.loads((root / "plotting" / "PLOT_INPUTS.json").read_text(encoding="utf-8"))
    output = {"scope": "Arithmetic on saved finite fields; no CAD/FE solve or continuum certification", "engineering": {}}
    for family in ("panel", "hull"):
        output["engineering"][family] = check_engineering(root, cfg["engineering"][family])
    with np.load(checked_path(root, cfg["F2"]["npz"]), allow_pickle=False) as data:
        iga, fem = data["IGA_U"], data["FEM_U"]
        if iga.shape != fem.shape or iga.ndim != 2 or iga.shape[1] != 3 or not np.isfinite(iga).all() or not np.isfinite(fem).all():
            raise ValueError("Invalid paired triangle displacement vectors")
        imax = float(np.linalg.norm(iga, axis=1).max())
        fmax = float(np.linalg.norm(fem, axis=1).max())
        output["triangle"] = {"fixed_nodes": len(iga), "P2_cells": len(data["P2_connectivity"]), "display_triangles": len(data["triangles"]),
                              "IGA_sampled_peak_mm": imax, "finite_P2_sampled_peak_mm": fmax,
                              "peak_difference_percent": None if fmax == 0 else abs(imax-fmax)/fmax*100,
                              "whole_area_vector_L2": "Not recomputed: node values alone do not supply the original whole-area integration rule"}
    print(json.dumps(output, ensure_ascii=False, indent=2, allow_nan=False))
    return output


if __name__ == "__main__":
    main()
