from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from .. import models, schemas

router = APIRouter(prefix="/vendors", tags=["Vendors & Purchase Orders"])


# ──────────────────── VENDORS ────────────────────────────────────────────────

@router.get("/", response_model=List[schemas.VendorResponse])
def get_vendors(db: Session = Depends(get_db)):
    return db.query(models.Vendor).all()


@router.post("/", response_model=schemas.VendorResponse)
def create_vendor(vendor: schemas.VendorCreate, db: Session = Depends(get_db)):
    db_vendor = models.Vendor(**vendor.model_dump())
    db.add(db_vendor)
    db.commit()
    db.refresh(db_vendor)
    return db_vendor


@router.delete("/{vendor_id}")
def delete_vendor(vendor_id: int, db: Session = Depends(get_db)):
    vendor = db.query(models.Vendor).filter(models.Vendor.id == vendor_id).first()
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    db.delete(vendor)
    db.commit()
    return {"message": "Vendor removed"}


# ──────────────────── PURCHASE ORDERS ────────────────────────────────────────

@router.get("/purchase-orders", response_model=List[schemas.PurchaseOrderResponse])
def get_purchase_orders(db: Session = Depends(get_db)):
    return db.query(models.PurchaseOrder).order_by(
        models.PurchaseOrder.created_at.desc()
    ).all()


@router.post("/purchase-orders", response_model=schemas.PurchaseOrderResponse)
def create_purchase_order(po: schemas.PurchaseOrderCreate, db: Session = Depends(get_db)):
    total = (po.unit_cost * po.quantity_ordered) if po.unit_cost else None
    db_po = models.PurchaseOrder(
        material_id=po.material_id,
        vendor_id=po.vendor_id,
        quantity_ordered=po.quantity_ordered,
        unit_cost=po.unit_cost,
        total_cost=total,
        notes=po.notes,
        status="DRAFT",
    )
    db.add(db_po)
    db.commit()
    db.refresh(db_po)
    return db_po


@router.put("/purchase-orders/{po_id}/send")
def send_purchase_order(po_id: int, db: Session = Depends(get_db)):
    po = db.query(models.PurchaseOrder).filter(models.PurchaseOrder.id == po_id).first()
    if not po:
        raise HTTPException(status_code=404, detail="PO not found")

    vendor = db.query(models.Vendor).filter(models.Vendor.id == po.vendor_id).first() if po.vendor_id else None
    material = db.query(models.Material).filter(models.Material.id == po.material_id).first()

    email_sent = False
    if vendor and vendor.email:
        try:
            _send_po_email(vendor, material, po)
            email_sent = True
        except Exception:
            pass  # Email is optional — don't fail the PO

    po.status = "SENT"
    db.commit()
    return {"message": "PO marked as SENT", "email_sent": email_sent}


@router.put("/purchase-orders/{po_id}/receive")
def receive_purchase_order(po_id: int, db: Session = Depends(get_db)):
    po = db.query(models.PurchaseOrder).filter(models.PurchaseOrder.id == po_id).first()
    if not po:
        raise HTTPException(status_code=404, detail="PO not found")

    material = db.query(models.Material).filter(models.Material.id == po.material_id).first()
    if material:
        material.total_stock += po.quantity_ordered

    po.status = "RECEIVED"
    db.commit()
    return {"message": "PO received — stock updated", "new_stock": material.total_stock if material else None}


@router.post("/auto-create-pos")
def auto_create_purchase_orders(db: Session = Depends(get_db)):
    """
    Scan all materials — auto-create DRAFT POs for any below reorder level.
    Order quantity = 3× reorder level (smart restocking).
    """
    materials = db.query(models.Material).all()
    created = []

    for mat in materials:
        if mat.total_stock <= mat.reorder_level:
            vendor = db.query(models.Vendor).filter(models.Vendor.material_id == mat.id).first()
            order_qty = mat.reorder_level * 3

            db_po = models.PurchaseOrder(
                material_id=mat.id,
                vendor_id=vendor.id if vendor else None,
                quantity_ordered=order_qty,
                unit_cost=vendor.unit_cost if vendor else None,
                total_cost=(vendor.unit_cost * order_qty) if (vendor and vendor.unit_cost) else None,
                notes=f"Auto-PO: {mat.name} at {mat.total_stock} units (reorder: {mat.reorder_level})",
                status="DRAFT",
            )
            db.add(db_po)
            created.append({
                "material": mat.name,
                "vendor": vendor.name if vendor else "No vendor assigned",
                "quantity": order_qty,
                "current_stock": mat.total_stock,
            })

    db.commit()
    return {"created": created, "count": len(created)}


def _send_po_email(vendor, material, po):
    """Optional: send PO email via SMTP. Set SMTP_USER and SMTP_PASS env vars."""
    import smtplib, os
    from email.mime.text import MIMEText

    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")
    if not smtp_user or not smtp_pass:
        return

    body = f"""Dear {vendor.name},

Purchase Order: PO-{po.id:04d}
Material: {material.name}
Quantity: {po.quantity_ordered} units
Unit Cost: {'${:.2f}'.format(po.unit_cost) if po.unit_cost else 'TBD'}
Total: {'${:.2f}'.format(po.total_cost) if po.total_cost else 'TBD'}
Notes: {po.notes or '-'}

Please confirm receipt and expected delivery date.

Inventory Intelligence System"""

    msg = MIMEText(body)
    msg["Subject"] = f"PO-{po.id:04d} — {material.name} ({po.quantity_ordered} units)"
    msg["From"] = smtp_user
    msg["To"] = vendor.email

    with smtplib.SMTP(os.getenv("SMTP_HOST", "smtp.gmail.com"),
                      int(os.getenv("SMTP_PORT", "587"))) as srv:
        srv.starttls()
        srv.login(smtp_user, smtp_pass)
        srv.sendmail(smtp_user, vendor.email, msg.as_string())
