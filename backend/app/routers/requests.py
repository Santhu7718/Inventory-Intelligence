from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from ..database import get_db
from .. import models, schemas

router = APIRouter(prefix="/requests", tags=["Requests"])


def _notify(db: Session, target_role: str, notif_type: str, message: str, request_id: Optional[int] = None):
    """Helper to persist a notification."""
    notif = models.Notification(
        target_role=target_role,
        notification_type=notif_type,
        message=message,
        request_id=request_id,
        is_read=False,
    )
    db.add(notif)


# -------- CREATE REQUEST --------
@router.post("/", response_model=schemas.RequestResponse)
def create_request(request: schemas.RequestCreate, db: Session = Depends(get_db)):
    new_request = models.Request(
        employee_id=request.employee_id,
        status="PENDING_HOD"
    )
    db.add(new_request)
    db.commit()
    db.refresh(new_request)

    for item in request.items:
        db_item = models.RequestItem(
            request_id=new_request.id,
            material_id=item.material_id,
            requested_qty=item.requested_qty
        )
        db.add(db_item)

    db.commit()
    db.refresh(new_request)

    # 🔔 Notify HOD — approval needed
    _notify(
        db, "HOD", "APPROVAL_NEEDED",
        f"📋 New material request #{new_request.id} from Employee #{request.employee_id} is waiting for your approval.",
        new_request.id
    )
    db.commit()

    return new_request


# -------- GET ALL REQUESTS --------
@router.get("/", response_model=List[schemas.RequestResponse])
def get_all_requests(db: Session = Depends(get_db)):
    return db.query(models.Request).all()


# -------- GET SINGLE REQUEST --------
@router.get("/{request_id}", response_model=schemas.RequestResponse)
def get_request(request_id: int, db: Session = Depends(get_db)):
    req = db.query(models.Request).filter(models.Request.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
    return req


# -------- APPROVAL MODEL --------
class ApprovalUpdate(BaseModel):
    approved_quantities: list[int]


# -------- APPROVE REQUEST --------
@router.put("/{request_id}/approve")
def approve_request(request_id: int, approval: ApprovalUpdate, db: Session = Depends(get_db)):
    req = db.query(models.Request).filter(models.Request.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")

    items = db.query(models.RequestItem).filter(
        models.RequestItem.request_id == request_id
    ).all()

    if len(approval.approved_quantities) != len(items):
        raise HTTPException(
            status_code=400,
            detail="Approved quantities count must match number of request items"
        )

    for item, approved_qty in zip(items, approval.approved_quantities):
        item.approved_qty = approved_qty

    req.status = "APPROVED"
    db.commit()

    # 🔔 Notify STORE — ready to issue
    _notify(
        db, "STORE", "ISSUE_NEEDED",
        f"✅ Request #{request_id} (Employee #{req.employee_id}) has been approved by HOD and is ready for material issuance.",
        request_id
    )
    db.commit()

    return {"message": "Request Approved"}


# -------- ISSUE REQUEST --------
@router.put("/{request_id}/issue")
def issue_request(request_id: int, db: Session = Depends(get_db)):
    req = db.query(models.Request).filter(models.Request.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")

    if req.status != "APPROVED":
        raise HTTPException(
            status_code=400,
            detail="Request must be approved before issuing"
        )

    items = db.query(models.RequestItem).filter(
        models.RequestItem.request_id == request_id
    ).all()

    for item in items:
        if item.approved_qty is None:
            raise HTTPException(
                status_code=400,
                detail=f"Item ID {item.id} has not been approved yet"
            )

        material = db.query(models.Material).filter(
            models.Material.id == item.material_id
        ).first()

        if material.total_stock < item.approved_qty:
            raise HTTPException(
                status_code=400,
                detail=f"Not enough stock for material '{material.name}' (available: {material.total_stock}, needed: {item.approved_qty})"
            )

        material.total_stock -= item.approved_qty
        item.issued_qty = item.approved_qty

        # 📊 Log consumption for AI demand forecasting
        db.add(models.ConsumptionLog(
            material_id=item.material_id,
            quantity=item.approved_qty,
            consumed_at=datetime.utcnow(),
            request_id=request_id,
        ))

    req.status = "ISSUED"
    db.commit()

    # 🔔 Check for low stock after issuance and notify ALL roles
    for item in items:
        material = db.query(models.Material).filter(
            models.Material.id == item.material_id
        ).first()
        if material and material.total_stock <= material.reorder_level:
            _notify(
                db, "ALL", "LOW_STOCK",
                f"⚠️ Low stock alert: '{material.name}' is at {material.total_stock} units (reorder level: {material.reorder_level}). Restock required.",
                request_id
            )
    db.commit()

    return {"message": "Items Issued & Stock Updated"}
