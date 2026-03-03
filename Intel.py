import json
import re
from config import client, MODEL_NAME
from models import Alert


def extract_json_block(text):
    """
    Extract first valid JSON object from model output.
    """
    matches = re.findall(r'\{.*?\}', text, re.DOTALL)
    for match in matches:
        try:
            return json.loads(match)
        except:
            continue
    return None


def safe_float(value, default=0.0):
    try:
        return float(value)
    except:
        return default


def safe_int(value, default=0):
    try:
        return int(float(value))
    except:
        return default


def analyze_signal(text):

    prompt = f"""
You are a disaster intelligence extraction system.

Your task is to extract structured disaster data from the report.

Rules:
- Return ONLY valid JSON.
- Do NOT include explanations.
- Do NOT invent numbers.
- If information is missing, use conservative low estimates.
- If uncertain, reduce confidence.
- Do NOT exaggerate severity.
- Only use values supported by the report.

Report:
{text}

Return ONLY valid JSON in this exact format:

{{
  "location": "string",
  "disaster_type": "flood | earthquake | fire | cyclone | landslide | other",
  "severity": number between 1 and 10,
  "people_at_risk": integer,
  "infrastructure_damage": number between 1 and 10,
  "urgency": number between 1 and 10,
  "confidence": number between 0 and 1
}}

Only JSON. No markdown. No extra text.
"""

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )

        raw_text = response.text
        print("Gemini Output:", raw_text)

        data = extract_json_block(raw_text)

        if not data:
            print("Failed to parse JSON")
            return None

        # Extract raw values
        severity = safe_float(data.get("severity"), 5)
        people = safe_int(data.get("people_at_risk"), 0)
        damage = safe_float(data.get("infrastructure_damage"), 5)
        urgency = safe_float(data.get("urgency"), 5)
        confidence = safe_float(data.get("confidence"), 0.5)

        severity = max(1, min(severity, 10))
        damage = max(1, min(damage, 10))
        urgency = max(1, min(urgency, 10))
        confidence = max(0, min(confidence, 1))

        people = max(0, min(people, 10000))

        if confidence < 0.3:
            severity = min(severity, 4)

        allowed_types = {"flood", "earthquake", "fire", "cyclone", "landslide", "other"}
        disaster_type = data.get("disaster_type", "other")
        if disaster_type not in allowed_types:
            disaster_type = "other"

        return Alert(
            location=data.get("location", "Unknown"),
            disaster_type=disaster_type,
            severity=severity,
            people_at_risk=people,
            infrastructure_damage=damage,
            urgency=urgency,
            confidence=confidence,
        )

    except Exception as e:
        print("Analyze Signal Error:", e)
        return None
