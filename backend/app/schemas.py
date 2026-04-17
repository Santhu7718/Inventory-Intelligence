from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# -------- USER --------
class UserCreate(BaseModel):
    name: str
    role: str
    department: str

class UserResponse(BaseModel):
    id: int
    name: str
    role: str
    department: str
    class Config:
        from_attributes = True

# -------- MATERIAL --------
class MaterialCreate(BaseModel):
    name: str
    total_stock: int
    reorder_level: int

class MaterialUpdate(BaseModel):
    name: Optional[str] = None
    total_stock: Optional[int] = None
    reorder_level: Optional[int] = None

class MaterialResponse(BaseModel):
    id: int
    name: str
    total_stock: int
    reorder_level: int
    class Config:
        from_attributes = True

# -------- REQUEST ITEM --------
class RequestItemCreate(BaseModel):
    material_id: int
    requested_qty: int

class RequestItemResponse(BaseModel):
    id: int
    material_id: int
    requested_qty: int
    approved_qty: Optional[int]
    issued_qty: Optional[int]
    class Config:
        from_attributes = True

# -------- REQUEST --------
class RequestCreate(BaseModel):
    employee_id: int
    items: List[RequestItemCreate]

class RequestResponse(BaseModel):
    id: int
    employee_id: int
    status: str
    items: List[RequestItemResponse]
    class Config:
        from_attributes = True

# -------- CONSUMPTION LOG --------
class ConsumptionLogResponse(BaseModel):
    id: int
    material_id: int
    quantity: int
    consumed_at: datetime
    request_id: Optional[int]
    class Config:
        from_attributes = True

# -------- VENDOR --------
class VendorCreate(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    material_id: int
    unit_cost: Optional[float] = None

class VendorResponse(BaseModel):
    id: int
    name: str
    email: Optional[str]
    phone: Optional[str]
    material_id: int
    unit_cost: Optional[float]
    class Config:
        from_attributes = True

# -------- PURCHASE ORDER --------
class PurchaseOrderCreate(BaseModel):
    material_id: int
    vendor_id: Optional[int] = None
    quantity_ordered: int
    unit_cost: Optional[float] = None
    notes: Optional[str] = None

class PurchaseOrderResponse(BaseModel):
    id: int
    material_id: int
    vendor_id: Optional[int]
    quantity_ordered: int
    unit_cost: Optional[float]
    total_cost: Optional[float]
    status: str
    created_at: datetime
    notes: Optional[str]
    class Config:
        from_attributes = True

# -------- RFID SCAN --------
class RFIDScanCreate(BaseModel):
    material_id: Optional[int] = None
    scan_data: str
    scan_type: str = "QR_IN"
    gate_id: Optional[str] = None

class RFIDScanResponse(BaseModel):
    id: int
    material_id: Optional[int]
    scan_data: str
    scan_type: str
    gate_id: Optional[str]
    scanned_at: datetime
    class Config:
        from_attributes = True
