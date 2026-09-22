import hashlib
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import AuditLog
from app.schemas import AuditLogResponse, AuditIntegrityCheckResponse

router = APIRouter(prefix="/audit", tags=["Cryptographic Audit Trail"])

@router.get("", response_model=List[AuditLogResponse])
def get_audit_logs(limit: int = 50, db: Session = Depends(get_db)):
    return db.query(AuditLog).order_by(AuditLog.id.desc()).limit(limit).all()

@router.get("/verify-integrity", response_model=AuditIntegrityCheckResponse)
def verify_audit_chain_integrity(db: Session = Depends(get_db)):
    logs = db.query(AuditLog).order_by(AuditLog.id.asc()).all()
    if not logs:
        return AuditIntegrityCheckResponse(
            total_records=0,
            is_chain_valid=True,
            broken_block_id=None,
            message="No audit logs recorded yet. Genesis state valid."
        )

    expected_prev = "0" * 64
    for log in logs:
        if log.prev_hash != expected_prev:
            return AuditIntegrityCheckResponse(
                total_records=len(logs),
                is_chain_valid=False,
                broken_block_id=log.id,
                message=f"Tamper detected at Block #{log.id}! Previous hash mismatch."
            )
            
        # Re-compute current hash
        payload = f"{log.prev_hash}|{log.created_at.isoformat()}|{log.actor_name}|{log.actor_role}|{log.action}|{log.entity_type}|{log.entity_id}|{log.previous_state or ''}|{log.new_state or ''}|{log.reason or ''}"
        recomputed = hashlib.sha256(payload.encode("utf-8")).hexdigest()
        
        if recomputed != log.curr_hash:
            return AuditIntegrityCheckResponse(
                total_records=len(logs),
                is_chain_valid=False,
                broken_block_id=log.id,
                message=f"Tamper detected at Block #{log.id}! Payload hash signature was altered."
            )
            
        expected_prev = log.curr_hash

    return AuditIntegrityCheckResponse(
        total_records=len(logs),
        is_chain_valid=True,
        broken_block_id=None,
        message=f"All {len(logs)} cryptographic audit blocks verified authentic using SHA-256 tamper-evident hash chaining."
    )
