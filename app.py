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
]

LOG_COLUMNS = ["Timestamp", "User", "Action", "Asset Code", "Details"]

# Page configuration
st.set_page_config(
    page_title="Lords Universal IT Asset ERP",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- INDIA / MUMBAI (KOLKATA) TIMEZONE (+5:30 IST) ---
IST_TZ = timezone(timedelta(hours=5, minutes=30))


def get_ist_now():
  return datetime.now(IST_TZ)


today_date_str = get_ist_now().strftime("%d-%m-%Y")

# --- CLEAN STYLING ---
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
        
        div[data-testid="stRadio"] label {
            padding: 12px 16px !important;
            border-radius: 8px !important;
            margin-bottom: 5px !important;
            color: #94A3B8 !important;
            font-weight: 500 !important;
            transition: all 0.2s ease;
        }
        div[data-testid="stRadio"] [data-checked="true"] label {
            background: #2563EB !important;
            color: #FFFFFF !important;
            font-weight: 600 !important;
            box-shadow: 0 4px 12px rgba(37, 99, 235, 0.25);
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

# LOGIN FORM
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


# REUSABLE DOWNLOAD FUNCTION
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

  # FULL DATABASE BACKUP DOWNLOAD FROM SIDEBAR
  if not df.empty:
    st.markdown("---")
    st.markdown(
        "<span style='font-size:11px; color:#38BDF8; font-weight:700;'>💾"
        " COMPLETE DATABASE BACKUP</span>",
        unsafe_allow_html=True,
    )
    backup_stream = BytesIO()
    with pd.ExcelWriter(backup_stream, engine="openpyxl") as bkw:
      df.to_excel(bkw, index=False)
    st.download_button(
        "📦 Export All Assets (.xlsx)",
        data=backup_stream.getvalue(),
        file_name=f"Full_ERP_Assets_Backup_{today_date_str}.xlsx",
        mime=(
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        ),
        use_container_width=True,
    )
    st.markdown("---")

  menu_options = [
      "📊 Dashboard",
      "🔍 Monthly Asset Audit",
      "➕ Add New Asset",
      "✏️ Edit / Update Asset",
      "📑 Issue / Allocate Item",
      "🛠️ Repair & Maintenance",
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
    st.markdown(
        "<div class='card-heading'>📂 Category-Wise Inventory Status</div>",
        unsafe_allow_html=True,
    )

    if not df.empty and "Category" in df.columns:
      cat_groups = (
          df.groupby("Category")
          .agg(
              Total=("Asset Code", "count"),
              Available=(
                  "Status",
                  lambda x: x.str.lower().isin(["available", "working"]).sum(),
              ),
              Issued=(
                  "Status",
                  lambda x: x.str.lower().isin(["issued", "in use"]).sum(),
              ),
              In_Repair=(
                  "Status",
                  lambda x: x.str.lower().str.contains("repair").sum(),
              ),
              Scrap=(
                  "Status",
                  lambda x: x.str.lower().isin(["scrap", "damaged"]).sum(),
              ),
          )
          .reset_index()
      )

      cat_html = (
          "<div style='overflow-x:auto; border:1px solid #334155;"
          " border-radius:10px;'><table class='erp-data-table'>"
      )
      cat_html += (
          "<thead><tr><th>Category Name</th><th>Total Stock</th><th"
          " style='color:#34D399;'>Available</th><th"
          " style='color:#FBBF24;'>Issued</th><th style='color:#60A5FA;'>In"
          " Repair</th><th style='color:#F87171;'>Scrap</th></tr></thead><tbody>"
      )

      for _, row in cat_groups.iterrows():
        cat_html += f"""<tr>
                        <td><b>{row['Category']}</b></td>
                        <td><span style='font-weight:700;'>{row['Total']}</span> Items</td>
                        <td><span class='status-pill pill-available'>{row['Available']}</span></td>
                        <td><span class='status-pill pill-issued'>{row['Issued']}</span></td>
                        <td><span class='status-pill pill-repair'>{row['In_Repair']}</span></td>
                        <td><span class='status-pill pill-scrap'>{row['Scrap']}</span></td>
                    </tr>"""
      cat_html += "</tbody></table></div>"
      st.markdown(cat_html, unsafe_allow_html=True)
    else:
      st.info("No categories to display.")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='workspace-clean-card'>", unsafe_allow_html=True)
    st.markdown(
        "<div class='card-heading'>📊 Quick Breakdown Filters</div>",
        unsafe_allow_html=True,
    )
    b1, b2, b3 = st.columns(3)
    cat_options = (
        sorted(df["Category"].unique().tolist())
        if not df.empty and "Category" in df.columns
        else []
    )
    loc_options = (
        sorted(df["Current Location"].unique().tolist())
        if not df.empty and "Current Location" in df.columns
        else []
    )
    assign_options = (
        sorted(df["Assigned To"].unique().tolist())
        if not df.empty and "Assigned To" in df.columns
        else []
    )

    selected_cat = b1.selectbox(
        "Filter by Category:", ["All Categories"] + cat_options
    )
    selected_loc = b2.selectbox(
        "Filter by Location:", ["All Locations"] + loc_options
    )
    selected_assign = b3.selectbox(
        "Filter by Assigned To:", ["All Personnel"] + assign_options
    )
    st.markdown("</div>", unsafe_allow_html=True)

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

    if selected_cat != "All Categories" and "Category" in df_view.columns:
      df_view = df_view[df_view["Category"] == selected_cat]
    if selected_loc != "All Locations" and "Current Location" in df_view.columns:
      df_view = df_view[df_view["Current Location"] == selected_loc]
    if selected_assign != "All Personnel" and "Assigned To" in df_view.columns:
      df_view = df_view[df_view["Assigned To"] == selected_assign]
    if live_query and not df_view.empty:
      df_view = df_view[
          df_view.astype(str)
          .apply(lambda x: x.str.contains(live_query, case=False))
          .any(axis=1)
      ]

    st.markdown(
        "<div class='card-heading' style='margin-top:10px;'>Active Ledger View"
        f" ({len(df_view)} Items)</div>",
        unsafe_allow_html=True,
    )
    render_comprehensive_ledger(
        df_view, file_prefix="Filtered_IT_Assets", key_id="main_grid"
    )
    st.markdown("</div>", unsafe_allow_html=True)

  elif st.session_state.current_dashboard_view == "Total_View":
    if st.button("⬅️ Back Dashboard"):
      st.session_state.current_dashboard_view = "Main_Grid"
      st.rerun()
    render_comprehensive_ledger(
        df, file_prefix="Total_IT_Assets", key_id="total"
    )
  elif st.session_state.current_dashboard_view == "Available_View":
    if st.button("⬅️ Back Dashboard"):
      st.session_state.current_dashboard_view = "Main_Grid"
      st.rerun()
    render_comprehensive_ledger(
        df[df["Status"].str.lower().isin(["available", "working"])]
        if not df.empty
        else df,
        file_prefix="Available_Assets",
        key_id="avail",
    )
  elif st.session_state.current_dashboard_view == "Issued_View":
    if st.button("⬅️ Back Dashboard"):
      st.session_state.current_dashboard_view = "Main_Grid"
      st.rerun()
    render_comprehensive_ledger(
        df[df["Status"].str.lower().isin(["issued", "in use"])]
        if not df.empty
        else df,
        file_prefix="Issued_Assets",
        key_id="issued",
    )
  elif st.session_state.current_dashboard_view == "Repair_View":
    if st.button("⬅️ Back Dashboard"):
      st.session_state.current_dashboard_view = "Main_Grid"
      st.rerun()
    render_comprehensive_ledger(
        df[df["Status"].str.lower().str.contains("repair")]
        if not df.empty
        else df,
        file_prefix="Repair_Assets",
        key_id="repair",
    )
  elif st.session_state.current_dashboard_view == "Scrap_View":
    if st.button("⬅️ Back Dashboard"):
      st.session_state.current_dashboard_view = "Main_Grid"
      st.rerun()
    render_comprehensive_ledger(
        df[df["Status"].str.lower().isin(["scrap", "damaged"])]
        if not df.empty
        else df,
        file_prefix="Scrap_Assets",
        key_id="scrap",
    )

# ==================== MODULE: MONTHLY ASSET AUDIT (NEW) ====================
elif menu_selection == "🔍 Monthly Asset Audit":
  st.markdown(
      "<div class='workspace-clean-card'><div class='card-heading'>Monthly"
      " Physical Verification & Asset Audit</div>",
      unsafe_allow_html=True,
  )

  # Calculate 30-Day Audit Stats
  today_dt = get_ist_now().date()
  verified_this_month = 0
  pending_audit = 0

  if not df.empty:
    for _, r in df.iterrows():
      v_date_str = str(r.get("Last Verified Date", "-")).strip()
      is_valid_recent = False
      if v_date_str not in ["-", ""]:
        for fmt in ("%d-%m-%Y", "%Y-%m-%d"):
          try:
            parsed = datetime.strptime(v_date_str, fmt).date()
            if (today_dt - parsed).days <= 30:
              is_valid_recent = True
            break
          except ValueError:
            pass
      if is_valid_recent:
        verified_this_month += 1
      else:
        pending_audit += 1

  # Metrics Row
  col_a1, col_a2, col_a3 = st.columns(3)
  with col_a1:
    st.markdown(
        f"<div class='metric-card-wrapper'><span class='card-label'>Total"
        f" Assets</span><div class='card-val'>{len(df)}</div></div>",
        unsafe_allow_html=True,
    )
  with col_a2:
    st.markdown(
        "<div class='metric-card-wrapper'><span class='card-label'"
        " style='color:#34D399;'>Verified (Past 30 Days)</span><div"
        f" class='card-val' style='color:#34D399;'>{verified_this_month}</div></div>",
        unsafe_allow_html=True,
    )
  with col_a3:
    st.markdown(
        "<div class='metric-card-wrapper'><span class='card-label'"
        " style='color:#F87171;'>Pending / Overdue Audit</span><div"
        f" class='card-val' style='color:#F87171;'>{pending_audit}</div></div>",
        unsafe_allow_html=True,
    )

  st.markdown("---")

  # Search / Scan Section
  st.subheader("🔍 Quick Scan / Search Asset for Verification")
  audit_search = st.text_input(
      "Scan Barcode / Enter Asset Code, Serial Number or MAC:",
      placeholder="e.g. LUC-LPT-001 or S/N...",
      key="audit_search_input",
  )

  if audit_search.strip():
    search_q = audit_search.strip().lower()
    matched = df[
        (df["Asset Code"].str.lower() == search_q)
        | (df["Serial Number"].str.lower() == search_q)
        | (df["MAC Address"].str.lower() == search_q)
    ]

    if matched.empty:
      matched = df[
          df.astype(str)
          .apply(lambda x: x.str.contains(search_q, case=False))
          .any(axis=1)
      ]

    if not matched.empty:
      item_row = matched.iloc[0]
      t_code = item_row["Asset Code"]

      st.success(
          f"Found: **{item_row.get('Asset Name', '')}** ({t_code}) - Brand:"
          f" {item_row.get('Brand', '')} | Current Location:"
          f" **{item_row.get('Current Location', '')}** | Assigned To:"
          f" **{item_row.get('Assigned To', '')}**"
      )

      with st.form("verify_single_asset_form"):
        v_c1, v_c2, v_c3 = st.columns(3)
        v_user = v_c1.text_input(
            "Auditor / Verified By", value=st.session_state.user_name
        )
        v_status = v_c2.selectbox(
            "Physical Asset Condition",
            [
                "Verified & Working",
                "Needs Repair",
                "Scrap / Damaged",
                "Missing / Not Found",
            ],
        )
        v_loc = v_c3.text_input(
            "Confirm Current Location",
            value=item_row.get("Current Location", "MAIN STORE"),
        )

        v_c4, v_c5 = st.columns(2)
        v_assigned = v_c4.text_input(
            "Confirm Assigned To", value=item_row.get("Assigned To", "-")
        )
        v_notes = v_c5.text_input(
            "Audit Notes / Remarks",
            value=f"Monthly audit verified on {today_date_str}",
        )

        if st.form_submit_button("✅ MARK AS VERIFIED TODAY"):
          updated_data = item_row.to_dict()
          updated_data["Last Verified Date"] = today_date_str
          updated_data["Verified By"] = v_user.strip()
          updated_data["Audit Status"] = (
              "Verified"
              if "Verified" in v_status
              else f"Discrepancy ({v_status})"
          )
          updated_data["Current Location"] = v_loc.strip()
          updated_data["Assigned To"] = v_assigned.strip()
          updated_data["Remarks"] = v_notes.strip()

          if v_status == "Needs Repair":
            updated_data["Status"] = "In Repair"
          elif v_status == "Scrap / Damaged":
            updated_data["Status"] = "Scrap"

          if db.update_row_in_sheet("Assets", "Asset Code", t_code, updated_data):
            log_activity(
                "MONTHLY_AUDIT",
                t_code,
                f"Audited by {v_user.strip()}, Status: {v_status}, Location:"
                f" {v_loc.strip()}",
            )
            st.cache_data.clear()
            st.success(
                f"Asset **{t_code}** successfully verified for {today_date_str}!"
            )
            st.rerun()
          else:
            st.error("Failed to update Google Sheet.")
    else:
      st.warning(f"No asset found matching '{audit_search}'.")

  st.markdown("---")

  # Table of Assets Pending Audit (Overdue)
  st.subheader("⚠️ Pending Physical Audit (Over 30 Days or Never Verified)")

  def check_overdue(date_val):
    d_str = str(date_val).strip()
    if d_str in ["-", ""]:
      return True
    for fmt in ("%d-%m-%Y", "%Y-%m-%d"):
      try:
        dt = datetime.strptime(d_str, fmt).date()
        return (today_dt - dt).days > 30
      except ValueError:
        pass
    return True

  if not df.empty:
    overdue_mask = df["Last Verified Date"].apply(check_overdue)
    overdue_df = df[overdue_mask]
    st.write(
        f"**{len(overdue_df)} Items** require physical verification this month."
    )
    render_comprehensive_ledger(
        overdue_df, file_prefix="Overdue_Audit_Assets", key_id="overdue_audit"
    )
  else:
    st.info("No items in the asset database.")

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
    in_vendor = r14.
