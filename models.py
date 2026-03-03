from dataclasses import dataclass

@dataclass
class Alert:
    location: str
    disaster_type: str
    severity: float
    people_at_risk: int
    infrastructure_damage: float
    urgency: float
    confidence: float
