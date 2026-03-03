# BEACON  
### Broad Emergency Alert & Coordination Network  

AI-Powered Disaster Intelligence & Safe Routing System

---

##  Overview

BEACON is an AI-driven disaster response system that:

- Analyzes live SOS messages using Gemini AI
- Extracts structured disaster intelligence
- Calculates regional risk scores
- Prioritizes emergency resource allocation
- Generates AI-assisted dispatch plans
- Computes the safest evacuation route avoiding high-risk zones
- Visualizes everything in real-time on an interactive map

---

## Core Architecture

### Signal Intelligence Layer
- Uses Google Gemini API
- Extracts:
  - Disaster type
  - Severity
  - People at risk
  - Infrastructure damage
  - Urgency
  - Confidence score
- Strict JSON validation + hallucination safeguards

---

### Risk Scoring Engine
Combines:

- Severity weight
- Infrastructure damage weight
- Urgency factor
- Population exposure (log scaled)
- Confidence modifier

Produces dynamic regional risk scores.

---

### Resource Allocation Engine
Classifies regions into:

- CRITICAL
- HIGH
- MODERATE
- LOW

Generates structured response recommendations.

---

### AI Dispatch Planner
Uses historical emergency dataset context  
Generates intelligent dispatch strategies via Gemini.

---

### Smart Safe Routing
- Built using Leaflet + OSRM
- Creates 100m hazard radius zones
- Evaluates alternative routes
- Computes normalized risk score
- Automatically selects safest route

---

## Features

- Real-time SOS ingestion
- AI structured extraction
- Dynamic risk aggregation
- Automated dispatch recommendations
- Intelligent safe evacuation routing
- Interactive dashboard visualization

---

## Tech Stack

Backend
- FastAPI
- Uvicorn
- Pandas
- Google Gemini API
- Pydantic

Frontend
- HTML/CSS/JavaScript
- Leaflet.js
- Leaflet Routing Machine
- OSRM Routing Engine

Deployment
- Render (Cloud Hosting)

---

## Security

- Gemini API key stored as environment variable
- No hardcoded secrets
- JSON schema enforcement
- Risk normalization to prevent hallucinated escalation

---

## Installation (Local)

bash
pip install -r requirements.txt