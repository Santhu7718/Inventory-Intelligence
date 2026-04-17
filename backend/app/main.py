from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine
from .models import Base
from .routers import users, inventory, requests, notifications, forecasting, analytics, rfid, vendors

app = FastAPI(
    title="Inventory Intelligence API",
    version="2.0",
    description="AI-powered inventory management with demand forecasting, RFID/QR integration, analytics, and vendor automation.",
)

# CORS — allows React Native mobile app and browser clients to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(users.router)
app.include_router(inventory.router)
app.include_router(requests.router)
app.include_router(notifications.router)
app.include_router(forecasting.router)
app.include_router(analytics.router)
app.include_router(rfid.router)
app.include_router(vendors.router)


@app.get("/")
def home():
    return {
        "message": "Inventory Intelligence API v2.0",
        "features": ["AI Demand Forecasting", "Advanced Analytics", "RFID/QR Scanning", "Vendor & PO Management"],
        "docs": "/docs",
    }
