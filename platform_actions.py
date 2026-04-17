import datetime
import platform
import re
import shutil
import subprocess
import webbrowser
from urllib.parse import quote_plus

import cv2

try:
    import pyautogui
except Exception:
    pyautogui = None


def open_url(url):
    webbrowser.open(url)
    return True, f"Opened {url}."


def open_site_by_name(site_name):
    cleaned = site_name.strip().lower()
    cleaned = re.sub(r"^(the\s+)", "", cleaned)
    cleaned = cleaned.replace(" dot ", ".").replace(" ", "")
    cleaned = re.sub(r"[^a-z0-9\.\-]", "", cleaned)
    if not cleaned:
        return False, "Please provide a website name."

    if "." not in cleaned:
        cleaned = f"{cleaned}.com"

    url = f"https://{cleaned}"
    return open_url(url)


def search_google(query):
    webbrowser.open(f"https://www.google.com/search?q={quote_plus(query)}")
    return True, f"Searched for {query} in Google."


def search_wikipedia(query):
    webbrowser.open(f"https://en.wikipedia.org/wiki/{quote_plus(query.replace(' ', '_'))}")
    return True, f"Searched for {query} in Wikipedia."


def search_youtube(query):
    webbrowser.open(f"https://www.youtube.com/results?search_query={quote_plus(query)}")
    return True, f"Searched for {query} in YouTube."


def open_calculator():
    system = platform.system()
    if system == "Windows":
        subprocess.Popen(["calc.exe"])
        return True, "Opened Calculator."

    for command in ("gnome-calculator", "kcalc", "galculator", "xcalc"):
        if shutil.which(command):
            subprocess.Popen([command])
            return True, f"Opened Calculator using {command}."

    return False, "No calculator app was found on this machine."


def _run_first_available(commands):
    errors = []
    for command in commands:
        executable = command[0]
        if not shutil.which(executable):
            continue

        completed = subprocess.run(command, capture_output=True, text=True)
        if completed.returncode == 0:
            return True, ""

        details = (completed.stderr or completed.stdout).strip()
        if not details:
            details = f"exit code {completed.returncode}"
        errors.append(f"{executable}: {details}")

    if errors:
        return False, " | ".join(errors)
    return False, "No supported tools were found."


def _run_xrandr_brightness(delta):
    if not shutil.which("xrandr"):
        return False, "xrandr not found."

    query = subprocess.run(["xrandr", "--verbose"], capture_output=True, text=True)
    if query.returncode != 0:
        return False, (query.stderr or query.stdout or "xrandr query failed").strip()

    output_name = None
    current_brightness = None
    lines = query.stdout.splitlines()
    for index, line in enumerate(lines):
        if " connected" in line and output_name is None:
            output_name = line.split()[0]
            for next_line in lines[index + 1 : index + 20]:
                stripped = next_line.strip()
                if stripped.startswith("Brightness:"):
                    try:
                        current_brightness = float(stripped.split(":", 1)[1].strip())
                    except ValueError:
                        current_brightness = 1.0
                    break
            break

    if not output_name:
        return False, "No connected display output reported by xrandr."

    if current_brightness is None:
        current_brightness = 1.0

    next_brightness = max(0.2, min(1.0, current_brightness + delta))
    set_cmd = ["xrandr", "--output", output_name, "--brightness", f"{next_brightness:.2f}"]
    applied = subprocess.run(set_cmd, capture_output=True, text=True)
    if applied.returncode == 0:
        return True, ""
    return False, (applied.stderr or applied.stdout or "xrandr brightness set failed").strip()


def volume_up():
    system = platform.system()
    if system == "Linux":
        ok, details = _run_first_available(
            [
                ["wpctl", "set-volume", "@DEFAULT_AUDIO_SINK@", "5%+"],
                ["pactl", "set-sink-volume", "@DEFAULT_SINK@", "+5%"],
                ["pamixer", "-i", "5"],
                ["amixer", "-D", "pulse", "sset", "Master", "5%+"],
                ["amixer", "sset", "Master", "5%+"],
            ]
        )
        if ok:
            return True, "Volume increased."
        return False, (
            "Could not increase volume. "
            "Ensure you run from your desktop user session. "
            f"Details: {details}"
        )

    return False, f"Volume controls are not configured for {system}."


def volume_down():
    system = platform.system()
    if system == "Linux":
        ok, details = _run_first_available(
            [
                ["wpctl", "set-volume", "@DEFAULT_AUDIO_SINK@", "5%-"],
                ["pactl", "set-sink-volume", "@DEFAULT_SINK@", "-5%"],
                ["pamixer", "-d", "5"],
                ["amixer", "-D", "pulse", "sset", "Master", "5%-"],
                ["amixer", "sset", "Master", "5%-"],
            ]
        )
        if ok:
            return True, "Volume decreased."
        return False, (
            "Could not decrease volume. "
            "Ensure you run from your desktop user session. "
            f"Details: {details}"
        )

    return False, f"Volume controls are not configured for {system}."


def volume_mute():
    system = platform.system()
    if system == "Linux":
        ok, details = _run_first_available(
            [
                ["wpctl", "set-mute", "@DEFAULT_AUDIO_SINK@", "1"],
                ["pactl", "set-sink-mute", "@DEFAULT_SINK@", "1"],
                ["pamixer", "--mute"],
                ["amixer", "-D", "pulse", "set", "Master", "mute"],
                ["amixer", "set", "Master", "mute"],
            ]
        )
        if ok:
            return True, "Muted volume."
        return False, (
            "Could not mute volume. "
            "Ensure you run from your desktop user session. "
            f"Details: {details}"
        )

    return False, f"Mute is not configured for {system}."


def volume_unmute():
    system = platform.system()
    if system == "Linux":
        ok, details = _run_first_available(
            [
                ["wpctl", "set-mute", "@DEFAULT_AUDIO_SINK@", "0"],
                ["pactl", "set-sink-mute", "@DEFAULT_SINK@", "0"],
                ["pamixer", "--unmute"],
                ["amixer", "-D", "pulse", "set", "Master", "unmute"],
                ["amixer", "set", "Master", "unmute"],
            ]
        )
        if ok:
            return True, "Unmuted volume."
        return False, (
            "Could not unmute volume. "
            "Ensure you run from your desktop user session. "
            f"Details: {details}"
        )

    return False, f"Unmute is not configured for {system}."


def brightness_up():
    system = platform.system()
    if system == "Linux":
        ok, details = _run_first_available([["brightnessctl", "set", "+10%"]])
        if ok:
            return True, "Brightness increased."
        xrandr_ok, xrandr_details = _run_xrandr_brightness(0.1)
        if xrandr_ok:
            return True, "Brightness increased."
        return False, (
            "Could not increase brightness. "
            f"brightnessctl: {details} | xrandr: {xrandr_details}"
        )

    return False, f"Brightness controls are not configured for {system}."


def brightness_down():
    system = platform.system()
    if system == "Linux":
        ok, details = _run_first_available([["brightnessctl", "set", "10%-"]])
        if ok:
            return True, "Brightness decreased."
        xrandr_ok, xrandr_details = _run_xrandr_brightness(-0.1)
        if xrandr_ok:
            return True, "Brightness decreased."
        return False, (
            "Could not decrease brightness. "
            f"brightnessctl: {details} | xrandr: {xrandr_details}"
        )

    return False, f"Brightness controls are not configured for {system}."


def open_camera_preview():
    video = cv2.VideoCapture(0)
    if not video.isOpened():
        return False, "Camera access is unavailable."

    try:
        while True:
            ok, frame = video.read()
            if not ok:
                return False, "Failed to read from the camera."

            cv2.imshow("Camera Preview", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        video.release()
        cv2.destroyAllWindows()

    return True, "Closed the camera preview."


def take_screenshot(output_dir):
    if pyautogui is None:
        return False, "Screenshot support is unavailable in this environment."

    try:
        file_path = output_dir / f"screenshot-{datetime.datetime.now():%Y%m%d-%H%M%S}.png"
        pyautogui.screenshot().save(str(file_path))
        return True, f"Screenshot saved to {file_path}."
    except Exception as exc:
        return False, f"Unable to take a screenshot: {exc}"
