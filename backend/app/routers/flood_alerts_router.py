from fastapi import APIRouter
import csv
import io
import requests
import json
from pathlib import Path
router = APIRouter(
    prefix="/flood-alerts",
    tags=["Flood Alerts"]
)

CWC_URL = "https://aff.india-water.gov.in/textdata/Floodday_table_view_header.txt"
SNAPSHOT_FILE = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "cwc_alerts_snapshot.json"
)
ALERT_LEVELS = {
    "extreme": "RED",
    "severe": "ORANGE",
    "above normal": "YELLOW",
    "normal": "GREEN",
}

# Stores the last successfully retrieved CWC data.
# This prevents a temporary CWC outage from breaking the application.
_last_successful_alerts = []


def fetch_cwc_alerts():
    response = requests.get(
        CWC_URL,
        timeout=(5, 15)
    )
    response.raise_for_status()

    reader = csv.DictReader(io.StringIO(response.text))

    alerts = []

    for row in reader:
        condition = (row.get("current_condition") or "").strip().lower()

        if condition not in ALERT_LEVELS:
            continue

        alerts.append({
            "station": row.get("Station"),
            "river": row.get("River"),
            "district": row.get("District"),
            "state": row.get("State"),
            "latitude": row.get("Latitude"),
            "longitude": row.get("Longitude"),
            "condition": row.get("current_condition"),
            "alert_level": ALERT_LEVELS[condition],
            "current_level": row.get("WIMS_Value"),
            "warning_level": row.get("WarningLevel"),
            "danger_level": row.get("DangerLevel"),
            "forecast_date": row.get("forecasted_date_ffs"),
            "forecast_level": row.get("forecast_value_ffs"),
            "source": "Central Water Commission",
        })

    return alerts
def save_snapshot(alerts):
    try:
        SNAPSHOT_FILE.parent.mkdir(parents=True, exist_ok=True)

        with open(SNAPSHOT_FILE, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "status": "SNAPSHOT",
                    "source": "Central Water Commission",
                    "count": len(alerts),
                    "alerts": alerts,
                },
                f,
                indent=2,
            )
    except Exception as e:
        print(f"Could not save CWC snapshot: {e}")


def load_snapshot():
    try:
        if not SNAPSHOT_FILE.exists():
            return []

        with open(SNAPSHOT_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        return data.get("alerts", [])

    except Exception as e:
        print(f"Could not load CWC snapshot: {e}")
        return []

@router.get("")
def get_flood_alerts():
    global _last_successful_alerts

    try:
        alerts = fetch_cwc_alerts()

        _last_successful_alerts = alerts

# Save the latest successful CWC data locally
        save_snapshot(alerts)

        return {
            "status": "LIVE",
            "source": "CWC Flood Forecasting System",
            "count": len(alerts),
            "alerts": alerts,
        }

    except requests.RequestException as e:
        print(f"CWC request failed: {e}")

    # First try the current server-memory cache
        alerts = _last_successful_alerts

    # If server memory is empty, load the local snapshot
        if not alerts:
            alerts = load_snapshot()

        if alerts:
            return {
                "status": "STALE",
                "source": "CWC Flood Forecasting System",
                "count": len(alerts),
                "alerts": alerts,
                "message": (
                    "Live CWC data is temporarily unavailable. "
                    "Showing the last successfully retrieved CWC snapshot."
                ),
            }

        return {
            "status": "UNAVAILABLE",
            "source": "CWC Flood Forecasting System",
            "count": 0,
            "alerts": [],
            "message": (
                "Live CWC data is temporarily unavailable and "
                "no previous CWC snapshot is available."
            ),
        }   