"""
roi_run.py — Wrapper to call roi_dll.dll via ctypes from Python 3.12.

Usage:
    python roi_run.py <roi_file> <tar_file> -o <output_dir>

The DLL internally saves .tif, .png, and .csv.  This wrapper uses a
temporary output directory, then copies only .png and .csv to the final
destination so the original input .tif files are never overwritten.
"""

import argparse
import ctypes
import os
import shutil
import sys
import tempfile


def main():
    parser = argparse.ArgumentParser(description="ROI DLL wrapper")
    parser.add_argument("roi_file", help="Full path to ROI reference image")
    parser.add_argument("tar_file", help="Full path to target image")
    parser.add_argument("-o", "--output", required=True, help="Output directory")
    args = parser.parse_args()

    dll_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "roi_dll.dll")
    if not os.path.isfile(dll_path):
        print(f"ERROR: DLL not found: {dll_path}", file=sys.stderr)
        sys.exit(1)

    lib = ctypes.CDLL(dll_path)
    lib.ROI_with_output.argtypes = [
        ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p,
    ]
    lib.ROI_with_output.restype = ctypes.c_int

    # Use a temp directory so the DLL doesn't overwrite input TIFs
    with tempfile.TemporaryDirectory() as tmp_dir:
        ret = lib.ROI_with_output(
            args.roi_file.encode("utf-8"),
            args.tar_file.encode("utf-8"),
            tmp_dir.encode("utf-8"),
        )

        if ret != 0:
            print(f"ERROR: DLL returned {ret}", file=sys.stderr)
            sys.exit(1)

        # Copy only .png and .csv to final output directory
        os.makedirs(args.output, exist_ok=True)
        for f in os.listdir(tmp_dir):
            if f.lower().endswith((".png", ".csv")):
                src = os.path.join(tmp_dir, f)
                dst = os.path.join(args.output, f)
                shutil.copy2(src, dst)
                print(f"  Saved: {f}")

    sys.exit(0)


if __name__ == "__main__":
    main()
