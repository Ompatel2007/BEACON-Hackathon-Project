import pandas as pd
from Intel import analyze_signal
from fusion import aggregate_by_region
from decision import allocate_resources


def load_data():
    df = pd.read_csv("data/tweets.csv")
    return df["text"].dropna().tolist()


def main():

    raw_signals = load_data()
    structured_alerts = []

    print("\nProcessing signals...\n")

    for text in raw_signals[:15]:  # limit for demo
        alert = analyze_signal(text)
        if alert:
            structured_alerts.append(alert)

    if not structured_alerts:
        print("No valid alerts extracted.")
        return

    regions = aggregate_by_region(structured_alerts)
    decisions = allocate_resources(regions)

    print("\n=== Disaster Intelligence Report ===\n")

    for region, info in decisions.items():
        print(f"Region: {region}")
        print(f"Risk Score: {info['risk_score']}")
        print(f"Priority: {info['priority']}")
        print(f"Estimated People at Risk: {info['estimated_people']}")
        print(f"Recommended Action: {info['recommended_action']}")
        print(f"Reasoning: {info['reasoning']}")
        print("-" * 50)


if __name__ == "__main__":
    main()
