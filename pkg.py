#!/usr/bin/env -S uv run --script
"""Build a .ankiaddon package from non-ignored files in src/."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

def get_included_files(repo_root: Path, src_dir: Path) -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "--", "src"],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    )
    files: list[Path] = []
    for line in result.stdout.splitlines():
        if not line:
            continue
        path = repo_root / line
        if path.is_file() and src_dir in path.parents:
            files.append(path)
    return files

def build_package(repo_root: Path, output_path: Path) -> None:
    src_dir = repo_root / "src"
    if not src_dir.is_dir():
        raise FileNotFoundError("Expected a src directory in the repository root.")

    included_files = get_included_files(repo_root, src_dir)
    if not included_files:
        raise RuntimeError("No files in src were selected for packaging.")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(output_path, "w", compression=ZIP_DEFLATED) as zf:
        for file_path in included_files:
            zf.write(file_path, arcname=file_path.relative_to(src_dir))

def main() -> int:
    repo_root = Path(__file__).resolve().parent
    output_path = (repo_root / "brainrot.ankiaddon").resolve()

    try:
        build_package(repo_root, output_path)
    except (subprocess.CalledProcessError, FileNotFoundError, RuntimeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(f"Wrote {output_path}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
