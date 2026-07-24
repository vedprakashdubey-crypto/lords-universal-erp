from datetime import datetime
from io import BytesIO
import pandas as pd
import streamlit as st
from supabase import create_client

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

# --- VERIFIED EXACT SUPABASE CREDENTIALS ---
SUPABASE_URL = "https://lhghbrbzhttfdyrorqfi.supabase.co"
SUPABASE_KEY = "sb_publishable_m6NT2_wKZ8QWJlxgQZCbIw_BjwyDLUg"


@st.cache_resource
def init_supabase():
    try:
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        return None


supabase = init_supabase()

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
        .workspace-clean-card { background: #1E293B; border: 1px solid #334155; border-radius: 12px; padding: 24px; margin-bottom: 24px; }
        .card-heading { font-size: 14px; font-weight: 800; color: #38BDF8; margin-bottom: 16px; border-bottom: 2px solid #334155; text-transform: uppercase; }
        .metric-card-wrapper { background-color: #1E293B !important; border: 1px solid #334155 !important; border-radius: 12px !important; padding: 20px 10px !important; text-align: center; }
        .card-label { font-size: 11px; font-weight: 700; color: #94A3B8; text-transform: uppercase; }
        .card-val { font-size: 36px; font-weight: 800; color: #FFFFFF; }
        .stButton > button { background-color: #0F172A !important; color: #38BDF8 !important; border: 1px solid #334155 !important; border-radius: 8px !important; font-size: 11px !important; font-weight: 700 !important; }
        .erp-data-table { width: 100%; border-collapse: collapse; font-size: 13px; background: #1E293B; }
        .erp-data-table th { background: #0F172A !important; color: #38BDF8 !important; font-weight: 700; padding: 12px; border: 1px solid #334155; }
        .erp-data-table td { padding: 10px; border: 1px solid #334155; color: #E2E8F0; }
        div[data-testid="stTextInput"] input, select { color: #FFFFFF !important; background-color: #0F172A !important; border: 1px solid #475569 !important; }
        label, p, span { color: #F8FAFC !important; }
    </style>
""",
    unsafe_allow_html=True,
)


def load_database_file():
    if not supabase:
        return pd.DataFrame(columns=COLUMNS_LIST)
    try:
        response = supabase.table("assets").select("*").execute()
        data = pd.DataFrame(response.data)
        if data.empty:
            return pd.DataFrame(columns=COLUMNS_LIST)

        rename_map = {}
        for col in data.columns:
            clean_c = col.lower().replace("_", " ")
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
    except Exception as e:
        return pd.DataFrame(columns=COLUMNS_LIST)


def commit_database_file(dataframe):
    if not supabase:
        st.error("Cloud Database connection missing.")
        return False

    try:
        records = []
        for _, row in dataframe.iterrows():
            rec = {}
            for col in COLUMNS_LIST:
                db_col_name = col.lower().replace(" ", "_")
                val = row[col]
                val_str = str(val).strip() if pd.notna(val) else "-"
                if val_str in ["", "nan", "None", "<NaT>", "NaT"]:
                    val_str = "-"
                rec[db_col_name] = val_str
            records.append(rec)

        chunk_size = 25
        progress_bar = st.progress(0)
        total_batches = (len(records) + chunk_size - 1) // chunk_size

        for i in range(0, len(records), chunk_size):
            chunk = records[i : i + chunk_size]
            supabase.table("assets").upsert(
                chunk, on_conflict="asset_code"
            ).execute()
            progress_bar.progress(((i // chunk_size) + 1) / total_batches)

        st.toast("✅ Data Cloud Me Save Ho Gaya!", icon="💾")
        return True
    except Exception as e:
        st.error(f"Save Error: {e}")
        return False


df = load_database_file()

# Credentials
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

if not st.session_state.authenticated:
    with st.form("login_form"):
        u = st.text_input("Corporate Email ID")
        p = st.text_input("Password", type="password")
        if st.form_submit_button("🔑 SECURE LOGIN"):
            if u.strip().lower() in USERS and USERS[u.strip().lower()]["pass"] == p:
                st.session_state.authenticated = True
                st.session_state.user_name = USERS[u.strip().lower()]["name"]
                st.session_state.user_role = USERS[u.strip().lower()]["role"]
                st.rerun()
            else:
                st.error("Invalid Login")
    st.stop()

with st.sidebar:
    st.title("LORDS IT ERP")
    if st.button("🚪 LOGOUT"):
        st.session_state.authenticated = False
        st.rerun()
    menu_selection = st.radio(
        "REGISTER:",
        [
            "📊 Dashboard",
            "➕ Add New Asset",
            "✏️ Edit Asset",
            "📁 Bulk Cloud Upload",
        ],
    )


def render_comprehensive_ledger(dataframe):
    if dataframe.empty:
        st.info("No items found.")
        return
    html = "<div style='overflow-x:auto;'><table class='erp-data-table'><thead><tr>"
    html += "".join(f"<th>{col}</th>" for col in COLUMNS_LIST) + "</tr></thead><tbody>"
    for _, row in dataframe.iterrows():
        html += (
            "<tr>"
            + "".join(f"<td>{row[col]}</td>" for col in COLUMNS_LIST)
            + "</tr>"
        )
    html += "</tbody></table></div>"
    st.markdown(html, unsafe_allow_html=True)


if menu_selection == "📊 Dashboard":
    st.markdown(f"### Total Items in Cloud Database: {len(df)}")
    render_comprehensive_ledger(df)

elif menu_selection == "➕ Add New Asset":
    with st.form("add_form"):
        c1, c2, c3 = st.columns(3)
        cat = c1.text_input("Category*")
        name = c2.text_input("Item Name")
        brand = c3.text_input("Brand")
        if st.form_submit_button("🚀 SAVE NEW ENTRY TO CLOUD"):
            if cat:
                acode = f"LUC-{cat[:3].upper()}-{len(df)+1:03d}"
                new_row = [acode, name, cat, brand] + ["-"] * 19
                new_df = pd.concat(
                    [df, pd.DataFrame([new_row], columns=COLUMNS_LIST)],
                    ignore_index=True,
                )
                if commit_database_file(new_df):
                    st.success(f"Saved to Cloud! Asset Code: {acode}")
                    st.rerun()

elif menu_selection == "📁 Bulk Cloud Upload":
    up_file = st.file_uploader("Select Excel File", type=["xlsx"])
    if up_file and st.button("🚀 UPLOAD ALL 265 ITEMS TO SUPABASE CLOUD"):
        imp_df = pd.read_excel(up_file)
        rename_map = {}
        for col in imp_df.columns:
            clean_c = str(col).strip().lower().replace("_", " ")
            for target_col in COLUMNS_LIST:
                if target_col.strip().lower() == clean_c:
                    rename_map[col] = target_col
        imp_df = imp_df.rename(columns=rename_map)
        for col in COLUMNS_LIST:
            if col not in imp_df.columns:
                imp_df[col] = "-"
        imp_df = imp_df[COLUMNS_LIST]

        if commit_database_file(imp_df):
            st.success("🎉 ALL 265 ITEMS SAVED PERMANENTLY TO SUPABASE CLOUD!")
            st.rerun()
