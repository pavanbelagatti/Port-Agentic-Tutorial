from __future__ import annotations

import json

from app.port_client import PortClient


def main() -> None:
    port = PortClient()
    entities = port.get_blueprint_entities("Microservice")

    print(f"Found {len(entities)} entities\n")

    for entity in entities[:20]:
        print(
            json.dumps(
                {
                    "identifier": entity.get("identifier"),
                    "title": entity.get("title"),
                },
                indent=2,
            )
        )


if __name__ == "__main__":
    main()