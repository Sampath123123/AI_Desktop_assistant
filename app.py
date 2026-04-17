import speech_recognition as sr
import streamlit as st

from commands import CommandRouter
from llm import GeminiService
from settings import get_settings, resolve_gemini_api_key
from speech import SpeechService


def listen_for_speech():
    try:
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            recognizer.pause_threshold = 1
            audio = recognizer.listen(source)
        return recognizer.recognize_google(audio, language="en-in"), None
    except Exception as exc:
        return None, str(exc)


def add_message(role, text):
    st.session_state.conversation_log.append(f"{role}: {text}")


def display_message(role, text):
    st.write(f"{role}: {text}")


def respond(text, speech_service):
    display_message("AI", text)
    speech_service.speak(text)
    add_message("AI", text)


def handle_user_query(query, router, gemini, speech_service):
    add_message("You", query)
    display_message("You", query)

    direct_command = router.infer_direct_command(query)
    if direct_command:
        display_message("AI", direct_command)
        add_message("AI", direct_command)
        result = router.route(direct_command, st.session_state)
        if result.handled and result.message:
            respond(result.message, speech_service)
        return

    if gemini.is_configured():
        try:
            reply = gemini.generate_reply(query, st.session_state.conversation_log)
        except Exception as exc:
            reply = f"Gemini is unavailable right now: {exc}"
    else:
        reply = (
            "Gemini is not configured. Add a key in the sidebar, Streamlit secrets, "
            "or the GENAI_API_KEY environment variable."
        )

    if reply and "command!" in reply.lower():
        display_message("AI", reply)
        add_message("AI", reply)
        result = router.route(reply, st.session_state)
        if result.handled and result.message:
            respond(result.message, speech_service)
        return

    if reply:
        respond(reply, speech_service)


def render_sidebar():
    with st.sidebar:
        st.header("Assistant Settings")
        st.checkbox("Enable voice output", key="voice_enabled")
        st.text_input(
            "Gemini API Key",
            key="gemini_api_key",
            type="password",
            placeholder="Paste your Gemini API key here",
            help="This key is used for Gemini responses in this session.",
        )
        if resolve_gemini_api_key():
            st.caption("Gemini is configured.")
        else:
            st.caption("Gemini key not set. Built-in commands still work.")
        st.markdown("---")
        if st.button("Show History"):
            for item in st.session_state.conversation_log:
                st.write(item)


def initialize_state():
    if "conversation_log" not in st.session_state:
        st.session_state.conversation_log = []
    if "detected_objects" not in st.session_state:
        st.session_state.detected_objects = []
    if "voice_enabled" not in st.session_state:
        st.session_state.voice_enabled = True
    if "gemini_api_key" not in st.session_state:
        st.session_state.gemini_api_key = ""


def main():
    st.set_page_config(page_title="Desktop Assistant", page_icon="🤖", layout="wide")
    initialize_state()
    render_sidebar()

    settings = get_settings()
    router = CommandRouter(settings)
    gemini = GeminiService(settings.gemini_api_key)
    speech_service = SpeechService(settings.sounds_dir, enabled=st.session_state.voice_enabled)

    st.title("🤖 Desktop Assistant")
    st.write("Built for modular commands, cross-platform actions, and YOLO object detection.")
    st.caption("Use text or microphone. Press q in OpenCV windows to close camera previews.")

    with st.form("text-command-form", clear_on_submit=True):
        query = st.text_input("Type a command or question")
        send_clicked = st.form_submit_button("Send")

    if send_clicked and query.strip():
        handle_user_query(query.strip(), router, gemini, speech_service)

    if st.button("Use Microphone"):
        spoken_text, error = listen_for_speech()
        if spoken_text:
            handle_user_query(spoken_text, router, gemini, speech_service)
        else:
            st.error(f"Microphone input failed: {error}")
