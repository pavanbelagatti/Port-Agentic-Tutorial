from __future__ import annotations

import argparse
from rich.console import Console
from rich.panel import Panel
from rich.pretty import pprint

from app.context_builder import ContextBuilder
from app.llm import LLMClient
from app.port_client import PortClient
from app.schema_discovery import BlueprintMap
from app.agents.query_understanding_agent import QueryUnderstandingAgent
from app.agents.service_context_agent import ServiceContextAgent
from app.agents.incident_analyst_agent import IncidentAnalystAgent
from app.agents.action_planner_agent import ActionPlannerAgent
from app.agents.orchestrator import Orchestrator

console = Console()


def main() -> None:
    parser = argparse.ArgumentParser(description="Port.io as Context Lake for Multi-Agent Apps")
    parser.add_argument("--query", required=True, help="Service name or natural-language service question")
    parser.add_argument(
        "--type",
        default="service",
        choices=["service", "team"],
        help="Query entity type",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show raw structured context for debugging",
    )
    args = parser.parse_args()

    console.print("[bold cyan]Initializing Port client...[/bold cyan]")
    port = PortClient()

    bp = BlueprintMap(
        service="Microservice",
        team=None,
        incident="new_relic_alerts_environments",
        deployment="Deployment",
        investigation=None,
    )

    builder = ContextBuilder(port, bp)
    llm = LLMClient()

    orchestrator = Orchestrator(
        agents=[
            QueryUnderstandingAgent(),
            ServiceContextAgent(builder),
            IncidentAnalystAgent(),
            ActionPlannerAgent(llm),
        ]
    )

    result = orchestrator.run(query=args.query, entity_type=args.type)

    context = result.get("context", {})
    analysis = result.get("analysis", {})
    action_plan = result.get("action_plan", "No action plan generated.")
    resolved_query = result.get("query", args.query)
    original_query = result.get("original_query", args.query)

    if args.type == "service" and not context.get("resolved_services"):
        console.print(
            Panel.fit(
                f"I could not find a matching service for '{original_query}'. "
                f"I tried resolving it as '{resolved_query}' in the Microservice blueprint.",
                title="Result"
            )
        )
        return

    console.print(Panel.fit(action_plan, title=f"Port Agent Response: {original_query}"))

    if args.verbose:
        console.print(Panel.fit("\n".join(result.get("trace", [])), title="Agent Trace"))
        console.print(
            Panel.fit(
                f"Original query: {original_query}\nResolved query: {resolved_query}\n"
                f"{analysis.get('summary', 'No summary available.')}",
                title="Analysis Summary"
            )
        )
        console.print("\n[bold yellow]Raw structured context:[/bold yellow]")
        pprint(context)


if __name__ == "__main__":
    main()