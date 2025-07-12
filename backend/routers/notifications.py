from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from db.database import get_db
from utils.auth_utils import get_current_user_id, get_current_user
from services.notification_service import NotificationService
from models.user import User

router = APIRouter(prefix="/notifications", tags=["notifications"])

@router.get("/", response_model=List[dict])
def get_user_notifications(
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Get all notifications for the current user"""
    notifications = NotificationService.get_user_notifications(db, current_user_id)
    
    result = []
    for notification in notifications:
        result.append({
            "id": notification.id,
            "type": notification.type,
            "title": notification.title,
            "message": notification.message,
            "related_id": notification.related_id,
            "is_read": notification.is_read,
            "created_at": notification.created_at.isoformat() if notification.created_at else None
        })
    
    return result

@router.patch("/{notification_id}/read", response_model=dict)
def mark_notification_as_read(
    notification_id: str,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Mark a notification as read"""
    notification = NotificationService.mark_as_read(db, notification_id, current_user_id)
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    return {
        "id": notification.id,
        "is_read": notification.is_read
    }

@router.delete("/{notification_id}", response_model=dict)
def delete_notification(
    notification_id: str,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Delete a notification"""
    success = NotificationService.delete_notification(db, notification_id, current_user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    return {
        "id": notification_id,
        "deleted": True
    }

@router.get("/platform-messages", response_model=List[dict])
def get_platform_messages(
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Get all platform messages"""
    messages = NotificationService.get_platform_messages(db)
    
    result = []
    for message in messages:
        result.append({
            "id": message.id,
            "message": message.message,
            "admin_id": message.admin_id,
            "admin_name": message.admin_name,
            "created_at": message.created_at.isoformat() if message.created_at else None
        })
    
    return result 