from __future__ import annotations

import argparse
import shutil
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a self-contained Hugging Face Space")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    for name in ("app.py", "README.md", "requirements.txt"):
        shutil.copy2(root / "huggingface" / "space" / name, output / name)
    package_output = output / "glossaryrag"
    if package_output.exists():
        shutil.rmtree(package_output)
    shutil.copytree(
        root / "src" / "glossaryrag",
        package_output,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
