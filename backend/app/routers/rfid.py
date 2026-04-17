from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, schemas
import json

router = APIRouter(prefix="/rfid", tags=["RFID & QR"])


@router.post("/scan", response_model=schemas.RFIDScanResponse)
def log_scan(scan: schemas.RFIDScanCreate, db: Session = Depends(get_db)):
    """
    Universal scan endpoint — accepts events from:
    - Physical RFID readers (via HTTP webhook)
    - QR code scanners (USB HID or mobile)
    - Manual entry from dashboard
    """
    db_scan = models.RFIDScan(
        material_id=scan.material_id,
        scan_data=scan.scan_data,
        scan_type=scan.scan_type,
        gate_id=scan.gate_id,
    )
    db.add(db_scan)
    db.commit()
    db.refresh(db_scan)
    return db_scan


@router.get("/logs", response_model=list[schemas.RFIDScanResponse])
def get_scan_logs(limit: int = 200, db: Session = Depends(get_db)):
    return db.query(models.RFIDScan).order_by(
        models.RFIDScan.scanned_at.desc()
    ).limit(limit).all()


@router.get("/qr/{material_id}")
def get_material_qr(material_id: int, db: Session = Depends(get_db)):
    """Generate QR code PNG for a material (for printing / gate scanning)."""
    mat = db.query(models.Material).filter(models.Material.id == material_id).first()
    if not mat:
        raise HTTPException(status_code=404, detail="Material not found")

    try:
        import qrcode
        from io import BytesIO

        qr_data = json.dumps({
            "material_id": mat.id,
            "name": mat.name,
            "stock": mat.total_stock,
            "reorder": mat.reorder_level,
        })

        qr = qrcode.QRCode(version=1, box_size=8, border=4)
        qr.add_data(qr_data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        buf = BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        return Response(content=buf.read(), media_type="image/png")
    except ImportError:
        raise HTTPException(status_code=500, detail="qrcode library not installed")


@router.get("/stats")
def get_rfid_stats(db: Session = Depends(get_db)):
    all_scans = db.query(models.RFIDScan).all()
    by_type = {}
    for s in all_scans:
        by_type[s.scan_type] = by_type.get(s.scan_type, 0) + 1
    return {
        "total_scans": len(all_scans),
        "by_type": by_type,
    }
