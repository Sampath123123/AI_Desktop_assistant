import os
from dataclasses import dataclass
from pathlib import Path

import streamlit as st

try:
    from config import GENAI_API_KEY as CONFIG_GENAI_API_KEY
except Exception:
    CONFIG_GENAI_API_KEY = ""


APP_ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = APP_ROOT / "output"
SCREENSHOTS_DIR = APP_ROOT / "screenshots"
SOUNDS_DIR = APP_ROOT / "sounds"
MODEL_PATH = APP_ROOT / "yolov8n.pt"


@dataclass(frozen=True)
class AppSettings:
    app_root: Path
    output_dir: Path
    screenshots_dir: Path
    sounds_dir: Path
    model_path: Path
    gemini_api_key: str


def ensure_runtime_dirs():
    OUTPUT_DIR.mkdir(exist_ok=True)
    SCREENSHOTS_DIR.mkdir(exist_ok=True)
    SOUNDS_DIR.mkdir(exist_ok=True)


def resolve_gemini_api_key():
    session_key = st.session_state.get("gemini_api_key", "").strip()
    if session_key:
        return session_key

    try:
        secret_key = str(st.secrets.get("GENAI_API_KEY", "")).strip()
        if secret_key:
            return secret_key
    except Exception:
        pass

    env_key = os.getenv("GENAI_API_KEY", "").strip()
    if env_key:
        return env_key

    return CONFIG_GENAI_API_KEY.strip()


def get_settings():
    ensure_runtime_dirs()
    return AppSettings(
        app_root=APP_ROOT,
        output_dir=OUTPUT_DIR,
        screenshots_dir=SCREENSHOTS_DIR,
        sounds_dir=SOUNDS_DIR,
        model_path=MODEL_PATH,
        gemini_api_key=resolve_gemini_api_key(),
    )
