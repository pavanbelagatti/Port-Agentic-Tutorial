from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    port_client_id: str = os.getenv("PORT_CLIENT_ID", "")
    port_client_secret: str = os.getenv("PORT_CLIENT_SECRET", "")
    port_api_url: str = os.getenv("PORT_API_URL", "https://api.port.io/v1")

    llm_mode: str = os.getenv("LLM_MODE", "mock")
    llm_base_url: str = os.getenv("LLM_BASE_URL", "")
    llm_api_key: str = os.getenv("LLM_API_KEY", "")
    llm_model: str = os.getenv("LLM_MODEL", "gpt-4o-mini")

    request_timeout: int = 30


settings = Settings()