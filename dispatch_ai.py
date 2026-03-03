import pandas as pd
import json
import time
from config import client, MODEL_NAME

# ================== DATASET CONFIG ==================

DATASET_PATH = "C:\\Users\\patel\\OneDrive\\Desktop\\Hackathon\\back\\kaggle_dataset.csv"

# ================== LOAD AI MEMORY ONCE ==================

print("Loading AI memory from Kaggle dataset...")

try:
    df = pd.read_csv(DATASET_PATH)
except Exception as e:
    print("Dataset load failed:", e)
    df = pd.DataFrame()

training_examples = "HISTORICAL EMERGENCY DISPATCH RECORDS:\n\n"

for _, row in df.head(6).iterrows():
    training_examples += (
        f"SCENARIO: Incident={row['Incident_Type']}, "
        f"Region={row['Region_Type']}, "
        f"Weather={row['Weather_Condition']}, "
        f"Injuries={row['Number_of_Injuries']}\n"
        f"DISPATCH: {{"
        f"\"severity\": \"{row['Incident_Severity']}\", "
        f"\"emergency_level\": \"{row['Emergency_Level']}\", "
        f"\"dispatch_action\": \"{row['Label']}\""
        f"}}\n\n"
    )

print("AI memory loaded successfully.")

# ================== CACHE ==================

last_ai_response = None
last_call_time = 0

# ================== DISPATCH AI FUNCTION ==================

def get_dispatch_recommendation(live_incident_details):
    global last_ai_response, last_call_time

    # Cache result for 2 minutes
    if time.time() - last_call_time < 120 and last_ai_response:
        return last_ai_response

    prompt = f"""
You are an Emergency Command Center AI.
Respond ONLY in valid JSON.

{training_examples}

NEW INCIDENT:
SCENARIO: {live_incident_details}

OUTPUT:
"""

    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt
            )

            last_ai_response = response.text
            last_call_time = time.time()

            return response.text

        except Exception as e:
            if "429" in str(e) or "Quota" in str(e):
                time.sleep(8)
            else:
                return json.dumps({
                    "error": "AI Service Error",
                    "details": str(e)
                })

    return json.dumps({"error": "Rate limit exceeded after retries"})
