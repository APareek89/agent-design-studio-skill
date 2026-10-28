#!/usr/bin/env python3
"""Build a skills-only plugin ZIP; never include generated user designs."""

import argparse
import hashlib
import json
from pathlib import Path
import zipfile


def package(output):
    root = Path(__file__).resolve().parents[1]
    manifest = json.loads((root / "plugin.json").read_text())
    files = [
        root / "plugin.json",
        root / ".codex-plugin/plugin.json",
        root / "LICENSE",
        root / "README.md",
    ]
    files += [
        p
        for p in (root / "skills").rglob("*")
        if p.is_file()
        and "__pycache__" not in p.parts
        and p.suffix not in (".pyc", ".pyo")
    ]
    if any(p.is_symlink() or not p.resolve().is_relative_to(root) for p in files):
        raise ValueError(
            "Plugin files must stay within the package and cannot be symlinks."
        )
    output = Path(output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    archive = output / f"{manifest['name']}-{manifest['version']}.zip"
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(files):
            z.write(p, f"{manifest['name']}/{p.relative_to(root).as_posix()}")
    checksum = hashlib.sha256(archive.read_bytes()).hexdigest()
    (output / (archive.name + ".sha256")).write_text(f"{checksum}  {archive.name}\n")
    print(
        json.dumps({"archive": str(archive), "sha256": checksum, "files": len(files)})
    )
    return archive


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="dist")
    args = parser.parse_args()
    package(args.output)
