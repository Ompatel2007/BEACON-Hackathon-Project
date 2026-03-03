from collections import defaultdict
import math

def compute_risk(alert):

    people_factor = math.log1p(alert.people_at_risk) / 2

    return (
        alert.severity * 2.5 +
        alert.infrastructure_damage * 2 +
        alert.urgency * 1.5 +
        people_factor +
        alert.confidence * 2
    )

import math

def aggregate_by_region(alerts):
    region_data = defaultdict(list)

    for alert in alerts:
        region_data[alert.location].append(alert)

    results = {}

    for region, alerts in region_data.items():

        risks = [compute_risk(a) for a in alerts]

        avg_risk = sum(risks) / len(risks)

        confirmation_factor = 1 + (math.log1p(len(alerts)) / 3)

        total_score = avg_risk * confirmation_factor

        total_people = max(a.people_at_risk for a in alerts)

        results[region] = {
            "risk_score": round(total_score, 2),
            "estimated_people": total_people
        }

    return results
