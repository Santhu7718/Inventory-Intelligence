from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models
from datetime import datetime, timedelta
from collections import defaultdict
import io, csv

router = APIRouter(prefix="/analytics", tags=["Analytics"])


def _last_12_months() -> list:
    now = datetime.utcnow()
    return [(now - timedelta(days=30 * i)).strftime("%Y-%m") for i in range(11, -1, -1)]


@router.get("/heatmap")
def get_heatmap(db: Session = Depends(get_db)):
    """Consumption heatmap: materials × months matrix."""
    months = _last_12_months()
    materials = db.query(models.Material).all()
    mat_map = {m.id: m.name for m in materials}

    data = {m.id: {mo: 0 for mo in months} for m in materials}

    logs = db.query(models.ConsumptionLog).filter(
        models.ConsumptionLog.consumed_at >= datetime.utcnow() - timedelta(days=365)
    ).all()
    for log in logs:
        key = log.consumed_at.strftime("%Y-%m")
        if log.material_id in data and key in data[log.material_id]:
            data[log.material_id][key] += log.quantity

    rows = []
    for mat_id, monthly in data.items():
        row = {"material": mat_map.get(mat_id, f"Mat #{mat_id}")}
        row.update(monthly)
        rows.append(row)

    return {"months": months, "data": rows}


@router.get("/trends")
def get_trends(db: Session = Depends(get_db)):
    """Month-over-month total consumption trend."""
    months = _last_12_months()
    totals = defaultdict(int)

    logs = db.query(models.ConsumptionLog).filter(
        models.ConsumptionLog.consumed_at >= datetime.utcnow() - timedelta(days=365)
    ).all()
    for log in logs:
        totals[log.consumed_at.strftime("%Y-%m")] += log.quantity

    return {"months": months, "totals": [totals.get(m, 0) for m in months]}


@router.get("/top-materials")
def get_top_materials(db: Session = Depends(get_db)):
    logs = db.query(models.ConsumptionLog).filter(
        models.ConsumptionLog.consumed_at >= datetime.utcnow() - timedelta(days=365)
    ).all()
    per_mat = defaultdict(int)
    for l in logs:
        per_mat[l.material_id] += l.quantity

    mat_map = {m.id: m.name for m in db.query(models.Material).all()}
    return [
        {"material_id": mid, "material": mat_map.get(mid, f"#{mid}"), "total_consumed": qty}
        for mid, qty in sorted(per_mat.items(), key=lambda x: -x[1])
    ]


@router.get("/summary")
def get_summary(db: Session = Depends(get_db)):
    now = datetime.utcnow()
    logs_30 = db.query(models.ConsumptionLog).filter(
        models.ConsumptionLog.consumed_at >= now - timedelta(days=30)).all()
    logs_365 = db.query(models.ConsumptionLog).filter(
        models.ConsumptionLog.consumed_at >= now - timedelta(days=365)).all()

    total_30 = sum(l.quantity for l in logs_30)
    total_365 = sum(l.quantity for l in logs_365)

    per_mat = defaultdict(int)
    for l in logs_365:
        per_mat[l.material_id] += l.quantity

    top_id = max(per_mat, key=per_mat.get) if per_mat else None
    top_name = None
    if top_id:
        m = db.query(models.Material).filter(models.Material.id == top_id).first()
        top_name = m.name if m else None

    return {
        "total_units_last_30_days": total_30,
        "total_units_last_year": total_365,
        "avg_monthly_consumption": round(total_365 / 12, 1),
        "top_consuming_material": top_name,
        "active_materials": len(per_mat),
    }


@router.get("/export/csv")
def export_csv(db: Session = Depends(get_db)):
    """Export all consumption data as CSV — compatible with Power BI."""
    logs = db.query(models.ConsumptionLog).all()
    mat_map = {m.id: m.name for m in db.query(models.Material).all()}

    out = io.StringIO()
    w = csv.writer(out)
    w.writerow(["Log ID", "Material ID", "Material Name", "Quantity Consumed", "Date"])
    for l in logs:
        w.writerow([l.id, l.material_id, mat_map.get(l.material_id, "Unknown"),
                    l.quantity, l.consumed_at.strftime("%Y-%m-%d %H:%M:%S")])
    out.seek(0)
    return StreamingResponse(
        iter([out.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=consumption_data.csv"}
    )
