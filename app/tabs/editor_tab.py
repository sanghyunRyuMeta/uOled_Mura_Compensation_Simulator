"""
Editor Tab: view and edit config.json with a syntax-highlighted text area.
"""

import os
from typing import Callable, Optional

import customtkinter as ctk

from app.theme import Colors, Fonts, Spacing, Heights
from app.widgets import AccentButton, StyledLabel


class EditorTab(ctk.CTkFrame):
    """Config file editor with toolbar and monospace text area."""

    def __init__(
        self, parent,
        file_path: str,
        log_callback: Optional[Callable[[str], None]] = None,
    ):
        super().__init__(parent, fg_color="transparent")
        self.pack(fill="both", expand=True)

        self._file_path = file_path
        self._log = log_callback or (lambda _: None)
        self._modified = False

        self._build_ui()
        self._load_file()

    # ─── UI ──────────────────────────────────────────────────────────

    def _build_ui(self):
        # ── Toolbar ──
        toolbar = ctk.CTkFrame(
            self, fg_color=Colors.BG_DEEPEST,
            height=Heights.EDITOR_TOOLBAR, corner_radius=0,
        )
        toolbar.pack(fill="x")
        toolbar.pack_propagate(False)

        StyledLabel(
            toolbar,
            text=os.path.basename(self._file_path),
            style="accent",
        ).pack(side="left", padx=Spacing.PAD_MD)

        StyledLabel(
            toolbar,
            text=self._file_path,
            style="small",
        ).pack(side="left", padx=Spacing.PAD_SM)

        AccentButton(
            toolbar, text="Reload", style="secondary", icon="🔄",
            width=100, command=self._load_file,
        ).pack(side="right", padx=(Spacing.PAD_XS, Spacing.PAD_MD), pady=Spacing.PAD_XS)

        AccentButton(
            toolbar, text="Save", style="primary", icon="💾",
            width=90, command=self._save_file,
        ).pack(side="right", padx=Spacing.PAD_XS, pady=Spacing.PAD_XS)

        self._status_label = StyledLabel(toolbar, text="", style="small")
        self._status_label.pack(side="right", padx=Spacing.PAD_MD)

        # ── Text editor ──
        self._editor = ctk.CTkTextbox(
            self,
            fg_color=Colors.CONSOLE_BG,
            text_color=Colors.TEXT_PRIMARY,
            font=ctk.CTkFont(family=Fonts.MONO, size=Fonts.MONO_SIZE),
            border_width=0,
            corner_radius=0,
            wrap="none",
        )
        self._editor.pack(fill="both", expand=True)

        self._editor.bind("<Key>", self._on_key)

    # ─── File Operations ─────────────────────────────────────────────

    def _load_file(self):
        try:
            with open(self._file_path, "r", encoding="utf-8") as f:
                content = f.read()
            self._editor.delete("1.0", "end")
            self._editor.insert("1.0", content)
            self._modified = False
            self._status_label.configure(text="")
            self._log(f"[INFO] Loaded {os.path.basename(self._file_path)}\n")
        except Exception as e:
            self._log(f"[ERROR] Could not load {self._file_path}: {e}\n")

    def _save_file(self):
        try:
            content = self._editor.get("1.0", "end-1c")
            with open(self._file_path, "w", encoding="utf-8") as f:
                f.write(content)
            self._modified = False
            self._status_label.configure(text="Saved ✓")
            self._log(f"[INFO] Saved {os.path.basename(self._file_path)}\n")
        except Exception as e:
            self._log(f"[ERROR] Could not save {self._file_path}: {e}\n")

    def _on_key(self, _event):
        if not self._modified:
            self._modified = True
            self._status_label.configure(text="● Modified")
