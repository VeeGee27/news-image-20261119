#!/usr/bin/env python3
"""Entrypoint: copy the rendered front page to the harness output dir.

Stdlib only. The image is rendered by draw.py at build time and shipped in
this repo as entry.png; this script just places it where the grader looks.
"""
import os
import shutil

SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")

def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, "entry.png")
    size = os.path.getsize(SRC)
    if size <= 0 or size > 1048576:
        raise SystemExit(f"entry.png size {size} out of range (must be 1..1048576)")
    shutil.copyfile(SRC, dst)
    print(f"copied entry.png ({size} bytes) -> {dst}")

if __name__ == "__main__":
    main()
