from datetime import datetime
from io import BytesIO
import os
import pandas as pd
import requests
import streamlit as st

# Page configuration
st.set_page_config(
    page_title="Lords Universal IT Asset ERP",
    layout="wide",
    initial_sidebar_state="expanded",
)

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

# Exact Published CSV Link from Google Sheets
PUBLISHED_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSsYM5MDGrSqD-g8nXEqSMQp71g9LTAfQ3FnrRvabNmbknht69U4ZnQ0vKqbAl6RO4OZDZr5hZVPcP/pub?output=csv"
GOOGLE_SHEET_ID = "1IiU4QesdM_8Qtn3tW1_9QGKU1_CQr0Ga6LHwg7Bwb9g"
LOCAL_FILE = "assets.xlsx"


def load_database_file():
  # 1. Fetch from Published Google Sheet CSV
  try:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
    }
    response = requests.get(PUBLISHED_CSV_URL, headers=headers, timeout=10)

    if response.status_code == 200:
      data = pd.read_csv(BytesIO(response.content))
      if not data.empty and len(data) > 0:
        data = clean_dataframe(data)
        return data, "Google Sheet (Live Sync)"
  except Exception as e:
    st.sidebar.warning(f"Google Sheet Fetch Notice: {e}")

  # 2. Fallback to Local assets.xlsx
  if os.path.exists(LOCAL_FILE):
    try:
      data = pd.read_excel(LOCAL_FILE)
      data = clean_dataframe(data)
      return data, "Local Master Backup"
    except Exception as e:
      st.sidebar.error(f"Local file read error: {e}")

  return pd.DataFrame(columns=COLUMNS_LIST), "None"


def clean_dataframe(data):
  rename_map = {}
  for col in data.columns:
    clean_c = str(col).strip().lower().replace("_", " ")
    for target_col in COLUMNS_LIST:
      if target_col.lower() == clean_c:
        rename_map[col] = target_col
  data = data.rename(columns=rename_map)

  for col in COLUMNS_LIST:
    if col not in data.columns:
      data[col] = "-"

  data = data.fillna("-")
  for col in data.columns:
    data[col] = (
        data[col]
        .astype(str)
        .str.strip()
        .replace("nan", "-")
        .replace("None", "-")
        .replace("<NaT>", "-")
    )
  return data[COLUMNS_LIST]


df, data_source = load_database_file()

# --- STYLING ---
st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght=400;500;600;700;800&display=swap');
        header, [data-testid="stHeader"] { background-color: #0F172A !important; }
        footer, [data-testid="stStatusWidget"], #MainMenu { display: none !important; }
        html, body, [data-testid="stAppViewContainer"], .main {
            background-color: #0F172A !important;
            color: #E2E8F0 !important;
            font-family: 'Plus Jakarta Sans', sans-serif !important;
        }
        .block-container { max-width: 99% !important; padding: 1rem 2rem !important; }
        [data-testid="stSidebar"] { background-color: #1E293B !important; }
        .erp-data-table { width: 100%; border-collapse: collapse; font-size: 13px; background: #1E293B; }
        .erp-data-table th { background: #0F172A !important; color: #38BDF8 !important; font-weight: 700; padding: 12px; border: 1px solid #334155; }
        .erp-data-table td { padding: 10px; border: 1px solid #334155; color: #E2E8F0; }
        .status-pill { padding: 4px 10px; border-radius: 6px; font-size: 11px; font-weight: 700; text-transform: uppercase; display: inline-block; }
        .pill-available { background-color: rgba(16, 185, 129, 0.2); color: #34D399; border: 1px solid #10B981; }
        .pill-issued { background-color: rgba(245, 158, 11, 0.2); color: #FBBF24; border: 1px solid #F59E0B; }
        .pill-repair { background-color: rgba(59, 130, 246, 0.2); color: #60A5FA; border: 1px solid #3B82F6; }
        .pill-scrap { background-color: rgba(239, 68, 68, 0.2); color: #F87171; border: 1px solid #EF4444; }
    </style>
""",
    unsafe_allow_html=True,
)

# LOGIN
USERS = {
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
}

if "authenticated" not in st.session_state:
  st.session_state.authenticated = False
  st.session_state.logged_user = ""
  st.session_state.user_role = "Admin"
  st.session_state.user_name = "Vedprakash Dubey"

if not st.session_state.authenticated:
  with st.form("login_form"):
    u = st.text_input("Corporate Email ID")
    p = st.text_input("Password", type="password")
    if st.form_submit_button("🔑 SECURE LOGIN"):
      u_clean = u.strip().lower()
      if u_clean in USERS and USERS[u_clean]["pass"] == p:
        st.session_state.authenticated = True
        st.session_state.logged_user = u_clean
        st.session_state.user_role = USERS[u_clean]["role"]
        st.session_state.user_name = USERS[u_clean]["name"]
        st.success("Login Successful!")
        st.rerun()
      else:
        st.error("Invalid Email or Password")
  st.stop()

with st.sidebar:
  st.markdown("## LORDS UNIVERSAL\n**IT Asset Control ERP**")

  st.markdown(
      "<div style='background:#0F172A; padding:10px; border-radius:8px;"
      " border:1px solid #334155; margin-bottom:15px;'><span"
      " style='font-size:12px; color:#38BDF8; font-weight:700;'>👑 FULL"
      " ADMIN</span><br><span style='font-size:13px;"
      " color:#FFFFFF;'>Vedprakash Dubey</span></div>",
      unsafe_allow_html=True,
  )

  st.info(f"📡 System Source: **{data_source}**")

  if st.button("🚪 LOGOUT"):
    st.session_state.authenticated = False
    st.rerun()

  if st.button("🔄 REFRESH LIVE SHEET"):
    st.rerun()

  menu_selection = st.radio(
      "NAVIGATION:",
      [
          "📊 Live Dashboard",
          "➕ Live Google Sheet Link",
          "📁 Download Backup",
      ],
  )


def render_table(dataframe):
  if dataframe.empty:
    st.info("No records found.")
    return
  html = "<div style='overflow-x:auto;'><table class='erp-data-table'><thead><tr>"
  html += "".join(f"<th>{col}</th>" for col in COLUMNS_LIST) + "</tr></thead><tbody>"
  for _, row in dataframe.iterrows():
    html += "<tr>"
    for col in COLUMNS_LIST:
      val = row[col]
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


if menu_selection == "📊 Live Dashboard":
  st.markdown(f"### 📦 Active System Inventory: {len(df)} Items")

  m1, m2, m3, m4, m5 = st.columns(5)
  m1.metric("Total Items", len(df))
  m2.metric(
      "Available",
      len(
          df[
              df["Status"]
              .str.lower()
              .str.contains("available|working", na=False)
          ]
      ),
  )
  m3.metric(
      "Issued / In Use",
      len(
          df[df["Status"].str.lower().str.contains("issued|in use", na=False)]
      ),
  )
  m4.metric(
      "In Repair",
      len(df[df["Status"].str.lower().str.contains("repair", na=False)]),
  )
  m5.metric(
      "Scrap",
      len(
          df[df["Status"].str.lower().str.contains("scrap|damaged", na=False)]
      ),
  )

  st.markdown("---")

  search_q = st.text_input(
      "🔍 Live Search Filter:",
      placeholder="Type Asset Code, Brand, Staff Name, Location...",
  )
  df_show = df.copy()
  if search_q:
    df_show = df_show[
        df_show.astype(str)
        .apply(lambda x: x.str.contains(search_q, case=False))
        .any(axis=1)
    ]

  st.markdown(f"**Showing {len(df_show)} Items:**")
  render_table(df_show)

elif menu_selection == "➕ Live Google Sheet Link":
  st.markdown("### 📝 Direct Live Sheet Access")
  st.success(
      "✅ Aapki Google Sheet live connected hai! Naye records direct Sheet me"
      " enter karein aur ERP App par '🔄 REFRESH LIVE SHEET' dabayein."
  )
  st.markdown(
      f"🔗 **Google Sheet Link:**"
      f" [https://docs.google.com/spreadsheets/d/{GOOGLE_SHEET_ID}](https://docs.google.com/spreadsheets/d/{GOOGLE_SHEET_ID})"
  )

elif menu_selection == "📁 Download Backup":
  io_stream = BytesIO()
  with pd.ExcelWriter(io_stream, engine="openpyxl") as ew:
    df.to_excel(ew, index=False)
  st.download_button(
      f"💾 DOWNLOAD COMPLETE EXCEL BACKUP ({len(df)} ITEMS)",
      data=io_stream.getvalue(),
      file_name=f"LUC_IT_Asset_Backup_{datetime.now().strftime('%Y%m%d')}.xlsx",
  )
