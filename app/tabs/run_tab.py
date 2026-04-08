"""
Run Tab: primary control panel for the Mura Compensation pipeline.
Config parameters, data folder interaction, run controls.
"""

import os
from typing import Callable, Optional

import customtkinter as ctk
from tkinter import filedialog, messagebox

from app.theme import Colors, Spacing
from app.widgets import (
    SectionCard, AccentButton, FormField, StyledLabel, LogConsole,
)
from app.config import (
    load_config, save_config, get_panels, get_ini_files, get_demla_dlls,
    DATA_DIR, BASE_DIR, FILES_DIR, MODES, DEMLA_SKIP,
)
from app.simulator import DemuraSimulator


class RunTab(ctk.CTkFrame):
    """Builds and manages the Run Mura Compensation tab."""

    def __init__(
        self, parent,
        log_callback: Optional[Callable[[str], None]] = None,
        status_bar=None,
        on_mode_change: Optional[Callable[[str], None]] = None,
    ):
        super().__init__(parent, fg_color="transparent")
        self.pack(fill="both", expand=True)

        self._log = log_callback or (lambda _: None)
        self._status_bar = status_bar
        self._on_mode_change_cb = on_mode_change
        self._simulator = DemuraSimulator(BASE_DIR)

        self._build_ui()
        self._load_from_config()

    # ─── UI Construction ─────────────────────────────────────────────

    def _build_ui(self):
        scroll = ctk.CTkScrollableFrame(
            self, fg_color="transparent",
            scrollbar_button_color=Colors.BG_SURFACE,
        )
        scroll.pack(fill="both", expand=True, padx=Spacing.PAD_MD, pady=Spacing.PAD_MD)

        self._build_config_card(scroll)
        self._build_ini_card(scroll)
        self._build_paths_card(scroll)
        self._build_actions(scroll)

    def _build_config_card(self, parent):
        card = SectionCard(parent, title="Configuration", icon="⚙")
        card.pack(fill="x", pady=(0, Spacing.SECTION_GAP))
        content = card.get_content_frame()

        # Row 1: Panel + Mode
        row1 = ctk.CTkFrame(content, fg_color="transparent")
        row1.pack(fill="x")
        row1.columnconfigure(0, weight=1)
        row1.columnconfigure(1, weight=1)

        panels = get_panels()
        self._panel_var = ctk.StringVar(value=panels[0] if panels else "P1S1")
        self.panel_field = FormField(
            row1, label="Panel:", field_type="combo",
            values=panels or ["P1S1"], variable=self._panel_var,
        )
        self.panel_field.grid(row=0, column=0, sticky="ew", padx=(0, Spacing.PAD_SM))

        self._mode_var = ctk.StringVar(value="RGB")
        self.mode_field = FormField(
            row1, label="Mode:", field_type="combo",
            values=MODES, variable=self._mode_var,
            on_change=self._on_mode_change,
        )
        self.mode_field.grid(row=0, column=1, sticky="ew")

        # Row 2: DeMLA DLL selector
        demla_dlls = get_demla_dlls()
        self._demla_var = ctk.StringVar(value=demla_dlls[0] if demla_dlls else DEMLA_SKIP)
        self.demla_field = FormField(
            content, label="DeMLA:", field_type="combo",
            values=demla_dlls, variable=self._demla_var,
            hint="Select demura_prepro DLL for pre-processing, or skip DeMLA entirely.",
        )
        self.demla_field.pack(fill="x")

        # Data directory (read-only display)
        self.data_dir_field = FormField(
            content, label="Data Dir:", readonly=True,
        )
        self.data_dir_field.pack(fill="x")

    def _build_ini_card(self, parent):
        card = SectionCard(parent, title="INI Configuration", icon="📋")
        card.pack(fill="x", pady=(0, Spacing.SECTION_GAP))
        content = card.get_content_frame()

        ini_names = list(get_ini_files().keys()) or ["RGBMode_1x1"]
        self._ini_var = ctk.StringVar(value=ini_names[0])

        self.ini_field = FormField(
            content, label="INI File:", field_type="combo",
            values=ini_names, variable=self._ini_var,
            on_change=self._on_ini_change,
        )
        self.ini_field.pack(fill="x")

        self._ini_info = StyledLabel(content, text="", style="small")
        self._ini_info.pack(anchor="w", pady=(4, 0))
        self._update_ini_info()

    def _build_paths_card(self, parent):
        card = SectionCard(parent, title="Output Paths", icon="📁")
        card.pack(fill="x", pady=(0, Spacing.SECTION_GAP))
        content = card.get_content_frame()

        self.output_dir_field = FormField(
            content, label="Output Dir:",
            browse_command=lambda: self._browse_dir(self.output_dir_field),
        )
        self.output_dir_field.pack(fill="x")

        self.output_dir2_field = FormField(
            content, label="Output Dir 2:",
            browse_command=lambda: self._browse_dir(self.output_dir2_field),
        )
        self.output_dir2_field.pack(fill="x")

    def _build_actions(self, parent):
        card = SectionCard(parent, title="Pipeline Control", icon="▶")
        card.pack(fill="x", pady=(0, Spacing.SECTION_GAP))
        content = card.get_content_frame()

        btn_row = ctk.CTkFrame(content, fg_color="transparent")
        btn_row.pack(fill="x")

        self._run_btn = AccentButton(
            btn_row, text="Run Mura Compensation Pipeline", icon="▶",
            style="success", command=self._run_pipeline,
        )
        self._run_btn.pack(side="left", padx=(0, Spacing.PAD_SM))

        AccentButton(
            btn_row, text="Save Config", icon="💾",
            style="primary", command=self._save_current_config,
        ).pack(side="left", padx=(0, Spacing.PAD_SM))

        AccentButton(
            btn_row, text="Reload Config", icon="🔄",
            style="secondary", command=self._load_from_config,
        ).pack(side="left")

    # ─── Config Load / Save ──────────────────────────────────────────

    def _load_from_config(self):
        """Populate UI fields from config.json."""
        try:
            config = load_config()
        except Exception as e:
            self._log(f"[ERROR] Failed to load config: {e}\n")
            return

        self._panel_var.set(config.get("panel", "P1S1"))
        self._mode_var.set(config.get("mode", "RGB").upper())
        self.data_dir_field.set_value(config.get("data_dir", "./data"))

        ini_path = config.get("ini_file", "")
        ini_name = os.path.splitext(os.path.basename(ini_path))[0]
        if ini_name in get_ini_files():
            self._ini_var.set(ini_name)
        self._update_ini_info()

        self.output_dir_field.set_value(config.get("output_dir", ""))
        self.output_dir2_field.set_value(config.get("output_dir_2", ""))

        self._log("[INFO] Config loaded from config.json\n")

    def _save_current_config(self):
        """Save current UI values back to config.json."""
        ini_name = self._ini_var.get()

        demla_sel = self._demla_var.get()
        demla_path = "" if demla_sel == DEMLA_SKIP else f"./files/{demla_sel}"

        config = {
            "panel": self._panel_var.get(),
            "mode": self._mode_var.get(),
            "Meta_dll_path": "./files/Meta_DMR.dll",
            "NVTDLLPath": "./files/NVTDemuraEncoderDLL.dll",
            "deMLA": demla_path,
            "ini_file": f"./files/{ini_name}.ini",
            "source_dir": "./",
            "data_dir": "./data",
            "output_dir": self.output_dir_field.get(),
            "output_dir_2": self.output_dir2_field.get(),
        }
        try:
            save_config(config)
            self._log("[INFO] Config saved to config.json\n")
            if self._status_bar:
                self._status_bar.set_status("Config saved", "ready")
        except Exception as e:
            self._log(f"[ERROR] Failed to save config: {e}\n")

    def _build_config_dict(self) -> dict:
        """Build config dict from current UI values for the simulator."""
        ini_files = get_ini_files()
        ini_name = self._ini_var.get()

        demla_sel = self._demla_var.get()
        demla_path = "" if demla_sel == DEMLA_SKIP else os.path.join(FILES_DIR, demla_sel)

        return {
            "panel": self._panel_var.get(),
            "mode": self._mode_var.get(),
            "Meta_dll_path": os.path.join(BASE_DIR, "files", "Meta_DMR.dll"),
            "NVTDLLPath": os.path.join(BASE_DIR, "files", "NVTDemuraEncoderDLL.dll"),
            "deMLA": demla_path,
            "ini_file": ini_files.get(ini_name, ""),
            "source_dir": BASE_DIR,
            "data_dir": os.path.join(BASE_DIR, "data"),
            "output_dir": self.output_dir_field.get(),
            "output_dir_2": self.output_dir2_field.get(),
        }

    # ─── Pipeline Execution ──────────────────────────────────────────

    def _run_pipeline(self):
        """Validate, save config, and run the Mura Compensation pipeline."""
        self._save_current_config()

        panel = self._panel_var.get()
        panel_dir = os.path.join(DATA_DIR, panel)
        if not os.path.isdir(panel_dir):
            messagebox.showerror(
                "Panel Not Found", f"Panel folder not found:\n{panel_dir}",
            )
            return

        mode = self._mode_var.get()
        if mode == "WHITE":
            required = ["W32.csv", "W128.csv"]
        else:
            required = [
                f"{c}{g}.csv"
                for c in ["Red", "Green", "Blue"]
                for g in [32, 128]
            ]

        missing = [
            f for f in required
            if not os.path.isfile(os.path.join(panel_dir, f))
        ]
        if missing:
            messagebox.showerror(
                "Missing Data Files",
                f"Missing CSV files in {panel}:\n" + "\n".join(missing),
            )
            return

        if self._status_bar:
            self._status_bar.set_status("Running pipeline...", "running")
        self._run_btn.configure(state="disabled")
        self._log(
            f"\n{'='*50}\n"
            f"▶  Starting Mura Compensation Pipeline  ({mode} mode, panel={panel})\n"
            f"{'='*50}\n\n"
        )

        config = self._build_config_dict()
        self._simulator.run_pipeline(
            config,
            log_callback=lambda msg: self.after(0, self._log, msg),
            done_callback=lambda: self.after(0, self._on_done),
        )

    def _on_done(self):
        self._run_btn.configure(state="normal")
        if self._status_bar:
            self._status_bar.set_status("Pipeline finished", "ready")

    # ─── Helpers ─────────────────────────────────────────────────────

    def _on_mode_change(self, value):
        """Auto-select appropriate INI when mode changes."""
        ini_files = get_ini_files()
        prefix = "white" if value == "WHITE" else "rgb"
        candidates = [k for k in ini_files if k.lower().startswith(prefix)]
        if candidates:
            self._ini_var.set(candidates[0])
            self._update_ini_info()
        if self._on_mode_change_cb:
            self._on_mode_change_cb(value)

    def _on_ini_change(self, _value):
        self._update_ini_info()

    def _update_ini_info(self):
        """Show the full path of the selected INI."""
        ini_files = get_ini_files()
        path = ini_files.get(self._ini_var.get(), "")
        self._ini_info.configure(
            text=f"Path: {path}" if path else "INI file not found",
        )

    def _browse_dir(self, field: FormField):
        d = filedialog.askdirectory(initialdir=BASE_DIR)
        if d:
            field.set_value(d)

    def open_data_folder(self):
        """Open the data folder in the OS file explorer."""
        if os.path.isdir(DATA_DIR):
            os.startfile(DATA_DIR)
        else:
            messagebox.showwarning("Not Found", f"Data folder not found:\n{DATA_DIR}")

    def open_output_folder(self):
        """Open the current output folder in the OS file explorer."""
        out = self.output_dir_field.get()
        abs_out = out if os.path.isabs(out) else os.path.join(BASE_DIR, out)
        if os.path.isdir(abs_out):
            os.startfile(abs_out)
        else:
            messagebox.showwarning(
                "Not Found",
                f"Output folder not found:\n{abs_out}\n"
                "Run the pipeline first to create it.",
            )
