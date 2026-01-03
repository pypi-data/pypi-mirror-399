import os
import subprocess
from pathlib import Path

GEOEXPRESS_BIN = r"C:\Program Files\LizardTech\GeoExpress\bin"

def check_geoexpress_installed():
    exe = Path(GEOEXPRESS_BIN) / "mrsidgeoencoder.exe"
    if not exe.exists():
        raise RuntimeError(
            "GeoExpress not found. Please install LizardTech GeoExpress."
        )

def check_geoexpress_license():
    """
    Run GeoExpress binary with --help or --version.
    Licensed installs return 0.
    Unlicensed installs return non-zero or error text.
    """
    exe = Path(GEOEXPRESS_BIN) / "mrsidgeoencoder.exe"

    result = subprocess.run(
        [str(exe), "--help"],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        raise RuntimeError(
            "GeoExpress license not found or expired.\n"
            "Please activate a valid GeoExpress license."
        )
