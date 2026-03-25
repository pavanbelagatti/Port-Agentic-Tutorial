from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

import requests

from app.config import settings


class PortClient:
    def __init__(self) -> None:
        self.api_url = settings.port_api_url.rstrip("/")
        self._access_token: Optional[str] = None

    def _authenticate(self) -> str:
        if self._access_token:
            return self._access_token

        payload = {
            "clientId": settings.port_client_id,
            "clientSecret": settings.port_client_secret,
        }

        response = requests.post(
            f"{self.api_url}/auth/access_token",
            json=payload,
            timeout=settings.request_timeout,
        )
        response.raise_for_status()

        data = response.json()
        self._access_token = data["accessToken"]
        return self._access_token

    def _headers(self) -> Dict[str, str]:
        token = self._authenticate()
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

    def list_blueprints(self) -> List[Dict[str, Any]]:
        response = requests.get(
            f"{self.api_url}/blueprints",
            headers=self._headers(),
            timeout=settings.request_timeout,
        )
        response.raise_for_status()
        data = response.json()

        if isinstance(data, dict):
            for key in ("blueprints", "items", "data"):
                if key in data and isinstance(data[key], list):
                    return data[key]

        if isinstance(data, list):
            return data

        raise ValueError(f"Unexpected blueprints response: {json.dumps(data)[:1000]}")

    def get_blueprint_entities(self, blueprint_id: str) -> List[Dict[str, Any]]:
        response = requests.get(
            f"{self.api_url}/blueprints/{blueprint_id}/entities",
            headers=self._headers(),
            timeout=settings.request_timeout,
        )
        response.raise_for_status()
        data = response.json()

        if isinstance(data, dict):
            for key in ("entities", "items", "data"):
                if key in data and isinstance(data[key], list):
                    return data[key]

        if isinstance(data, list):
            return data

        raise ValueError(f"Unexpected entities response: {json.dumps(data)[:1000]}")

    def get_entity(self, blueprint_id: str, entity_identifier: str) -> Dict[str, Any]:
        response = requests.get(
            f"{self.api_url}/blueprints/{blueprint_id}/entities/{entity_identifier}",
            headers=self._headers(),
            timeout=settings.request_timeout,
        )
        response.raise_for_status()
        return response.json()

    def create_entity(
        self,
        blueprint_id: str,
        entity_payload: Dict[str, Any],
    ) -> Dict[str, Any]:
        response = requests.post(
            f"{self.api_url}/blueprints/{blueprint_id}/entities",
            headers=self._headers(),
            json=entity_payload,
            timeout=settings.request_timeout,
        )
        response.raise_for_status()
        return response.json()