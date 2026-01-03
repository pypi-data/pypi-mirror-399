import subprocess

def check_geoexpress_license(encoder_path: str):
    """
    Verifies GeoExpress installation and license availability.
    Does NOT bypass licensing.
    """
    try:
        result = subprocess.run(
            [encoder_path, "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode != 0:
            raise RuntimeError(result.stderr)

        return True

    except Exception:
        raise RuntimeError(
            "GeoExpress is not licensed or not installed.\n"
            "Please install LizardTech GeoExpress and activate a valid license."
        )
