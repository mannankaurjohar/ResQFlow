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
from app.models import IST, User, UserRole, AuditLog
from app.schemas import TokenData

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/token",
    scopes={
        "ADMIN": "Administrator access",
        "EMERGENCY_COORDINATOR": "Emergency Coordinator access",
        "COMMUNITY": "Community access",
        "VOLUNTEER": "Volunteer access",
        "NGO_MANAGER": "NGO Manager access",
        "WAREHOUSE_MANAGER": "Warehouse Manager access",
        "DONOR": "Donor access",
    },
    auto_error=True
)

optional_oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/token",
    auto_error=False
)
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

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )

        username = payload.get("sub")
        token_role = payload.get("role")

        if not username or not token_role:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user = db.query(User).filter(
            User.username == username
        ).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive"
            )

        # Token role must match the actual database role
        actual_role = (
            user.role.value
            if hasattr(user.role, "value")
            else str(user.role)
        )

        if token_role != actual_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Authentication role mismatch"
            )

        return user

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )

    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
def get_optional_current_user(
    token: Optional[str] = Depends(optional_oauth2_scheme),
    db: Session = Depends(get_db)
) -> Optional[User]:

    if not token:
        return None

    return get_current_user(token=token, db=db)

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
    
    now = datetime.datetime.now(IST)

    hash_payload = (
        f"{prev_hash}|"
        f"{now.isoformat()}|"
        f"{actor_name}|"
        f"{actor_role}|"
        f"{action}|"
        f"{entity_type}|"
        f"{entity_id}|"
        f"{previous_state or ''}|"
        f"{new_state or ''}|"
        f"{reason or ''}"
    )

    curr_hash = hashlib.sha256(
        hash_payload.encode("utf-8")
    ).hexdigest()
    
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
        created_at=datetime.datetime.now(IST),
        prev_hash=prev_hash,
        curr_hash=curr_hash
    )
    db.add(audit_entry)
    db.commit()
    db.refresh(audit_entry)
    return audit_entry




