# Personal Desktop Assistant - AI

A voice-enabled desktop assistant with Streamlit UI, command routing, Gemini replies, and YOLOv8 object detection.

## Features

- Voice input with microphone (`speech_recognition`)
- Spoken responses (`gTTS` + `playsound`, Windows SAPI when available)
- Web commands (Google, YouTube, Wikipedia)
- Desktop utilities (calculator, screenshot, camera preview)
- YOLOv8 object detection from webcam

## Setup

1. Create and activate a virtual environment (recommended):

```bash
python3 -m venv env
source env/bin/activate
```

2. Install dependencies:

```bash
python -m pip install -r requirements.txt
```

3. Configure Gemini API key in one of these ways:
- `config.py` with `GENAI_API_KEY = "..."`, or
- environment variable `GENAI_API_KEY`, or
- Streamlit sidebar input field.

## Run

Use module execution to avoid broken launcher/shebang issues when folders are moved:

```bash
env/bin/python -m streamlit run assistant.py
```

Open the app at `http://localhost:8501`.

## Quick Smoke Test

```bash
env/bin/python test.py
```

## Example Commands

- "Open Camera"
- "Open Calculator"
- "Take Screenshot"
- "The Time"
- "Go Offline"
- "Search weather in Google"
- "Search python in Wikipedia"
- "Search lo-fi in YouTube"
- "Detect Objects"
- "What objects detected"
