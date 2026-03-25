from __future__ import annotations

import json
from typing import Any, Dict, List

import requests

from app.config import settings


class LLMClient:
    def complete(self, system_prompt: str, user_prompt: str) -> str:
        if settings.llm_mode == "mock":
            return self._natural_mock_response(system_prompt, user_prompt)

        if settings.llm_mode == "generic_openai_compatible":
            return self._openai_compatible_completion(system_prompt, user_prompt)

        raise ValueError(f"Unsupported LLM_MODE: {settings.llm_mode}")

    def _openai_compatible_completion(self, system_prompt: str, user_prompt: str) -> str:
        if not settings.llm_base_url or not settings.llm_api_key:
            raise ValueError("LLM_BASE_URL and LLM_API_KEY must be set for generic_openai_compatible mode.")

        payload: Dict[str, Any] = {
            "model": settings.llm_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.2,
        }

        headers = {
            "Authorization": f"Bearer {settings.llm_api_key}",
            "Content-Type": "application/json",
        }

        response = requests.post(
            settings.llm_base_url,
            headers=headers,
            json=payload,
            timeout=settings.request_timeout,
        )
        response.raise_for_status()

        data = response.json()
        return data["choices"][0]["message"]["content"]

    def _natural_mock_response(self, system_prompt: str, user_prompt: str) -> str:
        try:
            payload = json.loads(user_prompt)
        except Exception:
            return (
                "I reviewed the Port context and generated a draft response, "
                "but I could not parse the structured payload cleanly."
            )

        original_query = payload.get("original_query", "the user's question")
        resolved_query = payload.get("resolved_query", "the requested service")
        analysis = payload.get("analysis", {}) or {}
        findings: List[Dict[str, Any]] = analysis.get("service_findings", []) or []
        overall_risk = analysis.get("overall_risk", "unknown")

        if not findings:
            return (
                f"I interpreted your question **'{original_query}'** as a request about **{resolved_query}**, "
                f"but I could not find enough connected operational context in Port to produce a confident assessment. "
                f"The next thing I would check is whether incidents, deployments, ownership, and alerts are properly linked for this service in Port."
            )

        top = findings[0]
        service_title = top.get("service_title") or top.get("service_identifier") or resolved_query
        incident_count = top.get("incident_count", 0)
        deployment_count = top.get("deployment_count", 0)
        notes = top.get("notes", []) or []

        risk_sentence = {
            "critical": f"{service_title} appears to be in a critical state based on the current Port context.",
            "high": f"{service_title} appears to be high risk based on the current Port context.",
            "medium": f"{service_title} shows some operational risk signals in Port.",
            "low": f"{service_title} currently looks relatively stable from the Port data that was found.",
            "unknown": f"I found {service_title}, but the current Port context is not enough for a strong risk assessment.",
        }.get(overall_risk, f"I found {service_title} in Port and reviewed the available operational signals.")

        next_steps = []
        if overall_risk in {"critical", "high"}:
            next_steps.append("Check whether the active alert condition is still ongoing.")
            next_steps.append("Review the most recent deployment or rollout tied to this service.")
            next_steps.append("Validate service ownership, dashboards, and on-call routing.")
        elif overall_risk == "medium":
            next_steps.append("Review the recent incidents and compare them with recent deployments.")
            next_steps.append("Check whether this is a recurring issue or a one-off alert.")
            next_steps.append("Confirm that ownership and service metadata are complete in Port.")
        else:
            next_steps.append("Monitor the service and confirm the current Port metadata is complete.")
            next_steps.append("Verify that alerts, deployments, and ownership are linked correctly.")
            next_steps.append("Improve service documentation and operational relationships where needed.")

        note_text = " ".join(notes[:2]) if notes else "No detailed notes were generated."

        return (
            f"I interpreted your question **'{original_query}'** as a request about **{service_title}**.\n\n"
            f"I found this service in Port and reviewed its connected operational context. "
            f"{risk_sentence} I found **{incident_count} related incident-like records** and "
            f"**{deployment_count} related deployment records**. {note_text}\n\n"
            f"**What I would do next:**\n"
            f"1. {next_steps[0]}\n"
            f"2. {next_steps[1]}\n"
            f"3. {next_steps[2]}\n\n"
            f"**What would improve confidence:** clearer ownership, recent deployment metadata, dashboards, "
            f"and stronger alert-to-service relationships in Port."
        )