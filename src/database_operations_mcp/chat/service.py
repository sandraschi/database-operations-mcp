# database_operations_mcp/chat/service.py
"""Chat service for database-operations-mcp backend."""

import json as _json
import logging
import os
import urllib.request as _req
from typing import Any

from .memory import ChatMemory

logger = logging.getLogger(__name__)


class ChatService:
    """Encapsulates chat handling, provider dispatch and persistent memory.

    The service is instantiated once at application start-up and reused for all
    incoming ``/api/chat`` requests.
    """

    def __init__(self, db_path: str = "chat_memory.db", limit: int = 40):
        # Store in user app data directory or fallback to local
        local_app_data = os.environ.get("LOCALAPPDATA") or os.environ.get("APPDATA") or "."
        mcp_dir = os.path.join(local_app_data, "database-operations-mcp")
        try:
            os.makedirs(mcp_dir, exist_ok=True)
            self.db_path = os.path.join(mcp_dir, db_path)
        except Exception:
            self.db_path = db_path

        self.memory = ChatMemory(db_path=self.db_path, limit=limit)
        self._settings_cache: dict[str, Any] | None = None
        self._provider_order = ["lmstudio", "deepseek", "openai", "anthropic", "ollama"]

    # ---------------------------------------------------------------------
    # Private helpers
    # ---------------------------------------------------------------------
    def _load_settings(self) -> dict[str, Any]:
        if self._settings_cache is None:
            self._settings_cache = self._load_llm_settings()
        return self._settings_cache

    def _load_llm_settings(self) -> dict[str, Any]:
        return {"endpoint": os.environ.get("OLLAMA_HOST", "http://localhost:11434"), "model": "gemma4:e4b"}

    def _build_system_prompt(self, personality: str | None) -> str:
        base = "You are the SOTA Database Operations Assistant. You help manage databases, schemas, queries, and connection pools for the MCP Fleet."
        personality_instructions = {
            "professional": "",
            "pirate": "You speak like a pirate captain, using nautical terms and database analogies.",
            "sarcastic": "You respond with dry sarcasm and witty remarks about database administration.",
            "mentor": "You act as a supportive database mentor, explaining queries patiently and encouraging the user.",
        }
        instr = personality_instructions.get(personality or "professional", "")
        if instr:
            base += f"\n\n{instr}"

        # Load optional skill content (database-expert) if present.
        try:
            skills_dir = self._get_skills_dir()
            if skills_dir:
                expert_path = os.path.join(skills_dir, "database-expert", "SKILL.md")
                if os.path.isfile(expert_path):
                    with open(expert_path, encoding="utf-8") as f:
                        skill_content = f.read()
                    if skill_content.startswith("---"):
                        end = skill_content.find("---", 3)
                        if end != -1:
                            skill_content = skill_content[end + 3 :].strip()
                    base += f"\n\nUse the following skill guidelines when helping the user:\n{skill_content}"
        except Exception as e:
            logger.debug("Failed to load skills: %s", e)
        return base

    def _get_skills_dir(self) -> str | None:
        # __file__ is src/database_operations_mcp/chat/service.py
        # skills is at src/database_operations_mcp/skills
        package_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        candidate = os.path.join(package_dir, "skills")
        return candidate if os.path.isdir(candidate) else None

    def _build_messages(self, request: Any) -> list[dict[str, str]]:
        system_prompt = self._build_system_prompt(getattr(request, "personality", "professional"))
        session_id = getattr(request, "session_id", "default") or "default"
        history = self.memory.get_messages(session_id)
        messages = [{"role": h["role"], "content": h["content"]} for h in history]
        messages.insert(0, {"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": request.message})
        return messages

    def _load_keys(self) -> dict[str, str]:
        local_app_data = os.environ.get("LOCALAPPDATA") or os.environ.get("APPDATA") or "."
        keys_file = os.path.join(local_app_data, "database-operations-mcp", "keys.json")
        if os.path.isfile(keys_file):
            try:
                with open(keys_file) as f:
                    return _json.load(f)
            except Exception as e:
                logger.debug("Failed to load keys: %s", e)
        return {}

    # ---------------------------------------------------------------------
    # Public API
    # ---------------------------------------------------------------------
    async def ask(self, request: Any) -> dict[str, Any]:
        """Process a chat request and return a dictionary compatible with the
        original endpoint response.
        """
        try:
            settings = self._load_settings()
            endpoint = settings.get("endpoint", "http://localhost:11434").rstrip("/")
            preferred_model = getattr(request, "model", None) or settings.get("model", "gemma4:e4b")
            messages = self._build_messages(request)
            session_id = getattr(request, "session_id", "default") or "default"

            for provider in self._provider_order:
                # Ollama provider
                if provider == "ollama":
                    try:
                        # discover available models
                        try:
                            avail_req = _req.urlopen(f"{endpoint}/api/tags", timeout=3)  # noqa: S310
                            avail_data = _json.loads(avail_req.read())
                            models = [m["name"] for m in avail_data.get("models", [])]
                        except Exception:
                            models = []
                        _preferred = preferred_model
                        if _preferred not in models and models:
                            for fallback in (
                                "gemma4:e4b",
                                "gemma4:e2b",
                                "llama3.2:3b",
                                "llama3.2:1b",
                                "llama3.1:latest",
                                "qwen2.5-coder:latest",
                            ):
                                if fallback in models:
                                    _preferred = fallback
                                    break
                            else:
                                _preferred = models[0]
                        payload = _json.dumps(
                            {
                                "model": _preferred,
                                "messages": messages,
                                "stream": False,
                            }
                        ).encode()
                        oreq = _req.Request(  # noqa: S310
                            f"{endpoint}/api/chat",
                            data=payload,
                            headers={"Content-Type": "application/json"},
                        )
                        with _req.urlopen(oreq, timeout=120) as r:  # noqa: S310
                            data = _json.loads(r.read())
                        reply = data.get("message", {}).get("content", "")
                        if reply:
                            self.memory.append(session_id, "user", request.message)
                            self.memory.append(session_id, "assistant", reply)
                            return {"reply": reply, "provider": f"ollama ({_preferred})"}
                    except Exception as e:
                        logger.debug("Ollama provider failed: %s", e)
                        continue

                # OpenAI compatible provider
                if provider == "openai":
                    try:
                        keys = self._load_keys()
                        api_key = keys.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY", "")
                        headers = {"Content-Type": "application/json"}
                        if api_key:
                            headers["Authorization"] = f"Bearer {api_key}"
                        openai_url = endpoint.rstrip("/")
                        if not openai_url.endswith("/chat/completions"):
                            if not openai_url.endswith("/v1"):
                                openai_url += "/v1"
                            openai_url += "/chat/completions"
                        payload = _json.dumps(
                            {
                                "model": preferred_model or "gpt-4o-mini",
                                "messages": messages,
                                "max_tokens": 1024,
                                "stream": False,
                            }
                        ).encode()
                        oreq = _req.Request(openai_url, data=payload, headers=headers)  # noqa: S310
                        with _req.urlopen(oreq, timeout=60) as r:  # noqa: S310
                            data = _json.loads(r.read())
                        reply = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                        if reply:
                            self.memory.append(session_id, "user", request.message)
                            self.memory.append(session_id, "assistant", reply)
                            return {"reply": reply, "provider": f"openai compatible ({preferred_model})"}
                    except Exception as e:
                        logger.debug("OpenAI provider failed: %s", e)
                        continue

                # DeepSeek provider
                if provider == "deepseek":
                    try:
                        keys = self._load_keys()
                        api_key = keys.get("DEEPSEEK_API_KEY") or os.getenv("DEEPSEEK_API_KEY", "")
                        if not api_key:
                            continue
                        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
                        url = endpoint.rstrip("/")
                        if not url.endswith("/chat/completions"):
                            if not url.endswith("/v1"):
                                url += "/v1"
                            url += "/chat/completions"
                        payload = _json.dumps(
                            {
                                "model": preferred_model or "deepseek-v4-flash",
                                "messages": messages,
                                "max_tokens": 1024,
                            }
                        ).encode()
                        oreq = _req.Request(url, data=payload, headers=headers)  # noqa: S310
                        with _req.urlopen(oreq, timeout=60) as r:  # noqa: S310
                            data = _json.loads(r.read())
                        reply = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                        if reply:
                            self.memory.append(session_id, "user", request.message)
                            self.memory.append(session_id, "assistant", reply)
                            return {"reply": reply, "provider": f"deepseek ({preferred_model})"}
                    except Exception as e:
                        logger.debug("DeepSeek provider failed: %s", e)
                        continue

                # Anthropic provider
                if provider == "anthropic":
                    try:
                        keys = self._load_keys()
                        api_key = keys.get("ANTHROPIC_API_KEY") or os.getenv("ANTHROPIC_API_KEY", "")
                        if not api_key:
                            continue
                        headers = {
                            "Content-Type": "application/json",
                            "x-api-key": api_key,
                            "anthropic-version": "2023-06-01",
                        }
                        url = endpoint.rstrip("/") + "/v1/messages"
                        payload = _json.dumps(
                            {
                                "model": preferred_model or "claude-3-opus-20240229",
                                "messages": messages,
                                "max_tokens": 1024,
                            }
                        ).encode()
                        oreq = _req.Request(url, data=payload, headers=headers)  # noqa: S310
                        with _req.urlopen(oreq, timeout=60) as r:  # noqa: S310
                            data = _json.loads(r.read())
                        reply = data.get("content", [{}])[0].get("text", "")
                        if reply:
                            self.memory.append(session_id, "user", request.message)
                            self.memory.append(session_id, "assistant", reply)
                            return {"reply": reply, "provider": f"anthropic ({preferred_model})"}
                    except Exception as e:
                        logger.debug("Anthropic provider failed: %s", e)
                        continue

                # LM Studio provider
                if provider == "lmstudio":
                    try:
                        headers = {"Content-Type": "application/json"}
                        lm_url = endpoint.rstrip("/") + "/v1/chat/completions"
                        payload = _json.dumps(
                            {
                                "model": preferred_model,
                                "messages": messages,
                                "max_tokens": 1024,
                                "stream": False,
                            }
                        ).encode()
                        oreq = _req.Request(lm_url, data=payload, headers=headers)  # noqa: S310
                        with _req.urlopen(oreq, timeout=60) as r:  # noqa: S310
                            data = _json.loads(r.read())
                        reply = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                        if reply:
                            self.memory.append(session_id, "user", request.message)
                            self.memory.append(session_id, "assistant", reply)
                            return {"reply": reply, "provider": f"lmstudio ({preferred_model})"}
                    except Exception as e:
                        logger.debug("LM Studio provider failed: %s", e)
                        # try fallback port 1234
                        try:
                            fallback_url = "http://127.0.0.1:1234/v1/chat/completions"
                            oreq = _req.Request(fallback_url, data=payload, headers=headers)  # noqa: S310
                            with _req.urlopen(oreq, timeout=60) as r:  # noqa: S310
                                data = _json.loads(r.read())
                            reply = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                            if reply:
                                self.memory.append(session_id, "user", request.message)
                                self.memory.append(session_id, "assistant", reply)
                                return {"reply": reply, "provider": f"lmstudio ({preferred_model})"}
                        except Exception as e:
                            logger.debug("LM Studio fallback port failed: %s", e)
                            continue

            # Fallback when all providers fail
            return {
                "reply": "No local intelligence backend was reachable. Please make sure LM Studio (port 1234/10709) or Ollama (port 11434) is started.",
                "provider": None,
            }
        except Exception as e:
            return {"reply": f"Error interacting with intelligence core: {e}", "provider": None}
