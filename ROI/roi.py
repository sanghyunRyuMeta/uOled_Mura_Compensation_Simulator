"""
roi.py - All-in-one ROI image processing module.

Consolidates ChangePointDetector + ROIProcessor + module-level ROI() function.
This single file is the only Python dependency for roi_dll.dll.

Usage (standalone):
    from roi import ROI
    ROI("C:/data/W_ROI.png", "C:/data/W128.png")

Usage (with output dir):
    from roi import ROI_with_output
    ROI_with_output("C:/data/W_ROI.png", "C:/data/W128.png", "C:/output")

Usage (OOP):
    from roi import ROIProcessor
    p = ROIProcessor("W_ROI.png", "W128.png", data_dir="C:/data", output_dir="C:/out")
    results = p.run()
"""

import os
import sys
import time
import glob
import numpy as np
import cv2
from PIL import Image as PILImage

PILImage.MAX_IMAGE_PIXELS = None

from dataclasses import dataclass, field

try:
    import ruptures as rpt
except ImportError:
    rpt = None


# ======================================================================
#  Change-Point Detector
# ======================================================================
class ChangePointDetector:
    """
    Detects abrupt changes in a signal's mean.
    Equivalent to MATLAB's findchangepts(..., 'MaxNumChanges', n).
    Returns 1-based indices (MATLAB convention).
    """

    def __init__(self, model: str = "l2", min_size: int = 2):
        self.model = model
        self.min_size = min_size

    def detect(self, signal: np.ndarray, max_num_changes: int) -> np.ndarray:
        signal = np.array(signal, dtype=np.float64).flatten()
        n = len(signal)

        if rpt is None:
            raise ImportError("ruptures is required: pip install ruptures")

        jump = max(1, n // 2000)
        algo = rpt.Binseg(model=self.model, min_size=self.min_size, jump=jump).fit(
            signal
        )
        bkps = algo.predict(n_bkps=max_num_changes)
        bkps = [b for b in bkps if b < n]

        return np.array([b + 1 for b in bkps])


# ======================================================================
#  ROI Result Container
# ======================================================================
@dataclass
class ROIResult:
    filename: str = ""
    changePts_min_col: int = 0
    changePts_max_col: int = 0
    changePts_min_row: int = 0
    changePts_max_row: int = 0
    setRow_tl: int = 0
    setRow_tr: int = 0
    setRow_bl: int = 0
    setRow_br: int = 0
    setCol_tl: int = 0
    setCol_tr: int = 0
    setCol_bl: int = 0
    setCol_br: int = 0
    ROW_PRE: int = 0
    COL_PRE: int = 0
    ROW_CROP: int = 0
    COL_CROP: int = 0
    csv_ref_val: float = 0.0
    ref_val: float = 0.0
    src_pts: np.ndarray = field(default_factory=lambda: np.zeros((4, 2)))
    center_5x5: np.ndarray = field(default_factory=lambda: np.zeros((5, 5)))
    elapsed: float = 0.0


# ======================================================================
#  ROI Processor
# ======================================================================
class ROIProcessor:
    """
    Processes images to extract ROI, apply perspective correction,
    and resize to a target resolution.

    Pipeline:
      1. Load ROI reference image and normalise
      2. Collect intensity profiles at image centre
      3. Detect change-points to locate the active region
      4. Extract & threshold four corners to find precise edges
      5. For each target image: crop, warp, resize, and save
    """

    CORNER_SIZE = 200
    THRESHOLD = 2500 * 16
    MAX_NUM_CHANGES = 6
    ROW_DISP = 2288
    COL_DISP = 2412

    def __init__(
        self,
        roi_file: str,
        tar_pattern: str,
        data_dir: str = ".",
        output_dir: str = "./out_ROI",
        tar_files: list[str] | None = None,
    ):
        self.roi_file = roi_file
        self.tar_pattern = tar_pattern
        self.data_dir = data_dir
        self.output_dir = output_dir
        self._tar_files = tar_files

        self._detector = ChangePointDetector()
        self._img_org: np.ndarray | None = None
        self._ref_val: float = 0.0

        self._cp_min_col: int = 0
        self._cp_max_col: int = 0
        self._cp_min_row: int = 0
        self._cp_max_row: int = 0

        self._setRow = {"tl": 0, "tr": 0, "bl": 0, "br": 0}
        self._setCol = {"tl": 0, "tr": 0, "bl": 0, "br": 0}

        self._ROW_PRE: int = 0
        self._COL_PRE: int = 0

    # ------------------------------------------------------------------
    #  Public API
    # ------------------------------------------------------------------
    def run(self) -> list[ROIResult]:
        self._load_pattern_image()
        self._collect_profiles()
        self._detect_change_points()
        self._extract_corners_and_find_edges()

        os.makedirs(self.output_dir, exist_ok=True)

        if self._tar_files is not None:
            file_list = [p for p in self._tar_files if os.path.isfile(p)]
        else:
            tar_glob = os.path.join(self.data_dir, self.tar_pattern)
            file_list = sorted(glob.glob(tar_glob))
        if not file_list:
            print("No target files found.")
            return []

        results = []
        for tar_path in file_list:
            result = self._process_target(tar_path)
            results.append(result)
        return results

    # ------------------------------------------------------------------
    #  Step 1: Load & normalise
    # ------------------------------------------------------------------
    def _load_pattern_image(self) -> None:
        roi_path = os.path.join(self.data_dir, self.roi_file)
        img = np.array(PILImage.open(roi_path), dtype=np.float64)
        if img.ndim > 2:
            img = img[:, :, 0]

        ROW, COL = img.shape
        r1, r2 = ROW // 2 - 500, ROW // 2 + 501
        c1, c2 = COL // 2 - 500, COL // 2 + 501
        self._ref_val = np.mean(img[r1:r2, c1:c2])
        self._img_org = img / self._ref_val * (3500 * 2**4)

    # ------------------------------------------------------------------
    #  Step 2: Collect centre profiles
    # ------------------------------------------------------------------
    def _collect_profiles(self) -> None:
        img = self._img_org
        ROW, COL = img.shape
        col_c = round(COL / 2)
        row_c = round(ROW / 2)

        self._y_colc = np.mean(img[:, col_c - 5 : col_c + 6], axis=1)
        self._y_rowc = np.mean(img[row_c - 5 : row_c + 6, :], axis=0)

    # ------------------------------------------------------------------
    #  Step 3: Change-point detection
    # ------------------------------------------------------------------
    def _detect_change_points(self) -> None:
        n = self.MAX_NUM_CHANGES
        cp_colc = self._detector.detect(self._y_colc, n)
        cp_rowc = self._detector.detect(self._y_rowc, n)

        self._cp_min_col = int(np.min(cp_colc))
        self._cp_max_col = int(np.max(cp_colc))
        self._cp_min_row = int(np.min(cp_rowc))
        self._cp_max_row = int(np.max(cp_rowc))

        self._img_roi = self._img_org[
            self._cp_min_col - 1 - 100 : self._cp_max_col - 1 + 101,
            self._cp_min_row - 1 - 100 : self._cp_max_row - 1 + 101,
        ]

    # ------------------------------------------------------------------
    #  Step 4: Corner extraction & edge finding
    # ------------------------------------------------------------------
    def _extract_corners_and_find_edges(self) -> None:
        CS = self.CORNER_SIZE
        roi = self._img_roi

        corners = {
            "tl": roi[:CS, :CS].copy(),
            "tr": roi[:CS, -CS:].copy(),
            "bl": roi[-CS:, :CS].copy(),
            "br": roi[-CS:, -CS:].copy(),
        }

        for k in corners:
            corners[k] = corners[k] / np.percentile(corners[k], 99) * 3500 * 16

        masks = {k: v > self.THRESHOLD for k, v in corners.items()}

        for k in corners:
            corners[k][~masks[k]] = 0

        half = round(self.MAX_NUM_CHANGES / 2)

        col_sums = {k: np.sum(masks[k], axis=0).astype(np.float64) for k in masks}
        row_sums = {k: np.sum(masks[k], axis=1).astype(np.float64) for k in masks}

        changeCol1 = {k: self._detector.detect(col_sums[k], half) for k in masks}
        changeRow1 = {k: self._detector.detect(row_sums[k], half) for k in masks}

        changeCol = {
            "tl": int(np.min(changeCol1["tl"])),
            "tr": int(np.max(changeCol1["tr"])),
            "bl": int(np.min(changeCol1["bl"])),
            "br": int(np.max(changeCol1["br"])),
        }
        changeRow = {
            "tl": int(np.min(changeRow1["tl"])),
            "tr": int(np.min(changeRow1["tr"])),
            "bl": int(np.max(changeRow1["bl"])),
            "br": int(np.max(changeRow1["br"])),
        }

        masks["tl"][:, : changeCol["tl"] - 1 - 2] = 0
        masks["tr"][:, changeCol["tr"] - 1 + 2 :] = 0
        masks["bl"][:, : changeCol["bl"] - 1 - 2] = 0
        masks["br"][:, changeCol["br"] - 1 + 2 :] = 0

        masks["tl"][: changeRow["tl"] - 1 - 2, :] = 0
        masks["tr"][: changeRow["tr"] - 1 - 2, :] = 0
        masks["bl"][changeRow["bl"] - 1 + 2 :, :] = 0
        masks["br"][changeRow["br"] - 1 + 2 :, :] = 0

        for k in masks:
            rows_k, cols_k = np.where(masks[k])
            if k in ("tl", "tr"):
                self._setRow[k] = int(np.min(rows_k)) + 1
            else:
                self._setRow[k] = int(np.max(rows_k)) + 1
            if k in ("tl", "bl"):
                self._setCol[k] = int(np.min(cols_k)) + 1
            else:
                self._setCol[k] = int(np.max(cols_k)) + 1

        self._ROW_PRE, self._COL_PRE = roi.shape[:2]

    # ------------------------------------------------------------------
    #  Step 5: Process a single target
    # ------------------------------------------------------------------
    def _process_target(self, tar_path: str) -> ROIResult:
        t0 = time.time()

        tar_image = os.path.basename(tar_path)
        tar_name = os.path.splitext(tar_image)[0]

        tar_org = np.array(PILImage.open(tar_path), dtype=np.float64)
        if tar_org.ndim > 2:
            tar_org = tar_org[:, :, 0]

        img_roi_tar = tar_org[
            self._cp_min_col - 1 - 100 : self._cp_max_col - 1 + 101,
            self._cp_min_row - 1 - 100 : self._cp_max_row - 1 + 101,
        ]

        src_pts = np.array(
            [
                [self._setCol["tl"], self._setRow["tl"]],
                [self._COL_PRE - 200 + self._setCol["tr"], self._setRow["tr"]],
                [
                    self._COL_PRE - 200 + self._setCol["br"],
                    self._ROW_PRE - 200 + self._setRow["br"],
                ],
                [self._setCol["bl"], self._ROW_PRE - 200 + self._setRow["bl"]],
            ],
            dtype=np.float32,
        )

        mask = self._poly2mask(
            src_pts[:, 0].astype(int),
            src_pts[:, 1].astype(int),
            img_roi_tar.shape[0],
            img_roi_tar.shape[1],
        )
        rows_m, cols_m = np.where(mask)
        y_min, y_max = rows_m.min(), rows_m.max()
        x_min, x_max = cols_m.min(), cols_m.max()

        cropped = img_roi_tar[y_min : y_max + 1, x_min : x_max + 1]
        ROW_CROP, COL_CROP = cropped.shape

        dst_pts = np.array(
            [[0, 0], [COL_CROP, 0], [COL_CROP, ROW_CROP], [0, ROW_CROP]],
            dtype=np.float32,
        )
        M = cv2.getPerspectiveTransform(src_pts, dst_pts)
        img_rect = cv2.warpPerspective(
            img_roi_tar, M, (COL_CROP, ROW_CROP), flags=cv2.INTER_LINEAR
        )

        img_resized = cv2.resize(
            img_rect,
            (self.COL_DISP, self.ROW_DISP),
            interpolation=cv2.INTER_LINEAR,
        )

        GRAY = self._parse_gray(tar_image)

        csv_r1 = self.ROW_DISP // 2 - 500
        csv_r2 = self.ROW_DISP // 2 + 501
        csv_c1 = self.COL_DISP // 2 - 500
        csv_c2 = self.COL_DISP // 2 + 501
        csv_ref = np.mean(img_resized[csv_r1:csv_r2, csv_c1:csv_c2])
        csv_norm = img_resized / csv_ref

        if GRAY == 32:
            np.savetxt(
                os.path.join(self.output_dir, f"{tar_name}.csv"),
                csv_norm * 5.2,
                delimiter=",",
                fmt="%.6g",
            )
        elif GRAY == 128:
            np.savetxt(
                os.path.join(self.output_dir, f"{tar_name}.csv"),
                csv_norm * 109.8,
                delimiter=",",
                fmt="%.6g",
            )

        img16_png = np.clip(img_resized * 24, 0, 65535).astype(np.uint16)
        PILImage.fromarray(img16_png).save(
            os.path.join(self.output_dir, f"{tar_name}.png")
        )
        img16_tif = np.clip(img_resized, 0, 65535).astype(np.uint16)
        PILImage.fromarray(img16_tif).save(
            os.path.join(self.output_dir, f"{tar_name}.tif")
        )

        elapsed = time.time() - t0
        print(f"{tar_image}: Simulation elapsed time: {elapsed:.4f} seconds")

        c5 = img_resized[
            self.ROW_DISP // 2 - 2 : self.ROW_DISP // 2 + 3,
            self.COL_DISP // 2 - 2 : self.COL_DISP // 2 + 3,
        ]
        return ROIResult(
            filename=tar_name,
            changePts_min_col=self._cp_min_col,
            changePts_max_col=self._cp_max_col,
            changePts_min_row=self._cp_min_row,
            changePts_max_row=self._cp_max_row,
            setRow_tl=self._setRow["tl"],
            setRow_tr=self._setRow["tr"],
            setRow_bl=self._setRow["bl"],
            setRow_br=self._setRow["br"],
            setCol_tl=self._setCol["tl"],
            setCol_tr=self._setCol["tr"],
            setCol_bl=self._setCol["bl"],
            setCol_br=self._setCol["br"],
            ROW_PRE=self._ROW_PRE,
            COL_PRE=self._COL_PRE,
            ROW_CROP=ROW_CROP,
            COL_CROP=COL_CROP,
            csv_ref_val=csv_ref,
            ref_val=self._ref_val,
            src_pts=src_pts,
            center_5x5=c5,
            elapsed=elapsed,
        )

    # ------------------------------------------------------------------
    #  Helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _poly2mask(
        x_coords: np.ndarray, y_coords: np.ndarray, rows: int, cols: int
    ) -> np.ndarray:
        pts = np.column_stack((x_coords, y_coords)).astype(np.int32)
        mask = np.zeros((rows, cols), dtype=np.uint8)
        cv2.fillPoly(mask, [pts], 1)
        return mask.astype(bool)

    @staticmethod
    def _parse_gray(filename: str) -> int:
        g1 = filename[1:3]
        g2 = filename[1:4]
        if g1 == "32":
            return 32
        elif g2 == "128":
            return 128
        return 0

    @staticmethod
    def save_values_txt(result: "ROIResult", filepath: str) -> None:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w") as f:
            for key in [
                "changePts_min_col", "changePts_max_col",
                "changePts_min_row", "changePts_max_row",
                "setRow_tl", "setRow_tr", "setRow_bl", "setRow_br",
                "setCol_tl", "setCol_tr", "setCol_bl", "setCol_br",
                "ROW_PRE", "COL_PRE", "ROW_CROP", "COL_CROP",
            ]:
                f.write(f"{key}={getattr(result, key)}\n")
            f.write(f"csv_ref_val={result.csv_ref_val:.6f}\n")
            f.write(f"ref_val={result.ref_val:.6f}\n")
            sp = result.src_pts
            f.write(
                f"src_pts={sp[0,0]:.1f},{sp[0,1]:.1f};"
                f"{sp[1,0]:.1f},{sp[1,1]:.1f};"
                f"{sp[2,0]:.1f},{sp[2,1]:.1f};"
                f"{sp[3,0]:.1f},{sp[3,1]:.1f}\n"
            )
            c5 = result.center_5x5
            rows_str = []
            for r in range(c5.shape[0]):
                rows_str.append(",".join(f"{c5[r, c]:.4f}" for c in range(c5.shape[1])))
            f.write(f"center_5x5={';'.join(rows_str)}\n")


# ======================================================================
#  Module-level convenience functions (matches DLL interface)
# ======================================================================
def ROI(roi_file_name: str, tar_file_name: str) -> int:
    """
    Process ROI images — equivalent to MATLAB's ROI(roi_file, tar_file).

    Output saved to 'out_ROI/' folder next to the ROI reference image.

    Parameters
    ----------
    roi_file_name : str
        Full path to ROI reference image (e.g. "C:/data/W_ROI.png")
    tar_file_name : str
        Full path to target image (e.g. "C:/data/W128.png")

    Returns
    -------
    int
        0 on success, -1 on error.
    """
    try:
        data_dir = os.path.dirname(roi_file_name) or "."
        roi_base = os.path.basename(roi_file_name)
        tar_base = os.path.basename(tar_file_name)
        out_dir = os.path.join(data_dir, "out_ROI")

        p = ROIProcessor(
            roi_base, tar_base, data_dir, out_dir,
            tar_files=[tar_file_name],
        )
        results = p.run()
        return 0 if results else -1
    except Exception as e:
        print(f"ROI ERROR: {e}", file=sys.stderr)
        return -1


def ROI_with_output(roi_file_name: str, tar_file_name: str, output_dir: str) -> int:
    """
    Process ROI images with explicit output directory.

    Parameters
    ----------
    roi_file_name : str
        Full path to ROI reference image.
    tar_file_name : str
        Full path to target image.
    output_dir : str
        Full path to output directory (created if needed).

    Returns
    -------
    int
        0 on success, -1 on error.
    """
    try:
        data_dir = os.path.dirname(roi_file_name) or "."
        roi_base = os.path.basename(roi_file_name)
        tar_base = os.path.basename(tar_file_name)

        p = ROIProcessor(
            roi_base, tar_base, data_dir, output_dir,
            tar_files=[tar_file_name],
        )
        results = p.run()
        return 0 if results else -1
    except Exception as e:
        print(f"ROI ERROR: {e}", file=sys.stderr)
        return -1


# ======================================================================
#  CLI entry point
# ======================================================================
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="ROI Image Processor")
    parser.add_argument("roi_file", help="Full path to ROI reference image")
    parser.add_argument("tar_file", help="Full path to target image")
    parser.add_argument("-o", "--output", default=None, help="Output directory")
    args = parser.parse_args()

    if args.output:
        ret = ROI_with_output(args.roi_file, args.tar_file, args.output)
    else:
        ret = ROI(args.roi_file, args.tar_file)

    sys.exit(ret)
