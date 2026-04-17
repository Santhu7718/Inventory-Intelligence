from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Text, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    role = Column(String)  # EMPLOYEE, HOD, STORE
    department = Column(String)

class Material(Base):
    __tablename__ = "materials"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    total_stock = Column(Integer)
    reorder_level = Column(Integer)

class Request(Base):
    __tablename__ = "requests"
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("users.id"))
    status = Column(String, default="PENDING")
    created_at = Column(DateTime, default=datetime.utcnow)
    items = relationship("RequestItem", backref="request", cascade="all, delete")

class RequestItem(Base):
    __tablename__ = "request_items"
    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("requests.id"))
    material_id = Column(Integer, ForeignKey("materials.id"))
    requested_qty = Column(Integer)
    approved_qty = Column(Integer, nullable=True)
    issued_qty = Column(Integer, nullable=True)

class Notification(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True, index=True)
    target_role = Column(String)
    notification_type = Column(String)
    message = Column(Text)
    request_id = Column(Integer, nullable=True)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

# ─── NEW MODELS ────────────────────────────────────────────────────────────────

class ConsumptionLog(Base):
    """Tracks every material issue for AI forecasting."""
    __tablename__ = "consumption_logs"
    id = Column(Integer, primary_key=True, index=True)
    material_id = Column(Integer, ForeignKey("materials.id"))
    quantity = Column(Integer)
    consumed_at = Column(DateTime, default=datetime.utcnow)
    request_id = Column(Integer, nullable=True)

class Vendor(Base):
    """Vendor linked to a material for auto-PO creation."""
    __tablename__ = "vendors"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    material_id = Column(Integer, ForeignKey("materials.id"))
    unit_cost = Column(Float, nullable=True)

class PurchaseOrder(Base):
    """Auto-generated or manual Purchase Orders."""
    __tablename__ = "purchase_orders"
    id = Column(Integer, primary_key=True, index=True)
    material_id = Column(Integer, ForeignKey("materials.id"))
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=True)
    quantity_ordered = Column(Integer)
    unit_cost = Column(Float, nullable=True)
    total_cost = Column(Float, nullable=True)
    status = Column(String, default="DRAFT")  # DRAFT, SENT, RECEIVED
    created_at = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text, nullable=True)

class RFIDScan(Base):
    """Logs QR code and RFID scan events from gates/scanners."""
    __tablename__ = "rfid_scans"
    id = Column(Integer, primary_key=True, index=True)
    material_id = Column(Integer, ForeignKey("materials.id"), nullable=True)
    scan_data = Column(String)
    scan_type = Column(String, default="QR_IN")  # QR_IN, QR_OUT, RFID_IN, RFID_OUT
    gate_id = Column(String, nullable=True)
    scanned_at = Column(DateTime, default=datetime.utcnow)
