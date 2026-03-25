from __future__ import annotations

from typing import Any, Dict


def compact_entity(entity: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "identifier": entity.get("identifier"),
        "title": entity.get("title"),
        "blueprint": entity.get("blueprint"),
        "properties": entity.get("properties", {}),
        "relations": entity.get("relations", {}),
    }