"""
Admin Routes

API endpoints for admin functionality including user management.
All routes require admin authentication.
"""

from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import Optional, List
from datetime import datetime, timedelta
from pydantic import BaseModel

from app.db.session import get_db
from app.core.security import get_current_active_user
from app.users.models import User
from app.interviews.models import InterviewSession
from app.resumes.models import Resume


router = APIRouter()


# ===========================================
# ADMIN DEPENDENCY
# ===========================================


def get_current_admin(
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> dict:
    """
    Verify current user is an admin.
    Raises 403 if not admin.
    """
    user = db.query(User).filter(User.id == current_user["id"]).first()
    if not user or not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


# ===========================================
# PYDANTIC SCHEMAS
# ===========================================


class UserUpdateRequest(BaseModel):
    name: Optional[str] = None
    is_active: Optional[bool] = None
    is_admin: Optional[bool] = None


class UserStatsResponse(BaseModel):
    total_users: int
    active_users: int
    new_users_this_week: int
    total_interviews: int
    total_resumes: int


# ===========================================
# ADMIN ENDPOINTS
# ===========================================


@router.get(
    "/stats",
    summary="Get admin dashboard stats",
    description="Get overall platform statistics for admin dashboard."
)
async def get_admin_stats(
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get platform-wide statistics."""
    # Total users
    total_users = db.query(func.count(User.id)).scalar() or 0
    
    # Active users
    active_users = db.query(func.count(User.id)).filter(User.is_active == True).scalar() or 0
    
    # New users this week
    week_ago = datetime.utcnow() - timedelta(days=7)
    new_users_this_week = db.query(func.count(User.id)).filter(
        User.created_at >= week_ago
    ).scalar() or 0
    
    # Total interviews
    total_interviews = db.query(func.count(InterviewSession.id)).scalar() or 0
    
    # Total resumes
    total_resumes = db.query(func.count(Resume.id)).scalar() or 0
    
    return {
        "success": True,
        "stats": {
            "total_users": total_users,
            "active_users": active_users,
            "new_users_this_week": new_users_this_week,
            "total_interviews": total_interviews,
            "total_resumes": total_resumes,
        }
    }


@router.get(
    "/users",
    summary="List all users",
    description="Get paginated list of all users with filtering options."
)
async def list_users(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search by name or email"),
    status: Optional[str] = Query(None, description="Filter by status: active, inactive, all"),
    sort_by: Optional[str] = Query("created_at", description="Sort field"),
    sort_order: Optional[str] = Query("desc", description="Sort order: asc, desc"),
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get paginated list of all users."""
    # Base query
    query = db.query(User)
    
    # Search filter
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (User.name.ilike(search_pattern)) | 
            (User.email.ilike(search_pattern))
        )
    
    # Status filter
    if status == "active":
        query = query.filter(User.is_active == True)
    elif status == "inactive":
        query = query.filter(User.is_active == False)
    
    # Get total count before pagination
    total = query.count()
    
    # Sorting
    sort_column = getattr(User, sort_by, User.created_at)
    if sort_order == "desc":
        query = query.order_by(desc(sort_column))
    else:
        query = query.order_by(sort_column)
    
    # Pagination
    offset = (page - 1) * limit
    users = query.offset(offset).limit(limit).all()
    
    # Get interview counts for each user
    user_ids = [u.id for u in users]
    interview_counts = {}
    if user_ids:
        counts = db.query(
            InterviewSession.user_id,
            func.count(InterviewSession.id)
        ).filter(
            InterviewSession.user_id.in_(user_ids)
        ).group_by(InterviewSession.user_id).all()
        interview_counts = {uid: count for uid, count in counts}
    
    # Format response
    users_data = []
    for user in users:
        user_dict = user.to_dict()
        user_dict["interview_count"] = interview_counts.get(user.id, 0)
        users_data.append(user_dict)
    
    return {
        "success": True,
        "users": users_data,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": (total + limit - 1) // limit
        }
    }


@router.get(
    "/users/{user_id}",
    summary="Get user details",
    description="Get detailed information about a specific user."
)
async def get_user_details(
    user_id: str,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get detailed user information including activity stats."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get interview count
    interview_count = db.query(func.count(InterviewSession.id)).filter(
        InterviewSession.user_id == user_id
    ).scalar() or 0
    
    # Get resume count
    resume_count = db.query(func.count(Resume.id)).filter(
        Resume.user_id == user_id
    ).scalar() or 0
    
    # Get recent interviews
    recent_interviews = db.query(InterviewSession).filter(
        InterviewSession.user_id == user_id
    ).order_by(desc(InterviewSession.created_at)).limit(5).all()
    
    return {
        "success": True,
        "user": {
            **user.to_dict(),
            "interview_count": interview_count,
            "resume_count": resume_count,
            "recent_interviews": [
                {
                    "id": i.id,
                    "status": i.status,
                    "target_role": i.target_role,
                    "overall_score": i.overall_score,
                    "created_at": i.created_at.isoformat() if i.created_at else None
                }
                for i in recent_interviews
            ]
        }
    }


@router.put(
    "/users/{user_id}",
    summary="Update user",
    description="Update user details (admin only)."
)
async def update_user(
    user_id: str,
    request: UserUpdateRequest,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Update user information."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Prevent admin from deactivating themselves
    if user_id == current_admin["id"]:
        if request.is_active is False:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot deactivate your own account"
            )
        if request.is_admin is False:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot remove your own admin privileges"
            )
    
    # Update fields
    if request.name is not None:
        user.name = request.name.strip()
    if request.is_active is not None:
        user.is_active = request.is_active
    if request.is_admin is not None:
        user.is_admin = request.is_admin
    
    user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(user)
    
    return {
        "success": True,
        "message": "User updated successfully",
        "user": user.to_dict()
    }


@router.delete(
    "/users/{user_id}",
    summary="Delete user",
    description="Permanently delete a user account (admin only)."
)
async def delete_user(
    user_id: str,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Delete a user account permanently."""
    if user_id == current_admin["id"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Delete user
    db.delete(user)
    db.commit()
    
    return {
        "success": True,
        "message": f"User {user.email} deleted successfully"
    }


@router.post(
    "/users/{user_id}/toggle-admin",
    summary="Toggle admin status",
    description="Toggle admin privileges for a user."
)
async def toggle_admin_status(
    user_id: str,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Toggle admin status for a user."""
    if user_id == current_admin["id"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot modify your own admin status"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.is_admin = not user.is_admin
    user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(user)
    
    action = "granted" if user.is_admin else "revoked"
    return {
        "success": True,
        "message": f"Admin privileges {action} for {user.email}",
        "user": user.to_dict()
    }


@router.post(
    "/users/{user_id}/toggle-status",
    summary="Toggle user active status",
    description="Enable or disable a user account."
)
async def toggle_user_status(
    user_id: str,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Toggle active status for a user."""
    if user_id == current_admin["id"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot modify your own account status"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.is_active = not user.is_active
    user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(user)
    
    action = "activated" if user.is_active else "deactivated"
    return {
        "success": True,
        "message": f"User {user.email} {action}",
        "user": user.to_dict()
    }
