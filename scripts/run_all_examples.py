from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from trim_quad import load_case, run_case


def main() -> None:
    examples = sorted((ROOT / "data" / "examples").glob("*.json"))
    results = []
    for case_path in examples:
        case = load_case(case_path)
        for backend in ("triangle", "masking"):
            results.append(run_case(case, backend).__dict__)
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()

