from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models
from datetime import datetime, timedelta
from collections import defaultdict
import random

router = APIRouter(prefix="/forecast", tags=["AI Forecasting"])


def holt_double_exponential(data: list, periods: int = 12, alpha: float = 0.4, beta: float = 0.2) -> list:
    """
    Holt's Double Exponential Smoothing — industry-standard demand forecasting.
    Handles trend direction automatically (growing or declining demand).
    """
    if not data:
        return [0] * periods
    if len(data) == 1:
        return [max(0, int(data[0]))] * periods

    s = float(data[0])
    b = float(data[1] - data[0])

    for x in data[1:]:
        s_prev, b_prev = s, b
        s = alpha * x + (1 - alpha) * (s_prev + b_prev)
        b = beta * (s - s_prev) + (1 - beta) * b_prev

    return [max(0, int(round(s + i * b))) for i in range(1, periods + 1)]


def get_monthly_consumption(material_id: int, db: Session):
    """Aggregate consumption logs into 12 monthly buckets."""
    now = datetime.utcnow()
    monthly = {}
    for i in range(11, -1, -1):
        d = (now.replace(day=1) - timedelta(days=30 * i))
        monthly[d.strftime("%Y-%m")] = 0

    logs = db.query(models.ConsumptionLog).filter(
        models.ConsumptionLog.material_id == material_id,
        models.ConsumptionLog.consumed_at >= now - timedelta(days=365)
    ).all()

    for log in logs:
        key = log.consumed_at.strftime("%Y-%m")
        if key in monthly:
            monthly[key] += log.quantity

    months = sorted(monthly.keys())
    return months, [monthly[m] for m in months]


def future_month_labels(periods: int = 12) -> list:
    now = datetime.utcnow()
    return [(now + timedelta(days=30 * i)).strftime("%Y-%m") for i in range(1, periods + 1)]


@router.get("/{material_id}")
def forecast_material(material_id: int, db: Session = Depends(get_db)):
    mat = db.query(models.Material).filter(models.Material.id == material_id).first()
    if not mat:
        raise HTTPException(status_code=404, detail="Material not found")

    months, history = get_monthly_consumption(material_id, db)
    forecast_values = holt_double_exponential(history)
    avg_demand = sum(forecast_values) / 12 if any(forecast_values) else 0

    return {
        "material_id": material_id,
        "material_name": mat.name,
        "historical": {"months": months, "values": history},
        "forecast": {
            "months": future_month_labels(),
            "values": forecast_values,
            "upper": [int(v * 1.2) for v in forecast_values],
            "lower": [max(0, int(v * 0.8)) for v in forecast_values],
        },
        "summary": {
            "avg_monthly_demand": round(avg_demand, 1),
            "trend": ("📈 Increasing" if forecast_values and forecast_values[-1] > forecast_values[0]
                      else "📉 Decreasing" if forecast_values and forecast_values[-1] < forecast_values[0]
                      else "➡️ Stable"),
            "reorder_level": mat.reorder_level,
            "current_stock": mat.total_stock,
            "months_of_stock": round(mat.total_stock / avg_demand, 1) if avg_demand > 0 else 999,
        }
    }


@router.get("/all/summary")
def forecast_all_summary(db: Session = Depends(get_db)):
    results = []
    for mat in db.query(models.Material).all():
        _, history = get_monthly_consumption(mat.id, db)
        fc = holt_double_exponential(history)
        avg = sum(fc) / 12 if any(fc) else 0
        trend = ("📈 Up" if fc and fc[-1] > fc[0] else "📉 Down" if fc and fc[-1] < fc[0] else "➡️ Stable")
        results.append({
            "material_id": mat.id,
            "material_name": mat.name,
            "avg_monthly_demand": round(avg, 1),
            "trend": trend,
            "current_stock": mat.total_stock,
            "months_of_stock": round(mat.total_stock / avg, 1) if avg > 0 else 999,
        })
    return results


@router.post("/seed/{material_id}")
def seed_consumption_history(material_id: int, db: Session = Depends(get_db)):
    """Seeds 12 months of synthetic consumption history for demo/testing."""
    mat = db.query(models.Material).filter(models.Material.id == material_id).first()
    if not mat:
        raise HTTPException(status_code=404, detail="Material not found")

    db.query(models.ConsumptionLog).filter(
        models.ConsumptionLog.material_id == material_id
    ).delete()

    now = datetime.utcnow()
    base = max(5, mat.reorder_level // 2)
    trend = random.uniform(-0.02, 0.06)
    seeded = 0

    for offset in range(11, -1, -1):
        month_date = now - timedelta(days=30 * offset)
        monthly_qty = max(1, int(base * (1 + trend) ** (11 - offset) + random.gauss(0, base * 0.15)))
        entries = random.randint(2, 4)
        remaining = monthly_qty
        for j in range(entries):
            qty = (remaining // (entries - j)) if j < entries - 1 else remaining
            qty = max(1, qty)
            remaining -= qty
            entry_date = month_date.replace(day=1) + timedelta(days=random.randint(0, 27))
            db.add(models.ConsumptionLog(
                material_id=material_id,
                quantity=qty,
                consumed_at=entry_date
            ))
            seeded += 1

    db.commit()
    return {"message": f"Seeded {seeded} records for '{mat.name}'", "material_id": material_id}
