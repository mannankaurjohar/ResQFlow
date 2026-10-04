from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, UserRole, Organization
from app.auth import get_current_user


router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)


@router.get("/dashboard")
def get_admin_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Only System Administrators can access this endpoint
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=403,
            detail="Administrator access required"
        )

    total_users = db.query(User).count()

    active_users = (
        db.query(User)
        .filter(User.is_active == True)
        .count()
    )

    total_roles = (
        db.query(User.role)
        .distinct()
        .count()
    )

    total_organizations = (
        db.query(Organization)
        .count()
    )

    role_distribution = {}

    for role in UserRole:
        count = (
            db.query(User)
            .filter(User.role == role)
            .count()
        )

        role_distribution[role.value] = count

    return {
        "total_users": total_users,
        "active_users": active_users,
        "total_roles": total_roles,
        "total_organizations": total_organizations,
        "role_distribution": role_distribution
    }