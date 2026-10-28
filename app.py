from datetime import datetime, timedelta, timezone
from io import BytesIO
import os
import google_db as db
import pandas as pd
import streamlit as st

COLUMNS_LIST = [
    "Asset Code",
    "Asset Name",
    "Category",
    "Brand",
    "Model",
    "Serial Number",
    "Processor",
    "RAM",
    "Storage",
    "Operating System",
    "MAC Address",
    "IP Address",
    "Purchase Date",
    "Invoice Number",
    "Vendor",
    "Purchase Cost",
    "Warranty Start",
    "Warranty End",
    "Current Location",
    "Assigned To",
    "Department",
    "Status",
    "Remarks",
    "Last Verified Date",
    "Verified By",
    "Audit Status",
    "Damage & Issue Description",
]

LOG_COLUMNS = ["Timestamp", "User", "Action", "Asset Code", "Details"]

st.set_page_config(
    page_title="Lords Universal IT Asset ERP",
    layout="wide",
    initial_sidebar_state="expanded",
)

IST_TZ = timezone(timedelta(hours=5, minutes=30))


def get_ist_now():
  return datetime.now(IST_TZ)


today_date_str = get_ist_now().strftime("%d-%m-%Y")

# --- STYLING ---
st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght=400;500;600;700;800&display=swap');
        
        #MainMenu, footer, [data-testid="stStatusWidget"],
        [data-testid="manage-app-button"], [data-testid="stViewerBadge"],
        div[class*="viewerBadge"], div[class*="manageApp"] {
            display: none !important;
            visibility: hidden !important;
            opacity: 0 !important;
        }

        header[data-testid="stHeader"] {
            background-color: transparent !important;
        }
        
        [data-testid="stSidebarCollapsedControl"], 
        [data-testid="stSidebarCollapseButton"],
        button[aria-label="Toggle sidebar"] {
            display: flex !important;
            visibility: visible !important;
            opacity: 1 !important;
            background-color: #2563EB !important;
            color: #FFFFFF !important;
            border-radius: 8px !important;
            border: 2px solid #38BDF8 !important;
            z-index: 999999 !important;
            margin: 10px !important;
        }

        html, body, [data-testid="stAppViewContainer"], .main {
            background-color: #0F172A !important;
            color: #E2E8F0 !important;
            font-family: 'Plus Jakarta Sans', sans-serif !important;
        }
        
        .block-container {
            max-width: 99% !important;
            padding: 1.5rem 2rem !important;
        }
        
        [data-testid="stSidebar"] {
            background-color: #1E293B !important;
            border-right: 1px solid #334155 !important;
        }
        [data-testid="stSidebar"] [data-testid="stWidgetLabel"], 
        [data-testid="stSidebar"] p, [data-testid="stSidebar"] label, [data-testid="stSidebar"] span {
            color: #F8FAFC !important;
            font-size: 14px !important;
            font-weight: 600 !important;
        }
        
        .workspace-clean-card {
            background: #1E293B;
            border: 1px solid #334155;
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 24px;
        }
        
        .card-heading {
            font-size: 14px;
            font-weight: 800;
            color: #38BDF8;
            margin-bottom: 16px;
            padding-bottom: 8px;
            border-bottom: 2px solid #334155;
            text-transform: uppercase;
            letter-spacing: 0.8px;
        }

        .metric-card-wrapper {
            background-color: #1E293B !important;
            border: 1px solid #334155 !important;
            border-top-left-radius: 12px !important;
            border-top-right-radius: 12px !important;
            padding: 20px 10px 10px 10px !important;
            text-align: center;
        }
        .card-label { font-size: 11px; font-weight: 700; color: #94A3B8; text-transform: uppercase; }
        .card-val { font-size: 36px; font-weight: 800; color: #FFFFFF; margin-top: 4px; }

        .stButton > button {
            width: 100% !important;
            border-top-left-radius: 0px !important;
            border-top-right-radius: 0px !important;
            border-bottom-left-radius: 12px !important;
            border-bottom-right-radius: 12px !important;
            background-color: #0F172A !important;
            color: #38BDF8 !important;
            border: 1px solid #334155 !important;
            border-top: none !important;
            font-size: 11px !important;
            font-weight: 700 !important;
            text-transform: uppercase !important;
            padding: 8px 0px !important;
            transition: all 0.2s ease;
        }
        .stButton > button:hover {
            background-color: #2563EB !important;
            color: #FFFFFF !important;
            border-color: #2563EB !important;
        }

        .erp-data-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
            background: #1E293B;
        }
        .erp-data-table th {
            background: #0F172A !important;
            color: #38BDF8 !important;
            font-weight: 700;
            padding: 14px 16px;
            text-align: left;
            border: 1px solid #334155;
            white-space: nowrap;
        }
        .erp-data-table td {
            padding: 12px 16px;
            border: 1px solid #334155;
            color: #E2E8F0;
            white-space: nowrap;
        }
        .erp-data-table tr:nth-child(even) td { background-color: #111827; }
        .erp-data-table tr:hover td { background-color: #2D3748 !important; }
        
        .status-pill {
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
            display: inline-block;
        }
        .pill-available { background-color: rgba(16, 185, 129, 0.2); color: #34D399; border: 1px solid #10B981; }
        .pill-issued { background-color: rgba(245, 158, 11, 0.2); color: #FBBF24; border: 1px solid #F59E0B; }
        .pill-repair { background-color: rgba(59, 130, 246, 0.2); color: #60A5FA; border: 1px solid #3B82F6; }
        .pill-scrap { background-color: rgba(239, 68, 68, 0.2); color: #F87171; border: 1px solid #EF4444; }

        .timeline-box {
            border-left: 3px solid #38BDF8;
            margin-left: 10px;
            padding-left: 20px;
            position: relative;
            margin-bottom: 20px;
        }
        .timeline-box::before {
            content: '';
            position: absolute;
            left: -8px;
            top: 2px;
            width: 14px;
            height: 14px;
            border-radius: 50%;
            background-color: #2563EB;
            border: 2px solid #38BDF8;
        }

        div[data-testid="stTextInput"] input, .stTextInput input, textarea, select {
            color: #FFFFFF !important;
            background-color: #0F172A !important;
            border: 1px solid #475569 !important;
        }
        label, p, span { color: #F8FAFC !important; }
    </style>
""",
    unsafe_allow_html=True,
)

# USER CREDENTIALS MANAGEMENT
DEFAULT_USERS = {
    "vedprakash.dubey@universal.edu.in": {
        "pass": "Vedprakash@123",
        "role": "Admin",
        "name": "Vedprakash Dubey",
    },
    "vediset2011@gmail.com": {
        "pass": "Vedprakash@123",
        "role": "Admin",
        "name": "Vedprakash Dubey",
    },
    "giridhar.balakrishnan@universal.edu.in": {
        "pass": "Giridhar@123",
        "role": "Assistant",
        "name": "Giridhar Balakrishnan",
    },
    "ahtesham.qureshi@universal.edu.in": {
        "pass": "Ahtesham@123",
        "role": "Assistant",
        "name": "Ahtesham Qureshi",
    },
}


@st.cache_data(ttl=60)
def load_user_credentials():
  try:
    udf = db.load_data_from_sheet("Users")
    if not udf.empty and "Email" in udf.columns:
      users_dict = {}
      for _, r in udf.iterrows():
        users_dict[str(r["Email"]).strip().lower()] = {
            "pass": str(r["Password"]).strip(),
            "role": str(r["Role"]).strip(),
            "name": str(r["Name"]).strip(),
        }
      return users_dict
  except Exception:
    pass
  return DEFAULT_USERS


def save_user_credentials(email_id, new_pass):
  user_data = USERS.get(email_id)
  if user_data:
    updated_dict = {
        "Email": email_id,
        "Password": new_pass,
        "Role": user_data["role"],
        "Name": user_data["name"],
    }
    try:
      db.update_row_in_sheet("Users", "Email", email_id, updated_dict)
      st.cache_data.clear()
    except Exception as e:
      st.error(f"Error saving user details: {e}")


USERS = load_user_credentials()

if "authenticated" not in st.session_state:
  st.session_state.authenticated = False
  st.session_state.logged_user = ""
  st.session_state.user_role = ""
  st.session_state.user_name = ""

# LOGIN CHECK
if not st.session_state.authenticated:
  st.markdown(
      """
        <div style='max-width: 420px; margin: 60px auto; padding: 30px; background-color: #1E293B; border-radius: 12px; border: 1px solid #334155;'>
            <h2 style='text-align:center; color:#FFFFFF; margin-bottom:5px;'>LORDS UNIVERSAL IT ERP</h2>
            <p style='text-align:center; color:#38BDF8; font-size:13px; margin-bottom:25px;'>Enter Corporate Credentials to Access</p>
        </div>
    """,
      unsafe_allow_html=True,
  )
  with st.form("login_form"):
    username_input = st.text_input("Corporate Email ID")
    password_input = st.text_input("Password", type="password")
    submit = st.form_submit_button("🔑 SECURE LOGIN")
    if submit:
      u_clean = username_input.strip().lower()
      if u_clean in USERS and USERS[u_clean]["pass"] == password_input:
        st.session_state.authenticated = True
        st.session_state.logged_user = u_clean
        st.session_state.user_role = USERS[u_clean]["role"]
        st.session_state.user_name = USERS[u_clean]["name"]
        st.success("Login Successful!")
        st.rerun()
      else:
        st.error("Invalid Email ID or Password!")
  st.stop()


def log_activity(action, asset_code, details):
  try:
    now_ist = get_ist_now().strftime("%Y-%m-%d %H:%M:%S")
    current_user_email = st.session_state.get("logged_user", "Admin")
    current_user_name = st.session_state.get("user_name", "Vedprakash Dubey")
    user_str = f"{current_user_name} ({current_user_email})"
    log_data = {
        "Timestamp": now_ist,
        "User": user_str,
        "Action": action,
        "Asset Code": asset_code,
        "Details": details,
    }
    db.append_row_to_sheet("Activity_Logs", log_data)
  except Exception:
    pass


def load_logs():
  try:
    logs_df = db.load_data_from_sheet("Activity_Logs")
    if logs_df.empty:
      return pd.DataFrame(columns=LOG_COLUMNS)
    if "User Email" in logs_df.columns and "User" not in logs_df.columns:
      logs_df = logs_df.rename(columns={"User Email": "User"})
    for col in LOG_COLUMNS:
      if col not in logs_df.columns:
        logs_df[col] = "-"
    return logs_df[LOG_COLUMNS]
  except Exception:
    return pd.DataFrame(columns=LOG_COLUMNS)


@st.cache_data(ttl=60)
def load_database_file():
  try:
    data = db.load_data_from_sheet("Assets")
    if not data.empty:
      data = data.fillna("-")
      for col in COLUMNS_LIST:
        if col not in data.columns:
          data[col] = "-"
      for col in data.columns:
        data[col] = data[col].astype(str).str.strip()
      return data[COLUMNS_LIST]
  except Exception:
    pass
  return pd.DataFrame(columns=COLUMNS_LIST)


df = load_database_file()
logs_df = load_logs()


def generate_product_prefix(category_str):
  clean = str(category_str).strip().upper()
  if "ALL-IN-ONE" in clean or "ALL IN ONE" in clean or clean == "AIO":
    return "AIO"
  if "LAPTOP" in clean:
    return "LPT"
  if "PRINTER" in clean:
    return "PRN"
  if "KEYBOARD" in clean:
    return "KEY"
  if "MOUSE" in clean:
    return "MSE"
  if "ROUTER" in clean or "RTR" in clean:
    return "RTR"
  if "DVR" in clean or "NVR" in clean:
    return "DVR"
  clean_alpha = "".join(e for e in clean if e.isalnum())
  if not clean_alpha:
    return "AST"
  if len(clean_alpha) <= 3:
    return clean_alpha.ljust(3, "X")
  vowels = ["A", "E", "I", "O", "U"]
  no_vowels = [char for char in clean_alpha if char not in vowels]
  return "".join(no_vowels[:3]) if len(no_vowels) >= 3 else clean_alpha[:3]


def render_download_buttons(dataframe, file_prefix="LUC_IT_Export", key_id=""):
  if dataframe.empty:
    return
  col_d1, col_d2 = st.columns(2)
  excel_stream = BytesIO()
  with pd.ExcelWriter(excel_stream, engine="openpyxl") as ew:
    dataframe.to_excel(ew, index=False)
  col_d1.download_button(
      label="📥 Download Excel (.xlsx)",
      data=excel_stream.getvalue(),
      file_name=f"{file_prefix}_{today_date_str}.xlsx",
      mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
      key=f"dl_xlsx_{file_prefix}_{key_id}",
      use_container_width=True,
  )
  csv_data = dataframe.to_csv(index=False).encode("utf-8")
  col_d2.download_button(
      label="📄 Download CSV (.csv)",
      data=csv_data,
      file_name=f"{file_prefix}_{today_date_str}.csv",
      mime="text/csv",
      key=f"dl_csv_{file_prefix}_{key_id}",
      use_container_width=True,
  )


def render_comprehensive_ledger(
    dataframe, file_prefix="LUC_IT_Ledger", show_downloads=True, key_id="view"
):
  if dataframe.empty:
    st.info("No matching items found.")
    return
  if show_downloads:
    render_download_buttons(dataframe, file_prefix=file_prefix, key_id=key_id)
  html = (
      "<div style='overflow-x:auto; border:1px solid #334155; border-radius:10px;"
      " margin-top:12px;'><table class='erp-data-table'><thead><tr>"
  )
  html += (
      "".join(f"<th>{col}</th>" for col in COLUMNS_LIST) + "</tr></thead><tbody>"
  )
  for _, row in dataframe.iterrows():
    html += "<tr>"
    for col in COLUMNS_LIST:
      val = row.get(col, "-")
      if col == "Status":
        if str(val).lower() in ["available", "working"]:
          html += (
              f"<td><span class='status-pill pill-available'>{val}</span></td>"
          )
        elif str(val).lower() in ["issued", "in use"]:
          html += f"<td><span class='status-pill pill-issued'>{val}</span></td>"
        elif "repair" in str(val).lower():
          html += f"<td><span class='status-pill pill-repair'>{val}</span></td>"
        elif str(val).lower() in ["scrap", "damaged"]:
          html += f"<td><span class='status-pill pill-scrap'>{val}</span></td>"
        else:
          html += f"<td>{val}</td>"
      elif col == "Audit Status":
        if "verified" in str(val).lower():
          html += f"<td><span style='color:#34D399; font-weight:700;'>✅ {val}</span></td>"
        else:
          html += f"<td><span style='color:#F87171; font-weight:700;'>⏳ {val}</span></td>"
      elif col == "Damage & Issue Description":
        if str(val).strip() not in ["-", "", "None (Good Condition)"]:
          html += f"<td style='background-color:rgba(239, 68, 68, 0.2); color:#FCA5A5; font-weight:600;'>⚠️ {val}</td>"
        else:
          html += f"<td style='color:#94A3B8;'>{val}</td>"
      else:
        html += f"<td>{val}</td>"
    html += "</tr>"
  html += "</tbody></table></div>"
  st.markdown(html, unsafe_allow_html=True)


if "current_dashboard_view" not in st.session_state:
  st.session_state.current_dashboard_view = "Main_Grid"

# SIDEBAR CONTROL PANEL
with st.sidebar:
  st.markdown(
      "<div style='padding: 10px 0; border-bottom: 1px solid #334155;'><h2"
      " style='color:#FFFFFF; font-weight:800; font-size:18px; margin:0;'>LORDS"
      " UNIVERSAL</h2><p style='color:#38BDF8; font-size:11px; font-weight:600;"
      " margin:0;'>IT Asset Control ERP</p></div><br>",
      unsafe_allow_html=True,
  )

  role_badge = (
      "👑 FULL ADMIN" if st.session_state.user_role == "Admin" else "👤 ASSISTANT"
  )
  st.markdown(
      f"<div style='background:#0F172A; padding:10px; border-radius:8px;"
      " border:1px solid #334155; margin-bottom:15px;'><span"
      " style='font-size:12px; color:#38BDF8;"
      f" font-weight:700;'>{role_badge}</span><br><span style='font-size:13px;"
      f" color:#FFFFFF;'>{st.session_state.user_name}</span></div>",
      unsafe_allow_html=True,
  )

  if st.button("🔄 REFRESH LIVE DATA"):
    st.cache_data.clear()
    st.rerun()

  if st.button("🚪 LOGOUT"):
    st.session_state.authenticated = False
    st.rerun()

  menu_options = [
      "📊 Dashboard",
      "🔍 Monthly Asset Audit",
      "➕ Add New Asset",
      "✏️ Edit / Update Asset",
      "📑 Issue / Allocate Item",
      "🛠️ Repair & Maintenance",
      "📜 Asset Lifecycle & Repair History",
      "⏱️ Warranty Records",
  ]
  if st.session_state.user_role == "Admin":
    menu_options.append("📜 Activity Logs (Audit)")
    menu_options.append("🔑 Reset User Passwords")

  menu_selection = st.sidebar.radio(
      "NAVIGATION REGISTERS:", menu_options, label_visibility="collapsed"
  )

  if menu_selection != "📊 Dashboard":
    st.session_state.current_dashboard_view = "Main_Grid"

st.markdown(
    f"<div class='workspace-clean-card' style='background: linear-gradient(90deg,"
    " #1E293B, #0F172A); border-color:#334155; padding: 16px 24px;"
    " margin-bottom:20px;'><span style='font-size:20px; font-weight:800;"
    f" color:#FFFFFF;'>{menu_selection[2:].upper()} PANEL</span></div>",
    unsafe_allow_html=True,
)

# ==================== MODULE 1: INTERACTIVE DASHBOARD ====================
if menu_selection == "📊 Dashboard":
  if st.session_state.current_dashboard_view == "Main_Grid":
    t_count = len(df)
    a_count = (
        len(df[df["Status"].str.lower().isin(["available", "working"])])
        if not df.empty
        else 0
    )
    i_count = (
        len(df[df["Status"].str.lower().isin(["issued", "in use"])])
        if not df.empty
        else 0
    )
    r_count = (
        len(df[df["Status"].str.lower().str.contains("repair")])
        if not df.empty
        else 0
    )
    s_count = (
        len(df[df["Status"].str.lower().isin(["scrap", "damaged"])])
        if not df.empty
        else 0
    )

    damaged_df = pd.DataFrame()
    if not df.empty and "Damage & Issue Description" in df.columns:
      damaged_df = df[
          ~df["Damage & Issue Description"]
          .str.strip()
          .isin(["-", "", "None (Good Condition)"])
      ]

    if not damaged_df.empty:
      st.markdown(
          f"""
            <div style='background: linear-gradient(90deg, #7F1D1D, #991B1B); border: 2px solid #EF4444; border-radius: 12px; padding: 16px 20px; margin-bottom: 20px;'>
                <span style='font-size:16px; font-weight:800; color:#FFFFFF;'>🚨 ATTENTION REQUIRED: {len(damaged_df)} ASSETS WITH ACTIVE DAMAGES / ISSUES!</span>
                <p style='margin:4px 0 0 0; font-size:13px; color:#FECACA;'>These hardware issues require repair, maintenance, or replacement action.</p>
            </div>
            """,
          unsafe_allow_html=True,
      )

    m1, m2, m3, m4, m5 = st.columns(5)
    with m1:
      st.markdown(
          f"<div class='metric-card-wrapper'><span class='card-label'>Total"
          f" Items</span><div class='card-val'>{t_count}</div></div>",
          unsafe_allow_html=True,
      )
      if st.button("View Details ➡️", key="go_total"):
        st.session_state.current_dashboard_view = "Total_View"
        st.rerun()
    with m2:
      st.markdown(
          "<div class='metric-card-wrapper'><span class='card-label'"
          " style='color:#34D399;'>Available</span><div class='card-val'"
          f" style='color:#34D399;'>{a_count}</div></div>",
          unsafe_allow_html=True,
      )
      if st.button("View Details ➡️", key="go_avail"):
        st.session_state.current_dashboard_view = "Available_View"
        st.rerun()
    with m3:
      st.markdown(
          "<div class='metric-card-wrapper'><span class='card-label'"
          " style='color:#FBBF24;'>Issued</span><div class='card-val'"
          f" style='color:#FBBF24;'>{i_count}</div></div>",
          unsafe_allow_html=True,
      )
      if st.button("View Details ➡️", key="go_issued"):
        st.session_state.current_dashboard_view = "Issued_View"
        st.rerun()
    with m4:
      st.markdown(
          "<div class='metric-card-wrapper'><span class='card-label'"
          " style='color:#60A5FA;'>In Repair</span><div class='card-val'"
          f" style='color:#60A5FA;'>{r_count}</div></div>",
          unsafe_allow_html=True,
      )
      if st.button("View Details ➡️", key="go_repair"):
        st.session_state.current_dashboard_view = "Repair_View"
        st.rerun()
    with m5:
      st.markdown(
          "<div class='metric-card-wrapper'><span class='card-label'"
          " style='color:#F87171;'>Scrap Yard</span><div class='card-val'"
          f" style='color:#F87171;'>{s_count}</div></div>",
          unsafe_allow_html=True,
      )
      if st.button("View Details ➡️", key="go_scrap"):
        st.session_state.current_dashboard_view = "Scrap_View"
        st.rerun()

    st.markdown("<div class='workspace-clean-card'>", unsafe_allow_html=True)
    fc1, fc2 = st.columns([1.5, 2])
    grid_filter = fc1.selectbox(
        "Select Status Filter:",
        [
            "All Items Pool",
            "Available Stock",
            "Issued / Deployed",
            "In Repair Pipeline",
            "Scrap Yard Stock",
            "⚠️ Items with Damage / Issues",
        ],
    )
    live_query = fc2.text_input(
        "Live Data Search Filter:",
        placeholder="Type Tag, Brand, Staff Name, Location...",
    )

    df_view = df.copy()
    if "Available" in grid_filter and not df_view.empty:
      df_view = df_view[
          df_view["Status"].str.lower().isin(["available", "working"])
      ]
    elif "Issued" in grid_filter and not df_view.empty:
      df_view = df_view[df_view["Status"].str.lower().isin(["issued", "in use"])]
    elif "Repair" in grid_filter and not df_view.empty:
      df_view = df_view[df_view["Status"].str.lower().str.contains("repair")]
    elif "Scrap" in grid_filter and not df_view.empty:
      df_view = df_view[
          df_view["Status"].str.lower().isin(["scrap", "damaged"])
      ]
    elif "Damage" in grid_filter and not df_view.empty:
      df_view = df_view[
          ~df_view["Damage & Issue Description"]
          .str.strip()
          .isin(["-", "", "None (Good Condition)"])
      ]

    if live_query and not df_view.empty:
      df_view = df_view[
          df_view.astype(str)
          .apply(lambda x: x.str.contains(live_query, case=False))
          .any(axis=1)
      ]

    render_comprehensive_ledger(
        df_view, file_prefix="Filtered_IT_Assets", key_id="main_grid"
    )
    st.markdown("</div>", unsafe_allow_html=True)

# ==================== MODULE 5: REPAIR & MAINTENANCE ====================
elif menu_selection == "🛠️ Repair & Maintenance":
  st.markdown(
      "<div class='workspace-clean-card'><div class='card-heading'>Hardware"
      " Repair, Part Replacement & Cost Tracker</div>",
      unsafe_allow_html=True,
  )
  with st.form("repair_form"):
    all_assets = df["Asset Code"].tolist() if not df.empty else []
    rc1, rc2 = st.columns(2)
    maint_asset = rc1.selectbox(
        "Select Asset Tag / Laptop*:", all_assets if all_assets else ["-"]
    )
    maint_status = rc2.selectbox(
        "Change Asset Status to*:",
        [
            "In Repair",
            "Available (Repaired & Restored)",
            "Scrap (Unrepairable)",
        ],
    )

    rc3, rc4 = st.columns(2)
    maint_issue = rc3.text_input(
        "Fault / Part Repaired or Replaced*:",
        placeholder="e.g. Keyboard Replaced, Motherboard Chip Level Repair, Screen Cracked, RAM Issue",
    )
    maint_cost = rc4.text_input(
        "Repair / Service Cost (₹):",
        value="0",
        placeholder="e.g. 1500, 3500",
    )

    rc5, rc6 = st.columns(2)
    maint_vendor = rc5.text_input(
        "Service Vendor / Technician:",
        placeholder="e.g. Dell Authorized, Local Tech Shop, In-House",
    )
    maint_remarks = rc6.text_input(
        "Additional Notes / Invoice Ref:",
        value=f"Service recorded on {today_date_str}",
    )

    if st.form_submit_button("🛠️ LOG REPAIR & UPDATE STATUS") and all_assets:
      if not maint_issue.strip():
        st.error(
            "Kripya 'Fault / Part Repaired or Replaced' field jarur bharein!"
        )
      else:
        row_data = df[df["Asset Code"] == maint_asset].iloc[0].to_dict()

        status_tag = (
            "In Repair"
            if "In Repair" in maint_status
            else ("Available" if "Available" in maint_status else "Scrap")
        )
        row_data["Status"] = status_tag

        cost_val = maint_cost.strip().replace("₹", "").replace(",", "")
        if not cost_val.isdigit():
          cost_val = "0"

        # Structured log format for accurate parsing
        formatted_log_details = (
            f"REPAIRED: {maint_issue.strip()} | COST: ₹{cost_val} | VENDOR:"
            f" {maint_vendor.strip() if maint_vendor.strip() else 'In-House'} |"
            f" STATUS: {status_tag} | NOTES: {maint_remarks.strip()}"
        )

        if status_tag == "Available":
          row_data["Assigned To"] = "-"
          row_data["Current Location"] = "MAIN STORE"
          row_data["Remarks"] = (
              f"Repaired ({maint_issue.strip()}) on {today_date_str}"
          )
          row_data["Damage & Issue Description"] = "-"
        elif status_tag == "In Repair":
          row_data["Damage & Issue Description"] = (
              f"Under Repair: {maint_issue.strip()}"
          )
          row_data["Remarks"] = (
              f"Sent for repair ({maint_issue.strip()}) on {today_date_str}"
          )

        if db.update_row_in_sheet("Assets", "Asset Code", maint_asset, row_data):
          log_activity("MAINTENANCE_CHANGE", maint_asset, formatted_log_details)
          st.cache_data.clear()
          st.success(
              f"Repair record successfully logged for **{maint_asset}**! Cost:"
              f" ₹{cost_val}"
          )
          st.rerun()
        else:
          st.error("Failed to update Google Sheet.")

  st.markdown(
      "<br><div class='card-heading'>Active Items Under Repair Pipeline</div>",
      unsafe_allow_html=True,
  )
  render_comprehensive_ledger(
      df[df["Status"].str.lower().str.contains("repair")]
      if not df.empty
      else df,
      file_prefix="Repair_Items",
      key_id="module_repair",
  )
  st.markdown("</div>", unsafe_allow_html=True)

# ==================== MODULE: LIFECYCLE & REPAIR HISTORY ====================
elif menu_selection == "📜 Asset Lifecycle & Repair History":
  st.markdown(
      "<div class='workspace-clean-card'><div class='card-heading'>Item Repair"
      " Details, Parts Replaced & Cost Ledger</div>",
      unsafe_allow_html=True,
  )

  # Parse logs to extract clean repair events with costs and parts
  asset_repair_stats = {}
  parsed_repairs_by_asset = {}

  if not logs_df.empty:
    for _, log_r in logs_df.iterrows():
      act = str(log_r.get("Action", ""))
      det = str(log_r.get("Details", ""))
      a_code = str(log_r.get("Asset Code", "")).strip()

      if a_code not in asset_repair_stats:
        asset_repair_stats[a_code] = {"count": 0, "total_cost": 0}
        parsed_repairs_by_asset[a_code] = []

      # Detect repair events
      if (
          "MAINTENANCE_CHANGE" in act
          or "repair" in det.lower()
          or "REPAIRED:" in det
      ):
        # Extract part/issue
        part = "General Maintenance / Repair"
        cost = 0
        vendor = "-"

        if "REPAIRED:" in det:
          try:
            parts_split = det.split("|")
            for segment in parts_split:
              seg = segment.strip()
              if seg.startswith("REPAIRED:"):
                part = seg.replace("REPAIRED:", "").strip()
              elif seg.startswith("COST:"):
                cost_str = "".join(
                    c for c in seg.replace("COST:", "") if c.isdigit()
                )
                if cost_str:
                  cost = int(cost_str)
              elif seg.startswith("VENDOR:"):
                vendor = seg.replace("VENDOR:", "").strip()
          except Exception:
            part = det
        else:
          part = det

        asset_repair_stats[a_code]["count"] += 1
        asset_repair_stats[a_code]["total_cost"] += cost
        parsed_repairs_by_asset[a_code].append({
            "Date": str(log_r.get("Timestamp", "-")).split(" ")[0],
            "Repaired Item / Part Replaced": part,
            "Service Vendor": vendor,
            "Repair Cost (₹)": f"₹{cost:,}" if cost > 0 else "₹0",
            "Cost_Num": cost,
            "Logged By": log_r.get("User", "-"),
            "Raw Details": det,
        })

  # Dropdown to select Asset
  asset_options = sorted(df["Asset Code"].tolist()) if not df.empty else []
  col_s1, col_s2, col_s3 = st.columns([2, 1, 1])
  with col_s1:
    selected_asset = st.selectbox(
        "🔍 Select or Search Asset Tag (e.g. LAB101-LPT-02):",
        ["-- Select Asset --"] + asset_options,
    )

  with col_s2:
    if selected_asset != "-- Select Asset --":
      stat = asset_repair_stats.get(
          selected_asset, {"count": 0, "total_cost": 0}
      )
      pill_c = (
          "#34D399"
          if stat["count"] == 0
          else ("#FBBF24" if stat["count"] < 3 else "#F87171")
      )
      st.markdown(
          f"<div style='background:#0F172A; border:1px solid #334155; padding:10px 14px; border-radius:8px; text-align:center;'>"
          f"<span style='font-size:11px; color:#94A3B8; font-weight:700;'>TOTAL REPAIRS RECORDED</span><br>"
          f"<span style='font-size:22px; font-weight:800; color:{pill_c};'>{stat['count']} TIMES</span>"
          f"</div>",
          unsafe_allow_html=True,
      )

  with col_s3:
    if selected_asset != "-- Select Asset --":
      stat = asset_repair_stats.get(
          selected_asset, {"count": 0, "total_cost": 0}
      )
      st.markdown(
          f"<div style='background:#0F172A; border:1px solid #334155; padding:10px 14px; border-radius:8px; text-align:center;'>"
          f"<span style='font-size:11px; color:#94A3B8; font-weight:700;'>TOTAL REPAIR COST</span><br>"
          f"<span style='font-size:22px; font-weight:800; color:#38BDF8;'>₹{stat['total_cost']:,}</span>"
          f"</div>",
          unsafe_allow_html=True,
      )

  # DETAILED DOSSIER
  if selected_asset and selected_asset != "-- Select Asset --":
    asset_info = df[df["Asset Code"] == selected_asset].iloc[0]

    st.markdown("---")
    st.markdown(
        f"<h3 style='color:#38BDF8; font-weight:800; margin-bottom:14px;'>🖥️"
        f" Dossier: {selected_asset} - {asset_info.get('Asset Name', '')}</h3>",
        unsafe_allow_html=True,
    )

    # 4-Column Specs
    c1, c2, c3, c4 = st.columns(4)
    with c1:
      st.markdown(
          f"**Brand / Model:** {asset_info.get('Brand', '-')} /"
          f" {asset_info.get('Model', '-')}"
      )
      st.markdown(f"**Serial No (S/N):** `{asset_info.get('Serial Number', '-')}`")
      st.markdown(f"**MAC Address:** `{asset_info.get('MAC Address', '-')}`")
    with c2:
      st.markdown(
          f"**Config:** {asset_info.get('Processor', '-')} |"
          f" {asset_info.get('RAM', '-')} | {asset_info.get('Storage', '-')}"
      )
      st.markdown(f"**Operating System:** {asset_info.get('Operating System', '-')}")
      st.markdown(f"**IP Address:** `{asset_info.get('IP Address', '-')}`")
    with c3:
      curr_st = asset_info.get("Status", "-")
      p_class = (
          "pill-available"
          if curr_st.lower() in ["available", "working"]
          else (
              "pill-issued"
              if curr_st.lower() in ["issued", "in use"]
              else "pill-repair"
          )
      )
      st.markdown(
          f"**Current Status:** <span class='status-pill"
          f" {p_class}'>{curr_st}</span>",
          unsafe_allow_html=True,
      )
      st.markdown(
          f"**Current Location:** `{asset_info.get('Current Location', '-')}`"
      )
      st.markdown(f"**Assigned To:** `{asset_info.get('Assigned To', '-')}`")
    with c4:
      st.markdown(f"**Purchase Date:** {asset_info.get('Purchase Date', '-')}")
      st.markdown(f"**Warranty End:** {asset_info.get('Warranty End', '-')}")
      st.markdown(
          f"**Last Verified:** {asset_info.get('Last Verified Date', '-')}"
      )

    st.markdown("<br>", unsafe_allow_html=True)

    # REPAIR HISTORY TABLE
    st.markdown(
        "<div class='card-heading'>🛠️ Specific Repair History (Part Replaced,"
        " Dates & Cost)</div>",
        unsafe_allow_html=True,
    )

    specific_repairs = parsed_repairs_by_asset.get(selected_asset, [])
    if specific_repairs:
      rep_df = pd.DataFrame(specific_repairs)
      disp_table = rep_df[[
          "Date",
          "Repaired Item / Part Replaced",
          "Service Vendor",
          "Repair Cost (₹)",
          "Logged By",
      ]]

      r_html = (
          "<div style='overflow-x:auto; border:1px solid #334155;"
          " border-radius:10px;'><table class='erp-data-table'><thead><tr><th"
          " style='color:#38BDF8;'>Repair Date</th><th>What Got Repaired /"
          " Part Replaced</th><th>Vendor / Technician</th><th"
          " style='color:#FBBF24;'>Cost Incurred</th><th>Logged"
          " By</th></tr></thead><tbody>"
      )
      for _, r_item in disp_table.iterrows():
        r_html += f"""<tr>
                    <td><b>📅 {r_item['Date']}</b></td>
                    <td style='color:#FCA5A5; font-weight:700;'>⚠️ {r_item['Repaired Item / Part Replaced']}</td>
                    <td>{r_item['Service Vendor']}</td>
                    <td style='font-weight:800; color:#38BDF8;'>{r_item['Repair Cost (₹)']}</td>
                    <td style='color:#94A3B8;'>{r_item['Logged By']}</td>
                </tr>"""
      r_html += "</tbody></table></div>"
      st.markdown(r_html, unsafe_allow_html=True)
    else:
      st.info(
          f"No repair logs found for {selected_asset}. Jab bhi aap '🛠️ Repair"
          " & Maintenance' panel se repair enter karenge, details yaha dikhegi."
      )

    st.markdown("<br>", unsafe_allow_html=True)
    # COMPLETE CHRONOLOGICAL AUDIT & ISSUE TIMELINE
    st.markdown(
        "<div class='card-heading'>🕒 Complete Lifecycle Activity Timeline</div>",
        unsafe_allow_html=True,
    )

    asset_history_logs = pd.DataFrame()
    if not logs_df.empty:
      asset_history_logs = logs_df[
          logs_df["Asset Code"].str.lower() == selected_asset.lower()
      ].sort_values(by="Timestamp", ascending=False)

    if not asset_history_logs.empty:
      for _, h_row in asset_history_logs.iterrows():
        action_type = h_row.get("Action", "ACTION")
        badge_style = "color:#38BDF8;"
        if "REPAIR" in action_type or "MAINTENANCE" in action_type:
          badge_style = (
              "background-color:rgba(239, 68, 68, 0.2); color:#F87171; padding:"
              " 2px 8px; border-radius: 4px; font-weight:700;"
          )
        elif "ISSUE" in action_type:
          badge_style = (
              "background-color:rgba(245, 158, 11, 0.2); color:#FBBF24; padding:"
              " 2px 8px; border-radius: 4px; font-weight:700;"
          )
        elif "AUDIT" in action_type:
          badge_style = (
              "background-color:rgba(16, 185, 129, 0.2); color:#34D399; padding:"
              " 2px 8px; border-radius: 4px; font-weight:700;"
          )

        st.markdown(
            f"""
                <div class='timeline-box'>
                    <span style='font-size:12px; color:#94A3B8; font-weight:600;'>📅 {h_row.get('Timestamp', '-')}</span>
                    &nbsp;|&nbsp; <span style='font-size:12px; {badge_style}'>{action_type}</span>
                    &nbsp;|&nbsp; <span style='font-size:12px; color:#E2E8F0;'>Logged By: <b>{h_row.get('User', '-')}</b></span>
                    <div style='margin-top:6px; font-size:13px; color:#F1F5F9;'>
                        {h_row.get('Details', '-')}
                    </div>
                </div>
                """,
            unsafe_allow_html=True,
        )

  st.markdown("---")
  st.markdown(
      "<div class='card-heading'>📊 All Assets Repair Frequency & Cost"
      " Overview</div>",
      unsafe_allow_html=True,
  )

  summary_records = []
  if not df.empty:
    for _, item in df.iterrows():
      code = item.get("Asset Code", "-")
      st_dat = asset_repair_stats.get(code, {"count": 0, "total_cost": 0})
      summary_records.append({
          "Asset Code": code,
          "Asset Name": item.get("Asset Name", "-"),
          "Category": item.get("Category", "-"),
          "Serial Number": item.get("Serial Number", "-"),
          "Repair Count": st_dat["count"],
          "Total Repair Cost": f"₹{st_dat['total_cost']:,}",
          "Current Status": item.get("Status", "-"),
          "Current Location": item.get("Current Location", "-"),
          "Assigned To": item.get("Assigned To", "-"),
      })

  summary_df = pd.DataFrame(summary_records)
  if not summary_df.empty:
    summary_df = summary_df.sort_values(by="Repair Count", ascending=False)
    render_download_buttons(
        summary_df, file_prefix="Assets_Repair_Cost_Ledger", key_id="freq_cost"
    )

    t_html = (
        "<div style='overflow-x:auto; border:1px solid #334155;"
        " border-radius:10px;'><table class='erp-data-table'><thead><tr><th>Asset"
        " Code</th><th>Category</th><th>Asset Name</th><th>Serial"
        " No</th><th>Total Repairs</th><th style='color:#38BDF8;'>Total"
        " Cost</th><th>Current Status</th><th>Location</th><th>Assigned"
        " To</th></tr></thead><tbody>"
    )
    for _, s_row in summary_df.iterrows():
      r_badge = (
          f"<span style='color:#34D399; font-weight:700;'>0 Repairs</span>"
          if s_row["Repair Count"] == 0
          else (
              f"<span class='status-pill pill-issued'>{s_row['Repair Count']} Times</span>"
              if s_row["Repair Count"] < 3
              else f"<span class='status-pill pill-scrap'>⚠️ {s_row['Repair Count']} Times</span>"
          )
      )
      t_html += f"""<tr>
                <td><b>{s_row['Asset Code']}</b></td>
                <td>{s_row['Category']}</td>
                <td>{s_row['Asset Name']}</td>
                <td><code>{s_row['Serial Number']}</code></td>
                <td>{r_badge}</td>
                <td style='font-weight:700; color:#38BDF8;'>{s_row['Total Repair Cost']}</td>
                <td>{s_row['Current Status']}</td>
                <td>{s_row['Current Location']}</td>
                <td>{s_row['Assigned To']}</td>
            </tr>"""
    t_html += "</tbody></table></div>"
    st.markdown(t_html, unsafe_allow_html=True)

  st.markdown("</div>", unsafe_allow_html=True)

# ==================== MODULE 2: DATA ENTRY ====================
elif menu_selection == "➕ Add New Asset":
  st.markdown(
      "<div class='workspace-clean-card'><div class='card-heading'>Add New Item"
      " Form (Asset Code Auto-Generates)</div>",
      unsafe_allow_html=True,
  )
  with st.form("master_injection_form", clear_on_submit=True):
    r1, r2, r3, r4 = st.columns(4)
    in_cat = r1.text_input(
        "Category / Product Type*",
        placeholder="e.g. All-in-One, Laptop, Keyboard, Mouse",
    )
    in_name = r2.text_input("Asset / Item Name")
    in_brand = r3.text_input("Brand")
    in_model = r4.text_input("Model Number")

    r5, r6, r7, r8 = st.columns(4)
    in_serial = r5.text_input("Serial Number (S/N)")
    in_proc = r6.text_input("Processor", value="-")
    in_ram = r7.text_input("RAM", value="-")
    in_storage = r8.text_input("Storage", value="-")

    r9, r10, r11, r12 = st.columns(4)
    in_os = r9.text_input("Operating System", value="-")
    in_mac = r10.text_input("MAC Address", value="-")
    in_ip = r11.text_input("IP Address", value="-")
    in_pdate = r12.text_input("Purchase Date (DD-MM-YYYY)", value="-")

    r13, r14, r15, r16 = st.columns(4)
    in_inv = r13.text_input("Invoice Number", value="-")
    in_vendor = r14.text_input("Vendor", value="-")
    in_cost = r15.text_input("Purchase Cost", value="-")
    in_wstart = r16.text_input("Warranty Start", value="-")

    r17, r18, r19, r20 = st.columns(4)
    in_wend = r17.text_input("Warranty End", value="-")
    in_loc = r18.text_input("Current Location", value="MAIN STORE")
    in_teach = r19.text_input("Assigned To", value="-")
    in_dept = r20.text_input("Department", value="IT")

    r21, r22 = st.columns([2, 2])
    in_status = r21.selectbox(
        "Status", ["Available", "Issued", "In Repair", "Scrap"]
    )
    in_rem = r22.text_input("Remarks", value=f"Added to ERP on {today_date_str}")
    in_damage = st.text_input(
        "Any Damage / Fault Details (If applicable):", value="-"
    )

    if st.form_submit_button("🚀 SAVE DEVICE WITH AUTO-CODE"):
      if in_cat.strip():
        serial_clean = in_serial.strip()
        mac_clean = in_mac.strip()
        is_duplicate = False
        duplicate_msg = ""

        if not df.empty:
          if serial_clean and serial_clean != "-":
            matching_sn = df[
                df["Serial Number"].str.lower() == serial_clean.lower()
            ]
            if not matching_sn.empty:
              is_duplicate = True
              duplicate_msg = (
                  "⚠️ Duplicate Entry Blocked! Serial Number"
                  f" '{serial_clean}' already exists."
              )
          if not is_duplicate and mac_clean and mac_clean != "-":
            matching_mac = df[
                df["MAC Address"].str.lower() == mac_clean.lower()
            ]
            if not matching_mac.empty:
              is_duplicate = True
              duplicate_msg = (
                  f"⚠️ Duplicate Entry Blocked! MAC Address '{mac_clean}'"
                  " already exists."
              )

        if is_duplicate:
          st.error(duplicate_msg)
        else:
          prefix = generate_product_prefix(in_cat)
          full_prefix = f"LUC-{prefix}-"
          matching_codes = (
              df[df["Asset Code"].str.startswith(full_prefix)][
                  "Asset Code"
              ].tolist()
              if not df.empty
              else []
          )
          max_num = 0
          for code in matching_codes:
            try:
              num_part = int(code.split("-")[-1])
              if num_part > max_num:
                max_num = num_part
            except ValueError:
              continue

          next_num = max_num + 1
          generated_asset_code = f"{full_prefix}{str(next_num).zfill(3)}"

          new_row_dict = {
              "Asset Code": generated_asset_code,
              "Asset Name": in_name.strip(),
              "Category": in_cat.strip(),
              "Brand": in_brand.strip(),
              "Model": in_model.strip(),
              "Serial Number": serial_clean,
              "Processor": in_proc.strip(),
              "RAM": in_ram.strip(),
              "Storage": in_storage.strip(),
              "Operating System": in_os.strip(),
              "MAC Address": mac_clean,
              "IP Address": in_ip.strip(),
              "Purchase Date": in_pdate.strip(),
              "Invoice Number": in_inv.strip(),
              "Vendor": in_vendor.strip(),
              "Purchase Cost": in_cost.strip(),
              "Warranty Start": in_wstart.strip(),
              "Warranty End": in_wend.strip(),
              "Current Location": in_loc.strip(),
              "Assigned To": in_teach.strip(),
              "Department": in_dept.strip(),
              "Status": in_status,
              "Remarks": in_rem.strip(),
              "Last Verified Date": today_date_str,
              "Verified By": st.session_state.user_name,
              "Audit Status": "Verified",
              "Damage & Issue Description": in_damage.strip(),
          }

          if db.append_row_to_sheet("Assets", new_row_dict):
            log_activity(
                "ADD_ASSET",
                generated_asset_code,
                f"Added {in_name.strip()} ({in_cat.strip()}) under Location:"
                f" {in_loc.strip()}",
            )
            st.cache_data.clear()
            st.success(
                "Successfully Added! Generated Code:"
                f" **{generated_asset_code}**"
            )
            st.rerun()
          else:
            st.error("Failed to save to Google Sheets.")
      else:
        st.error("Please fill the 'Category / Product Type' field.")
  st.markdown("</div>", unsafe_allow_html=True)

# ==================== MODULE 3: EDIT / UPDATE ASSET ====================
elif menu_selection == "✏️ Edit / Update Asset":
  st.markdown(
      "<div class='workspace-clean-card'><div class='card-heading'>Modify"
      " Existing Asset Details & Code</div>",
      unsafe_allow_html=True,
  )
  asset_list = sorted(df["Asset Code"].tolist()) if not df.empty else []
  selected_edit_code = st.selectbox(
      "Select Asset Code to Edit:", ["-- Select Code --"] + asset_list
  )

  if selected_edit_code != "-- Select Code --":
    row_data = df[df["Asset Code"] == selected_edit_code].iloc[0]
    with st.form("master_edit_form"):
      st.warning(f"You are modifying item record: {selected_edit_code}")
      c_code, c_autotick = st.columns([2, 2])
      edit_asset_code = c_code.text_input(
          "Asset Code (Can be modified manually)*", value=selected_edit_code
      )
      auto_recode = c_autotick.checkbox(
          "⚡ Auto-Update Asset Code according to Category?"
      )

      er1, er2, er3, er4 = st.columns(4)
      edit_cat = er1.text_input(
          "Category / Product Type*", value=row_data.get("Category", "")
      )
      edit_name = er2.text_input(
          "Asset / Item Name", value=row_data.get("Asset Name", "")
      )
      edit_brand = er3.text_input("Brand", value=row_data.get("Brand", ""))
      edit_model = er4.text_input(
          "Model Number", value=row_data.get("Model", "")
      )

      er5, er6, er7, er8 = st.columns(4)
      edit_serial = er5.text_input(
          "Serial Number (S/N)", value=row_data.get("Serial Number", "")
      )
      edit_proc = er6.text_input(
          "Processor", value=row_data.get("Processor", "-")
      )
      edit_ram = er7.text_input("RAM", value=row_data.get("RAM", "-"))
      edit_storage = er8.text_input(
          "Storage", value=row_data.get("Storage", "-")
      )

      er9, er10, er11, er12 = st.columns(4)
      edit_os = er9.text_input(
          "Operating System", value=row_data.get("Operating System", "-")
      )
      edit_mac = er10.text_input(
          "MAC Address", value=row_data.get("MAC Address", "-")
      )
      edit_ip = er11.text_input(
          "IP Address", value=row_data.get("IP Address", "-")
      )
      edit_pdate = er12.text_input(
          "Purchase Date", value=row_data.get("Purchase Date", "-")
      )

      er13, er14, er15, er16 = st.columns(4)
      edit_inv = er13.text_input(
          "Invoice Number", value=row_data.get("Invoice Number", "-")
      )
      edit_vendor = er14.text_input(
          "Vendor", value=row_data.get("Vendor", "-")
      )
      edit_cost = er15.text_input(
          "Purchase Cost", value=row_data.get("Purchase Cost", "-")
      )
      edit_wstart = er16.text_input(
          "Warranty Start", value=row_data.get("Warranty Start", "-")
      )

      er17, er18, er19, er20 = st.columns(4)
      edit_wend = er17.text_input(
          "Warranty End", value=row_data.get("Warranty End", "-")
      )
      edit_loc = er18.text_input(
          "Current Location",
          value=row_data.get("Current Location", "MAIN STORE"),
      )
      edit_teach = er19.text_input(
          "Assigned To", value=row_data.get("Assigned To", "-")
      )
      edit_dept = er20.text_input(
          "Department", value=row_data.get("Department", "IT")
      )

      er21, er22 = st.columns([2, 2])
      status_index = ["Available", "Issued", "In Repair", "Scrap"]
      current_status = row_data.get("Status", "Available")
      if current_status not in status_index:
        current_status = "Available"
      edit_status = er21.selectbox(
          "Status", status_index, index=status_index.index(current_status)
      )
      edit_rem = er22.text_input(
          "Remarks", value=row_data.get("Remarks", "-")
      )
      edit_damage = st.text_input(
          "Damage & Issue Description:",
          value=row_data.get("Damage & Issue Description", "-"),
      )

      if st.form_submit_button("💾 UPDATE CHANGES"):
        if edit_cat.strip():
          final_asset_code = edit_asset_code.strip()
          if auto_recode:
            prefix = generate_product_prefix(edit_cat)
            full_prefix = f"LUC-{prefix}-"
            matching_codes = (
                df[df["Asset Code"].str
