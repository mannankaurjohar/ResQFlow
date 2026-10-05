from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import csv
import io
import requests
import json
from pathlib import Path

from app.database import get_db
from app.models import CWCAlertSnapshot

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


def save_database_snapshot(db: Session, alerts):
    snapshot = (
        db.query(CWCAlertSnapshot)
        .order_by(CWCAlertSnapshot.id.desc())
        .first()
    )

    alerts_json = json.dumps(alerts)

    if snapshot:
        snapshot.alerts_json = alerts_json
    else:
        snapshot = CWCAlertSnapshot(
            alerts_json=alerts_json
        )
        db.add(snapshot)

    db.commit()


def load_database_snapshot(db: Session):
    snapshot = (
        db.query(CWCAlertSnapshot)
        .order_by(CWCAlertSnapshot.id.desc())
        .first()
    )

    if not snapshot:
        return []

    try:
        return json.loads(snapshot.alerts_json)
    except (json.JSONDecodeError, TypeError):
        return []


def load_seed_snapshot():
    try:
        if not SNAPSHOT_FILE.exists():
            return []

        with open(SNAPSHOT_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        return data.get("alerts", [])

    except Exception:
        return []


@router.get("")
def get_flood_alerts(
    db: Session = Depends(get_db)
):
    global _last_successful_alerts

    try:
        alerts = fetch_cwc_alerts()

        _last_successful_alerts = alerts

        # Persist latest successful CWC data in the database.
        save_database_snapshot(db, alerts)

        return {
            "status": "LIVE",
            "source": "CWC Flood Forecasting System",
            "count": len(alerts),
            "alerts": alerts,
        }

    except requests.RequestException:
        alerts = _last_successful_alerts

        # Database is the primary fallback.
        if not alerts:
            alerts = load_database_snapshot(db)

        # JSON is only the initial seed fallback.
        if not alerts:
            alerts = load_seed_snapshot()

            if alerts:
                save_database_snapshot(db, alerts)

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