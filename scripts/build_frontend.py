import os
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PUBLIC_DIR = ROOT / "public"
DIST_DIR = ROOT / "dist"


def build_frontend():
    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)

    shutil.copytree(PUBLIC_DIR, DIST_DIR)

    api_base_url = os.environ.get("COURSE_MATCHER_API_BASE_URL", "").strip()
    config_js = "window.APP_CONFIG = {\n"
    config_js += f'  apiBaseUrl: "{api_base_url}",\n'
    config_js += "};\n"

    (DIST_DIR / "config.js").write_text(config_js, encoding="utf-8")


if __name__ == "__main__":
    build_frontend()
