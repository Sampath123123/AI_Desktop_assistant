import platform

import streamlit as st
from gtts import gTTS
from playsound import playsound

try:
    import win32com.client
except ImportError:
    win32com = None


class SpeechService:
    def __init__(self, sounds_dir, enabled=True):
        self.sounds_dir = sounds_dir
        self.enabled = enabled

    def speak(self, text):
        if not self.enabled:
            return

        if win32com is not None and platform.system() == "Windows":
            speaker = win32com.client.Dispatch("SAPI.SpVoice")
            speaker.Speak(text)
            return

        try:
            output = gTTS(text=text, lang="en", slow=False)
            output_path = self.sounds_dir / "output.mp3"
            output.save(str(output_path))
            playsound(str(output_path))
        except Exception as exc:
            st.caption(f"Voice playback unavailable: {exc}")
