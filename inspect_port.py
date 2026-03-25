from __future__ import annotations

import json
from rich.console import Console
from rich.panel import Panel

from app.port_client import PortClient

console = Console()


def main() -> None:
    port = PortClient()
    blueprints = port.list_blueprints()

    console.print(Panel.fit(f"Found {len(blueprints)} blueprints", title="Port"))

    for bp in blueprints[:40]:
        identifier = bp.get("identifier")
        title = bp.get("title", identifier)

        console.print(f"\n[bold cyan]Blueprint:[/bold cyan] {title} [dim]({identifier})[/dim]")

        try:
            entities = port.get_blueprint_entities(identifier)

            if not entities:
                console.print("[yellow]No entities returned[/yellow]")
                continue

            for idx, entity in enumerate(entities[:2], start=1):
                console.print(
                    Panel.fit(
                        json.dumps(
                            {
                                "identifier": entity.get("identifier"),
                                "title": entity.get("title"),
                                "blueprint": entity.get("blueprint"),
                                "properties_keys": list((entity.get("properties") or {}).keys()),
                                "relations_keys": list((entity.get("relations") or {}).keys()),
                            },
                            indent=2,
                        ),
                        title=f"{identifier} sample #{idx}",
                    )
                )

        except Exception as exc:
            console.print(f"[red]Could not inspect {identifier}: {exc}[/red]")


if __name__ == "__main__":
    main()