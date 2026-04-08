"""
Main GUI window for the Mura Compensation Simulator application.
Meta Reality Labs — Clay Light Mode Theme.

Auto-sizes to fit 1920×1080 displays at any DPI scaling (100%/125%/150%).
"""

import os

import customtkinter as ctk

from app.theme import Colors, APP_TITLE, APP_SUBTITLE, APP_VERSION
from app.widgets import HeaderBanner, StatusBar, LogConsole, ICON_ICO
from app.tabs.run_tab import RunTab
from app.tabs.editor_tab import EditorTab
from app.tabs.roi_tab import ROITab
from app.config import CONFIG_FILE


class DemuraGUI(ctk.CTk):
    """Main application window — DPI-aware sizing."""

    # Target: use 85% of screen width and height (leaves room for taskbar)
    SCREEN_RATIO_W = 0.55
    SCREEN_RATIO_H = 0.85
    # Absolute limits (prevents too-small or absurdly large windows)
    MIN_W, MIN_H = 800, 560
    MAX_W, MAX_H = 1400, 950

    def __init__(self):
        super().__init__()

        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        self.title(APP_TITLE)
        self.configure(fg_color=Colors.BG_PRIMARY)

        if os.path.exists(ICON_ICO):
            self.iconbitmap(ICON_ICO)

        # ── DPI-aware window sizing ──
        self._apply_dynamic_geometry()

        # ── Grid: header(0) | main(1) | statusbar(2) ──
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # ── Header ──
        header = HeaderBanner(self, title=APP_TITLE, subtitle=APP_SUBTITLE)
        header.grid(row=0, column=0, sticky="ew")

        # ── Main content (tabs + console) ──
        main_pane = ctk.CTkFrame(
            self, fg_color=Colors.BG_PRIMARY, corner_radius=0,
        )
        main_pane.grid(row=1, column=0, sticky="nsew")
        main_pane.grid_rowconfigure(0, weight=3)
        main_pane.grid_rowconfigure(1, weight=1)
        main_pane.grid_columnconfigure(0, weight=1)

        # ── Tab View ──
        self.tabs = ctk.CTkTabview(
            main_pane,
            fg_color=Colors.BG_PRIMARY,
            segmented_button_fg_color=Colors.TAB_BG,
            segmented_button_selected_color=Colors.TAB_SELECTED,
            segmented_button_selected_hover_color="#E8A930",
            segmented_button_unselected_color=Colors.TAB_BG,
            segmented_button_unselected_hover_color=Colors.TAB_HOVER,
            text_color=Colors.TEXT_PRIMARY,
            corner_radius=0,
        )
        self.tabs.grid(row=0, column=0, sticky="nsew")

        roi_frame = self.tabs.add("🎯  ROI Processing")
        run_frame = self.tabs.add("▶  Mura Compensation Simulator")
        config_frame = self.tabs.add("📄  Config File Setting")

        # ── Shared Console ──
        self.console = LogConsole(
            main_pane,
            toolbar_buttons=[
                {
                    "text": "Data Folder", "icon": "📂",
                    "style": "secondary", "width": 120,
                    "command": self._open_data_folder,
                },
                {
                    "text": "Output Folder", "icon": "📁",
                    "style": "secondary", "width": 130,
                    "command": self._open_output_folder,
                },
            ],
        )
        self.console.grid(row=1, column=0, sticky="nsew")

        # ── Status Bar ──
        self.status_bar = StatusBar(self, version=APP_VERSION)
        self.status_bar.grid(row=2, column=0, sticky="ew")

        # ── Build tabs ──
        self.run_tab = RunTab(
            run_frame,
            log_callback=self.console.write,
            status_bar=self.status_bar,
            on_mode_change=self._update_output_paths,
        )
        self.roi_tab = ROITab(
            roi_frame,
            log_callback=self.console.write,
            status_bar=self.status_bar,
            on_panel_change=self._on_roi_panel_change,
        )
        self.config_editor = EditorTab(
            config_frame,
            CONFIG_FILE,
            log_callback=self.console.write,
        )

        self.tabs.set("🎯  ROI Processing")

        # Set initial output paths now that all tabs are ready
        self._update_output_paths()

    def _apply_dynamic_geometry(self):
        """
        Calculate window size based on actual screen resolution.

        tkinter's winfo_screenwidth/height already return DPI-scaled values,
        so on a 1920×1080 screen at 125% scaling they return ~1536×864.
        We size relative to those values to always fit.
        """
        self.update_idletasks()

        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()

        win_w = int(screen_w * self.SCREEN_RATIO_W)
        win_h = int(screen_h * self.SCREEN_RATIO_H)

        win_w = max(self.MIN_W, min(win_w, self.MAX_W))
        win_h = max(self.MIN_H, min(win_h, self.MAX_H))

        # Center on screen
        x = (screen_w - win_w) // 2
        y = max(0, (screen_h - win_h) // 2 - 20)  # slight upward bias

        self.geometry(f"{win_w}x{win_h}+{x}+{y}")
        self.minsize(self.MIN_W, self.MIN_H)

    def _open_data_folder(self):
        self.run_tab.open_data_folder()

    def _open_output_folder(self):
        self.run_tab.open_output_folder()

    def _on_roi_panel_change(self, panel: str):
        """When ROI panel selection changes, update Run tab output paths."""
        if hasattr(self, 'run_tab') and hasattr(self, 'roi_tab'):
            self._update_output_paths()

    def _update_output_paths(self, _mode=None):
        """Update Run tab output paths based on current panel and mode."""
        if not hasattr(self, 'run_tab') or not hasattr(self, 'roi_tab'):
            return
        panel = self.roi_tab._panel_var.get()
        if not panel:
            return
        mode = self.run_tab._mode_var.get()
        mode_folder = "WhiteMode" if mode == "WHITE" else "RGBMode"
        panel_dir = os.path.join("./data", panel, mode_folder)
        self.run_tab.output_dir_field.set_value(os.path.join(panel_dir, "SW_out"))
        self.run_tab.output_dir2_field.set_value(os.path.join(panel_dir, "HW_out"))
        self.run_tab.data_dir_field.set_value("./data")
