"""
Meta Reality Labs — Clay Light Mode Theme
Design inspired by clay.com — warm cream tones with high contrast

Color philosophy — warm light tones with clear layering:
  ┌──────────────────────────────────────────────────────────┐
  │  BG_DEEPEST   #FFFFFF  ← Header, status bar (pure white) │
  │  BG_PRIMARY   #FAF9F7  ← Main canvas (Warm Cream)        │
  │  BG_ELEVATED  #FFFFFF  ← Cards (Pure White)               │
  │  BG_INPUT     #FAF9F7  ← Input fields (Cream inset)       │
  │  BG_HOVER     #EEE9DF  ← Hover (Oat Light)                │
  │  BORDER       #DAD4C8  ← Card edges (Oat Border)          │
  └──────────────────────────────────────────────────────────┘

  Warm undertone (cream/oat) prevents the "sterile white" feel.
  Cards (white) float above the cream canvas for clear depth.

Typography scale (1.25 ratio):
  26 → 18 → 15 → 13 → 12
  ↑     ↑     ↑     ↑     ↑
  H1   H2  Section Body Small
"""


class Colors:
    # ── Layered backgrounds (warm light) ──
    BG_DEEPEST = "#FFFFFF"
    BG_PRIMARY = "#FAF9F7"
    BG_ELEVATED = "#FFFFFF"
    BG_INPUT = "#FAF9F7"
    BG_HOVER = "#EEE9DF"
    BG_ACTIVE = "#DAD4C8"

    # Aliases
    BG_DARKEST = BG_DEEPEST
    BG_DARK = BG_DEEPEST
    BG_SURFACE = BG_ELEVATED
    BG_CARD = BG_ELEVATED
    BG_CARD_HOVER = BG_HOVER

    # ── Accent — Clay Lemon Gold + Matcha ──
    ACCENT_PRIMARY = "#FBBD41"
    ACCENT_PRIMARY_HOVER = "#E8A930"
    ACCENT_PRIMARY_DIM = "#D49A28"
    ACCENT_PRIMARY_MUTED = "#FBBD4118"
    ACCENT_PRIMARY_GLOW = "#FBBD4130"

    # Legacy aliases (for backward compatibility)
    ACCENT_BLUE = "#FBBD41"
    ACCENT_BLUE_HOVER = "#E8A930"
    ACCENT_BLUE_DIM = "#D49A28"
    ACCENT_BLUE_MUTED = "#FBBD4118"
    ACCENT_BLUE_GLOW = "#FBBD4130"

    ACCENT_TEAL = "#078A52"
    ACCENT_PURPLE = "#3BD3FD"
    ACCENT_PURPLE_HOVER = "#2BC0E8"

    # ── Semantic colors ──
    SUCCESS = "#078A52"
    SUCCESS_DIM = "#84E7A5"
    WARNING = "#FBBD41"
    WARNING_DIM = "#D49A28"
    ERROR = "#FC7981"
    ERROR_DIM = "#E5545C"
    INFO = "#3BD3FD"

    # ── Text hierarchy (high contrast on light) ──
    TEXT_PRIMARY = "#000000"
    TEXT_SECONDARY = "#55534E"
    TEXT_MUTED = "#9F9B93"
    TEXT_FAINT = "#C4BAB0"
    TEXT_ACCENT = "#01418D"
    TEXT_ON_ACCENT = "#000000"

    # ── Borders — Clay Oat ──
    BORDER = "#DAD4C8"
    BORDER_CARD = "#EEE9DF"
    BORDER_SUBTLE = "#EEE9DF"
    BORDER_ACCENT = "#FBBD4140"
    BORDER_INPUT_FOCUS = "#FBBD41"

    # ── Buttons — Clay 4 variants ──
    BTN_PRIMARY = "#000000"
    BTN_PRIMARY_HOVER = "#333333"
    BTN_SECONDARY = "#FFFFFF"
    BTN_SECONDARY_HOVER = "#EEE9DF"
    BTN_DANGER = "#FC7981"
    BTN_DANGER_HOVER = "#E5545C"
    BTN_SUCCESS = "#078A52"
    BTN_SUCCESS_HOVER = "#84E7A5"

    # ── Tabs ──
    TAB_BG = "#FAF9F7"
    TAB_SELECTED = "#FBBD41"
    TAB_HOVER = "#EEE9DF"

    # ── Console ──
    CONSOLE_BG = "#FAF9F7"
    CONSOLE_BORDER = "#DAD4C8"
    CONSOLE_TEXT = "#078A52"


class Fonts:
    FAMILY = "Segoe UI"
    MONO = "Cascadia Code"
    MONO_FALLBACK = "Consolas"

    HEADER_SIZE = 26
    SUBHEADER_SIZE = 18
    SECTION_SIZE = 15
    TITLE_SIZE = 15
    BODY_SIZE = 13
    SMALL_SIZE = 12
    MONO_SIZE = 12


class Spacing:
    """8px grid — balanced for 1920×1080 @ 100-125% DPI."""
    PAD_XS = 4
    PAD_SM = 8
    PAD_MD = 14
    PAD_LG = 22
    PAD_XL = 28

    CARD_PAD = 18
    CARD_PAD_HEADER = 12
    SECTION_GAP = 14
    WIDGET_GAP = 6
    FORM_LABEL_GAP = 8

    CORNER_RADIUS = 16
    CORNER_RADIUS_SM = 12
    CORNER_RADIUS_LG = 20
    CORNER_RADIUS_INPUT = 10

    BORDER_WIDTH = 2
    BORDER_WIDTH_ACCENT = 2


class Heights:
    """Fixed-height elements — balanced for 1080p."""
    HEADER_BANNER = 64
    STATUS_BAR = 30
    CONSOLE_TOOLBAR = 38
    CONSOLE_TEXTBOX = 150
    BUTTON = 36
    INPUT = 34
    EDITOR_TOOLBAR = 42


APP_TITLE = "uOLED Mura Compensation Simulator"
APP_VERSION = "v1.0.3"
APP_SUBTITLE = "uOLED Mura Compensation Simulator"
