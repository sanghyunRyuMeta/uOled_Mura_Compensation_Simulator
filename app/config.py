"""
Paths and constants for the Oona_Seeya Demura Distribution project.
"""

import os
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CONFIG_FILE = os.path.join(BASE_DIR, "config.json")
DATA_DIR = os.path.join(BASE_DIR, "data")
FILES_DIR = os.path.join(BASE_DIR, "files")

# INI file options available in files/
INI_FILES = {
    "RGBMode_1x1": os.path.join(FILES_DIR, "RGBMode_1x1.ini"),
    "RGBMode": os.path.join(FILES_DIR, "RGBMode.ini"),
    "WhiteMode_1x1": os.path.join(FILES_DIR, "WhiteMode_1x1.ini"),
    "WhiteMode": os.path.join(FILES_DIR, "WhiteMode.ini"),
}

# DLL files
META_DLL = os.path.join(FILES_DIR, "Meta_DMR.dll")
NVT_DLL = os.path.join(FILES_DIR, "NVTDemuraEncoderDLL.dll")
DEMLA_DLL = os.path.join(FILES_DIR, "demura_prepro.dll")

DEFAULT_MODE = "RGB"
MODES = ["RGB", "WHITE"]

DEMLA_SKIP = "(Skip DeMLA)"


def get_demla_dlls():
    """Scan files/ for available demura_prepro*.dll files + skip option."""
    dlls = []
    if os.path.isdir(FILES_DIR):
        for entry in sorted(os.listdir(FILES_DIR)):
            if entry.lower().startswith("demura_prepro") and entry.lower().endswith(".dll"):
                dlls.append(entry)
    dlls.append(DEMLA_SKIP)
    return dlls


def load_config():
    """Load config.json and return as dict."""
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)


def save_config(config: dict):
    """Save dict back to config.json."""
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)


def get_panels():
    """Scan data/ directory for available panel folders."""
    panels = []
    if os.path.isdir(DATA_DIR):
        for entry in sorted(os.listdir(DATA_DIR)):
            full = os.path.join(DATA_DIR, entry)
            if os.path.isdir(full):
                panels.append(entry)
    return panels


def get_ini_files():
    """Return list of available INI files in files/ directory."""
    found = {}
    if os.path.isdir(FILES_DIR):
        for entry in os.listdir(FILES_DIR):
            if entry.lower().endswith(".ini"):
                name = os.path.splitext(entry)[0]
                found[name] = os.path.join(FILES_DIR, entry)
    return found
