import streamlit as st
import requests as req_lib
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import json
from datetime import datetime

# ─── CONFIG ────────────────────────────────────────────────────────────────────
API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Inventory Intelligence System",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── CUSTOM CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }

.stApp {
    background: linear-gradient(135deg, #0a0e1a 0%, #0d1421 50%, #0a1628 100%);
    color: #e2e8f0;
}
header[data-testid="stHeader"] { background: transparent; }

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1b2e 0%, #0a1520 100%);
    border-right: 1px solid rgba(56,189,248,0.15);
}
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2 { color: #cbd5e1 !important; }

.metric-card {
    background: linear-gradient(135deg, rgba(15,23,42,0.9), rgba(20,30,50,0.9));
    border: 1px solid rgba(56,189,248,0.2);
    border-radius: 16px; padding: 24px 20px;
    text-align: center; backdrop-filter: blur(10px);
    transition: all 0.3s ease; position: relative; overflow: hidden;
}
.metric-card::before {
    content:''; position:absolute; top:0; left:0; right:0; height:3px;
    background: linear-gradient(90deg, #38bdf8, #818cf8, #f472b6);
}
.metric-card:hover {
    border-color: rgba(56,189,248,0.5);
    transform: translateY(-2px);
    box-shadow: 0 8px 32px rgba(56,189,248,0.15);
}
.metric-card .metric-value {
    font-size: 2.8rem; font-weight: 800;
    background: linear-gradient(135deg, #38bdf8, #818cf8);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    line-height: 1; margin-bottom: 8px;
}
.metric-card .metric-label {
    font-size: 0.78rem; color: #64748b; font-weight: 500;
    text-transform: uppercase; letter-spacing: 1px;
}
.metric-card .metric-icon { font-size: 1.8rem; margin-bottom: 12px; }

.section-header {
    display: flex; align-items: center; gap: 12px;
    margin: 28px 0 16px 0; padding-bottom: 10px;
    border-bottom: 1px solid rgba(56,189,248,0.15);
}
.section-header h2 { font-size: 1.3rem; font-weight: 700; color: #e2e8f0; margin: 0; }
.section-badge {
    background: linear-gradient(135deg, #38bdf8, #818cf8);
    color: #0a0e1a; font-size: 0.65rem; font-weight: 700;
    padding: 2px 9px; border-radius: 20px;
    text-transform: uppercase; letter-spacing: 1px;
}

.data-card {
    background: rgba(15,23,42,0.8);
    border: 1px solid rgba(56,189,248,0.12);
    border-radius: 16px; padding: 20px;
    backdrop-filter: blur(10px); margin-bottom: 14px;
}

.badge { display:inline-block; padding:3px 10px; border-radius:20px;
    font-size:0.7rem; font-weight:700; letter-spacing:0.5px; text-transform:uppercase; }
.badge-pending { background:rgba(251,191,36,0.15); color:#fbbf24; border:1px solid rgba(251,191,36,0.3); }
.badge-approved { background:rgba(52,211,153,0.15); color:#34d399; border:1px solid rgba(52,211,153,0.3); }
.badge-issued { background:rgba(56,189,248,0.15); color:#38bdf8; border:1px solid rgba(56,189,248,0.3); }
.badge-store { background:rgba(129,140,248,0.15); color:#818cf8; border:1px solid rgba(129,140,248,0.3); }
.badge-hod { background:rgba(244,114,182,0.15); color:#f472b6; border:1px solid rgba(244,114,182,0.3); }
.badge-employee { background:rgba(52,211,153,0.15); color:#34d399; border:1px solid rgba(52,211,153,0.3); }

.form-card {
    background: rgba(15,23,42,0.85);
    border: 1px solid rgba(56,189,248,0.15);
    border-radius: 16px; padding: 28px 24px; backdrop-filter: blur(10px);
}

/* Notification cards */
.notif-card {
    border-radius: 12px; padding: 14px 18px; margin-bottom: 10px;
    border-left: 4px solid; position: relative; transition: all 0.2s;
}
.notif-approval { background:rgba(244,114,182,0.08); border-left-color:#f472b6; }
.notif-issue    { background:rgba(52,211,153,0.08); border-left-color:#34d399; }
.notif-stock    { background:rgba(251,191,36,0.08);  border-left-color:#fbbf24; }
.notif-unread-dot {
    width:8px; height:8px; border-radius:50%; background:#38bdf8;
    display:inline-block; margin-right:6px; flex-shrink:0;
}
.notif-time { font-size:0.72rem; color:#475569; margin-top:4px; }
.notif-msg { font-size:0.88rem; color:#cbd5e1; font-weight:500; }

/* User avatar */
.user-avatar {
    width:38px; height:38px; border-radius:50%;
    background:linear-gradient(135deg,#38bdf8,#818cf8);
    display:inline-flex; align-items:center; justify-content:center;
    font-weight:800; font-size:0.9rem; color:#0a0e1a; flex-shrink:0;
}

/* Streamlit overrides */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stSelectbox > div > div {
    background: rgba(15,23,42,0.9) !important;
    border: 1px solid rgba(56,189,248,0.2) !important;
    border-radius: 10px !important; color: #e2e8f0 !important;
}
.stTextInput label, .stNumberInput label, .stSelectbox label {
    color: #94a3b8 !important; font-size: 0.83rem !important; font-weight: 500 !important;
}
.stButton > button {
    background: linear-gradient(135deg, #38bdf8, #818cf8) !important;
    color: #0a0e1a !important; border: none !important;
    border-radius: 10px !important; font-weight: 700 !important;
    font-family: 'Inter', sans-serif !important; width: 100% !important;
    transition: all 0.3s !important;
}
.stButton > button:hover {
    opacity: 0.9 !important; transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(56,189,248,0.3) !important;
}
hr { border: none; border-top: 1px solid rgba(56,189,248,0.1); margin: 20px 0; }
.page-title {
    font-size: 1.9rem; font-weight: 800;
    background: linear-gradient(135deg, #38bdf8 0%, #818cf8 50%, #f472b6 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    margin-bottom: 4px;
}
.page-subtitle { color: #475569; font-size: 0.88rem; margin-bottom: 24px; }
</style>
""", unsafe_allow_html=True)

# ─── HELPERS ───────────────────────────────────────────────────────────────────
def api_get(endpoint, params=None):
    try:
        r = req_lib.get(f"{API_URL}{endpoint}", params=params, timeout=5)
        r.raise_for_status()
        return r.json(), None
    except req_lib.exceptions.ConnectionError:
        return None, "Cannot connect to backend"
    except Exception as e:
        return None, str(e)

def api_post(endpoint, data):
    try:
        r = req_lib.post(f"{API_URL}{endpoint}", json=data, timeout=5)
        r.raise_for_status()
        return r.json(), None
    except req_lib.exceptions.HTTPError:
        try: return None, r.json().get("detail", r.text)
        except: return None, r.text
    except Exception as e:
        return None, str(e)

def api_put(endpoint, data=None):
    try:
        r = req_lib.put(f"{API_URL}{endpoint}", json=data, timeout=5)
        r.raise_for_status()
        return r.json(), None
    except req_lib.exceptions.HTTPError:
        try: return None, r.json().get("detail", r.text)
        except: return None, r.text
    except Exception as e:
        return None, str(e)

def api_delete(endpoint):
    try:
        r = req_lib.delete(f"{API_URL}{endpoint}", timeout=5)
        r.raise_for_status()
        return r.json(), None
    except req_lib.exceptions.HTTPError:
        try: return None, r.json().get("detail", r.text)
        except: return None, r.text
    except Exception as e:
        return None, str(e)

def status_badge(status):
    m = {
        "PENDING_HOD": ("badge-pending", "⏳ Pending HOD"),
        "APPROVED": ("badge-approved", "✅ Approved"),
        "ISSUED": ("badge-issued", "📦 Issued"),
    }
    cls, label = m.get(status, ("badge-pending", status))
    return f'<span class="badge {cls}">{label}</span>'

def role_badge(role):
    m = {
        "EMPLOYEE": ("badge-employee", "👤 Employee"),
        "HOD": ("badge-hod", "🎯 HOD"),
        "STORE": ("badge-store", "🏪 Store"),
    }
    cls, label = m.get(role, ("badge-employee", role))
    return f'<span class="badge {cls}">{label}</span>'

def fmt_time(dt_str):
    try:
        dt = datetime.fromisoformat(dt_str)
        return dt.strftime("%d %b %Y, %H:%M")
    except:
        return dt_str or "—"

# ─── SESSION STATE ──────────────────────────────────────────────────────────────
if "current_role" not in st.session_state:
    st.session_state["current_role"] = "HOD"

# ─── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:20px 0 24px 0;">
        <div style="font-size:2.4rem;margin-bottom:8px;">🏭</div>
        <div style="font-size:1.05rem;font-weight:800;color:#e2e8f0;">Inventory</div>
        <div style="font-size:1.05rem;font-weight:800;background:linear-gradient(135deg,#38bdf8,#818cf8);
                    -webkit-background-clip:text;-webkit-text-fill-color:transparent;">Intelligence</div>
        <div style="font-size:0.65rem;color:#475569;margin-top:4px;text-transform:uppercase;letter-spacing:2px;">Management System</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Role selector
    st.markdown("<p style='font-size:0.72rem;color:#475569;text-transform:uppercase;letter-spacing:1px;margin-bottom:4px;'>Viewing as</p>", unsafe_allow_html=True)
    current_role = st.selectbox(
        "Role", ["HOD", "STORE", "EMPLOYEE"],
        index=["HOD", "STORE", "EMPLOYEE"].index(st.session_state["current_role"]),
        key="role_select", label_visibility="collapsed"
    )
    st.session_state["current_role"] = current_role

    # Unread notification count for this role
    notif_count_data, _ = api_get("/notifications/unread-count", params={"role": current_role})
    unread = notif_count_data.get("count", 0) if notif_count_data else 0

    st.markdown("---")

    # Navigation — only show pages relevant to the selected role
    notif_label = f"🔔  Notifications  {'🔴' if unread > 0 else ''}"

    ROLE_PAGES = {
        "EMPLOYEE": [
            "🏠  Dashboard",
            "📋  Material Requests",
            notif_label,
        ],
        "STORE": [
            "🏠  Dashboard",
            "📦  Materials & Stock",
            "🚀  Issue Materials",
            "📡  RFID & QR Scan",
            "🛒  Vendors & POs",
            notif_label,
        ],
        "HOD": [
            "🏠  Dashboard",
            "👥  User Management",
            "📦  Materials & Stock",
            "📋  Material Requests",
            "✅  Approve Requests",
            "🚀  Issue Materials",
            "🤖  AI Forecast",
            "📊  Analytics",
            "📡  RFID & QR Scan",
            "🛒  Vendors & POs",
            notif_label,
        ],
    }

    nav_pages = ROLE_PAGES.get(current_role, ROLE_PAGES["EMPLOYEE"])
    st.session_state["nav_pages"] = nav_pages  # expose for redirect

    # Handle redirect from notification Take Action button
    redirect_kw = st.session_state.pop("redirect_page_kw", None)
    default_idx = 0
    if redirect_kw:
        for i, p in enumerate(nav_pages):
            if redirect_kw in p:
                default_idx = i
                break
    else:
        prev_page = st.session_state.get("current_page", nav_pages[0])
        for i, p in enumerate(nav_pages):
            if p.strip()[:6] == prev_page.strip()[:6]:
                default_idx = i
                break

    page = st.selectbox(
        "Navigate",
        nav_pages,
        index=default_idx,
        label_visibility="collapsed"
    )
    st.session_state["current_page"] = page

    st.markdown("---")

    # Backend status
    health, err = api_get("/")
    if health:
        st.markdown("""
        <div style="display:flex;align-items:center;gap:8px;padding:9px 14px;
                     background:rgba(52,211,153,0.1);border:1px solid rgba(52,211,153,0.3);border-radius:10px;">
            <span style="color:#34d399;font-size:0.7rem;">●</span>
            <span style="font-size:0.78rem;color:#34d399;font-weight:600;">Backend Connected</span>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="display:flex;align-items:center;gap:8px;padding:9px 14px;
                     background:rgba(248,113,113,0.1);border:1px solid rgba(248,113,113,0.3);border-radius:10px;">
            <span style="color:#f87171;font-size:0.7rem;">●</span>
            <span style="font-size:0.78rem;color:#f87171;font-weight:600;">Backend Offline</span>
        </div>""", unsafe_allow_html=True)

    if unread > 0:
        st.markdown(f"""
        <div style="margin-top:10px;padding:9px 14px;background:rgba(248,113,113,0.1);
                    border:1px solid rgba(248,113,113,0.3);border-radius:10px;">
            <span style="font-size:0.78rem;color:#f87171;font-weight:700;">
                🔔 {unread} unread notification{'s' if unread != 1 else ''}
            </span>
        </div>""", unsafe_allow_html=True)

    st.markdown(f"""
    <div style="margin-top:10px;padding:9px 14px;background:rgba(15,23,42,0.6);
                border-radius:10px;border:1px solid rgba(56,189,248,0.1);">
        <div style="font-size:0.65rem;color:#475569;text-transform:uppercase;letter-spacing:1px;">Last Refreshed</div>
        <div style="font-size:0.75rem;color:#64748b;margin-top:3px;">{datetime.now().strftime('%d %b %Y, %H:%M')}</div>
    </div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════
if "Dashboard" in page:
    st.markdown('<div class="page-title">Operations Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Real-time inventory, user, and request overview</div>', unsafe_allow_html=True)

    users_data, _ = api_get("/users/")
    mats_data, _ = api_get("/materials/")
    reqs_data, _ = api_get("/requests/")
    users_data = users_data or []
    mats_data = mats_data or []
    reqs_data = reqs_data or []

    pending = [r for r in reqs_data if r["status"] == "PENDING_HOD"]
    approved = [r for r in reqs_data if r["status"] == "APPROVED"]
    issued = [r for r in reqs_data if r["status"] == "ISSUED"]
    low_stock = [m for m in mats_data if m["total_stock"] <= m["reorder_level"]]

    # KPI Row
    c1, c2, c3, c4, c5 = st.columns(5)
    for col, val, label, icon in [
        (c1, len(users_data), "Total Users", "👥"),
        (c2, len(mats_data), "Materials", "📦"),
        (c3, len(pending), "Pending HOD", "⏳"),
        (c4, len(approved), "Approved", "✅"),
        (c5, len(low_stock), "Low Stock", "⚠️"),
    ]:
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-icon">{icon}</div>
                <div class="metric-value">{val}</div>
                <div class="metric-label">{label}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col_left, col_right = st.columns([1.3, 1])

    with col_left:
        st.markdown("""<div class="section-header">
            <h2>📋 Recent Requests</h2>
            <span class="section-badge">Live</span>
        </div>""", unsafe_allow_html=True)
        if reqs_data:
            df = pd.DataFrame([{
                "ID": r["id"], "Employee ID": r["employee_id"],
                "Status": r["status"].replace("_", " "), "Items": len(r["items"])
            } for r in reqs_data[-5:][::-1]])
            st.dataframe(df, width='stretch', hide_index=True)
        else:
            st.info("No requests yet.")

    with col_right:
        st.markdown("""<div class="section-header"><h2>📦 Stock Levels</h2></div>""", unsafe_allow_html=True)
        for m in mats_data:
            pct = min(int((m["total_stock"] / max(m["reorder_level"] * 3, 1)) * 100), 100)
            bar_color = "#f87171" if m["total_stock"] <= m["reorder_level"] else "#34d399"
            st.markdown(f"""
            <div style="margin-bottom:14px;">
                <div style="display:flex;justify-content:space-between;margin-bottom:5px;">
                    <span style="font-size:0.83rem;color:#cbd5e1;font-weight:500;">{m['name']}</span>
                    <span style="font-size:0.8rem;color:{bar_color};font-weight:600;">{m['total_stock']} units</span>
                </div>
                <div style="background:rgba(15,23,42,0.8);border-radius:6px;height:7px;overflow:hidden;">
                    <div style="width:{pct}%;height:100%;background:{bar_color};border-radius:6px;"></div>
                </div>
                <div style="font-size:0.68rem;color:#475569;margin-top:3px;">Reorder at {m['reorder_level']} units</div>
            </div>""", unsafe_allow_html=True)

    # Workflow status pipeline
    st.markdown("---")
    st.markdown("""<div class="section-header"><h2>🔄 Request Workflow Pipeline</h2></div>""", unsafe_allow_html=True)
    p1, p2, p3, p4 = st.columns(4)
    for col, count, label, desc, color in [
        (p1, len(reqs_data), "Total Requests", "All time", "#64748b"),
        (p2, len(pending), "Pending HOD", "Awaiting approval", "#fbbf24"),
        (p3, len(approved), "Approved", "Ready to issue", "#34d399"),
        (p4, len(issued), "Issued", "Completed", "#38bdf8"),
    ]:
        with col:
            st.markdown(f"""
            <div style="background:rgba(15,23,42,0.6);border:1px solid rgba(56,189,248,0.12);
                        border-radius:14px;padding:18px;text-align:center;">
                <div style="font-size:2rem;font-weight:800;color:{color};">{count}</div>
                <div style="font-size:0.82rem;font-weight:600;color:#94a3b8;margin-top:4px;">{label}</div>
                <div style="font-size:0.7rem;color:#475569;margin-top:2px;">{desc}</div>
            </div>""", unsafe_allow_html=True)

    if low_stock:
        st.markdown("---")
        st.markdown("""<div class="section-header">
            <h2>⚠️ Low Stock Alerts</h2>
            <span class="section-badge" style="background:linear-gradient(135deg,#f87171,#ef4444);">Action Required</span>
        </div>""", unsafe_allow_html=True)
        for m in low_stock:
            st.warning(f"⚠️ **{m['name']}** — Stock: **{m['total_stock']}** | Reorder Level: **{m['reorder_level']}** — Restock required!")


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: USER MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════════════
elif "User Management" in page:
    st.markdown('<div class="page-title">User Management</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Register, view, and remove system users</div>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["👥  All Users", "➕  Add New User"])

    with tab1:
        users_data, err = api_get("/users/")
        if err:
            st.error(err)
        elif not users_data:
            st.info("No users registered yet.")
        else:
            st.markdown(f"<p style='color:#64748b;font-size:0.83rem;margin-bottom:12px;'>{len(users_data)} user(s) registered</p>", unsafe_allow_html=True)
            for u in users_data:
                initials = "".join([w[0].upper() for w in u["name"].split()[:2]]) if u["name"] else "?"
                col_info, col_del = st.columns([5, 1])
                with col_info:
                    st.markdown(f"""
                    <div style="display:flex;align-items:center;justify-content:space-between;
                                background:rgba(15,23,42,0.6);border:1px solid rgba(56,189,248,0.1);
                                border-radius:12px;padding:14px 18px;margin-bottom:8px;">
                        <div style="display:flex;align-items:center;gap:14px;">
                            <div class="user-avatar">{initials}</div>
                            <div>
                                <div style="font-weight:700;color:#e2e8f0;font-size:0.9rem;">{u['name']}</div>
                                <div style="font-size:0.75rem;color:#64748b;margin-top:2px;">🏢 {u['department']}</div>
                            </div>
                        </div>
                        <div style="display:flex;align-items:center;gap:10px;">
                            {role_badge(u['role'])}
                            <span style="font-size:0.72rem;color:#475569;background:rgba(15,23,42,0.8);
                                         padding:3px 8px;border-radius:6px;">ID #{u['id']}</span>
                        </div>
                    </div>""", unsafe_allow_html=True)

                with col_del:
                    confirm_key = f"confirm_{u['id']}"
                    st.markdown("<div style='margin-top:6px;'>", unsafe_allow_html=True)
                    if st.session_state.get(confirm_key):
                        c1, c2 = st.columns(2)
                        with c1:
                            if st.button("✓", key=f"yes_{u['id']}", help="Confirm delete"):
                                res, del_err = api_delete(f"/users/{u['id']}")
                                if del_err:
                                    st.error(del_err)
                                else:
                                    st.toast(f"User '{u['name']}' removed.", icon="🗑️")
                                st.session_state[confirm_key] = False
                                st.rerun()
                        with c2:
                            if st.button("✗", key=f"no_{u['id']}", help="Cancel"):
                                st.session_state[confirm_key] = False
                                st.rerun()
                    else:
                        if st.button("🗑️", key=f"del_{u['id']}", help=f"Remove {u['name']}"):
                            st.session_state[confirm_key] = True
                            st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)

    with tab2:
        st.markdown('<div class="form-card">', unsafe_allow_html=True)
        st.markdown("#### 👤 Register New User")
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Full Name", placeholder="e.g. Arjun Kumar", key="u_name")
            department = st.text_input("Department", placeholder="e.g. Production", key="u_dept")
        with col2:
            role = st.selectbox("Role", ["EMPLOYEE", "HOD", "STORE"], key="u_role")
            st.markdown("""
            <div style="background:rgba(56,189,248,0.05);border:1px solid rgba(56,189,248,0.15);
                        border-radius:10px;padding:12px 14px;font-size:0.78rem;color:#64748b;margin-top:8px;">
                <strong style="color:#94a3b8;">Role Guide</strong><br>
                🟢 EMPLOYEE — Submits material requests<br>
                🟣 HOD — Approves/rejects requests<br>
                🔵 STORE — Issues materials from inventory
            </div>""", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("➕ Create User", key="create_user_btn"):
            if not name.strip() or not department.strip():
                st.error("Name and Department are required.")
            else:
                res, err = api_post("/users/", {"name": name, "role": role, "department": department})
                if err:
                    st.error(f"❌ {err}")
                else:
                    st.success(f"✅ User **{res['name']}** created with ID #{res['id']}")
                    st.balloons()
        st.markdown('</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: MATERIALS & STOCK
# ═══════════════════════════════════════════════════════════════════════════════
elif "Materials & Stock" in page or ("Materials" in page and "Issue" not in page):
    st.markdown('<div class="page-title">Materials & Stock</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Track inventory, monitor stock health, add new materials</div>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["📦  All Materials", "➕  Add Material"])

    with tab1:
        mats_data, err = api_get("/materials/")
        if err:
            st.error(err)
        elif not mats_data:
            st.info("No materials in inventory yet.")
        else:
            cols = st.columns(min(len(mats_data), 3))
            for i, m in enumerate(mats_data):
                with cols[i % 3]:
                    pct = min(int((m["total_stock"] / max(m["reorder_level"] * 3, 1)) * 100), 100)
                    is_low = m["total_stock"] <= m["reorder_level"]
                    bar_color = "#f87171" if is_low else "#34d399"
                    status_text = "⚠️ Low Stock — Restock!" if is_low else "✅ Adequate Stock"
                    st.markdown(f"""
                    <div class="metric-card" style="text-align:left;margin-bottom:16px;">
                        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
                            <span style="font-size:0.95rem;font-weight:700;color:#e2e8f0;">{m['name']}</span>
                            <span style="font-size:0.7rem;color:#475569;background:rgba(15,23,42,0.8);padding:2px 8px;border-radius:6px;">ID #{m['id']}</span>
                        </div>
                        <div style="display:flex;gap:20px;margin-bottom:12px;">
                            <div>
                                <div style="font-size:1.7rem;font-weight:800;color:{bar_color};">{m['total_stock']}</div>
                                <div style="font-size:0.65rem;color:#475569;text-transform:uppercase;letter-spacing:1px;">Current Stock</div>
                            </div>
                            <div>
                                <div style="font-size:1.7rem;font-weight:800;color:#64748b;">{m['reorder_level']}</div>
                                <div style="font-size:0.65rem;color:#475569;text-transform:uppercase;letter-spacing:1px;">Reorder Level</div>
                            </div>
                        </div>
                        <div style="background:rgba(15,23,42,0.8);border-radius:6px;height:6px;margin-bottom:8px;">
                            <div style="width:{pct}%;height:100%;background:{bar_color};border-radius:6px;"></div>
                        </div>
                        <div style="font-size:0.75rem;color:{bar_color};font-weight:600;">{status_text}</div>
                    </div>""", unsafe_allow_html=True)

            st.markdown("---")
            st.markdown("#### 📊 Full Inventory Table")
            df = pd.DataFrame([{
                "ID": m["id"], "Material": m["name"],
                "Stock": m["total_stock"], "Reorder Level": m["reorder_level"],
                "Health": "⚠️ Low" if m["total_stock"] <= m["reorder_level"] else "✅ OK"
            } for m in mats_data])
            st.dataframe(df, width='stretch', hide_index=True)

    with tab2:
        st.markdown('<div class="form-card">', unsafe_allow_html=True)
        st.markdown("#### 📦 Add New Material")
        c1, c2, c3 = st.columns(3)
        with c1:
            mat_name = st.text_input("Material Name", placeholder="e.g. Steel Rod", key="m_name")
        with c2:
            total_stock = st.number_input("Initial Stock (units)", min_value=0, step=1, key="m_stock")
        with c3:
            reorder_level = st.number_input("Reorder Level", min_value=0, step=1, key="m_reorder")
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("➕ Add Material", key="add_mat_btn"):
            if not mat_name.strip():
                st.error("Material name is required.")
            elif reorder_level >= total_stock and total_stock > 0:
                st.warning("Reorder level should be less than initial stock.")
            else:
                res, err = api_post("/materials/", {"name": mat_name, "total_stock": int(total_stock), "reorder_level": int(reorder_level)})
                if err:
                    st.error(f"❌ {err}")
                else:
                    st.success(f"✅ **{res['name']}** added with {res['total_stock']} units.")
                    st.balloons()
        st.markdown('</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: MATERIAL REQUESTS
# ═══════════════════════════════════════════════════════════════════════════════
elif "Requests" in page and "Approve" not in page and "Issue" not in page:
    st.markdown('<div class="page-title">Material Requests</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Submit material requests — HOD will be notified automatically</div>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["📋  All Requests", "➕  New Request"])

    with tab1:
        reqs_data, err = api_get("/requests/")
        if err:
            st.error(err)
        elif not reqs_data:
            st.info("No requests found yet.")
        else:
            status_filter = st.selectbox("Filter by Status", ["All", "PENDING_HOD", "APPROVED", "ISSUED"], key="req_filter")
            filtered = reqs_data if status_filter == "All" else [r for r in reqs_data if r["status"] == status_filter]
            st.markdown(f"<p style='color:#64748b;font-size:0.83rem;'>{len(filtered)} request(s)</p>", unsafe_allow_html=True)
            for r in filtered[::-1]:
                with st.expander(f"Request #{r['id']}  ·  Employee #{r['employee_id']}  ·  {r['status'].replace('_',' ')}", expanded=False):
                    col_a, col_b, col_c, col_d = st.columns(4)
                    with col_a:
                        st.markdown(f"**Request ID**<br>#{r['id']}", unsafe_allow_html=True)
                    with col_b:
                        st.markdown(f"**Employee**<br>#{r['employee_id']}", unsafe_allow_html=True)
                    with col_c:
                        st.markdown(f"**Status**<br>{r['status'].replace('_',' ')}", unsafe_allow_html=True)
                    with col_d:
                        st.markdown(f"**Items**<br>{len(r['items'])}", unsafe_allow_html=True)
                    st.dataframe(pd.DataFrame([{
                        "Item ID": it["id"], "Material ID": it["material_id"],
                        "Requested": it["requested_qty"],
                        "Approved": it["approved_qty"] if it["approved_qty"] is not None else "—",
                        "Issued": it["issued_qty"] if it["issued_qty"] is not None else "—",
                    } for it in r["items"]]), width='stretch', hide_index=True)

    with tab2:
        users_data, _ = api_get("/users/")
        mats_data, _ = api_get("/materials/")
        users_data = users_data or []
        mats_data = mats_data or []
        employees = [u for u in users_data if u["role"] == "EMPLOYEE"]

        st.markdown('<div class="form-card">', unsafe_allow_html=True)
        st.markdown("#### 📋 Submit New Material Request")
        st.info("📣 HOD will be automatically notified to approve this request.")

        if not employees:
            st.warning("No employees found. Please add users first.")
        elif not mats_data:
            st.warning("No materials found. Please add materials first.")
        else:
            emp_opts = {f"{u['name']} (#{u['id']}) — {u['department']}": u["id"] for u in employees}
            mat_opts = {f"{m['name']}  [Stock: {m['total_stock']}]": m["id"] for m in mats_data}

            c1, c2 = st.columns(2)
            with c1:
                emp_label = st.selectbox("Requesting Employee", list(emp_opts.keys()), key="req_emp")
                employee_id = emp_opts[emp_label]
            with c2:
                mat_label = st.selectbox("Material", list(mat_opts.keys()), key="req_mat")
                material_id = mat_opts[mat_label]

            c3, _ = st.columns([1, 2])
            with c3:
                qty = st.number_input("Quantity", min_value=1, step=1, key="req_qty")

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("📋 Submit Request", key="submit_req_btn"):
                data = {"employee_id": employee_id, "items": [{"material_id": material_id, "requested_qty": int(qty)}]}
                res, err = api_post("/requests/", data)
                if err:
                    st.error(f"❌ {err}")
                else:
                    st.success(f"✅ Request #{res['id']} submitted! HOD has been notified for approval.")
                    st.toast("🔔 HOD notified!", icon="📣")
        st.markdown('</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: APPROVE REQUESTS
# ═══════════════════════════════════════════════════════════════════════════════
elif "Approve" in page:
    st.markdown('<div class="page-title">Approve Requests</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">HOD Panel — approve requests to notify Store for issuance</div>', unsafe_allow_html=True)

    reqs_data, err = api_get("/requests/")
    if err:
        st.error(err)
    else:
        pending = [r for r in (reqs_data or []) if r["status"] == "PENDING_HOD"]
        if not pending:
            st.success("✅ No pending requests. All requests have been processed.")
        else:
            st.warning(f"⏳ **{len(pending)}** request(s) awaiting your approval")
            for r in pending:
                with st.container():
                    st.markdown(f"""
                    <div class="data-card">
                        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;">
                            <div>
                                <span style="font-size:1rem;font-weight:700;color:#e2e8f0;">Request #{r['id']}</span>
                                <span style="margin-left:10px;font-size:0.8rem;color:#64748b;">Employee #{r['employee_id']}</span>
                            </div>
                            {status_badge(r['status'])}
                        </div>
                    </div>""", unsafe_allow_html=True)

                    st.dataframe(pd.DataFrame([{
                        "Material ID": it["material_id"],
                        "Requested Qty": it["requested_qty"]
                    } for it in r["items"]]), width='stretch', hide_index=True)

                    st.markdown("**Set Approved Quantities:**")
                    approved_qtys = []
                    for j, item in enumerate(r["items"]):
                        aq = st.number_input(
                            f"Approved Qty — Material #{item['material_id']} (requested: {item['requested_qty']})",
                            min_value=0, max_value=item["requested_qty"],
                            value=item["requested_qty"],
                            key=f"aq_{r['id']}_{j}"
                        )
                        approved_qtys.append(aq)

                    if st.button(f"✅ Approve Request #{r['id']}", key=f"approve_{r['id']}"):
                        with st.spinner("Approving…"):
                            payload = {"approved_quantities": [int(q) for q in approved_qtys]}
                            res_data, err = api_put(f"/requests/{r['id']}/approve", payload)
                        if err:
                            st.error(f"❌ {err}")
                        else:
                            st.success(f"✅ Request #{r['id']} approved! Store has been notified for issuance.")
                            st.toast("🔔 Store keeper notified!", icon="🏪")
                            st.rerun()
                    st.markdown("---")


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: ISSUE MATERIALS
# ═══════════════════════════════════════════════════════════════════════════════
elif "Issue Materials" in page or ("Issue" in page and "Notifications" not in page and "Requests" not in page):
    st.markdown('<div class="page-title">Issue Materials</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Store Panel — issue approved materials and update stock automatically</div>', unsafe_allow_html=True)

    reqs_data, err = api_get("/requests/")
    mats_data, _ = api_get("/materials/")
    mat_map = {m["id"]: m for m in (mats_data or [])}

    if err:
        st.error(f"❌ Error fetching requests: {err}")
    else:
        approved = [r for r in (reqs_data or []) if r["status"] == "APPROVED"]
        if not approved:
            st.success("✅ No approved requests pending issuance.")
        else:
            st.info(f"📦 **{len(approved)}** request(s) are approved and ready to issue")
            for r in approved:
                st.markdown(f"""
                <div class="data-card">
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;">
                        <div>
                            <span style="font-size:1rem;font-weight:700;color:#e2e8f0;">Request #{r['id']}</span>
                            <span style="margin-left:10px;font-size:0.8rem;color:#64748b;">Employee #{r['employee_id']}</span>
                        </div>
                        {status_badge(r['status'])}
                    </div>
                </div>""", unsafe_allow_html=True)

                rows = []
                can_issue = True
                for it in r["items"]:
                    mat = mat_map.get(it["material_id"], {})
                    after = (mat.get("total_stock", 0) - (it["approved_qty"] or 0)) if mat else "—"
                    rows.append({
                        "Material": mat.get("name", f"ID #{it['material_id']}"),
                        "Approved Qty": it["approved_qty"],
                        "Current Stock": mat.get("total_stock", "—"),
                        "Stock After Issue": after if isinstance(after, str) else max(after, 0),
                    })
                    if mat and mat.get("total_stock", 0) < (it["approved_qty"] or 0):
                        can_issue = False

                st.dataframe(pd.DataFrame(rows), width='stretch', hide_index=True)

                if not can_issue:
                    st.error("❌ Insufficient stock for one or more items. Cannot issue.")
                else:
                    if st.button(f"🚀 Issue Materials — Request #{r['id']}", key=f"issue_{r['id']}"):
                        with st.spinner(f"Issuing materials for Request #{r['id']}…"):
                            res_data, err_msg = api_put(f"/requests/{r['id']}/issue")
                        if err_msg:
                            st.error(f"❌ {err_msg}")
                        else:
                            st.success(f"📦 **Request #{r['id']}** issued successfully! Stock has been updated.")
                            st.toast("✅ Materials issued & stock updated!", icon="📦")
                            st.rerun()
                st.markdown("---")

    # Current stock summary
    st.markdown("""<div class="section-header"><h2>📊 Current Inventory Snapshot</h2></div>""", unsafe_allow_html=True)
    if mats_data:
        df = pd.DataFrame([{
            "ID": m["id"], "Material": m["name"],
            "Stock": m["total_stock"], "Reorder Level": m["reorder_level"],
            "Status": "⚠️ Low" if m["total_stock"] <= m["reorder_level"] else "✅ OK"
        } for m in mats_data])
        st.dataframe(df, width='stretch', hide_index=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: NOTIFICATIONS
# ═══════════════════════════════════════════════════════════════════════════════
elif "Notifications" in page or "🔔" in page:
    role = st.session_state.get("current_role", "HOD")
    st.markdown(f'<div class="page-title">🔔 Notifications</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="page-subtitle">Showing alerts for <strong style="color:#38bdf8;">{role}</strong> role — change role in the sidebar</div>', unsafe_allow_html=True)

    notifs_data, err = api_get("/notifications/", params={"role": role})
    if err:
        st.error(f"❌ {err}")
    elif not notifs_data:
        st.info("🎉 No notifications. You're all caught up!")
    else:
        unread_notifs = [n for n in notifs_data if not n["is_read"]]
        read_notifs = [n for n in notifs_data if n["is_read"]]

        col_counts, col_action = st.columns([3, 1])
        with col_counts:
            st.markdown(f"""
            <div style="display:flex;gap:12px;margin-bottom:16px;">
                <span style="background:rgba(248,113,113,0.15);color:#f87171;border:1px solid rgba(248,113,113,0.3);
                              padding:4px 12px;border-radius:20px;font-size:0.8rem;font-weight:700;">
                    🔴 {len(unread_notifs)} Unread
                </span>
                <span style="background:rgba(100,116,139,0.15);color:#94a3b8;border:1px solid rgba(100,116,139,0.2);
                              padding:4px 12px;border-radius:20px;font-size:0.8rem;font-weight:600;">
                    ✓ {len(read_notifs)} Read
                </span>
            </div>""", unsafe_allow_html=True)
        with col_action:
            if unread_notifs:
                if st.button("✓ Mark All Read", key="mark_all"):
                    api_put("/notifications/mark-all-read", {"role": role})
                    st.toast("All notifications marked as read", icon="✅")
                    st.rerun()

        # Maps notification type → (target role, page keyword, button label)
        ACTION_MAP = {
            "APPROVAL_NEEDED": ("HOD",   "Approve",   "✅ Go to Approve Requests"),
            "ISSUE_NEEDED":    ("STORE",  "Issue",     "🚀 Go to Issue Materials"),
            "LOW_STOCK":       ("HOD",    "Materials", "📦 Go to Materials & Stock"),
        }

        def render_notif(n):
            type_map = {
                "APPROVAL_NEEDED": ("notif-approval", "🔔", "#f472b6"),
                "ISSUE_NEEDED":    ("notif-issue",    "📦", "#34d399"),
                "LOW_STOCK":       ("notif-stock",    "⚠️", "#fbbf24"),
            }
            card_cls, icon, color = type_map.get(n["notification_type"], ("notif-approval", "📌", "#64748b"))
            dot = '<span class="notif-unread-dot"></span>' if not n["is_read"] else ""
            req_tag = f'<span style="font-size:0.7rem;color:#475569;margin-left:8px;">Request #{n["request_id"]}</span>' if n.get("request_id") else ""
            st.markdown(f"""
            <div class="notif-card {card_cls}">
                <div style="display:flex;align-items:flex-start;gap:10px;">
                    <span style="font-size:1.3rem;flex-shrink:0;">{icon}</span>
                    <div style="flex:1;">
                        <div style="display:flex;align-items:center;">
                            {dot}
                            <span class="notif-msg">{n['message']}</span>
                            {req_tag}
                        </div>
                        <div class="notif-time">{fmt_time(n.get('created_at',''))}</div>
                    </div>
                </div>
            </div>""", unsafe_allow_html=True)

            action = ACTION_MAP.get(n["notification_type"])
            btn_col, mark_col = st.columns([2, 1])
            with btn_col:
                if action:
                    target_role, page_kw, btn_label = action
                    if st.button(btn_label, key=f"action_{n['id']}", use_container_width=True):
                        # Mark read and redirect — only set non-widget state here
                        api_put(f"/notifications/{n['id']}/read")
                        st.session_state["current_role"] = target_role   # sidebar reads this for the index
                        st.session_state["redirect_page_kw"] = page_kw
                        st.rerun()
            with mark_col:
                if not n["is_read"]:
                    if st.button("Mark read", key=f"read_{n['id']}"):
                        api_put(f"/notifications/{n['id']}/read")
                        st.rerun()

        if unread_notifs:
            st.markdown("### 🔴 Unread")
            for n in unread_notifs:
                render_notif(n)

        if read_notifs:
            with st.expander(f"✓ {len(read_notifs)} Read Notifications", expanded=False):
                for n in read_notifs:
                    render_notif(n)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: AI DEMAND FORECAST
# ═══════════════════════════════════════════════════════════════════════════════
elif "AI Forecast" in page:
    st.markdown('<div class="page-title">🤖 AI Demand Forecast</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">12-month demand prediction using Holt\'s Double Exponential Smoothing</div>', unsafe_allow_html=True)

    mats_data, _ = api_get("/materials/")
    mats_data = mats_data or []

    if not mats_data:
        st.warning("No materials found. Add materials first.")
    else:
        # Summary forecast for all materials
        all_fc, _ = api_get("/forecast/all/summary")
        if all_fc:
            st.markdown("""
            <div class="section-header"><h2>📈 Demand Forecast Summary</h2>
            <span class="section-badge">AI Engine</span></div>
            """, unsafe_allow_html=True)
            cols = st.columns(min(len(all_fc), 4))
            for i, item in enumerate(all_fc[:4]):
                mos = item['months_of_stock']
                mos_display = f"{mos}" if mos < 900 else "∞"
                health = "#f87171" if mos < 2 else ("#fbbf24" if mos < 4 else "#34d399")
                with cols[i % 4]:
                    st.markdown(f"""
                    <div class="metric-card" style="text-align:left;">
                        <div style="font-size:0.82rem;font-weight:700;color:#e2e8f0;margin-bottom:8px;">{item['material_name']}</div>
                        <div style="font-size:1.6rem;font-weight:800;color:{health};">{mos_display} mo</div>
                        <div style="font-size:0.68rem;color:#475569;text-transform:uppercase;letter-spacing:1px;">Stock Runway</div>
                        <div style="margin-top:8px;font-size:0.78rem;color:#64748b;">{item['trend']} &nbsp;·&nbsp; {item['avg_monthly_demand']} u/mo avg</div>
                    </div>""", unsafe_allow_html=True)

        st.markdown("---")
        mat_opts = {m["name"]: m["id"] for m in mats_data}
        col_sel, col_btn = st.columns([3, 1])
        with col_sel:
            selected_mat = st.selectbox("Select Material to Forecast", list(mat_opts.keys()), key="fc_mat")
        mat_id = mat_opts[selected_mat]

        with col_btn:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🌱 Seed 12-Month History", key="seed_btn", help="Generate demo history for AI forecasting"):
                res, err = api_post(f"/forecast/seed/{mat_id}", {})
                if err:
                    st.error(err)
                else:
                    st.success(res.get("message", "History seeded!"))
                    st.rerun()

        fc_data, err = api_get(f"/forecast/{mat_id}")
        if err:
            st.error(f"Error: {err}")
        elif fc_data:
            hist = fc_data["historical"]
            fc = fc_data["forecast"]
            summary = fc_data["summary"]

            # KPIs
            k1, k2, k3, k4 = st.columns(4)
            mos_val = summary['months_of_stock']
            mos_str = str(mos_val) if mos_val < 900 else "∞"
            for col, val, label, color in [
                (k1, f"{summary['avg_monthly_demand']} units", "Avg Monthly Demand", "#38bdf8"),
                (k2, summary['trend'], "Demand Trend", "#818cf8"),
                (k3, f"{summary['current_stock']} units", "Current Stock", "#34d399"),
                (k4, f"{mos_str} months", "Stock Runway", "#f472b6"),
            ]:
                with col:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-value" style="font-size:1.4rem;">{val}</div>
                        <div class="metric-label">{label}</div>
                    </div>""", unsafe_allow_html=True)

            # Combined historical + forecast chart
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=hist["months"], y=hist["values"],
                name="Historical Consumption",
                marker_color="rgba(56,189,248,0.6)",
            ))
            fig.add_trace(go.Scatter(
                x=fc["months"], y=fc["values"],
                name="AI Forecast", mode="lines+markers",
                line=dict(color="#818cf8", width=3),
                marker=dict(size=7),
            ))
            fig.add_trace(go.Scatter(
                x=fc["months"] + fc["months"][::-1],
                y=fc["upper"] + fc["lower"][::-1],
                fill="toself", fillcolor="rgba(129,140,248,0.12)",
                line=dict(color="rgba(0,0,0,0)"),
                name="Confidence Band", showlegend=True,
            ))
            fig.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(10,14,26,0)",
                plot_bgcolor="rgba(10,14,26,0)",
                font=dict(color="#94a3b8"),
                title=dict(text=f"12-Month Demand Forecast — {selected_mat}", font=dict(color="#e2e8f0", size=15)),
                xaxis=dict(gridcolor="rgba(56,189,248,0.08)"),
                yaxis=dict(gridcolor="rgba(56,189,248,0.08)", title="Units"),
                legend=dict(bgcolor="rgba(15,23,42,0.8)", bordercolor="rgba(56,189,248,0.2)", borderwidth=1),
                height=420,
            )
            st.plotly_chart(fig, width='stretch')


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: ADVANCED ANALYTICS
# ═══════════════════════════════════════════════════════════════════════════════
elif "Analytics" in page:
    st.markdown('<div class="page-title">📊 Advanced Analytics</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Consumption heatmaps, trends, and Power BI export</div>', unsafe_allow_html=True)

    summary, _ = api_get("/analytics/summary")
    if summary:
        a1, a2, a3, a4 = st.columns(4)
        for col, val, label, icon in [
            (a1, summary.get("total_units_last_30_days", 0), "Units (30 days)", "📦"),
            (a2, summary.get("total_units_last_year", 0), "Units (12 months)", "📅"),
            (a3, summary.get("avg_monthly_consumption", 0), "Avg Monthly", "📈"),
            (a4, summary.get("top_consuming_material") or "—", "Top Material", "🏆"),
        ]:
            with col:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-icon">{icon}</div>
                    <div class="metric-value" style="font-size:1.5rem;">{val}</div>
                    <div class="metric-label">{label}</div>
                </div>""", unsafe_allow_html=True)

    tab_heat, tab_trend, tab_top, tab_export = st.tabs(
        ["🔥 Heatmap", "📈 Consumption Trend", "🏆 Top Materials", "📤 Power BI Export"]
    )

    with tab_heat:
        hmap, err = api_get("/analytics/heatmap")
        if err:
            st.error(err)
        elif hmap and hmap.get("data"):
            months = hmap["months"]
            materials = [row["material"] for row in hmap["data"]]
            z = [[row.get(m, 0) for m in months] for row in hmap["data"]]
            fig = go.Figure(data=go.Heatmap(
                z=z, x=months, y=materials,
                colorscale=[[0, "#0a0e1a"], [0.5, "#1e3a5f"], [1, "#38bdf8"]],
                hoverongaps=False,
                text=[[str(v) for v in row] for row in z],
                texttemplate="%{text}",
            ))
            fig.update_layout(
                template="plotly_dark", paper_bgcolor="rgba(10,14,26,0)",
                plot_bgcolor="rgba(10,14,26,0)", font=dict(color="#94a3b8"),
                title=dict(text="Consumption Heatmap — Material × Month", font=dict(color="#e2e8f0", size=15)),
                height=max(250, len(materials) * 60),
                xaxis=dict(side="top"),
            )
            st.plotly_chart(fig, width='stretch')
        else:
            st.info("No consumption data yet. Use 'Seed History' on the AI Forecast page to generate demo data.")

    with tab_trend:
        trends, err = api_get("/analytics/trends")
        if err:
            st.error(err)
        elif trends:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=trends["months"], y=trends["totals"],
                mode="lines+markers", fill="tozeroy",
                line=dict(color="#38bdf8", width=3),
                fillcolor="rgba(56,189,248,0.08)",
                marker=dict(size=8, color="#818cf8"),
                name="Total Consumption",
            ))
            fig.update_layout(
                template="plotly_dark", paper_bgcolor="rgba(10,14,26,0)",
                plot_bgcolor="rgba(10,14,26,0)", font=dict(color="#94a3b8"),
                title=dict(text="Monthly Consumption Trend (Last 12 Months)", font=dict(color="#e2e8f0", size=15)),
                xaxis=dict(gridcolor="rgba(56,189,248,0.08)"),
                yaxis=dict(gridcolor="rgba(56,189,248,0.08)", title="Total Units Consumed"),
                height=380,
            )
            st.plotly_chart(fig, width='stretch')

    with tab_top:
        top_mats, err = api_get("/analytics/top-materials")
        if err:
            st.error(err)
        elif top_mats:
            names = [m["material"] for m in top_mats]
            vals = [m["total_consumed"] for m in top_mats]
            fig = go.Figure(go.Bar(
                x=vals, y=names, orientation="h",
                marker=dict(color="rgba(129,140,248,0.8)", line=dict(color="#818cf8", width=1)),
            ))
            fig.update_layout(
                template="plotly_dark", paper_bgcolor="rgba(10,14,26,0)",
                plot_bgcolor="rgba(10,14,26,0)", font=dict(color="#94a3b8"),
                title=dict(text="Top Consuming Materials (12 months)", font=dict(color="#e2e8f0", size=15)),
                xaxis=dict(title="Total Units Consumed", gridcolor="rgba(56,189,248,0.08)"),
                yaxis=dict(autorange="reversed"),
                height=max(300, len(names) * 45),
            )
            st.plotly_chart(fig, width='stretch')
        else:
            st.info("No data yet.")

    with tab_export:
        st.markdown("""
        <div class="data-card">
            <div style="font-size:1rem;font-weight:700;color:#e2e8f0;margin-bottom:12px;">📤 Power BI Compatible Export</div>
            <div style="font-size:0.85rem;color:#64748b;margin-bottom:16px;">
                Download your complete consumption dataset as CSV. Import directly into Power BI Desktop or Excel for advanced dashboards.
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(f"""
        <a href="{API_URL}/analytics/export/csv" target="_blank">
            <button style="background:linear-gradient(135deg,#38bdf8,#818cf8);color:#0a0e1a;border:none;
                           padding:12px 28px;border-radius:10px;font-weight:700;cursor:pointer;
                           font-size:0.9rem;width:100%;">
                ⬇️ Download Consumption CSV
            </button>
        </a>""", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.info("**Power BI Steps:**  Open Power BI Desktop → Get Data → CSV → Select downloaded file → Load → Build your custom dashboards!")


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: RFID & QR SCAN
# ═══════════════════════════════════════════════════════════════════════════════
elif "RFID" in page:
    st.markdown('<div class="page-title">📡 RFID & QR Scan</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Generate QR codes, log scan events, and view gate activity</div>', unsafe_allow_html=True)

    stats, _ = api_get("/rfid/stats")
    if stats:
        s1, s2 = st.columns(2)
        with s1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-icon">📡</div>
                <div class="metric-value">{stats['total_scans']}</div>
                <div class="metric-label">Total Scan Events</div>
            </div>""", unsafe_allow_html=True)
        with s2:
            by_type = stats.get("by_type", {})
            type_html = " &nbsp;·&nbsp; ".join([f"<strong>{t}</strong>: {c}" for t, c in by_type.items()])
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-icon">🔍</div>
                <div class="metric-value" style="font-size:1rem;">{type_html or '—'}</div>
                <div class="metric-label">Breakdown by Type</div>
            </div>""", unsafe_allow_html=True)

    tab_qr, tab_scan, tab_log = st.tabs(["📷 Generate QR Code", "⌨️ Log Scan Event", "📋 Scan History"])

    mats_data, _ = api_get("/materials/")
    mats_data = mats_data or []
    mat_opts = {m["name"]: m["id"] for m in mats_data}

    with tab_qr:
        if not mats_data:
            st.warning("No materials found.")
        else:
            st.markdown("#### 📷 Material QR Code Generator")
            st.info("Print these QR codes and attach to storage shelves, bins, or RFID gates.")
            qr_mat = st.selectbox("Select Material", list(mat_opts.keys()), key="qr_mat_sel")
            mat_id = mat_opts[qr_mat]
            if st.button("🔲 Generate QR Code", key="gen_qr_btn"):
                qr_url = f"{API_URL}/rfid/qr/{mat_id}"
                st.image(qr_url, width=220, caption=f"QR Code — {qr_mat}")
                st.markdown(f"""
                <div style="background:rgba(15,23,42,0.8);border:1px solid rgba(56,189,248,0.15);
                            border-radius:10px;padding:14px 18px;margin-top:12px;">
                    <div style="font-size:0.75rem;color:#64748b;margin-bottom:4px;">QR contains:</div>
                    <code style="color:#38bdf8;font-size:0.82rem;">
                        material_id: {mat_id} | name: {qr_mat}
                    </code><br>
                    <a href="{qr_url}" target="_blank" style="font-size:0.8rem;color:#818cf8;">🔗 Download PNG</a>
                </div>""", unsafe_allow_html=True)

    with tab_scan:
        st.markdown("#### ⌨️ Log Scan Event")
        st.info("""
        **Physical scanner note:** USB HID barcode/QR scanners type directly into the focused text field below.
        RFID readers can POST to: `POST /rfid/scan` with `{scan_data, scan_type, gate_id}`
        """)
        sc1, sc2 = st.columns(2)
        with sc1:
            scan_data_input = st.text_input("Scan Data (QR content or RFID tag)",
                                             placeholder="Scan with device or type manually", key="scan_data_inp")
            scan_type = st.selectbox("Scan Type", ["QR_IN", "QR_OUT", "RFID_IN", "RFID_OUT"], key="scan_type_sel")
        with sc2:
            if mats_data:
                sc_mat_opts = {"— Auto-detect —": None, **{m["name"]: m["id"] for m in mats_data}}
                sc_mat = st.selectbox("Material (optional)", list(sc_mat_opts.keys()), key="sc_mat_sel")
                mat_id_scan = sc_mat_opts[sc_mat]
            gate_id = st.text_input("Gate ID (optional)", placeholder="e.g. GATE-A1", key="gate_id_inp")

        if st.button("📡 Log Scan", key="log_scan_btn"):
            if not scan_data_input.strip():
                st.error("Scan data is required.")
            else:
                payload = {
                    "scan_data": scan_data_input,
                    "scan_type": scan_type,
                    "material_id": mat_id_scan if mats_data else None,
                    "gate_id": gate_id or None,
                }
                res, err = api_post("/rfid/scan", payload)
                if err:
                    st.error(f"❌ {err}")
                else:
                    st.success(f"✅ Scan logged — ID #{res['id']} | {res['scan_type']} | {res['scanned_at'][:16]}")

    with tab_log:
        st.markdown("#### 📋 Scan History")
        logs, err = api_get("/rfid/logs")
        if err:
            st.error(err)
        elif not logs:
            st.info("No scan events yet. Use the Log Scan tab to record events.")
        else:
            df = pd.DataFrame([{
                "ID": l["id"],
                "Material ID": l["material_id"] or "—",
                "Scan Data": l["scan_data"][:40],
                "Type": l["scan_type"],
                "Gate": l["gate_id"] or "—",
                "Time": l["scanned_at"][:16],
            } for l in logs])
            st.dataframe(df, width='stretch', hide_index=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: VENDORS & PURCHASE ORDERS
# ═══════════════════════════════════════════════════════════════════════════════
elif "Vendors" in page:
    st.markdown('<div class="page-title">🛒 Vendors & Purchase Orders</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Manage vendors and auto-generate POs for low-stock materials</div>', unsafe_allow_html=True)

    tab_vendors, tab_pos, tab_auto = st.tabs(["🏭 Vendors", "📄 Purchase Orders", "⚡ Auto-Create POs"])

    mats_data, _ = api_get("/materials/")
    mats_data = mats_data or []
    mat_map = {m["id"]: m["name"] for m in mats_data}

    with tab_vendors:
        vendors_data, _ = api_get("/vendors/")
        vendors_data = vendors_data or []

        col_vlist, col_vadd = st.columns([1.4, 1])
        with col_vlist:
            st.markdown("#### 🏭 Registered Vendors")
            if not vendors_data:
                st.info("No vendors yet. Add one on the right.")
            else:
                for v in vendors_data:
                    mat_name = mat_map.get(v["material_id"], f"#{v['material_id']}")
                    c_info, c_del = st.columns([5, 1])
                    with c_info:
                        st.markdown(f"""
                        <div style="background:rgba(15,23,42,0.7);border:1px solid rgba(56,189,248,0.12);
                                    border-radius:12px;padding:14px 18px;margin-bottom:8px;">
                            <div style="font-weight:700;color:#e2e8f0;">{v['name']}</div>
                            <div style="font-size:0.78rem;color:#64748b;margin-top:4px;">
                                📦 {mat_name} &nbsp;·&nbsp;
                                {'📧 ' + v['email'] if v.get('email') else '📭 No email'} &nbsp;·&nbsp;
                                {'💰 $' + str(v['unit_cost']) + '/unit' if v.get('unit_cost') else '💰 Cost TBD'}
                            </div>
                        </div>""", unsafe_allow_html=True)
                    with c_del:
                        if st.button("🗑️", key=f"del_v_{v['id']}"):
                            api_delete(f"/vendors/{v['id']}")
                            st.rerun()

        with col_vadd:
            st.markdown("#### ➕ Add Vendor")
            if not mats_data:
                st.warning("Add materials first.")
            else:
                mat_sel_opts = {m["name"]: m["id"] for m in mats_data}
                v_name = st.text_input("Vendor Name", key="vname")
                v_email = st.text_input("Email (for PO sending)", key="vemail")
                v_phone = st.text_input("Phone", key="vphone")
                v_mat = st.selectbox("Supplies Material", list(mat_sel_opts.keys()), key="vmat")
                v_cost = st.number_input("Unit Cost ($)", min_value=0.0, step=0.5, format="%.2f", key="vcost")
                if st.button("✅ Add Vendor", key="add_vendor_btn"):
                    if not v_name.strip():
                        st.error("Vendor name required.")
                    else:
                        res, err = api_post("/vendors/", {
                            "name": v_name, "email": v_email or None, "phone": v_phone or None,
                            "material_id": mat_sel_opts[v_mat], "unit_cost": v_cost or None
                        })
                        if err:
                            st.error(f"❌ {err}")
                        else:
                            st.success(f"✅ Vendor '{res['name']}' added!")
                            st.rerun()

    with tab_pos:
        pos_data, _ = api_get("/vendors/purchase-orders")
        pos_data = pos_data or []

        po_col1, po_col2 = st.columns([1.4, 1])
        with po_col1:
            st.markdown("#### 📄 Purchase Orders")
            if not pos_data:
                st.info("No purchase orders yet.")
            else:
                status_color = {"DRAFT": "#fbbf24", "SENT": "#38bdf8", "RECEIVED": "#34d399"}
                for po in pos_data:
                    mat_name = mat_map.get(po["material_id"], f"#{po['material_id']}")
                    sc = status_color.get(po["status"], "#64748b")
                    with st.expander(f"PO-{po['id']:04d} — {mat_name} — {po['quantity_ordered']} units — {po['status']}"):
                        c1, c2, c3 = st.columns(3)
                        c1.metric("Qty Ordered", po["quantity_ordered"])
                        c2.metric("Unit Cost", f"${po['unit_cost']:.2f}" if po.get("unit_cost") else "TBD")
                        c3.metric("Total", f"${po['total_cost']:.2f}" if po.get("total_cost") else "TBD")
                        st.markdown(f"**Notes:** {po.get('notes') or '—'}")
                        if po["status"] == "DRAFT":
                            if st.button(f"📤 Send PO-{po['id']:04d}", key=f"send_po_{po['id']}"):
                                res, err = api_put(f"/vendors/purchase-orders/{po['id']}/send")
                                st.success("PO sent!" + (" Email dispatched." if res and res.get("email_sent") else ""))
                                st.rerun()
                        elif po["status"] == "SENT":
                            if st.button(f"✅ Mark Received — PO-{po['id']:04d}", key=f"recv_po_{po['id']}"):
                                res, err = api_put(f"/vendors/purchase-orders/{po['id']}/receive")
                                st.success(f"Stock updated! New stock: {res.get('new_stock', '?')} units")
                                st.rerun()

        with po_col2:
            st.markdown("#### ➕ Create PO Manually")
            vendors_data_po, _ = api_get("/vendors/")
            vendors_data_po = vendors_data_po or []
            if not mats_data:
                st.warning("Add materials first.")
            else:
                po_mat_opts = {m["name"]: m["id"] for m in mats_data}
                po_ven_opts = {"None": None, **{f"{v['name']} (#{v['id']})": v["id"] for v in vendors_data_po}}
                po_mat = st.selectbox("Material", list(po_mat_opts.keys()), key="po_mat")
                po_vendor = st.selectbox("Vendor", list(po_ven_opts.keys()), key="po_vendor")
                po_qty = st.number_input("Quantity", min_value=1, step=1, key="po_qty")
                po_cost = st.number_input("Unit Cost ($)", min_value=0.0, format="%.2f", key="po_cost")
                po_notes = st.text_area("Notes", key="po_notes", height=80)
                if st.button("📄 Create PO", key="create_po_btn"):
                    res, err = api_post("/vendors/purchase-orders", {
                        "material_id": po_mat_opts[po_mat],
                        "vendor_id": po_ven_opts[po_vendor],
                        "quantity_ordered": int(po_qty),
                        "unit_cost": po_cost or None,
                        "notes": po_notes or None
                    })
                    if err:
                        st.error(f"❌ {err}")
                    else:
                        st.success(f"✅ PO-{res['id']:04d} created!")
                        st.rerun()

    with tab_auto:
        st.markdown("#### ⚡ Auto-Create POs for Low-Stock Materials")
        low_stock = [m for m in mats_data if m["total_stock"] <= m["reorder_level"]]
        if not low_stock:
            st.success("✅ All materials are adequately stocked. No POs needed.")
        else:
            st.warning(f"⚠️ {len(low_stock)} material(s) below reorder level:")
            for m in low_stock:
                st.markdown(f"- **{m['name']}** — Stock: {m['total_stock']} | Reorder: {m['reorder_level']}")

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🚀 Auto-Create All POs", key="auto_po_btn"):
                res, err = api_post("/vendors/auto-create-pos", {})
                if err:
                    st.error(f"❌ {err}")
                elif res:
                    st.success(f"✅ {res['count']} PO(s) created!")
                    for item in res.get("created", []):
                        st.markdown(f"- **{item['material']}** → {item['quantity']} units from {item['vendor']}")
                    st.rerun()
