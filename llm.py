import google.generativeai as genai


SYSTEM_PROMPT = (
    "You are a personal desktop assistant. "
    "When the user is asking to open apps, search websites, take a screenshot, "
    "open the camera, detect objects, or tell time, respond with a concise command "
    "formatted as 'Command! ...'. "
    "For normal conversation, answer naturally and briefly."
)

PREFERRED_MODELS = (
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-1.5-flash",
    "gemini-1.5-flash-8b",
)


class GeminiService:
    def __init__(self, api_key, model_name=None):
        self.api_key = api_key.strip()
        self.model_name = model_name
        self._resolved_model_name = None

    def is_configured(self):
        return bool(self.api_key)

    @staticmethod
    def _normalize_model_name(name):
        return name.split("/", 1)[1] if name.startswith("models/") else name

    def _list_supported_models(self):
        supported_models = []
        for model in genai.list_models():
            methods = getattr(model, "supported_generation_methods", []) or []
            if "generateContent" not in methods:
                continue

            normalized_name = self._normalize_model_name(model.name)
            supported_models.append(normalized_name)
        return supported_models

    def _resolve_model_name(self):
        if self._resolved_model_name:
            return self._resolved_model_name

        configured_name = (self.model_name or "").strip()
        if configured_name:
            self._resolved_model_name = configured_name
            return self._resolved_model_name

        supported_models = self._list_supported_models()

        for preferred_name in PREFERRED_MODELS:
            if preferred_name in supported_models:
                self._resolved_model_name = preferred_name
                return self._resolved_model_name

        for candidate_name in supported_models:
            if "flash" in candidate_name:
                self._resolved_model_name = candidate_name
                return self._resolved_model_name

        if supported_models:
            self._resolved_model_name = supported_models[0]
            return self._resolved_model_name

        raise RuntimeError("No Gemini models with generateContent support were returned for this API key.")

    def generate_reply(self, user_query, conversation_log):
        if not self.api_key:
            return None

        genai.configure(api_key=self.api_key)
        prompt = SYSTEM_PROMPT + "\n\n" + "\n".join(conversation_log)

        candidate_models = []
        resolved_name = self._resolve_model_name()
        if resolved_name:
            candidate_models.append(resolved_name)

        supported_models = self._list_supported_models()
        for model_name in supported_models:
            if model_name not in candidate_models:
                candidate_models.append(model_name)

        for preferred_name in PREFERRED_MODELS:
            if preferred_name not in candidate_models:
                candidate_models.append(preferred_name)

        last_error = None
        for model_name in candidate_models:
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(prompt)
                self._resolved_model_name = model_name
                return str(response.text).strip().replace("AI: ", "").strip()
            except Exception as exc:
                last_error = exc

        available_hint = ", ".join(supported_models[:8]) if supported_models else "none returned"
        raise RuntimeError(
            "Gemini request failed for all candidate models. "
            f"Last error: {last_error}. "
            f"Models returned by ListModels: {available_hint}"
        )
