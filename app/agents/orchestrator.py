from __future__ import annotations

from typing import Any, Dict, List

from app.agents.base import Agent


class Orchestrator:
    def __init__(self, agents: List[Agent]) -> None:
        self.agents = agents

    def run(self, query: str, entity_type: str = "service") -> Dict[str, Any]:
        state: Dict[str, Any] = {
            "query": query,
            "entity_type": entity_type,
            "trace": [],
        }

        for agent in self.agents:
            state = agent.run(state)

        return state