from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, schemas

router = APIRouter(prefix="/materials", tags=["Materials"])


@router.post("/", response_model=schemas.MaterialResponse)
def create_material(material: schemas.MaterialCreate, db: Session = Depends(get_db)):
    db_material = models.Material(
        name=material.name,
        total_stock=material.total_stock,
        reorder_level=material.reorder_level,
    )
    db.add(db_material)
    db.commit()
    db.refresh(db_material)
    return db_material


@router.get("/", response_model=list[schemas.MaterialResponse])
def get_materials(db: Session = Depends(get_db)):
    return db.query(models.Material).all()


@router.get("/{material_id}", response_model=schemas.MaterialResponse)
def get_material(material_id: int, db: Session = Depends(get_db)):
    mat = db.query(models.Material).filter(models.Material.id == material_id).first()
    if not mat:
        raise HTTPException(status_code=404, detail="Material not found")
    return mat


@router.put("/{material_id}", response_model=schemas.MaterialResponse)
def update_material(material_id: int, update: schemas.MaterialUpdate, db: Session = Depends(get_db)):
    mat = db.query(models.Material).filter(models.Material.id == material_id).first()
    if not mat:
        raise HTTPException(status_code=404, detail="Material not found")
    for field, value in update.model_dump(exclude_unset=True).items():
        setattr(mat, field, value)
    db.commit()
    db.refresh(mat)
    return mat


@router.delete("/{material_id}")
def delete_material(material_id: int, db: Session = Depends(get_db)):
    mat = db.query(models.Material).filter(models.Material.id == material_id).first()
    if not mat:
        raise HTTPException(status_code=404, detail="Material not found")
    db.delete(mat)
    db.commit()
    return {"message": f"Material '{mat.name}' deleted"}
