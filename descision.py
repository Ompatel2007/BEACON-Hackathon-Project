def classify_priority(score):
    if score >= 70:
        return "CRITICAL"
    elif score >= 45:
        return "HIGH"
    elif score >= 25:
        return "MODERATE"
    else:
        return "LOW"

def allocate_resources(region_data):

    decisions = {}

    for region, data in region_data.items():

        score = data["risk_score"]
        people = data["estimated_people"]
        priority = classify_priority(score)

        if priority == "CRITICAL":
            action = "Deploy national disaster response force, medical units, and evacuation teams immediately."
        elif priority == "HIGH":
            action = "Deploy multiple rescue teams and emergency medical support."
        elif priority == "MODERATE":
            action = "Send assessment team and standby rescue units."
        else:
            action = "Monitor situation and prepare contingency resources."

        decisions[region] = {
            "risk_score": score,
            "priority": priority,
            "estimated_people": people,
            "recommended_action": action,
            "reasoning": f"Risk score {score} classified as {priority} based on severity, infrastructure damage, urgency, and population exposure."
        }

    return decisions
