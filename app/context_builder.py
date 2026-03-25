from __future__ import annotations

from typing import Any, Dict, List

from app.port_client import PortClient
from app.schema_discovery import BlueprintMap
from app.utils import compact_entity


class ContextBuilder:
    def __init__(self, port: PortClient, bp: BlueprintMap) -> None:
        self.port = port
        self.bp = bp

    def _all_entities(self, blueprint_id: str) -> List[Dict[str, Any]]:
        try:
            return self.port.get_blueprint_entities(blueprint_id)
        except Exception:
            return []

    def _matches(self, entity: Dict[str, Any], query: str) -> bool:
        q = query.lower().strip()

        identifier = str(entity.get("identifier", "")).lower().strip()
        title = str(entity.get("title", "")).lower().strip()

        if q == identifier or q == title:
            return True

        fields = [
            identifier,
            title,
            str(entity.get("properties", "")),
            str(entity.get("relations", "")),
        ]

        blob = " ".join(fields).lower()
        return q in blob

    def find_services_by_name(self, service_name: str) -> List[Dict[str, Any]]:
        if not self.bp.service:
            return []

        q = service_name.lower().strip()
        entities = self._all_entities(self.bp.service)

        exact_matches = []
        partial_matches = []

        for e in entities:
            identifier = str(e.get("identifier", "")).lower().strip()
            title = str(e.get("title", "")).lower().strip()

            if q == identifier or q == title:
                exact_matches.append(e)
            elif self._matches(e, service_name):
                partial_matches.append(e)

        return exact_matches + partial_matches

    def get_related_incidents(self, service_entity: Dict[str, Any]) -> List[Dict[str, Any]]:
        if not self.bp.incident:
            return []

        incidents = self._all_entities(self.bp.incident)
        service_id = str(service_entity.get("identifier", "")).lower()
        service_title = str(service_entity.get("title", "")).lower()

        matched: List[Dict[str, Any]] = []
        for item in incidents:
            blob = (
                str(item.get("title", "")) + " " +
                str(item.get("properties", "")) + " " +
                str(item.get("relations", ""))
            ).lower()

            if service_id and service_id in blob:
                matched.append(item)
            elif service_title and service_title in blob:
                matched.append(item)

        return matched

    def get_related_deployments(self, service_entity: Dict[str, Any]) -> List[Dict[str, Any]]:
        if not self.bp.deployment:
            return []

        deployments = self._all_entities(self.bp.deployment)
        service_id = str(service_entity.get("identifier", "")).lower()
        service_title = str(service_entity.get("title", "")).lower()

        matched: List[Dict[str, Any]] = []
        for item in deployments:
            blob = (
                str(item.get("title", "")) + " " +
                str(item.get("properties", "")) + " " +
                str(item.get("relations", ""))
            ).lower()

            if service_id and service_id in blob:
                matched.append(item)
            elif service_title and service_title in blob:
                matched.append(item)

        return matched

    def build_service_context(self, service_name: str) -> Dict[str, Any]:
        services = self.find_services_by_name(service_name)[:5]

        enriched: List[Dict[str, Any]] = []
        for svc in services:
            incidents = self.get_related_incidents(svc)[:10]
            deployments = self.get_related_deployments(svc)[:10]

            enriched.append(
                {
                    "service": compact_entity(svc),
                    "incidents": [compact_entity(x) for x in incidents],
                    "deployments": [compact_entity(x) for x in deployments],
                }
            )

        return {
            "query": service_name,
            "resolved_services": enriched,
            "blueprints": {
                "service": self.bp.service,
                "incident": self.bp.incident,
                "deployment": self.bp.deployment,
            },
        }

    def build_team_context(self, team_name: str) -> Dict[str, Any]:
        return {
            "query": team_name,
            "resolved_teams": [],
            "blueprints": {
                "service": self.bp.service,
                "incident": self.bp.incident,
                "deployment": self.bp.deployment,
            },
            "note": "Team lookup is disabled for now until we confirm the correct team blueprint in your demo account.",
        }