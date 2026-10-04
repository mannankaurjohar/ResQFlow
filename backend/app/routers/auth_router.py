from fastapi import APIRouter, Depends, HTTPException, status, Form
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, UserRole
from app.schemas import (
    UserLogin,
    Token,
    UserResponse,
    WorkerCreate,
    WorkerCreateResponse,
    WorkerResetPasswordResponse,
    ChangePasswordRequest,
)
from app.auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    get_current_user,
)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post("/login", response_model=Token)
def login(
    login_data: UserLogin,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(
        User.username == login_data.username
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid login credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )

    if not verify_password(
        login_data.password,
        user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid login credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if user.role != login_data.role:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid login credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={
            "sub": user.username,
            "role": user.role.value
        }
    )

    return Token(
        access_token=access_token,
        token_type="bearer",
        user=user,
        password_reset_required=user.password_reset_required
    )

@router.post("/token")
def oauth2_token(
    username: str = Form(...),
    password: str = Form(...),
    scope: str = Form(""),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(
        User.username == username
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid login credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )

    if not verify_password(
        password,
        user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid login credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    requested_scopes = scope.split()

    if len(requested_scopes) != 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Select exactly one role"
        )

    requested_role = requested_scopes[0]

    actual_role = (
        user.role.value
        if hasattr(user.role, "value")
        else str(user.role)
    )

    if requested_role != actual_role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Selected role does not match user role"
        )

    access_token = create_access_token(
        data={
            "sub": user.username,
            "role": actual_role
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "password_reset_required": user.password_reset_required
    }
@router.get("/me", response_model=UserResponse)
def get_me(
    current_user: User = Depends(get_current_user)
):
    return current_user
# -------------------------------------------------
# ADMIN USER MANAGEMENT
# -------------------------------------------------

import secrets
import string


def generate_login_id(role: UserRole, db: Session) -> str:
    """
    Generate a unique login ID based on the user's role.
    Example: volunteer_4827
    """
    prefix = role.value.lower()

    while True:
        number = secrets.randbelow(9000) + 1000
        login_id = f"{prefix}_{number}"

        existing = db.query(User).filter(
            User.username == login_id
        ).first()

        if not existing:
            return login_id


def generate_temporary_password(length: int = 14) -> str:
    """
    Generate a secure temporary password.
    """
    alphabet = string.ascii_letters + string.digits + "@#$%&*!?"

    return "".join(
        secrets.choice(alphabet)
        for _ in range(length)
    )


@router.post(
    "/workers",
    response_model=WorkerCreateResponse
)
def create_worker(
    worker_data: WorkerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Only ADMIN can create accounts
    if current_user.role not in [
        UserRole.ADMIN,
        UserRole.EMERGENCY_COORDINATOR
    ]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators and emergency coordinators can view users"
        )

    # Generate credentials on the backend
    login_id = generate_login_id(worker_data.role, db)
    temporary_password = generate_temporary_password()

    # Use a generated internal email if none was provided
    email = worker_data.email

    if email is None:
        email = f"{login_id}@resqflow.local"
    else:
        existing_email = db.query(User).filter(
            User.email == str(email)
        ).first()

        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists"
            )

    new_user = User(
        username=login_id,
        email=str(email),
        full_name=worker_data.full_name.strip(),
        hashed_password=get_password_hash(temporary_password),
        role=worker_data.role,
        organization_id=worker_data.organization_id,
        phone=worker_data.phone,
        assigned_warehouse_id=worker_data.assigned_warehouse_id,
        is_active=True,
        password_reset_required=True
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return WorkerCreateResponse(
        user=new_user,
        login_id=login_id,
        temporary_password=temporary_password
    )


@router.get(
    "/workers",
    response_model=list[UserResponse]
)
def get_all_workers(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Only ADMIN can view all users
    if current_user.role not in [
        UserRole.ADMIN,
        UserRole.EMERGENCY_COORDINATOR
    ]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators and emergency coordinators can view users"
        )

    return db.query(User).order_by(User.id.asc()).all()


@router.post(
    "/workers/{user_id}/reset-password",
    response_model=WorkerResetPasswordResponse
)
def reset_worker_password(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Only ADMIN can reset another user's password
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can reset passwords"
        )

    user = db.query(User).filter(
        User.id == user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Generate a new temporary password
    temporary_password = generate_temporary_password()

    user.hashed_password = get_password_hash(
        temporary_password
    )
    user.password_reset_required = True
    db.commit()
    db.refresh(user)

    return WorkerResetPasswordResponse(
        user=user,
        login_id=user.username,
        temporary_password=temporary_password
    )


@router.post(
    "/change-password",
    response_model=UserResponse
)
def change_password(
    password_data: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Verify current password
    if not verify_password(
        password_data.current_password,
        current_user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )

    # Prevent using the same password
    if password_data.current_password == password_data.new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be different from current password"
        )

    current_user.hashed_password = get_password_hash(
        password_data.new_password
    )

    current_user.password_reset_required = False

    db.commit()
    db.refresh(current_user)

    return current_user