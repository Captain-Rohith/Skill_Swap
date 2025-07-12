from sqlalchemy.orm import Session
from models.swap import Notification, PlatformMessage
from typing import List, Optional
import uuid

class NotificationService:
    @staticmethod
    def create_notification(
        db: Session,
        user_id: str,
        notification_type: str,
        title: str,
        message: str,
        related_id: Optional[str] = None
    ) -> Notification:
        """Create a new notification for a user"""
        notification = Notification(
            id=str(uuid.uuid4()),
            user_id=user_id,
            type=notification_type,
            title=title,
            message=message,
            related_id=related_id,
            is_read=False
        )
        db.add(notification)
        db.commit()
        db.refresh(notification)
        return notification

    @staticmethod
    def get_user_notifications(db: Session, user_id: str) -> List[Notification]:
        """Get all notifications for a user"""
        return db.query(Notification).filter(
            Notification.user_id == user_id
        ).order_by(Notification.created_at.desc()).all()

    @staticmethod
    def mark_as_read(db: Session, notification_id: str, user_id: str) -> Optional[Notification]:
        """Mark a notification as read"""
        notification = db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == user_id
        ).first()
        
        if notification:
            notification.is_read = True
            db.commit()
            db.refresh(notification)
        
        return notification

    @staticmethod
    def delete_notification(db: Session, notification_id: str, user_id: str) -> bool:
        """Delete a notification"""
        notification = db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == user_id
        ).first()
        
        if notification:
            db.delete(notification)
            db.commit()
            return True
        
        return False

    @staticmethod
    def create_swap_request_notification(
        db: Session,
        to_user_id: str,
        from_user_name: str,
        skill_offered: str,
        skill_wanted: str,
        swap_id: str
    ) -> Notification:
        """Create a notification for a new swap request"""
        title = f"New Swap Request from {from_user_name}"
        message = f"{from_user_name} wants to swap '{skill_offered}' for '{skill_wanted}'"
        
        return NotificationService.create_notification(
            db, to_user_id, 'swap_request', title, message, swap_id
        )

    @staticmethod
    def create_swap_response_notification(
        db: Session,
        to_user_id: str,
        from_user_name: str,
        status: str,
        swap_id: str
    ) -> Notification:
        """Create a notification for swap request response"""
        title = f"Swap Request {status.title()}"
        message = f"{from_user_name} has {status} your swap request"
        
        return NotificationService.create_notification(
            db, to_user_id, f'swap_{status}', title, message, swap_id
        )

    @staticmethod
    def create_platform_message_notification(
        db: Session,
        user_id: str,
        message: str,
        admin_name: str
    ) -> Notification:
        """Create a notification for a platform-wide message"""
        title = f"Platform Message from {admin_name}"
        
        return NotificationService.create_notification(
            db, user_id, 'platform_message', title, message
        )

    @staticmethod
    def send_platform_message(
        db: Session,
        admin_id: str,
        admin_name: str,
        message: str
    ) -> PlatformMessage:
        """Send a platform-wide message to all users"""
        # Create platform message record
        platform_message = PlatformMessage(
            id=str(uuid.uuid4()),
            message=message,
            admin_id=admin_id,
            admin_name=admin_name
        )
        db.add(platform_message)
        db.commit()
        db.refresh(platform_message)
        
        # Get all active users and create notifications for them
        from services.user_service import UserService
        users = UserService.get_all_public_users(db)
        
        for user in users:
            if user.id != admin_id:  # Don't notify the admin who sent the message
                NotificationService.create_platform_message_notification(
                    db, user.id, message, admin_name
                )
        
        return platform_message

    @staticmethod
    def get_platform_messages(db: Session) -> List[PlatformMessage]:
        """Get all platform messages"""
        return db.query(PlatformMessage).order_by(PlatformMessage.created_at.desc()).all() 