import datetime
from dataclasses import dataclass

from detector import ObjectDetector
from platform_actions import (
    brightness_down,
    brightness_up,
    open_calculator,
    open_camera_preview,
    open_site_by_name,
    open_url,
    search_google,
    search_wikipedia,
    search_youtube,
    take_screenshot,
    volume_down,
    volume_mute,
    volume_unmute,
    volume_up,
)


@dataclass
class CommandResult:
    message: str
    handled: bool = True


class CommandRouter:
    def __init__(self, settings):
        self.settings = settings
        self.detector = ObjectDetector(settings.model_path)

    @staticmethod
    def normalize(query):
        return query.lower().replace("command!", "").strip()

    def route(self, query, session_state):
        normalized = self.normalize(query)

        if "go offline" in normalized:
            return CommandResult("Going offline.")

        if "open youtube" in normalized:
            _, message = open_url("https://www.youtube.com")
            return CommandResult(message)

        if "open google" in normalized:
            _, message = open_url("https://www.google.com")
            return CommandResult(message)

        if "open wikipedia" in normalized:
            _, message = open_url("https://www.wikipedia.org")
            return CommandResult(message)

        if normalized.startswith("open "):
            site_name = normalized.replace("open ", "", 1).strip()
            if site_name and site_name not in {"camera", "calculator"}:
                _, message = open_site_by_name(site_name)
                return CommandResult(message)

        if "search" in normalized and "in google" in normalized:
            search_query = normalized.replace("search", "", 1).replace("in google", "", 1).strip()
            _, message = search_google(search_query)
            return CommandResult(message)

        if "search" in normalized and "in wikipedia" in normalized:
            search_query = normalized.replace("search", "", 1).replace("in wikipedia", "", 1).strip()
            _, message = search_wikipedia(search_query)
            return CommandResult(message)

        if "search" in normalized and "in youtube" in normalized:
            search_query = normalized.replace("search", "", 1).replace("in youtube", "", 1).strip()
            _, message = search_youtube(search_query)
            return CommandResult(message)

        if "the time" in normalized or "time" == normalized:
            now = datetime.datetime.now()
            return CommandResult(f"The time is {now.strftime('%H')} hours {now.strftime('%M')} minutes.")

        if "open calculator" in normalized:
            _, message = open_calculator()
            return CommandResult(message)

        if "open camera" in normalized:
            _, message = open_camera_preview()
            return CommandResult(message)

        if "take screenshot" in normalized:
            _, message = take_screenshot(self.settings.screenshots_dir)
            return CommandResult(message)

        if "volume up" in normalized or "increase volume" in normalized:
            _, message = volume_up()
            return CommandResult(message)

        if "volume down" in normalized or "decrease volume" in normalized:
            _, message = volume_down()
            return CommandResult(message)

        if "unmute" in normalized:
            _, message = volume_unmute()
            return CommandResult(message)

        if "mute" in normalized:
            _, message = volume_mute()
            return CommandResult(message)

        if "brightness up" in normalized or "increase brightness" in normalized:
            _, message = brightness_up()
            return CommandResult(message)

        if "brightness down" in normalized or "decrease brightness" in normalized:
            _, message = brightness_down()
            return CommandResult(message)

        if (
            "detect objects" in normalized
            or "see objects" in normalized
            or "what is in front of camera" in normalized
        ):
            _, labels, message = self.detector.detect_from_camera()
            session_state["detected_objects"] = labels
            return CommandResult(message)

        if "what objects detected" in normalized:
            labels = session_state.get("detected_objects", [])
            if labels:
                return CommandResult("I detected: " + ", ".join(labels) + ".")
            return CommandResult("I have not detected any objects yet.")

        return CommandResult("", handled=False)

    def infer_direct_command(self, query):
        normalized = self.normalize(query)
        direct_commands = {
            "go offline": "Command! Go Offline",
            "open camera": "Command! Open Camera",
            "open calculator": "Command! Open Calculator",
            "take screenshot": "Command! Take Screenshot",
            "detect objects": "Command! Detect Objects",
            "see objects": "Command! Detect Objects",
            "what is in front of camera": "Command! Detect Objects",
            "what objects detected": "Command! What Objects Detected",
            "open youtube": "Command! Open YouTube",
            "open google": "Command! Open Google",
            "open wikipedia": "Command! Open Wikipedia",
            "volume up": "Command! Volume Up",
            "increase volume": "Command! Volume Up",
            "volume down": "Command! Volume Down",
            "decrease volume": "Command! Volume Down",
            "mute": "Command! Mute",
            "unmute": "Command! Mute",
            "brightness up": "Command! Brightness Up",
            "increase brightness": "Command! Brightness Up",
            "brightness down": "Command! Brightness Down",
            "decrease brightness": "Command! Brightness Down",
            "time": "Command! The Time",
            "the time": "Command! The Time",
        }

        for phrase, command in direct_commands.items():
            if phrase in normalized:
                return command

        for platform_name in ("google", "wikipedia", "youtube"):
            marker = f"in {platform_name}"
            if "search" in normalized and marker in normalized:
                search_query = normalized.replace("search", "", 1).replace(marker, "", 1).strip()
                if search_query:
                    return f"Command! Search {search_query} in {platform_name.title()}"

        if normalized.startswith("open "):
            site_name = normalized.replace("open ", "", 1).strip()
            if site_name and site_name not in {"camera", "calculator"}:
                return f"Command! Open {site_name}"

        return None
