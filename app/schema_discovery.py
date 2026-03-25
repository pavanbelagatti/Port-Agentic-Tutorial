from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class BlueprintMap:
    # Hardcoded for your demo account for now
    service: Optional[str] = "Microservice"
    team: Optional[str] = None
    incident: Optional[str] = "new_relic_alerts_environments"
    deployment: Optional[str] = "Deployment"
    investigation: Optional[str] = None