from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import time
import requests
from dispatch_ai import get_dispatch_recommendation
from Intel import analyze_signal
from fusion import aggregate_by_region
from descision import allocate_resources
import os
print("KEY EXISTS:", os.getenv("GEMINI_API_KEY") is not None)
print("✅ BACKEND FILE LOADED")

priority_rank = {
    "CRITICAL": 4,
    "HIGH": 3,
    "MODERATE": 2,
    "LOW": 1
}

app = FastAPI(title="ResQAI Disaster Intelligence API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

active_alerts = []


class SOSRequest(BaseModel):
    location: str
    message: str


@app.get("/")
def root():
    return {"message": "Backend running successfully"}


# =============================
# GEOCODING
# =============================

def get_coordinates(location_text):

    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            "q": location_text,
            "format": "json",
            "limit": 1
        }

        response = requests.get(
            url,
            params=params,
            headers={"User-Agent": "resqai"}
        )

        data = response.json()

        if data:
            return float(data[0]["lat"]), float(data[0]["lon"])

    except Exception as e:
        print("Geocoding error:", e)

    return 12.8449, 80.1500


# =============================
# SEND SOS
# =============================

@app.post("/api/send-sos")
def send_sos(request: SOSRequest):

    combined_text = f"Location: {request.location}. Message: {request.message}"

    alert = analyze_signal(combined_text)

    if not alert:
        return {"status": "error", "message": "Analysis failed"}

    regions = aggregate_by_region([alert])
    decisions = allocate_resources(regions)

    region_name = list(decisions.keys())[0]
    decision = decisions[region_name]
    dispatch_input = f"""
    Incident: {alert.disaster_type}
    Location: {region_name}
    Priority: {decision['priority']}
    Estimated People: {decision['estimated_people']}
    Risk Score: {decision['risk_score']}
    """

    ai_dispatch = get_dispatch_recommendation(dispatch_input)
    lat, lng = get_coordinates(request.location)

    record = {
        "id": int(time.time()),
        "location": region_name,
        "original_message": request.message,
        "hazard": alert.disaster_type,
        "severity": decision["priority"],
        "action": decision["recommended_action"],
        "lat": lat,
        "lng": lng,
        "status": "ACTIVE"
    }

    active_alerts.append(record)

    # SORT BY PRIORITY
    active_alerts.sort(
        key=lambda x: priority_rank.get(x["severity"], 0),
        reverse=True
    )

    return {
        "status": "success",
        "message": "SOS received",
        "analysis": decision,
        "ai_dispatch": ai_dispatch,
        "lat": lat,
        "lng": lng
    }


# =============================
# DISPATCH
# =============================

@app.post("/api/dispatch/{alert_id}")
def dispatch(alert_id: int):

    global active_alerts

    for alert in active_alerts:
        if alert["id"] == alert_id:

            active_alerts.remove(alert)
            break

    return {
        "status": "success",
        "message": "🚑 Rescue units are on their way"
    }

@app.get("/api/get-dashboard-data")
def dashboard():
    return {
        "active_alerts": active_alerts,
        "total_active": len(active_alerts)
    }

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

# Serve index.html at root
@app.get("/")
def serve_index():
    return FileResponse("index.html")

# Serve static files (JS, CSS)
app.mount("/static", StaticFiles(directory="."), name="static")
