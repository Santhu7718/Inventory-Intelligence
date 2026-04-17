from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional
from ..database import get_db
from .. import models

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("/")
def get_notifications(role: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(models.Notification).order_by(models.Notification.created_at.desc())
    if role:
        query = query.filter(
            (models.Notification.target_role == role) |
            (models.Notification.target_role == "ALL")
        )
    return query.all()


@router.get("/unread-count")
def get_unread_count(role: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(models.Notification).filter(models.Notification.is_read == False)
    if role:
        query = query.filter(
            (models.Notification.target_role == role) |
            (models.Notification.target_role == "ALL")
        )
    return {"count": query.count()}


@router.put("/{notification_id}/read")
def mark_read(notification_id: int, db: Session = Depends(get_db)):
    notif = db.query(models.Notification).filter(models.Notification.id == notification_id).first()
    if notif:
        notif.is_read = True
        db.commit()
    return {"message": "Marked as read"}


@router.put("/mark-all-read")
def mark_all_read(role: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(models.Notification).filter(models.Notification.is_read == False)
    if role:
        query = query.filter(
            (models.Notification.target_role == role) |
            (models.Notification.target_role == "ALL")
        )
    query.update({"is_read": True}, synchronize_session=False)
    db.commit()
    return {"message": "All notifications marked as read"}
