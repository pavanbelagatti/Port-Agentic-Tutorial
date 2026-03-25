from __future__ import annotations

from typing import Any, Dict

from app.agents.base import Agent
from app.context_builder import ContextBuilder


class ServiceContextAgent(Agent):
    name = "service-context-agent"

    def __init__(self, builder: ContextBuilder) -> None:
        self.builder = builder

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        entity_type = state.get("entity_type", "service")
        query = state["query"]

        if entity_type == "team":
            state["context"] = self.builder.build_team_context(query)
        else:
            state["context"] = self.builder.build_service_context(query)

        state["trace"].append(
            f"{self.name}: built context from Port for {entity_type}='{query}'"
        )
        return state