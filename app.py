import os
from datetime import datetime
from io import BytesIO
import pandas as pd
import streamlit as st

# EXCEL FILE DEFINITIONS
EXCEL_FILE = "assets.xlsx"
LOG_FILE = "activity_logs.xlsx"
USERS_FILE = "user_credentials.xlsx"

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

# --- GLOBAL STYLING: ABSOLUTE HIDE FOR MANAGE APP / FLOATING TOOLBARS ---
st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght=400;500;600;700;800&display=swap');
        
        /* AGGRESSIVE CSS TO REMOVE MANAGE APP & STREAMLIT BADGES */
        #MainMenu, footer, header, [data-testid="stHeader"], [data-testid="stStatusWidget"],
        .stAppToolbar, [data-testid="manage-app-button"], [data-testid="stViewerBadge"],
        div[class*="viewerBadge"], div[class*="manageApp"] {
            display: none !important;
            visibility: hidden !important;
            opacity: 0 !important;
            height: 0px !important;
            width: 0px !important;
            pointer-events: none !important;
        }

        html, body, [data-testid="stAppViewContainer"], .main {
            background-color: #0F172A !important;
            color: #E2E8F0 !important;
            font-family: 'Plus Jakarta Sans', sans-serif !important;
        }
        .block-container { max-width: 99% !important; padding: 1.5rem 2rem !important; }
        [data-testid="stSidebar"] { background-color: #1E293B !important; border-right: 1px solid #334155 !important; }
        [data-testid="stSidebar"] [data-testid="stWidgetLabel"], 
        [data-testid="stSidebar"] p, [data-testid="stSidebar"] label, [data-testid="stSidebar"] span {
            color: #F8FAFC !important; font-size: 14px !important; font-weight: 600 !important;
        }
        div[data-testid="stRadio"] label {
            padding: 12px 16px !important; border-radius: 8px !important; margin-bottom: 5px !important;
            color: #94A3B8 !important; font-weight: 500 !important; transition: all 0.2s ease;
        }
        div[data-testid="stRadio"] [data-checked="true"] label {
            background: #2563EB !important; color: #FFFFFF !important; font-weight: 600 !important;
            box-shadow: 0 4px 12px rgba(37, 99, 235, 0.25);
        }
        .workspace-clean-card { background: #1E293B; border: 1px solid #334155; border-radius: 12px; padding: 24px; margin-bottom: 24px; }
        .card-heading { font-size: 14px; font-weight: 800; color: #38BDF8; margin-bottom: 16px; padding-bottom: 8px; border-bottom: 2px solid #334155; text-transform: uppercase; letter-spacing: 0.8px; }
        .metric-card-wrapper { background-color: #1E293B !important; border: 1px solid #334155 !important; border-top-left-radius: 12px !important; border-top-right-radius: 12px !important; padding: 20px 10px 10px 10px !important; text-align: center; }
        .card-label { font-size: 11px; font-weight: 700; color: #94A3B8; text-transform: uppercase; }
        .card-val { font-size: 36px; font-weight: 800; color: #FFFFFF; margin-top: 4px; }
        .stButton > button { width: 100% !important; border-top-left-radius: 0px !important; border-top-right-radius: 0px !important; border-bottom-left-radius: 12px !important; border-bottom-right-radius: 12px !important; background-color: #0F172A !important; color: #38BDF8 !important; border: 1px solid #334155 !important; border-top: none !important; font-size: 11px !important; font-weight: 700 !important; text-transform: uppercase !important; padding: 8px 0px !important; transition: all 0.2s ease; }
        .stButton > button:hover { background-color: #2563EB !important; color: #FFFFFF !important; border-color: #2563EB !important; }
        .erp-data-table { width: 100%; border-collapse: collapse; font-size: 13px; background: #1E293B; }
        .erp-data-table th { background: #0F172A !important; color: #38BDF8 !important; font-weight: 700; padding: 14px 16px; text-align: left; border: 1px solid #334155; white-space: nowrap; }
        .erp-data-table td { padding: 12px 16px; border: 1px solid #334155; color: #E2E8F0; white-space: nowrap; }
        .erp-data-table tr:nth-child(even) td { background-color: #111827; }
        .erp-data-table tr:hover td { background-color: #2D3748 !important; }
        .status-pill { padding: 4px 10px; border-radius: 6px; font-size: 11px; font-weight: 700; text-transform: uppercase; display: inline-block; }
        .pill-available { background-color: rgba(16, 185, 129, 0.2); color: #34D399; border: 1px solid #10B981; }
        .pill-issued { background-color: rgba(245, 158, 11, 0.2); color: #FBBF24; border: 1px solid #F59E0B; }
        .pill-repair { background-color: rgba(59, 130, 246, 0.2); color: #60A5FA; border: 1px solid #3B82F6; }
        .pill-scrap { background-color: rgba(239, 68, 68, 0.2); color: #F87171; border: 1px solid #EF4444; }
        div[data-testid="stTextInput"] input, .stTextInput input, textarea, select { color: #FFFFFF !important; background-color: #0F172A !important; border: 1px solid #475569 !important; }
        label, p, span { color: #F8FAFC !important; }
    </style>
""",
    unsafe_allow_html=True,
)

# --- USER CREDENTIALS ENGINE ---
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
    if os.path.exists(USERS_FILE):
        try:
            udf = pd.read_excel(USERS_FILE)
            users_dict = {}
            for _, r in udf.iterrows():
                users_dict[str(r["Email"]).strip().lower()] = {
                    "pass": str(r["Password"]).strip(),
                    "role": str(r["Role"]).strip(),
                    "name": str(r["Name"]).strip(),
                }
            return users_dict
        except Exception:
            return DEFAULT_USERS
    else:
        rows = [
            {
                "Email": k,
                "Password": v["pass"],
                "Role": v["role"],
                "Name": v["name"],
            }
            for k, v in DEFAULT_USERS.items()
        ]
        pd.DataFrame(rows).to_excel(USERS_FILE, index=False)
        return DEFAULT_USERS


def save_user_credentials(users_dict):
    rows = [
        {
            "Email": k,
            "Password": v["pass"],
            "Role": v["role"],
            "Name": v["name"],
        }
        for k, v in users_dict.items()
    ]
    try:
        pd.DataFrame(rows).to_excel(USERS_FILE, index=False)
    except Exception as e:
        st.error(f"Failed to update passwords: {e}")


USERS = load_user_credentials()

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.logged_user = ""
    st.session_state.user_role = ""

# LOGIN SCREEN
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
    new_log = [now, st.session_state.logged_user, action, asset_code, details]
    log_df = (
        pd.read_excel(LOG_FILE)
        if os.path.exists(LOG_FILE)
        else pd.DataFrame(columns=LOG_COLUMNS)
    )
    log_df = pd.concat(
        [log_df, pd.DataFrame([new_log], columns=LOG_COLUMNS)], ignore_index=True
    )
    try:
        log_df.to_excel(LOG_FILE, index=False)
    except Exception:
        pass


def load_logs():
    return (
        pd.read_excel(LOG_FILE)
        if os.path.exists(LOG_FILE)
        else pd.DataFrame(columns=LOG_COLUMNS)
    )


def load_database_file():
    if os.path.exists(EXCEL_FILE):
        try:
            data = pd.read_excel(EXCEL_FILE).fillna("-")
            for col in COLUMNS_LIST:
                if col not in data.columns:
                    data[col] = "-"
            for col in data.columns:
                data[col] = data[col].astype(str).str.strip()
            return data[COLUMNS_LIST]
        except Exception:
            return pd.DataFrame(columns=COLUMNS_LIST)
    return pd.DataFrame(columns=COLUMNS_LIST)


def commit_database_file(dataframe):
    try:
        dataframe.to_excel(EXCEL_FILE, index=False)
    except Exception as e:
        st.error(f"Error saving database: {e}")


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
    return (
        "".join(no_vowels[:3]) if len(no_vowels) >= 3 else clean_alpha[:3]
    )


if "current_dashboard_view" not in st.session_state:
    st.session_state.current_dashboard_view = "Main_Grid"

# SIDEBAR
with st.sidebar:
    st.markdown(
        "<div style='padding: 10px 0; border-bottom: 1px solid #334155;'><h2 style='color:#FFFFFF; font-weight:800; font-size:18px; margin:0;'>LORDS UNIVERSAL</h2><p style='color:#38BDF8; font-size:11px; font-weight:600; margin:0;'>IT Asset Control ERP</p></div><br>",
        unsafe_allow_html=True,
    )

    role_badge = (
        "👑 FULL ADMIN"
        if st.session_state.user_role == "Admin"
        else "👤 ASSISTANT"
    )
    st.markdown(
        f"<div style='background:#0F172A; padding:10px; border-radius:8px; border:1px solid #334155; margin-bottom:15px;'><span style='font-size:12px; color:#38BDF8; font-weight:700;'>{role_badge}</span><br><span style='font-size:13px; color:#FFFFFF;'>{st.session_state.user_name}</span></div>",
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

st.markdown(
    f"<div class='workspace-clean-card' style='background: linear-gradient(90deg, #1E293B, #0F172A); border-color:#334155; padding: 16px 24px; margin-bottom:20px;'><span style='font-size:20px; font-weight:800; color:#FFFFFF;'>{menu_selection[2:].upper()} PANEL</span></div>",
    unsafe_allow_html=True,
)


def render_comprehensive_ledger(dataframe):
    if dataframe.empty:
        st.info("No matching items found.")
        return
    html = "<div style='overflow-x:auto; border:1px solid #334155; border-radius:10px;'><table class='erp-data-table'><thead><tr>"
    html += (
        "".join(f"<th>{col}</th>" for col in COLUMNS_LIST) + "</tr></thead><tbody>"
    )
    for _, row in dataframe.iterrows():
        html += "<tr>"
        for col in COLUMNS_LIST:
            val = row[col]
            if col == "Status":
                if str(val).lower() in ["available", "working"]:
                    html += f"<td><span class='status-pill pill-available'>{val}</span></td>"
                elif str(val).lower() in ["issued", "in use"]:
                    html += f"<td><span class='status-pill pill-issued'>{val}</span></td>"
                elif "repair" in str(val).lower():
                    html += f"<td><span class='status-pill pill-repair'>{val}</span></td>"
                elif str(val).lower() in ["scrap", "damaged"]:
                    html += f"<td><span class='status-pill pill-scrap'>{val}</span></td>"
                else:
                    html += f"<td>{val}</td>"
            else:
                html += f"<td>{val}</td>"
        html += "</tr>"
    html += "</tbody></table></div>"
    st.markdown(html, unsafe_allow_html=True)


# MODULE 1: DASHBOARD
if menu_selection == "📊 Dashboard":
    t_count, a_count, i_count = (
        len(df),
        len(df[df["Status"].str.lower().isin(["available", "working"])]),
        len(df[df["Status"].str.lower().isin(["issued", "in use"])]),
    )
    r_count, s_count = len(
        df[df["Status"].str.lower().str.contains("repair")]
    ), len(df[df["Status"].str.lower().isin(["scrap", "damaged"])])

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Total Items", t_count)
    m2.metric("Available", a_count)
    m3.metric("Issued", i_count)
    m4.metric("In Repair", r_count)
    m5.metric("Scrap", s_count)

    st.markdown("<div class='workspace-clean-card'>", unsafe_allow_html=True)
    st.markdown(
        "<div class='card-heading'>Active Inventory View</div>",
        unsafe_allow_html=True,
    )
    render_comprehensive_ledger(df)
    st.markdown("</div>", unsafe_allow_html=True)

# MODULE 2: ADD
elif menu_selection == "➕ Add New Asset":
    st.markdown(
        "<div class='workspace-clean-card'><div class='card-heading'>Add New Item Form</div>",
        unsafe_allow_html=True,
    )
    with st.form("add_form", clear_on_submit=True):
        r1, r2, r3, r4 = st.columns(4)
        in_cat = r1.text_input("Category*")
        in_name = r2.text_input("Asset Name")
        in_brand = r3.text_input("Brand")
        in_model = r4.text_input("Model")

        r5, r6, r7, r8 = st.columns(4)
        in_serial = r5.text_input("Serial Number")
        in_loc = r6.text_input("Location", value="MAIN STORE")
        in_teach = r7.text_input("Assigned To", value="-")
        in_status = r8.selectbox(
            "Status", ["Available", "Issued", "In Repair", "Scrap"]
        )

        if st.form_submit_button("🚀 SAVE DEVICE"):
            if in_cat.strip():
                prefix = generate_product_prefix(in_cat)
                gen_code = f"LUC-{prefix}-{len(df)+1:03d}"
                new_row = [
                    gen_code,
                    in_name.strip(),
                    in_cat.strip(),
                    in_brand.strip(),
                    in_model.strip(),
                    in_serial.strip(),
                    "-",
                    "-",
                    "-",
                    "-",
                    "-",
                    "-",
                    "-",
                    "-",
                    "-",
                    "-",
                    "-",
                    "-",
                    in_loc.strip(),
                    in_teach.strip(),
                    "IT",
                    in_status,
                    "-",
                ]
                df = pd.concat(
                    [df, pd.DataFrame([new_row], columns=COLUMNS_LIST)],
                    ignore_index=True,
                )
                commit_database_file(df)
                log_activity(
                    "ADD_ASSET",
                    gen_code,
                    f"Added {in_name.strip()} ({in_cat.strip()})",
                )
                st.success(f"Added! Generated Code: **{gen_code}**")
                st.rerun()

# MODULE 3: EDIT
elif menu_selection == "✏️ Edit / Update Asset":
    st.markdown(
        "<div class='workspace-clean-card'><div class='card-heading'>Modify Asset</div>",
        unsafe_allow_html=True,
    )
    asset_list = sorted(df["Asset Code"].tolist())
    selected_code = st.selectbox(
        "Select Code:", ["-- Select Code --"] + asset_list
    )
    if selected_code != "-- Select Code --":
        row_data = df[df["Asset Code"] == selected_code].iloc[0]
        with st.form("edit_form"):
            e_name = st.text_input("Asset Name", value=row_data["Asset Name"])
            e_loc = st.text_input(
                "Location", value=row_data["Current Location"]
            )
            e_status = st.selectbox(
                "Status",
                ["Available", "Issued", "In Repair", "Scrap"],
                index=["Available", "Issued", "In Repair", "Scrap"].index(
                    row_data["Status"]
                    if row_data["Status"]
                    in ["Available", "Issued", "In Repair", "Scrap"]
                    else "Available"
                ),
            )
            if st.form_submit_button("💾 UPDATE"):
                df.loc[
                    df["Asset Code"] == selected_code,
                    ["Asset Name", "Current Location", "Status"],
                ] = [e_name.strip(), e_loc.strip(), e_status]
                commit_database_file(df)
                log_activity(
                    "EDIT_ASSET",
                    selected_code,
                    f"Updated Name: {e_name.strip()}, Location: {e_loc.strip()}, Status: {e_status}",
                )
                st.success("Updated Successfully!")
                st.rerun()

# MODULE 4: ALLOCATE
elif menu_selection == "📑 Issue / Allocate Item":
    render_comprehensive_ledger(
        df[df["Status"].str.lower().isin(["issued", "in use"])]
    )

# MODULE 5: REPAIR
elif menu_selection == "🛠️ Repair & Maintenance":
    render_comprehensive_ledger(
        df[df["Status"].str.lower().str.contains("repair")]
    )

# MODULE 6: WARRANTY
elif menu_selection == "⏱️ Warranty Records":
    render_comprehensive_ledger(df)

# MODULE 7: AUDIT LOGS
elif menu_selection == "📜 Activity Logs (Audit)":
    if st.session_state.user_role == "Admin":
        st.dataframe(
            load_logs().sort_values(by="Timestamp", ascending=False),
            use_container_width=True,
        )

# MODULE 8: RESET PASSWORDS
elif menu_selection == "🔑 Reset User Passwords":
    if st.session_state.user_role == "Admin":
        with st.form("reset_pwd_form"):
            sel_u = st.selectbox("User:", list(USERS.keys()))
            nP = st.text_input("New Password", type="password")
            cP = st.text_input("Confirm Password", type="password")
            if st.form_submit_button("🔄 RESET PASSWORD"):
                if nP and nP == cP:
                    USERS[sel_u]["pass"] = nP
                    save_user_credentials(USERS)
                    log_activity(
                        "PASSWORD_RESET",
                        "-",
                        f"Admin reset password for: {sel_u}",
                    )
                    st.success(f"Password for {sel_u} updated!")
                else:
                    st.error("Passwords do not match!")
