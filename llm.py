import os
from dotenv import load_dotenv

load_dotenv()

DEFAULT_MODELS = {"anthropic": "claude-sonnet-5-5", "gemini": "gemini-2.5-flash", "ollama": "llama3.1"}

def _anthropic(system, user, model):
    from anthropic import Anthropic
    r = Anthropic().messages.create(model=model, max_tokens=4000, system=system,
                                    messages=[{"role": "user", "content": user}])
    return r.content[0].text

def _gemini(system, user, model):
    from google import genai
    from google.genai import types
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    r = client.models.generate_content(
        model=model, contents=user,
        config=types.GenerateContentConfig(system_instruction=system,
                                           response_mime_type="application/json"))
    return r.text

def _ollama(system, user, model):
    import ollama
    client = ollama.Client(host=os.getenv("OLLAMA_HOST", "http://localhost:11434"))
    r = client.chat(model=model, format="json",
                    options={"temperature": 0, "num_ctx": 16384},  # larger context for the profile JSON
                    messages=[{"role": "system", "content": system},
                              {"role": "user", "content": user}])
    return r["message"]["content"]

PROVIDERS = {"anthropic": _anthropic, "gemini": _gemini, "ollama": _ollama}

def complete(system: str, user: str, provider: str | None = None) -> str:
    provider = (provider or os.getenv("LLM_PROVIDER") or "anthropic").lower()
    if provider not in PROVIDERS:
        raise ValueError(f"Unknown provider '{provider}'. Choose from {list(PROVIDERS)}")
    model = os.getenv(f"{provider.upper()}_MODEL") or DEFAULT_MODELS[provider]
    return PROVIDERS[provider](system, user, model)