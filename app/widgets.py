"""
Reusable styled widgets — Meta Reality Labs Clay Light Mode Theme

Visual upgrade summary:
  • Cards: pure white (#FFFFFF) on warm cream canvas (#FAF9F7) with Oat border
  • Buttons: Clay Black primary, White secondary, 12px radius
  • Inputs: cream background (#FAF9F7) with Oat border, 10px radius
  • Typography: 15px bold section titles, 13px body, 12px hints
  • Header: white with Clay Black text + gold underline
  • Console: cream background (#FAF9F7) with Matcha green (#078A52) text
"""

import os
from typing import Callable, Optional, List

import customtkinter as ctk
from PIL import Image
from app.theme import Colors, Fonts, Spacing, Heights

# ── Asset paths ──────────────────────────────────────────────────────
ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")
LOGO_PATH = os.path.join(ASSETS_DIR, "meta_logo.png")
ICON_ICO = os.path.join(ASSETS_DIR, "meta_icon.ico")
ICON_PNG = os.path.join(ASSETS_DIR, "meta_icon.png")


# ═══════════════════════════════════════════════════════════════════
#  SECTION CARD — white card on cream canvas
# ═══════════════════════════════════════════════════════════════════
class SectionCard(ctk.CTkFrame):
    """
    Card component with white surface on cream canvas.
    Border uses Oat Light (#EEE9DF) with 2px width for clear separation.
    Accent stripe uses Clay Black (#000000).
    """

    def __init__(self, parent, title: str = "", icon: str = "", **kwargs):
        super().__init__(
            parent,
            fg_color=Colors.BG_ELEVATED,
            corner_radius=Spacing.CORNER_RADIUS,
            border_width=Spacing.BORDER_WIDTH,
            border_color=Colors.BORDER_CARD,
            **kwargs,
        )

        if title:
            header = ctk.CTkFrame(self, fg_color="transparent", height=36)
            header.pack(
                fill="x",
                padx=Spacing.CARD_PAD,
                pady=(Spacing.CARD_PAD, Spacing.CARD_PAD_HEADER),
            )
            header.pack_propagate(False)

            # Accent stripe — Clay Black
            ctk.CTkFrame(
                header, width=4, height=20,
                fg_color="#000000",
                corner_radius=2,
            ).pack(side="left", padx=(0, Spacing.PAD_SM + 2), pady=7)

            label_text = f"{icon}  {title}" if icon else title
            ctk.CTkLabel(
                header, text=label_text,
                font=ctk.CTkFont(
                    family=Fonts.FAMILY,
                    size=Fonts.SECTION_SIZE,
                    weight="bold",
                ),
                text_color=Colors.TEXT_PRIMARY,
            ).pack(side="left")

    def get_content_frame(self) -> ctk.CTkFrame:
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(
            fill="both", expand=True,
            padx=Spacing.CARD_PAD,
            pady=(0, Spacing.CARD_PAD),
        )
        return content


# ═══════════════════════════════════════════════════════════════════
#  ACCENT BUTTON — Clay 4 variants
# ═══════════════════════════════════════════════════════════════════
class AccentButton(ctk.CTkButton):
    """
    Styled button with 4 semantic variants (Clay style):
      primary   — Clay Black bg, white text
      secondary — White bg, Oat border, Clay Black text
      success   — Matcha bg, white text
      danger    — Pomegranate bg, white text
    """

    STYLES = {
        "primary": (Colors.BTN_PRIMARY, Colors.BTN_PRIMARY_HOVER),
        "secondary": (Colors.BTN_SECONDARY, Colors.BTN_SECONDARY_HOVER),
        "success": (Colors.BTN_SUCCESS, Colors.BTN_SUCCESS_HOVER),
        "danger": (Colors.BTN_DANGER, Colors.BTN_DANGER_HOVER),
    }

    _TEXT_COLORS = {
        "primary": "#FFFFFF",
        "secondary": "#000000",
        "success": "#FFFFFF",
        "danger": "#FFFFFF",
    }

    _BORDER_COLORS = {
        "primary": "#333333",
        "secondary": Colors.BORDER,
        "success": Colors.SUCCESS,
        "danger": Colors.ERROR_DIM,
    }

    def __init__(
        self, parent, text: str, style: str = "primary",
        icon: str = "", **kwargs,
    ):
        fg, hover = self.STYLES.get(style, self.STYLES["primary"])
        text_color = self._TEXT_COLORS.get(style, "#FFFFFF")
        border_color = self._BORDER_COLORS.get(style, Colors.BORDER)
        display_text = f"{icon}  {text}" if icon else text

        super().__init__(
            parent,
            text=display_text,
            fg_color=fg,
            hover_color=hover,
            text_color=text_color,
            border_color=border_color,
            border_width=1,
            font=ctk.CTkFont(
                family=Fonts.FAMILY, size=Fonts.BODY_SIZE, weight="bold",
            ),
            corner_radius=Spacing.CORNER_RADIUS_SM,
            height=Heights.BUTTON,
            **kwargs,
        )


# ═══════════════════════════════════════════════════════════════════
#  STYLED ENTRY — cream inset with Oat border
# ═══════════════════════════════════════════════════════════════════
class StyledEntry(ctk.CTkEntry):
    """
    Input field with cream background (#FAF9F7) inside white cards,
    creating a subtle inset appearance with Oat border.
    """

    def __init__(self, parent, **kwargs):
        super().__init__(
            parent,
            fg_color=Colors.BG_INPUT,
            border_color=Colors.BORDER,
            text_color=Colors.TEXT_PRIMARY,
            placeholder_text_color=Colors.TEXT_FAINT,
            font=ctk.CTkFont(family=Fonts.FAMILY, size=Fonts.BODY_SIZE),
            corner_radius=Spacing.CORNER_RADIUS_INPUT,
            border_width=Spacing.BORDER_WIDTH,
            height=Heights.INPUT,
            **kwargs,
        )

    def set_value(self, value: str):
        prev = self.cget("state")
        self.configure(state="normal")
        self.delete(0, "end")
        self.insert(0, value)
        self.configure(state=prev)


# ═══════════════════════════════════════════════════════════════════
#  STYLED COMBOBOX — cream + Oat border
# ═══════════════════════════════════════════════════════════════════
class StyledComboBox(ctk.CTkComboBox):
    """Dropdown with cream-input style and gold toggle button."""

    def __init__(
        self, parent,
        variable: Optional[ctk.StringVar] = None,
        values: Optional[List[str]] = None,
        **kwargs,
    ):
        super().__init__(
            parent,
            variable=variable,
            values=values or [],
            fg_color=Colors.BG_INPUT,
            border_color=Colors.BORDER,
            button_color="#55534E",
            button_hover_color="#9F9B93",
            dropdown_fg_color=Colors.BG_ELEVATED,
            dropdown_hover_color=Colors.BG_HOVER,
            text_color=Colors.TEXT_PRIMARY,
            font=ctk.CTkFont(family=Fonts.FAMILY, size=Fonts.BODY_SIZE),
            corner_radius=Spacing.CORNER_RADIUS_INPUT,
            height=Heights.INPUT,
            **kwargs,
        )


# ═══════════════════════════════════════════════════════════════════
#  STYLED LABEL — 4 visual tiers
# ═══════════════════════════════════════════════════════════════════
class StyledLabel(ctk.CTkLabel):
    """
    Label with clear visual hierarchy:
      title  — 15px bold, Clay Black     (card headings)
      body   — 13px normal, Warm Charcoal (descriptions)
      small  — 12px normal, Warm Silver   (hints, timestamps)
      accent — 13px bold, Blueberry 800   (links, file names)
    """

    _STYLES = {
        "body": (Fonts.BODY_SIZE, "normal", Colors.TEXT_SECONDARY),
        "title": (Fonts.SECTION_SIZE, "bold", Colors.TEXT_PRIMARY),
        "small": (Fonts.SMALL_SIZE, "normal", Colors.TEXT_MUTED),
        "accent": (Fonts.BODY_SIZE, "bold", Colors.TEXT_ACCENT),
    }

    def __init__(self, parent, text: str, style: str = "body", **kwargs):
        size, weight, color = self._STYLES.get(style, self._STYLES["body"])
        super().__init__(
            parent, text=text,
            font=ctk.CTkFont(family=Fonts.FAMILY, size=size, weight=weight),
            text_color=color,
            **kwargs,
        )


# ═══════════════════════════════════════════════════════════════════
#  FORM FIELD — label + widget + browse + hint + error
# ═══════════════════════════════════════════════════════════════════
class FormField(ctk.CTkFrame):
    """
    Reusable form row with proper spacing and inline validation.
    Label uses bold secondary text so it's visible but not dominant.
    """

    def __init__(
        self,
        parent,
        label: str = "",
        field_type: str = "entry",
        placeholder: str = "",
        default: str = "",
        readonly: bool = False,
        values: Optional[List[str]] = None,
        variable: Optional[ctk.StringVar] = None,
        on_change: Optional[Callable] = None,
        browse_command: Optional[Callable] = None,
        browse_text: str = "Browse",
        checkbox_text: str = "",
        checkbox_var: Optional[ctk.BooleanVar] = None,
        checkbox_command: Optional[Callable] = None,
        hint: str = "",
        validator: Optional[Callable] = None,
        **kwargs,
    ):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self.columnconfigure(1, weight=1)
        self._validator = validator
        self._error_label = None
        self.widget = None

        row = 0
        v_pad = Spacing.WIDGET_GAP

        # ── Label ──
        if label and field_type != "checkbox":
            ctk.CTkLabel(
                self, text=label,
                font=ctk.CTkFont(
                    family=Fonts.FAMILY,
                    size=Fonts.BODY_SIZE,
                    weight="bold",
                ),
                text_color=Colors.TEXT_SECONDARY,
                width=95,
                anchor="w",
            ).grid(
                row=row, column=0, sticky="w",
                padx=(0, Spacing.FORM_LABEL_GAP),
                pady=v_pad,
            )

        # ── Widget ──
        if field_type == "entry":
            self.widget = StyledEntry(self, placeholder_text=placeholder)
            if default:
                self.widget.insert(0, default)
            if readonly:
                self.widget.configure(state="disabled")
            self.widget.grid(
                row=row, column=1, sticky="ew",
                padx=(0, Spacing.PAD_SM if browse_command else 0),
                pady=v_pad,
            )

        elif field_type == "combo":
            self.widget = StyledComboBox(
                self, variable=variable,
                values=values or [], command=on_change,
            )
            self.widget.grid(
                row=row, column=1, sticky="ew",
                pady=v_pad,
            )

        elif field_type == "checkbox":
            if checkbox_var is None:
                checkbox_var = ctk.BooleanVar(value=False)
            self._checkbox_var = checkbox_var
            self.widget = ctk.CTkCheckBox(
                self,
                text=checkbox_text or label,
                variable=checkbox_var,
                command=checkbox_command,
                fg_color="#000000",
                hover_color="#333333",
                border_color=Colors.BORDER,
                checkmark_color="#FFFFFF",
                text_color=Colors.TEXT_PRIMARY,
                font=ctk.CTkFont(
                    family=Fonts.FAMILY, size=Fonts.BODY_SIZE,
                ),
                checkbox_height=20,
                checkbox_width=20,
                corner_radius=4,
            )
            self.widget.grid(
                row=row, column=0, columnspan=3, sticky="w",
                pady=v_pad,
            )

        # ── Browse button ──
        if browse_command and field_type == "entry":
            AccentButton(
                self, text=browse_text, style="secondary", width=75,
                command=browse_command,
            ).grid(row=row, column=2, pady=v_pad)

        # ── Hint ──
        if hint:
            row += 1
            ctk.CTkLabel(
                self, text=hint,
                font=ctk.CTkFont(family=Fonts.FAMILY, size=Fonts.SMALL_SIZE),
                text_color=Colors.TEXT_MUTED,
                anchor="w",
                justify="left",
                wraplength=500,
            ).grid(
                row=row, column=0, columnspan=3, sticky="w",
                pady=(0, 2),
            )

        # ── Error label (hidden) ──
        row += 1
        self._error_label = ctk.CTkLabel(
            self, text="",
            font=ctk.CTkFont(family=Fonts.FAMILY, size=Fonts.SMALL_SIZE),
            text_color=Colors.ERROR,
            anchor="w",
        )
        self._error_label.grid(
            row=row, column=0, columnspan=3, sticky="w",
        )
        self._error_label.grid_remove()

    # ── Public API ──

    def get(self) -> str:
        if isinstance(self.widget, ctk.CTkCheckBox):
            return str(self._checkbox_var.get())
        if isinstance(self.widget, StyledComboBox):
            return self.widget.get()
        if isinstance(self.widget, StyledEntry):
            return self.widget.get().strip()
        return ""

    def set_value(self, value: str):
        if isinstance(self.widget, StyledEntry):
            self.widget.set_value(value)
        elif isinstance(self.widget, StyledComboBox):
            self.widget.set(value)

    def set_state(self, state: str):
        if self.widget:
            self.widget.configure(state=state)

    def show_error(self, message: str):
        if self._error_label:
            self._error_label.configure(text=f"⚠  {message}")
            self._error_label.grid()
        if isinstance(self.widget, StyledEntry):
            self.widget.configure(border_color=Colors.ERROR)

    def clear_error(self):
        if self._error_label:
            self._error_label.grid_remove()
        if isinstance(self.widget, StyledEntry):
            self.widget.configure(border_color=Colors.BORDER)

    def validate(self) -> bool:
        self.clear_error()
        if self._validator:
            error = self._validator(self.get())
            if error:
                self.show_error(error)
                return False
        return True


# ═══════════════════════════════════════════════════════════════════
#  LOG CONSOLE — cream background + Matcha green text
# ═══════════════════════════════════════════════════════════════════
class LogConsole(ctk.CTkFrame):
    """Console panel with cream background and Matcha green text."""

    def __init__(
        self, parent,
        toolbar_buttons: Optional[List[dict]] = None,
        **kwargs,
    ):
        super().__init__(parent, fg_color="transparent", **kwargs)

        # ── Toolbar ──
        toolbar = ctk.CTkFrame(
            self, fg_color=Colors.BG_DEEPEST,
            height=Heights.CONSOLE_TOOLBAR, corner_radius=0,
        )
        toolbar.pack(fill="x")
        toolbar.pack_propagate(False)

        # Top divider — Oat border
        ctk.CTkFrame(
            toolbar, height=1, fg_color=Colors.BORDER, corner_radius=0,
        ).pack(fill="x", side="top")

        if toolbar_buttons:
            for btn_cfg in toolbar_buttons:
                AccentButton(
                    toolbar,
                    text=btn_cfg.get("text", ""),
                    style=btn_cfg.get("style", "secondary"),
                    icon=btn_cfg.get("icon", ""),
                    width=btn_cfg.get("width", 100),
                    command=btn_cfg.get("command"),
                ).pack(
                    side=btn_cfg.get("side", "left"),
                    padx=Spacing.PAD_XS,
                    pady=4,
                )

        ctk.CTkLabel(
            toolbar, text="CONSOLE",
            font=ctk.CTkFont(
                family=Fonts.FAMILY, size=Fonts.SMALL_SIZE, weight="bold",
            ),
            text_color=Colors.TEXT_MUTED,
        ).pack(side="left", padx=Spacing.PAD_MD)

        AccentButton(
            toolbar, text="Clear", style="danger", icon="🗑",
            width=75, command=self.clear,
        ).pack(side="right", padx=Spacing.PAD_SM, pady=4)

        # ── Text area ──
        self._textbox = ctk.CTkTextbox(
            self,
            fg_color=Colors.CONSOLE_BG,
            text_color=Colors.CONSOLE_TEXT,
            font=ctk.CTkFont(family=Fonts.MONO, size=Fonts.MONO_SIZE),
            border_width=1,
            border_color=Colors.CONSOLE_BORDER,
            corner_radius=0,
            height=Heights.CONSOLE_TEXTBOX,
            state="disabled",
        )
        self._textbox.pack(fill="both", expand=True)

    def write(self, text: str):
        self._textbox.configure(state="normal")
        self._textbox.insert("end", text)
        self._textbox.see("end")
        self._textbox.configure(state="disabled")

    def clear(self):
        self._textbox.configure(state="normal")
        self._textbox.delete("1.0", "end")
        self._textbox.configure(state="disabled")


# ═══════════════════════════════════════════════════════════════════
#  STATUS BAR — white bg + Warm Charcoal text
# ═══════════════════════════════════════════════════════════════════
class StatusBar(ctk.CTkFrame):
    """Bottom status bar with color-coded status dot (12px)."""

    _COLOR_MAP = {
        "ready": Colors.SUCCESS,
        "running": "#FBBD41",
        "warning": Colors.WARNING,
        "error": Colors.ERROR,
    }

    def __init__(self, parent, version: str = ""):
        super().__init__(
            parent, fg_color=Colors.BG_DEEPEST,
            height=Heights.STATUS_BAR, corner_radius=0,
        )
        self.pack_propagate(False)

        ctk.CTkFrame(
            self, height=1, fg_color=Colors.BORDER, corner_radius=0,
        ).pack(fill="x", side="top")

        self._dot = ctk.CTkLabel(
            self, text="●", font=ctk.CTkFont(size=12),
            text_color=Colors.SUCCESS, width=18,
        )
        self._dot.pack(side="left", padx=(Spacing.PAD_MD, 0))

        self._status_label = ctk.CTkLabel(
            self, text="Ready",
            font=ctk.CTkFont(family=Fonts.FAMILY, size=Fonts.SMALL_SIZE),
            text_color=Colors.TEXT_SECONDARY,
        )
        self._status_label.pack(side="left", padx=Spacing.PAD_XS)

        if version:
            ctk.CTkLabel(
                self, text=version,
                font=ctk.CTkFont(family=Fonts.FAMILY, size=Fonts.SMALL_SIZE),
                text_color=Colors.TEXT_MUTED,
            ).pack(side="right", padx=Spacing.PAD_MD)

    def set_status(self, text: str, status: str = "ready"):
        self._status_label.configure(text=text)
        self._dot.configure(
            text_color=self._COLOR_MAP.get(status, Colors.TEXT_MUTED),
        )


# ═══════════════════════════════════════════════════════════════════
#  HEADER BANNER — white bg + Clay Black text + gold underline
# ═══════════════════════════════════════════════════════════════════
class HeaderBanner(ctk.CTkFrame):
    """Branded header with Meta logo, title, subtitle, and gold accent underline."""

    def __init__(self, parent, title: str, subtitle: str):
        super().__init__(
            parent, fg_color=Colors.BG_DEEPEST,
            height=Heights.HEADER_BANNER, corner_radius=0,
        )
        self.pack_propagate(False)

        inner = ctk.CTkFrame(self, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=Spacing.PAD_XL)

        left = ctk.CTkFrame(inner, fg_color="transparent")
        left.pack(side="left", fill="y", pady=Spacing.PAD_SM)

        self._logo_image = None
        if os.path.exists(LOGO_PATH):
            try:
                img = Image.open(LOGO_PATH)
                img.thumbnail((130, 44), Image.Resampling.LANCZOS)
                self._logo_image = ctk.CTkImage(
                    light_image=img, dark_image=img, size=(130, 44),
                )
                ctk.CTkLabel(
                    left, image=self._logo_image, text="",
                ).pack(side="left", padx=(0, Spacing.PAD_LG))
            except Exception:
                self._add_fallback_logo(left)
        else:
            self._add_fallback_logo(left)

        text_frame = ctk.CTkFrame(left, fg_color="transparent")
        text_frame.pack(side="left", fill="y", anchor="center")

        ctk.CTkLabel(
            text_frame, text=title,
            font=ctk.CTkFont(
                family=Fonts.FAMILY,
                size=Fonts.SUBHEADER_SIZE,
                weight="bold",
            ),
            text_color=Colors.TEXT_PRIMARY,
            anchor="w",
        ).pack(anchor="w")

        ctk.CTkLabel(
            text_frame, text=subtitle,
            font=ctk.CTkFont(
                family=Fonts.FAMILY, size=Fonts.SMALL_SIZE,
            ),
            text_color=Colors.TEXT_MUTED,
            anchor="w",
        ).pack(anchor="w", pady=(2, 0))

        # Gold accent underline
        ctk.CTkFrame(
            self, height=2, fg_color="#FBBD41", corner_radius=0,
        ).pack(side="bottom", fill="x")

    def _add_fallback_logo(self, parent):
        logo_frame = ctk.CTkFrame(
            parent, width=40, height=40,
            fg_color="#FBBD41",
            corner_radius=Spacing.CORNER_RADIUS,
        )
        logo_frame.pack(side="left", padx=(0, Spacing.PAD_LG))
        logo_frame.pack_propagate(False)
        ctk.CTkLabel(
            logo_frame, text="◈",
            font=ctk.CTkFont(size=22),
            text_color="#000000",
        ).place(relx=0.5, rely=0.5, anchor="center")
