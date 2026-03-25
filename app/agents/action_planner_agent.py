from __future__ import annotations

import json
from typing import Any, Dict

from app.agents.base import Agent
from app.llm import LLMClient


class ActionPlannerAgent(Agent):
    name = "action-planner-agent"

    def __init__(self, llm: LLMClient) -> None:
        self.llm = llm

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        context = state.get("context", {})
        analysis = state.get("analysis", {})

        system_prompt = (
            "You are an engineering operations assistant. "
            "Write the final answer in natural, human-friendly language. "
            "Do not dump raw JSON. "
            "Speak like a helpful engineering teammate.\n\n"
            "Your response must include:\n"
            "1. What service was resolved from the user's question.\n"
            "2. A short explanation of what was found.\n"
            "3. A plain-English assessment of risk.\n"
            "4. Practical next steps.\n"
            "5. What additional Port data would make the answer stronger.\n\n"
            "Keep it concise but useful."
        )

        user_prompt = json.dumps(
            {
                "original_query": state.get("original_query", state["query"]),
                "resolved_query": state["query"],
                "entity_type": state["entity_type"],
                "context": context,
                "analysis": analysis,
            },
            indent=2,
        )

        plan = self.llm.complete(system_prompt=system_prompt, user_prompt=user_prompt)
        state["action_plan"] = plan
        state["trace"].append(f"{self.name}: generated natural language action plan")
        return state