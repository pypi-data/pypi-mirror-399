import subprocess
from pathlib import Path
from .license import check_geoexpress_installed, check_geoexpress_license

GE_ENCODE = r"C:\Program Files\LizardTech\GeoExpress\bin\mrsidgeoencoder.exe"

def encode_to_mrsid(input_tif: str, output_sid: str):
    # 🔒 LICENSE CHECK
    check_geoexpress_installed()
    check_geoexpress_license()

    cmd = [
        GE_ENCODE,
        "-i", input_tif,
        "-o", output_sid
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        raise RuntimeError(result.stderr)

    return output_sid
