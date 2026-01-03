import os
from pathlib import Path

DEFAULT_GE_PATH = r"C:\Program Files\LizardTech\GeoExpress\bin"

def find_geoexpress_encoder() -> str:
    env_path = os.getenv("GEOEXPRESS_BIN")
    if env_path:
        exe = Path(env_path) / "mrsidgeoencoder.exe"
        if exe.exists():
            return str(exe)

    default = Path(DEFAULT_GE_PATH) / "mrsidgeoencoder.exe"
    if default.exists():
        return str(default)

    raise FileNotFoundError(
        "mrsidgeoencoder.exe not found. "
        "Install GeoExpress or set GEOEXPRESS_BIN env variable."
    )
