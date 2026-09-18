import datetime
import hashlib
import json
from typing import Optional, List
import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import User, UserRole, AuditLog
from app.schemas import TokenData

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login", auto_error=False)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        return False

def get_password_hash(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

def create_access_token(data: dict, expires_delta: Optional[datetime.timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.datetime.utcnow() + expires_delta
    else:
        expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def get_current_user(token: Optional[str] = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Optional[User]:
    if not token:
        # Fallback default authority demo user if unauthenticated for smooth hackathon demo testing
        return db.query(User).filter(User.username == "authority_admin").first()
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid credentials token")
        token_data = TokenData(username=username, role=payload.get("role"))
    except Exception:
        raise HTTPException(status_code=401, detail="Could not validate credentials")
    
    user = db.query(User).filter(User.username == token_data.username).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

def require_role(roles: List[UserRole]):
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in roles and current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation not permitted for role {current_user.role}"
            )
        return current_user
    return role_checker

def log_audit_event(
    db: Session,
    actor_id: Optional[int],
    actor_name: str,
    actor_role: str,
    action: str,
    entity_type: str,
    entity_id: str,
    previous_state: Optional[str] = None,
    new_state: Optional[str] = None,
    reason: Optional[str] = None
) -> AuditLog:
    # 1. Fetch latest audit log for hash chaining
    last_log = db.query(AuditLog).order_by(AuditLog.id.desc()).first()
    prev_hash = last_log.curr_hash if last_log else "0" * 64
    
    now = datetime.datetime.utcnow()
    # 2. Compute SHA-256 block hash
    hash_payload = f"{prev_hash}|{now.isoformat()}|{actor_name}|{actor_role}|{action}|{entity_type}|{entity_id}|{previous_state or ''}|{new_state or ''}|{reason or ''}"
    curr_hash = hashlib.sha256(hash_payload.encode("utf-8")).hexdigest()
    
    audit_entry = AuditLog(
        actor_id=actor_id,
        actor_name=actor_name,
        actor_role=actor_role,
        action=action,
        entity_type=entity_type,
        entity_id=str(entity_id),
        previous_state=previous_state,
        new_state=new_state,
        reason=reason,
        timestamp=now,
        prev_hash=prev_hash,
        curr_hash=curr_hash
    )
    db.add(audit_entry)
    db.commit()
    db.refresh(audit_entry)
    return audit_entry
