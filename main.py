#!/usr/bin/env python3
"""Grader entry point (stdlib only): copy the pre-rendered entry.png
into MAKEFUN_OUTPUT_DIR. No third-party imports: the grader image has no
Pillow, so this file uses os/shutil only. The image itself is rendered at
build time by gen.py (Pillow) and committed as entry.png.
"""
import os
import shutil


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "entry.png")
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "out")
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, "entry.png")
    shutil.copyfile(src, dst)
    # Fail loudly if the copy did not land, instead of passing silently.
    if not os.path.isfile(dst) or os.path.getsize(dst) == 0:
        raise RuntimeError("entry.png was not copied to " + out_dir)


if __name__ == "__main__":
    main()
