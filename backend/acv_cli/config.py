import os
import toml
from pathlib import Path
from typing import Any, Optional
from functools import lru_cache

DEFAULT_CONFIG_PATH = "config.toml"

class Config:
    def __init__(self, config_path: Optional[str] = None):
        self._config_path = Path(config_path or DEFAULT_CONFIG_PATH)
        self._data: dict[str, Any] = {}
        self._loaded = False

    def load(self) -> None:
        if self._loaded:
            return
        if self._config_path.exists():
            self._data = toml.load(self._config_path)
        else:
            self._data = {}
        self._loaded = True

    def get(self, key: str, default: Any = None) -> Any:
        self.load()
        keys = key.split(".")
        value = self._data
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
            if value is None:
                return default
        return value

    @property
    def data_paths(self) -> dict[str, str]:
        return self.get("data_paths", {
            "base_dir": "./data",
            "sessions_dir": "./data/sessions",
            "knowledge_dir": "./data/knowledge",
            "skills_dir": "./skills",
            "db_path": "./data/index.db",
        })

    @property
    def agents(self) -> dict[str, str]:
        return self.get("agents", {
            "claude": "claude",
            "gemini": "gemini",
            "codex": "copilot",
        })

    @property
    def logging(self) -> dict[str, str]:
        return self.get("logging", {"log_level": "INFO"})

    @property
    def web(self) -> dict[str, Any]:
        return self.get("web", {"host": "127.0.0.1", "port": 8787, "reload": True})

    @property
    def search(self) -> dict[str, Any]:
        return self.get("search", {"default_limit": 20, "enable_fts": True})

    @property
    def skills(self) -> dict[str, Any]:
        return self.get("skills", {"enabled": True, "auto_summarize": False})

    def get_agent_command(self, agent: str, profile: Optional[str] = None) -> str:
        agents = self.agents
        if profile:
            profile_key = f"{agent}.{profile}"
            profile_cmd = self.get(f"agent_profiles.{profile_key}.command")
            if profile_cmd:
                return profile_cmd
        return agents.get(agent, agent)

@lru_cache()
def get_config(config_path: Optional[str] = None) -> Config:
    return Config(config_path)
