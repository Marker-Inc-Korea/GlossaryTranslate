from __future__ import annotations

import argparse
import shutil
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a Hugging Face aggregate result dataset")
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    shutil.copy2(root / "huggingface" / "results" / "README.md", output / "README.md")
    shutil.copy2(args.report, output / "public-benchmark.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
