from datetime import datetime
from io import BytesIO
import os
import pandas as pd
import streamlit as st
import google_db as db

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
]

LOG_COLUMNS = ["Timestamp", "User Email", "Action", "Asset Code", "Details"]

# Page configuration
st.set_page_config(
    page_title="Lords Universal IT Asset ERP",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- GLOBAL STYLING + FIXED SIDEBAR TOGGLE ---
st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght=400;500;600;700;800&display=swap');
        
        /* HIDE UNWANTED STREAMLIT ELEMENTS WHILE KEEPING SIDEBAR TOGGLE VISIBLE */
        #MainMenu, footer, [data-testid="stStatusWidget"],
        .stAppToolbar, [data-testid="manage-app-button"], [data-testid="stViewerBadge"],
        div[class*="viewerBadge"], div[class*="manageApp"] {
            display: none !important;
            visibility: hidden !important;
            opacity: 0 !important;
        }

        /* ENSURE SIDEBAR TOGGLE BUTTON IS ALWAYS VISIBLE AND STYLED BEAUTIFULLY */
        [data-testid="stHeader"] {
            background-color: transparent !important;
            z-index: 99999 !important;
        }
        [data-testid="stSidebarCollapseButton"], button[aria-label="Toggle sidebar"] {
            background-color: #2563EB !important;
            color: #FFFFFF !important;
            border-radius: 8px !important;
            border: 1px solid #38BDF8 !important;
            visibility: visible !important;
            display: flex !important;
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
        
        /* SIDEBAR SYSTEM PANEL */
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

        /* METRIC PANEL STYLING */
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

        /* BUTTON MODIFIERS */
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

        /* DATA GRID MANAGEMENT */
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
        
        /* STATUS PILLS */
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

# --- USER CREDENTIALS MANAGEMENT VIA GOOGLE SHEETS ---
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


def load_user_credentials():
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
    db.update_row_in_sheet("Users", "Email", email_id, updated_dict)


USERS = load_user_credentials()

if "authenticated" not in st.session_state:
  st.session_state.authenticated = False
  st.session_state.logged_user = ""
  st.session_state.user_role = ""

# --- LOGIN FORM ---
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
  now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
  log_data = {
      "Timestamp": now,
      "User Email": st.session_state.logged_user,
      "Action": action,
      "Asset Code": asset_code,
      "Details": details,
  }
  db.append_row_to_sheet("Activity_Logs", log_data)


def load_logs():
  logs_df = db.load_data_from_sheet("Activity_Logs")
  if logs_df.empty:
    return pd.DataFrame(columns=LOG_COLUMNS)
  return logs_df


def load_database_file():
  data = db.load_data_from_sheet("Assets")
  if not data.empty:
    data = data.fillna("-")
    for col in COLUMNS_LIST:
      if col not in data.columns:
        data[col] = "-"
    for col in data.columns:
      data[col] = data[col].astype(str).str.strip()
    return data[COLUMNS_LIST]
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
  clean_alpha = "".join(e for e in clean if e.isalnum())
  if not clean_alpha:
    return "AST"
  if len(clean_alpha) <= 3:
    return clean_alpha.ljust(3, "X")
  vowels = ["A", "E", "I", "O", "U"]
  no_vowels = [char for char in clean_alpha if char not in vowels]
  return "".join(no_vowels[:3]) if len(no_vowels) >= 3 else clean_alpha[:3]


if "current_dashboard_view" not in st.session_state:
  st.session_state.current_dashboard_view = "Main_Grid"

# --- SIDEBAR CONTROL PANEL ---
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

  if st.button("🚪 LOGOUT"):
    st.session_state.authenticated = False
    st.rerun()

  menu_options = [
      "📊 Dashboard",
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


def render_comprehensive_ledger(dataframe):
  if dataframe.empty:
    st.info("No matching items found.")
    return
  html = (
      "<div style='overflow-x:auto; border:1px solid #334155;"
      " border-radius:10px;'><table class='erp-data-table'><thead><tr>"
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
          html += (
              f"<td><span class='status-pill pill-issued'>{val}</span></td>"
          )
        elif "repair" in str(val).lower():
          html += (
              f"<td><span class='status-pill pill-repair'>{val}</span></td>"
          )
        elif str(val).lower() in ["scrap", "damaged"]:
          html += f"<td><span class='status-pill pill-scrap'>{val}</span></td>"
        else:
          html += f"<td>{val}</td>"
      else:
        html += f"<td>{val}</td>"
    html += "</tr>"
  html += "</tbody></table></div>"
  st.markdown(html, unsafe_allow_html=True)


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
    fc1, fc2, fc3 = st.columns([1.5, 2, 1])
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

    io_stream = BytesIO()
    with pd.ExcelWriter(io_stream, engine="openpyxl") as ew:
      df_view.to_excel(ew, index=False)
    fc3.markdown("<div style='margin-top:28px;'></div>", unsafe_allow_html=True)
    fc3.download_button(
        "📥 Export Current View",
        data=io_stream.getvalue(),
        file_name="LUC_IT_Inventory.xlsx",
        use_container_width=True,
    )

    st.markdown(
        "<div class='card-heading' style='margin-top:20px;'>Active Ledger View"
        f" ({len(df_view)} Items)</div>",
        unsafe_allow_html=True,
    )
    render_comprehensive_ledger(df_view)
    st.markdown("</div>", unsafe_allow_html=True)

  elif st.session_state.current_dashboard_view == "Total_View":
    if st.button("⬅️ Back Dashboard"):
      st.session_state.current_dashboard_view = "Main_Grid"
      st.rerun()
    render_comprehensive_ledger(df)
  elif st.session_state.current_dashboard_view == "Available_View":
    if st.button("⬅️ Back Dashboard"):
      st.session_state.current_dashboard_view = "Main_Grid"
      st.rerun()
    render_comprehensive_ledger(
        df[df["Status"].str.lower().isin(["available", "working"])]
        if not df.empty
        else df
    )
  elif st.session_state.current_dashboard_view == "Issued_View":
    if st.button("⬅️ Back Dashboard"):
      st.session_state.current_dashboard_view = "Main_Grid"
      st.rerun()
    render_comprehensive_ledger(
        df[df["Status"].str.lower().isin(["issued", "in use"])]
        if not df.empty
        else df
    )
  elif st.session_state.current_dashboard_view == "Repair_View":
    if st.button("⬅️ Back Dashboard"):
      st.session_state.current_dashboard_view = "Main_Grid"
      st.rerun()
    render_comprehensive_ledger(
        df[df["Status"].str.lower().str.contains("repair")]
        if not df.empty
        else df
    )
  elif st.session_state.current_dashboard_view == "Scrap_View":
    if st.button("⬅️ Back Dashboard"):
      st.session_state.current_dashboard_view = "Main_Grid"
      st.rerun()
    render_comprehensive_ledger(
        df[df["Status"].str.lower().isin(["scrap", "damaged"])]
        if not df.empty
        else df
    )

# ==================== MODULE 2: DATA ENTRY WITH DUPLICATE CHECK ====================
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
    in_rem = r22.text_input("Remarks", value="-")

    if st.form_submit_button("🚀 SAVE DEVICE WITH AUTO-CODE"):
      if in_cat.strip():
        # --- DUPLICATE CHECK LOGIC ---
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
              existing_code = matching_sn.iloc[0]["Asset Code"]
              duplicate_msg = f"⚠️ Duplicate Entry Blocked! Serial Number **'{serial_clean}'** already exists for Asset Code: **{existing_code}**"

          if not is_duplicate and mac_clean and mac_clean != "-":
            matching_mac = df[
                df["MAC Address"].str.lower() == mac_clean.lower()
            ]
            if not matching_mac.empty:
              is_duplicate = True
              existing_code = matching_mac.iloc[0]["Asset Code"]
              duplicate_msg = f"⚠️ Duplicate Entry Blocked! MAC Address **'{mac_clean}'** already exists for Asset Code: **{existing_code}**"

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
          }

          if db.append_row_to_sheet("Assets", new_row_dict):
            log_activity(
                "ADD_ASSET",
                generated_asset_code,
                f"Added {in_name.strip()} ({in_cat.strip()}) under Location:"
                f" {in_loc.strip()}",
            )
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
      " Existing Asset Details</div>",
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

      if st.form_submit_button("💾 UPDATE CHANGES"):
        if edit_cat.strip():
          updated_dict = {
              "Asset Code": selected_edit_code,
              "Asset Name": edit_name.strip(),
              "Category": edit_cat.strip(),
              "Brand": edit_brand.strip(),
              "Model": edit_model.strip(),
              "Serial Number": edit_serial.strip(),
              "Processor": edit_proc.strip(),
              "RAM": edit_ram.strip(),
              "Storage": edit_storage.strip(),
              "Operating System": edit_os.strip(),
              "MAC Address": edit_mac.strip(),
              "IP Address": edit_ip.strip(),
              "Purchase Date": edit_pdate.strip(),
              "Invoice Number": edit_inv.strip(),
              "Vendor": edit_vendor.strip(),
              "Purchase Cost": edit_cost.strip(),
              "Warranty Start": edit_wstart.strip(),
              "Warranty End": edit_wend.strip(),
              "Current Location": edit_loc.strip(),
              "Assigned To": edit_teach.strip(),
              "Department": edit_dept.strip(),
              "Status": edit_status,
              "Remarks": edit_rem.strip(),
          }
          if db.update_row_in_sheet(
              "Assets", "Asset Code", selected_edit_code, updated_dict
          ):
            log_activity(
                "EDIT_ASSET",
                selected_edit_code,
                f"Updated Name: {edit_name.strip()}, Location:"
                f" {edit_loc.strip()}, Status: {edit_status}",
            )
            st.success(
                f"Asset Record **{selected_edit_code}** updated successfully!"
            )
            st.rerun()
          else:
            st.error("Failed to update record in Google Sheets.")
        else:
          st.error("Category cannot be empty.")
  st.markdown("</div>", unsafe_allow_html=True)

# ==================== MODULE 4: ALLOCATION ====================
elif menu_selection == "📑 Issue / Allocate Item":
  st.markdown(
      "<div class='workspace-clean-card'><div class='card-heading'>Issue Item"
      " Form</div>",
      unsafe_allow_html=True,
  )
  with st.form("issue_form"):
    available_assets = (
        df[df["Status"].str.lower().isin(["available", "working"])][
            "Asset Code"
        ].tolist()
        if not df.empty
        else []
    )
    c1, c2, c3 = st.columns(3)
    target_asset = c1.selectbox(
        "Select Asset Tag:",
        available_assets if available_assets else ["No Stock Available"],
    )
    assign_user = c2.text_input("Assigned To (Staff Name)*")
    target_loc = c3.text_input("Current Location (Room/Lab)*")
    c4, c5 = st.columns(2)
    target_dept = c4.text_input("Department", value="IT")
    issue_remarks = c5.text_input(
        "Remarks / Notes", value="Issued for official college use"
    )

    if st.form_submit_button("⚡ ASSIGN / ISSUE NOW") and available_assets:
      if assign_user.strip() and target_loc.strip():
        row_data = df[df["Asset Code"] == target_asset].iloc[0].to_dict()
        row_data["Assigned To"] = assign_user.strip()
        row_data["Current Location"] = target_loc.strip()
        row_data["Department"] = target_dept.strip()
        row_data["Status"] = "Issued"
        row_data["Remarks"] = issue_remarks.strip()

        if db.update_row_in_sheet(
            "Assets", "Asset Code", target_asset, row_data
        ):
          log_activity(
              "ISSUE_ASSET",
              target_asset,
              f"Assigned To: {assign_user.strip()}, Location:"
              f" {target_loc.strip()}",
          )
          st.success("Allocation updated successfully.")
          st.rerun()

  st.markdown(
      "<br><div class='card-heading'>Currently Issued Items Matrix</div>",
      unsafe_allow_html=True,
  )
  render_comprehensive_ledger(
      df[df["Status"].str.lower().isin(["issued", "in use"])]
      if not df.empty
      else df
  )
  st.markdown("</div>", unsafe_allow_html=True)

# ==================== MODULE 5: REPAIR ====================
elif menu_selection == "🛠️ Repair & Maintenance":
  st.markdown(
      "<div class='workspace-clean-card'><div class='card-heading'>Maintenance"
      " Loop Control</div>",
      unsafe_allow_html=True,
  )
  with st.form("repair_form"):
    all_assets = df["Asset Code"].tolist() if not df.empty else []
    rc1, rc2, rc3 = st.columns(3)
    maint_asset = rc1.selectbox(
        "Select Asset Tag:", all_assets if all_assets else ["-"]
    )
    maint_status = rc2.selectbox("Set Status to:", ["In Repair", "Available"])
    maint_remarks = rc3.text_input(
        "Fault / Repair Logs:", value="Servicing requested"
    )

    if st.form_submit_button("🛠️ UPDATE MAINTENANCE STATUS") and all_assets:
      row_data = df[df["Asset Code"] == maint_asset].iloc[0].to_dict()
      row_data["Status"] = maint_status
      row_data["Remarks"] = maint_remarks.strip()
      if maint_status == "Available":
        row_data["Assigned To"] = "-"
        row_data["Current Location"] = "MAIN STORE"

      if db.update_row_in_sheet("Assets", "Asset Code", maint_asset, row_data):
        log_activity(
            "MAINTENANCE_CHANGE",
            maint_asset,
            f"Status changed to: {maint_status}, Note: {maint_remarks.strip()}",
        )
        st.success("Maintenance log updated.")
        st.rerun()

  st.markdown(
      "<br><div class='card-heading'>Active Items Under Repair</div>",
      unsafe_allow_html=True,
  )
  render_comprehensive_ledger(
      df[df["Status"].str.lower().str.contains("repair")]
      if not df.empty
      else df
  )
  st.markdown("</div>", unsafe_allow_html=True)

# ==================== MODULE 6: WARRANTY ====================
elif menu_selection == "⏱️ Warranty Records":
  st.markdown(
      "<div class='workspace-clean-card'><div class='card-heading'>Warranty &"
      " AMC Status Ledger</div>",
      unsafe_allow_html=True,
  )
  render_comprehensive_ledger(df)
  st.markdown("</div>", unsafe_allow_html=True)

# ==================== MODULE 7: AUDIT LOGS (ADMIN ONLY) ====================
elif menu_selection == "📜 Activity Logs (Audit)":
  if st.session_state.user_role == "Admin":
    st.markdown(
        "<div class='workspace-clean-card'><div class='card-heading'>User"
        " Activity & Audit Ledger</div>",
        unsafe_allow_html=True,
    )

    logs_df = load_logs()
    if not logs_df.empty:
      st.dataframe(
          logs_df.sort_values(by="Timestamp", ascending=False),
          use_container_width=True,
      )

      log_stream = BytesIO()
      with pd.ExcelWriter(log_stream, engine="openpyxl") as lw:
        logs_df.to_excel(lw, index=False)
      st.download_button(
          "📥 Export Audit Logs Excel",
          data=log_stream.getvalue(),
          file_name="ERP_Activity_Logs.xlsx",
          use_container_width=True,
      )
    else:
      st.info("No user activity logged yet.")
    st.markdown("</div>", unsafe_allow_html=True)

# ==================== MODULE 8: RESET PASSWORDS (ADMIN ONLY) ====================
elif menu_selection == "🔑 Reset User Passwords":
  if st.session_state.user_role == "Admin":
    st.markdown(
        "<div class='workspace-clean-card'><div class='card-heading'>User"
        " Password Management</div>",
        unsafe_allow_html=True,
    )

    user_list = list(USERS.keys())

    with st.form("reset_pwd_form"):
      selected_user = st.selectbox(
          "Select User Account to Reset:", user_list
      )
      new_pwd = st.text_input("New Password", type="password")
      confirm_pwd = st.text_input("Confirm New Password", type="password")

      if st.form_submit_button("🔄 UPDATE PASSWORD NOW"):
        if new_pwd and new_pwd == confirm_pwd:
          USERS[selected_user]["pass"] = new_pwd
          save_user_credentials(selected_user, new_pwd)
          log_activity(
              "PASSWORD_RESET",
              "-",
              f"Admin reset password for user: {selected_user}",
          )
          st.success(
              f"Password for **{selected_user}** has been successfully updated!"
          )
        elif new_pwd != confirm_pwd:
          st.error("Passwords do not match!")
        else:
          st.error("Please enter a valid password.")
    st.markdown("</div>", unsafe_allow_html=True)
