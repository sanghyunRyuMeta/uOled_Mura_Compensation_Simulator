"""
ROI Tab: Region-of-Interest extraction from raw captured images.
Calls roi_dll.dll via a subprocess wrapper (roi_run.py) using Python 3.12.

The wrapper processes each target through the DLL, outputs to a temp
directory, then copies only .png and .csv to the panel folder — the
original input .tif files are never overwritten.
"""

import os
import subprocess
import threading
from typing import Callable, Optional

import customtkinter as ctk
from tkinter import messagebox

from app.theme import Colors, Spacing
from app.widgets import SectionCard, AccentButton, FormField, StyledLabel
from app.config import DATA_DIR, BASE_DIR

ROI_WRAPPER = os.path.join(BASE_DIR, "ROI", "roi_run.py")
PYTHON312 = r"C:\Users\sanghyunryu\AppData\Local\Programs\Python\Python312\python.exe"


class ROITab(ctk.CTkFrame):
    """Builds and manages the ROI Processing tab."""

    ROI_REF_PREFIX = "W_ROI"
    TARGET_PREFIXES = ["W32", "W128"]
    SUPPORTED_EXT = (".tif", ".tiff")

    def __init__(
        self,
        parent,
        log_callback: Optional[Callable[[str], None]] = None,
        status_bar=None,
        on_panel_change: Optional[Callable[[str], None]] = None,
    ):
        super().__init__(parent, fg_color="transparent")
        self.pack(fill="both", expand=True)

        self._log = log_callback or (lambda _: None)
        self._status_bar = status_bar
        self._on_panel_change = on_panel_change
        self._running = False

        self._build_ui()
        self._scan_panel()

    # ─── UI Construction ─────────────────────────────────────────────

    def _build_ui(self):
        scroll = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_button_color=Colors.BG_SURFACE,
        )
        scroll.pack(
            fill="both", expand=True,
            padx=Spacing.PAD_MD, pady=Spacing.PAD_MD,
        )

        self._build_panel_card(scroll)
        self._build_files_card(scroll)
        self._build_actions(scroll)

    def _build_panel_card(self, parent):
        card = SectionCard(parent, title="Panel Selection", icon="📂")
        card.pack(fill="x", pady=(0, Spacing.SECTION_GAP))
        content = card.get_content_frame()

        panels = self._get_panels()
        self._panel_var = ctk.StringVar(
            value=panels[0] if panels else "",
        )
        self.panel_field = FormField(
            content,
            label="Panel:",
            field_type="combo",
            values=panels or ["(no panels found)"],
            variable=self._panel_var,
            on_change=lambda _: self._scan_panel(),
            hint="Select a panel folder inside data/. "
                 "It must contain W_ROI + target images (W32, W128).",
        )
        self.panel_field.pack(fill="x")

    def _build_files_card(self, parent):
        card = SectionCard(parent, title="Detected Files", icon="🔍")
        card.pack(fill="x", pady=(0, Spacing.SECTION_GAP))
        content = card.get_content_frame()

        self._roi_file_label = StyledLabel(content, text="ROI Reference:  —", style="body")
        self._roi_file_label.pack(anchor="w", pady=(0, Spacing.WIDGET_GAP))

        self._target_label = StyledLabel(content, text="Targets:  —", style="body")
        self._target_label.pack(anchor="w", pady=(0, Spacing.WIDGET_GAP))

        self._output_label = StyledLabel(content, text="Output to:  —", style="small")
        self._output_label.pack(anchor="w")

    def _build_actions(self, parent):
        card = SectionCard(parent, title="ROI Processing", icon="🎯")
        card.pack(fill="x", pady=(0, Spacing.SECTION_GAP))
        content = card.get_content_frame()

        btn_row = ctk.CTkFrame(content, fg_color="transparent")
        btn_row.pack(fill="x")

        self._run_btn = AccentButton(
            btn_row,
            text="Run ROI Processing",
            icon="▶",
            style="success",
            command=self._run_roi,
        )
        self._run_btn.pack(side="left", padx=(0, Spacing.PAD_SM))

        AccentButton(
            btn_row,
            text="Refresh Files",
            icon="🔄",
            style="secondary",
            command=self._scan_panel,
        ).pack(side="left", padx=(0, Spacing.PAD_SM))

        AccentButton(
            btn_row,
            text="Open Folder",
            icon="📁",
            style="secondary",
            command=self._open_panel_folder,
        ).pack(side="left")

    # ─── File Scanning ───────────────────────────────────────────────

    def _get_panels(self) -> list[str]:
        panels = []
        if os.path.isdir(DATA_DIR):
            for entry in sorted(os.listdir(DATA_DIR)):
                full = os.path.join(DATA_DIR, entry)
                if os.path.isdir(full):
                    panels.append(entry)
        return panels

    def _get_panel_dir(self) -> str:
        return os.path.join(DATA_DIR, self._panel_var.get())

    def _scan_panel(self):
        """Scan the selected panel folder for ROI reference and target images."""
        panel_dir = self._get_panel_dir()
        if not os.path.isdir(panel_dir):
            self._roi_file_label.configure(text="ROI Reference:  ❌ Panel folder not found")
            self._target_label.configure(text="Targets:  —")
            self._output_label.configure(text="Output to:  —")
            return

        # Find ROI reference (.tif only)
        self._roi_path = None
        for ext in self.SUPPORTED_EXT:
            candidate = os.path.join(panel_dir, f"{self.ROI_REF_PREFIX}{ext}")
            if os.path.isfile(candidate):
                self._roi_path = candidate
                break

        if self._roi_path:
            self._roi_file_label.configure(
                text=f"ROI Reference:  ✅  {os.path.basename(self._roi_path)}",
            )
        else:
            self._roi_file_label.configure(text="ROI Reference:  ❌ W_ROI image not found")

        # Find target files (.tif only)
        self._target_paths = []
        for prefix in self.TARGET_PREFIXES:
            for ext in self.SUPPORTED_EXT:
                candidate = os.path.join(panel_dir, f"{prefix}{ext}")
                if os.path.isfile(candidate):
                    self._target_paths.append(candidate)
                    break

        if self._target_paths:
            names = ", ".join(os.path.basename(p) for p in self._target_paths)
            self._target_label.configure(text=f"Targets:  ✅  {names}")
        else:
            self._target_label.configure(text="Targets:  ❌ No W32/W128 images found")

        self._output_label.configure(text=f"Output to:  {panel_dir}")

        # Notify GUI to update Run tab output paths
        panel = self._panel_var.get()
        if self._on_panel_change and panel:
            self._on_panel_change(panel)

    # ─── ROI Execution ───────────────────────────────────────────────

    def _run_roi(self):
        """Validate inputs and run ROI processing in a background thread."""
        if self._running:
            return

        if not self._roi_path or not os.path.isfile(self._roi_path):
            messagebox.showerror(
                "ROI Reference Missing",
                "No W_ROI image found in the selected panel folder.",
            )
            return

        if not self._target_paths:
            messagebox.showerror(
                "No Targets",
                "No target images (W32, W128) found in the selected panel folder.",
            )
            return

        if not os.path.isfile(PYTHON312):
            messagebox.showerror(
                "Python 3.12 Not Found",
                f"Python 3.12 not found at:\n{PYTHON312}\n\n"
                "roi_dll.dll requires Python 3.12.",
            )
            return

        self._running = True
        self._run_btn.configure(state="disabled")
        if self._status_bar:
            self._status_bar.set_status("Running ROI processing...", "running")

        panel = self._panel_var.get()
        output_dir = self._get_panel_dir()

        self._log(
            f"\n{'='*50}\n"
            f"🎯  Starting ROI Processing  (panel={panel})\n"
            f"{'='*50}\n\n"
        )
        self._log(f"[INFO] ROI reference: {os.path.basename(self._roi_path)}\n")
        self._log(f"[INFO] Output folder: {output_dir}\n")

        thread = threading.Thread(
            target=self._run_roi_thread,
            args=(self._roi_path, list(self._target_paths), output_dir),
            daemon=True,
        )
        thread.start()

    def _run_roi_thread(self, roi_path: str, target_paths: list[str], output_dir: str):
        """Background thread: call roi_dll.dll via roi_run.py subprocess."""
        success_count = 0
        total = len(target_paths)

        for i, tar_path in enumerate(target_paths, 1):
            tar_name = os.path.basename(tar_path)
            base = os.path.splitext(tar_name)[0]
            self.after(0, self._log, f"\n[{i}/{total}] Processing {tar_name}...\n")

            cmd = [PYTHON312, ROI_WRAPPER, roi_path, tar_path, "-o", output_dir]

            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=300,
                )

                if result.stdout.strip():
                    for line in result.stdout.strip().splitlines():
                        self.after(0, self._log, f"  {line}\n")

                if result.returncode == 0:
                    success_count += 1
                    self.after(0, self._log,
                               f"  ✅ {tar_name} → {base}.png, {base}.csv\n")
                else:
                    err = result.stderr.strip() if result.stderr else "unknown error"
                    self.after(0, self._log,
                               f"  ❌ {tar_name} failed (exit code {result.returncode})\n"
                               f"  {err}\n")
            except subprocess.TimeoutExpired:
                self.after(0, self._log, f"  ❌ {tar_name} timed out (300s)\n")
            except Exception as e:
                self.after(0, self._log, f"  ❌ {tar_name} error: {e}\n")

        self.after(0, self._log,
                   f"\n{'='*50}\n"
                   f"ROI Processing Complete: {success_count}/{total} succeeded\n"
                   f"{'='*50}\n\n")
        self.after(0, self._on_done, success_count == total)

    def _on_done(self, success: bool = True):
        self._running = False
        self._run_btn.configure(state="normal")
        if self._status_bar:
            if success:
                self._status_bar.set_status("ROI processing finished", "ready")
            else:
                self._status_bar.set_status("ROI processing finished with errors", "warning")

    # ─── Helpers ─────────────────────────────────────────────────────

    def _open_panel_folder(self):
        panel_dir = self._get_panel_dir()
        if os.path.isdir(panel_dir):
            os.startfile(panel_dir)
        else:
            messagebox.showwarning(
                "Not Found",
                f"Panel folder not found:\n{panel_dir}",
            )
