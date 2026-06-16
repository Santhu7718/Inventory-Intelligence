# 🏭 Inventory Intelligence System

An **AI-powered inventory management platform** that revolutionizes how businesses manage stock, forecast demand, and automate vendor interactions. Built with real-time RFID/QR scanning, advanced analytics, and intelligent demand forecasting.

[![FastAPI](https://img.shields.io/badge/FastAPI-v0.129.0-009688?style=flat&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?style=flat&logo=streamlit)](https://streamlit.io/)
[![React Native](https://img.shields.io/badge/React_Native-Mobile-61DAFB?style=flat&logo=react)](https://reactnative.dev/)
[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=flat&logo=python)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-336791?style=flat&logo=postgresql)](https://www.postgresql.org/)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Database Models](#database-models)
- [Contributing](#contributing)
- [License](#license)

---

## 🎯 Overview

**Inventory Intelligence System** is a comprehensive solution for modern inventory management. It combines:

- **AI-Powered Demand Forecasting** — Uses Holt's Double Exponential Smoothing to predict future demand with trend analysis
- **Real-Time Tracking** — RFID and QR code scanning for accurate stock monitoring
- **Advanced Analytics** — Consumption heatmaps, trends, and performance metrics
- **Vendor Automation** — Intelligent purchase order (PO) generation and vendor management
- **Multi-Role Access Control** — Dedicated interfaces for employees, heads of departments, and store managers
- **Real-Time Notifications** — Alerts for low stock, overstock, and order updates

### Use Cases

✅ Manufacturing facilities tracking raw materials and components  
✅ Warehouses managing multi-category inventory across gates  
✅ Hospitals optimizing medical supplies and equipment  
✅ Retail chains monitoring stock across multiple locations  
✅ E-commerce backends automating fulfillment and restocking  

---

## 🚀 Key Features

### 1. **AI Demand Forecasting**
- Holt's Double Exponential Smoothing algorithm for trend detection
- 12-month rolling forecast with automatic model adjustment
- Handles seasonal and trend variations
- Predicts demand for optimized reordering

### 2. **RFID & QR Code Integration**
- Universal scan endpoint for physical RFID readers, QR scanners, and manual entry
- Automatic QR code generation for materials
- Gate-based tracking for inbound/outbound movements
- Scan logging with timestamps and metadata

### 3. **Advanced Analytics Dashboard**
- **Consumption Heatmap** — Materials × Months visualization
- **Monthly Trends** — Track usage patterns over time
- **Stock Levels** — Current availability vs. reorder points
- **Top Consumers** — Identify high-usage materials
- **Export Reports** — CSV download for analysis
- **Real-time Metrics** — Dashboard with KPIs and alerts

### 4. **Intelligent Request Management**
- Material request workflow with approval hierarchy
- Status tracking (PENDING → APPROVED → FULFILLED)
- User-specific request history
- Automated stock deduction on fulfillment

### 5. **Vendor & Purchase Order Management**
- Vendor database with contact information and performance metrics
- Automated PO generation based on reorder levels
- PO tracking with status updates (DRAFT → SUBMITTED → DELIVERED)
- Cost analysis and vendor rating system

### 6. **Notification System**
- Low stock alerts
- Overstock warnings
- PO status updates
- User-specific notification feed

### 7. **Role-Based Access Control**
- **EMPLOYEE** — Request materials, view inventory
- **HOD** (Head of Department) — Approve requests, monitor department consumption
- **STORE** (Store Manager) — Manage inventory, configure reorder levels, generate reports

### 8. **User Authentication**
- JWT-based token authentication
- Secure password hashing with bcrypt
- Role-based endpoint authorization

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   Frontend Layer                            │
├──────────────────────┬──────────────────────┬───────────────┤
│  Streamlit Dashboard │   React Native App   │   Web UI      │
│  (Analytics & Mgmt)  │   (Mobile Scanning)  │   (Reports)   │
└──────────────────────┴──────────────────────┴───────────────┘
                              ↓
            ┌─────────────────────────────────────┐
            │      FastAPI Backend (REST API)     │
            │  Port: 8000                         │
            ├─────────────────────────────────────┤
            │ Core Routers:                       │
            │ • /users       — Authentication     │
            │ • /inventory   — Stock Management   │
            │ • /requests    — Material Requests  │
            │ • /forecast    — AI Forecasting     │
            │ • /analytics   — Reports & Heatmap │
            │ • /rfid        — Scan Integration   │
            │ • /vendors     — PO Management      │
            │ • /notify      — Notifications      │
            └─────────────────────────────────────┘
                              ↓
            ┌─────────────────────────────────────┐
            │     PostgreSQL Database             │
            │     (SQLAlchemy ORM)                │
            └─────────────────────────────────────┘
```

---

## 💾 Tech Stack

### Backend
- **Framework** — FastAPI 0.129.0 (async REST API)
- **ORM** — SQLAlchemy 2.0.46 (database abstraction)
- **Database** — PostgreSQL 11+ (production database)
- **Authentication** — JWT + bcrypt
- **Forecasting** — NumPy (Holt's Exponential Smoothing)
- **Server** — Uvicorn 0.40.0

### Frontend
- **Dashboard** — Streamlit (Python-based interactive UI)
- **Visualizations** — Plotly.js (interactive charts and heatmaps)
- **Data Processing** — Pandas (CSV export, analytics)

### Mobile
- **Framework** — React Native (iOS & Android)
- **QR/RFID Support** — Mobile camera and external scanner integration

### DevOps
- **Code Quality** — Pyright (static type checking)
- **CORS** — FastAPI middleware for cross-origin requests

---

## 📂 Project Structure

```
Inventory-Intelligence/
├── backend/                          # FastAPI backend application
│   ├── app/
│   │   ├── main.py                  # FastAPI app initialization & routing
│   │   ├── database.py              # PostgreSQL connection & session management
│   │   ├── models.py                # SQLAlchemy ORM models
│   │   ├── schemas.py               # Pydantic request/response schemas
│   │   ├── auth.py                  # JWT token generation & verification
│   │   └── routers/
│   │       ├── users.py             # User registration, login, profile
│   │       ├── inventory.py         # Material CRUD & stock management
│   │       ├── requests.py          # Material request workflow
│   │       ├── forecasting.py       # AI demand forecasting endpoints
│   │       ├── analytics.py         # Heatmap, trends, reports
│   │       ├── rfid.py              # RFID/QR scan logging & QR generation
│   │       ├── vendors.py           # Vendor & PO management
│   │       └── notifications.py     # Notification alerts & feed
│   └── requirements.txt             # Python dependencies
├── frontend.py                       # Streamlit dashboard application
├── mobile/                           # React Native mobile app
│   └── (React Native project files)
├── pyrightconfig.json               # Pyright type checking config
└── README.md                         # This file

### Database Models
- **User** — Employee profiles with roles (EMPLOYEE, HOD, STORE)
- **Material** — Inventory items with stock levels & reorder points
- **Request** — Material requests with approval workflow
- **RequestItem** — Individual items in a request
- **ConsumptionLog** — Historical usage tracking
- **RFIDScan** — RFID/QR scan events with timestamps
- **Vendor** — Supplier information & performance metrics
- **PurchaseOrder** — PO creation & tracking
- **POItem** — Individual line items in a PO
- **Notification** — User alerts & feed
```

---

## 📦 Installation

### Prerequisites

- **Python 3.9+**
- **PostgreSQL 11+**
- **Node.js 16+** (for React Native)
- **Git**

### Backend Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Santhu7718/Inventory-Intelligence.git
   cd Inventory-Intelligence
   ```

2. **Create a Python virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

4. **Set up PostgreSQL database:**
   ```bash
   # Ensure PostgreSQL is running
   # Create database
   createdb inventory_intelligence
   
   # Database tables are auto-created on first app run via SQLAlchemy
   ```

5. **Configure environment variables:**
   ```bash
   # Create .env file in backend/ directory
   # Format: ******host:port/database
   DATABASE_URL=******localhost:5432/inventory_intelligence
   SECRET_KEY=your-super-secret-key-change-this
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```

6. **Run the backend server:**
   ```bash
   cd app
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```
   - API will be available at: `http://localhost:8000`
   - Interactive API docs: `http://localhost:8000/docs`
   - ReDoc documentation: `http://localhost:8000/redoc`

### Frontend Setup (Streamlit Dashboard)

1. **Navigate to the root directory:**
   ```bash
   cd ..  # Back to Inventory-Intelligence root
   ```

2. **Install Streamlit and dependencies:**
   ```bash
   pip install streamlit pandas plotly requests
   ```

3. **Run the Streamlit app:**
   ```bash
   streamlit run frontend.py
   ```
   - Dashboard will open at: `http://localhost:8501`

### Mobile Setup (React Native)

1. **Navigate to mobile directory:**
   ```bash
   cd mobile
   ```

2. **Install dependencies:**
   ```bash
   npm install
   # or
   yarn install
   ```

3. **Run on Android:**
   ```bash
   npm run android
   # or
   react-native run-android
   ```

4. **Run on iOS:**
   ```bash
   npm run ios
   # or
   react-native run-ios
   ```

---

## ⚙️ Configuration

### Backend Configuration

Edit `backend/app/main.py` or use environment variables. Replace the `**` placeholders with your actual credentials:

```python
# Format: ****://username:password@host:port/database
DATABASE_URL = "******localhost:5432/inventory_intelligence"
SECRET_KEY = "your-secret-key"  # Change this in production!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
```

### Frontend Configuration

Edit `frontend.py` to change the API URL:

```python
API_URL = "http://127.0.0.1:8000"  # Change for production
```

### RFID/QR Scanner Configuration

1. **Physical RFID Readers:**
   - Configure reader to POST scan data to: `http://your-server:8000/rfid/scan`
   - Expected JSON payload:
     ```json
     {
       "material_id": 1,
       "scan_data": "RFID-001",
       "scan_type": "RFID",
       "gate_id": "GATE-INBOUND-01"
     }
     ```

2. **QR Code Scanning:**
   - Generate QR codes via API: `GET /rfid/qr/{material_id}`
   - Mobile app or USB scanner can scan and POST to `/rfid/scan` endpoint
   - QR data format: `{"material_id": 1, "scan_type": "QR"}`

---

## 🎯 Usage

### 1. **User Registration & Login**

```bash
# Register a new user
curl -X POST "http://localhost:8000/users/register" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "password": "secure123",
    "role": "EMPLOYEE",
    "department": "Manufacturing"
  }'

# Login
curl -X POST "http://localhost:8000/users/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "secure123"
  }'
# Returns: {"access_token": "******", "token_type": "bearer"}
```

### 2. **Add Materials to Inventory**

```bash
curl -X POST "http://localhost:8000/inventory/add" \
  -H "Authorization: ******" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Stainless Steel Bolt M8",
    "total_stock": 500,
    "reorder_level": 100
  }'
```

### 3. **Request Materials (Employee)**

```bash
curl -X POST "http://localhost:8000/requests/create" \
  -H "Authorization: ******" \
  -H "Content-Type: application/json" \
  -d '{
    "items": [
      {"material_id": 1, "quantity": 10}
    ]
  }'
```

### 4. **Approve Requests (HOD)**

```bash
curl -X PUT "http://localhost:8000/requests/1/approve" \
  -H "Authorization: ******"
```

### 5. **View Demand Forecast**

```bash
curl -X GET "http://localhost:8000/forecast/demand?material_id=1&periods=12" \
  -H "Authorization: ******"
```

### 6. **Generate Analytics Report**

```bash
curl -X GET "http://localhost:8000/analytics/heatmap" \
  -H "Authorization: ******"
# Returns: Consumption matrix for last 12 months
```

### 7. **RFID Scan Event**

```bash
curl -X POST "http://localhost:8000/rfid/scan" \
  -H "Content-Type: application/json" \
  -d '{
    "material_id": 1,
    "scan_data": "RFID-ABC-123",
    "scan_type": "RFID",
    "gate_id": "GATE-INBOUND-01"
  }'
```

### 8. **Create Purchase Order**

```bash
curl -X POST "http://localhost:8000/vendors/create-po" \
  -H "Authorization: ******" \
  -H "Content-Type: application/json" \
  -d '{
    "vendor_id": 1,
    "items": [
      {"material_id": 1, "quantity": 100, "unit_price": 2.50}
    ],
    "delivery_date": "2024-07-15"
  }'
```

> **Note:** Replace `Authorization: ******` with the actual ****** format. After login, use:  
> ```
> -H "Authorization: ******<actual_token_from_login>"
> ```
> For example: `Authorization: ************

---

## 📚 API Documentation

### Quick Reference

| Module | Endpoints |
|--------|-----------|
| **Users** | `POST /users/register`, `POST /users/login`, `GET /users/profile` |
| **Inventory** | `GET /inventory/list`, `POST /inventory/add`, `PUT /inventory/{id}`, `DELETE /inventory/{id}` |
| **Requests** | `POST /requests/create`, `GET /requests/my-requests`, `PUT /requests/{id}/approve`, `PUT /requests/{id}/fulfill` |
| **Forecasting** | `GET /forecast/demand?material_id={id}&periods=12` |
| **Analytics** | `GET /analytics/heatmap`, `GET /analytics/trends`, `GET /analytics/export-csv` |
| **RFID** | `POST /rfid/scan`, `GET /rfid/logs`, `GET /rfid/qr/{material_id}` |
| **Vendors** | `GET /vendors/list`, `POST /vendors/add`, `POST /vendors/create-po`, `GET /vendors/purchase-orders` |
| **Notifications** | `GET /notify/feed`, `PUT /notify/{id}/read`, `DELETE /notify/{id}` |

### Interactive API Docs

Once the backend is running, access:
- **Swagger UI** — http://localhost:8000/docs
- **ReDoc** — http://localhost:8000/redoc

These provide interactive API exploration with try-it-out functionality.

---

## 🗄️ Database Models

### Core Entities

**User**
```
id (PK)         : Integer
name            : String
role            : String (EMPLOYEE | HOD | STORE)
department      : String
created_at      : DateTime
```

**Material**
```
id (PK)         : Integer
name            : String
total_stock     : Integer
reorder_level   : Integer
category        : String
unit_price      : Float
last_updated    : DateTime
```

**Request**
```
id (PK)         : Integer
employee_id (FK): User.id
status          : String (PENDING | APPROVED | FULFILLED | REJECTED)
created_at      : DateTime
approved_by     : Integer (FK to User)
approved_at     : DateTime
items           : Relationship[RequestItem]
```

**RFIDScan**
```
id (PK)         : Integer
material_id (FK): Material.id
scan_data       : String
scan_type       : String (RFID | QR | MANUAL)
gate_id         : String
scanned_at      : DateTime
```

**Vendor**
```
id (PK)         : Integer
name            : String
contact_email   : String
contact_phone   : String
rating          : Float
lead_time_days  : Integer
```

**PurchaseOrder**
```
id (PK)         : Integer
vendor_id (FK)  : Vendor.id
status          : String (DRAFT | SUBMITTED | CONFIRMED | DELIVERED | CANCELLED)
created_at      : DateTime
delivery_date   : DateTime
total_cost      : Float
items           : Relationship[POItem]
```

---

## 🛠️ Development

### Running Tests

```bash
# Backend tests (if implemented)
pytest backend/tests/

# Type checking
pyright backend/app/
```

### Code Style

- **Python** — PEP 8 compliant
- **Type Hints** — Full type annotations with Pyright
- **Linting** — Follow FastAPI best practices

### Database Migrations

SQLAlchemy creates tables automatically on app startup. For production migrations, use Alembic:

```bash
# Install Alembic
pip install alembic

# Initialize migrations
alembic init migrations

# Create a migration
alembic revision --autogenerate -m "Add new column"

# Apply migrations
alembic upgrade head
```

---

## 🚢 Deployment

### Production Deployment

1. **Environment Variables:**
   ```bash
   # Format: ****://username:password@host:port/database
   export DATABASE_URL="******prod-db:5432/inventory"
   export SECRET_KEY="production-secret-key-min-32-chars"
   export ENVIRONMENT="production"
   ```

2. **Run with Gunicorn (Production WSGI Server):**
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:8000 backend.app.main:app
   ```

3. **Docker Deployment:**
   Create a `Dockerfile` and `docker-compose.yml` for containerized deployment.

4. **Reverse Proxy:**
   - Configure Nginx or Apache as reverse proxy
   - Enable HTTPS/SSL certificates

---

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. **Fork the repository**
2. **Create a feature branch:** `git checkout -b feature/your-feature-name`
3. **Make your changes** and ensure code quality
4. **Run tests:** `pytest` and `pyright`
5. **Commit with clear messages:** `git commit -m "feat: add new feature"`
6. **Push to your fork:** `git push origin feature/your-feature-name`
7. **Create a Pull Request** with a detailed description

### Code Quality Standards

- Type hints on all functions
- Docstrings for complex logic
- Unit tests for new features
- Follow FastAPI best practices
- Update README if adding new features

---

## 📋 Roadmap

- [ ] Advanced ML forecasting (ARIMA, Prophet)
- [ ] Real-time WebSocket notifications
- [ ] Multi-warehouse support
- [ ] Supply chain optimization recommendations
- [ ] Mobile app iOS/Android release
- [ ] Barcode/1D code support in addition to QR
- [ ] Integration with ERP systems
- [ ] Machine learning model monitoring & retraining

---

## 📝 License

This project is licensed under the MIT License — see the LICENSE file for details.

---

## 📞 Support & Contact

For issues, feature requests, or questions:

- **GitHub Issues** — [Report a Bug](https://github.com/Santhu7718/Inventory-Intelligence/issues)
- **Email** — Contact the development team
- **Documentation** — Full API docs available at `/docs` when running the server

---

## 🙏 Acknowledgments

Built with ❤️ using:
- **FastAPI** — Modern, fast web framework
- **Streamlit** — Rapid dashboard development
- **SQLAlchemy** — Powerful ORM
- **PostgreSQL** — Reliable database

---

**Version:** 2.0  
**Last Updated:** June 2024  
**Maintainer:** Santhu7718

Made with ❤️ for smarter inventory management.
