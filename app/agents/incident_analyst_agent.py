from __future__ import annotations

from typing import Any, Dict, List

from app.agents.base import Agent


class IncidentAnalystAgent(Agent):
    name = "incident-analyst-agent"

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        context = state.get("context", {})
        analysis: Dict[str, Any] = {
            "summary": "",
            "service_findings": [],
            "overall_risk": "unknown",
        }

        resolved_services = context.get("resolved_services", [])
        findings: List[Dict[str, Any]] = []

        for item in resolved_services:
            service = item["service"]
            incidents = item.get("incidents", [])
            deployments = item.get("deployments", [])

            risk = self._score_risk(incidents=incidents, deployments=deployments)

            findings.append(
                {
                    "service_identifier": service.get("identifier"),
                    "service_title": service.get("title"),
                    "incident_count": len(incidents),
                    "deployment_count": len(deployments),
                    "risk": risk,
                    "notes": self._notes_for_service(incidents, deployments),
                }
            )

        analysis["service_findings"] = findings
        analysis["overall_risk"] = self._overall_risk(findings)
        analysis["summary"] = self._build_summary(context, analysis)

        state["analysis"] = analysis
        state["trace"].append(f"{self.name}: completed risk and incident analysis")
        return state

    def _score_risk(self, incidents: List[Dict[str, Any]], deployments: List[Dict[str, Any]]) -> str:
        incident_count = len(incidents)
        deployment_count = len(deployments)

        if incident_count >= 5:
            return "critical"
        if incident_count >= 3:
            return "high"
        if incident_count >= 1 and deployment_count >= 3:
            return "medium"
        if incident_count >= 1:
            return "medium"
        if deployment_count >= 4:
            return "low"
        return "low"

    def _notes_for_service(self, incidents: List[Dict[str, Any]], deployments: List[Dict[str, Any]]) -> List[str]:
        notes: List[str] = []
        if incidents:
            notes.append(f"{len(incidents)} related incident-like records found in Port")
        if deployments:
            notes.append(f"{len(deployments)} related deployment/release-like records found in Port")
        if not notes:
            notes.append("No obvious incident/deployment signals found in the current Port context")
        return notes

    def _overall_risk(self, findings: List[Dict[str, Any]]) -> str:
        text = str(findings).lower()
        if "critical" in text:
            return "critical"
        if "high" in text:
            return "high"
        if "medium" in text:
            return "medium"
        if findings:
            return "low"
        return "unknown"

    def _build_summary(self, context: Dict[str, Any], analysis: Dict[str, Any]) -> str:
        if context.get("resolved_services"):
            return (
                f"Found {len(context['resolved_services'])} service candidate(s) in Port. "
                f"Overall assessed risk is {analysis['overall_risk']}."
            )
        return "No matching service context was found in Port."