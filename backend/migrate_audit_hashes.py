import hashlib
from app.database import SessionLocal
from app.models import AuditLog

db = SessionLocal()

try:
    logs = (
        db.query(AuditLog)
        .order_by(AuditLog.id.asc())
        .all()
    )

    if not logs:
        print("No audit logs found.")
        raise SystemExit

    previous_hash = "0" * 64

    for log in logs:
        # Keep the existing stored timestamp.
        # Only recompute the cryptographic chain.
        hash_payload = (
            f"{previous_hash}|"
            f"{log.created_at.isoformat()}|"
            f"{log.actor_name}|"
            f"{log.actor_role}|"
            f"{log.action}|"
            f"{log.entity_type}|"
            f"{log.entity_id}|"
            f"{log.previous_state or ''}|"
            f"{log.new_state or ''}|"
            f"{log.reason or ''}"
        )

        new_hash = hashlib.sha256(
            hash_payload.encode("utf-8")
        ).hexdigest()

        log.prev_hash = previous_hash
        log.curr_hash = new_hash

        previous_hash = new_hash

        print(
            f"Block #{log.id} re-signed: "
            f"{new_hash}"
        )

    db.commit()

    print()
    print(f"Successfully re-signed {len(logs)} audit blocks.")

finally:
    db.close()