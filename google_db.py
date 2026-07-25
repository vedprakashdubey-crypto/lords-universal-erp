import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# Google Sheets & Drive API Scopes
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

@st.cache_resource
def get_gspread_client():
    """Streamlit Secrets se Google Credentials load karta hai."""
    try:
        if "gcp_service_account" in st.secrets:
            creds_dict = dict(st.secrets["gcp_service_account"])
            creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
            return gspread.authorize(creds)
        else:
            st.error("❌ Streamlit Secrets me 'gcp_service_account' nahi mila.")
            return None
    except Exception as e:
        st.error(f"❌ Connection Error: {e}")
        return None

def get_worksheet(sheet_name):
    """Specific Google Sheet tab open karta hai."""
    client = get_gspread_client()
    if client:
        try:
            spreadsheet_name = st.secrets.get("SPREADSHEET_NAME", "LUC_IT_Assets")
            sheet = client.open(spreadsheet_name)
            return sheet.worksheet(sheet_name)
        except Exception as e:
            st.error(f"❌ Tab '{sheet_name}' open karne me issue aaya: {e}")
            return None
    return None

# ==================== CRUD OPERATIONS ====================

def load_data_from_sheet(worksheet_name):
    """Google Sheet se data read karke DataFrame deta hai."""
    ws = get_worksheet(worksheet_name)
    if ws:
        data = ws.get_all_records()
        return pd.DataFrame(data)
    return pd.DataFrame()

def append_row_to_sheet(worksheet_name, row_data_dict):
    """Google Sheet me Nayi Row (Record) permanent save karta hai."""
    ws = get_worksheet(worksheet_name)
    if ws:
        headers = ws.row_values(1)
        row_to_append = [row_data_dict.get(h, "") for h in headers]
        ws.append_row(row_to_append)
        return True
    return False

def update_row_in_sheet(worksheet_name, id_col_name, id_value, updated_dict):
    """Existing Row ko update karta hai."""
    ws = get_worksheet(worksheet_name)
    if ws:
        data = ws.get_all_records()
        headers = ws.row_values(1)
        row_idx = None
        for idx, row in enumerate(data, start=2):
            if str(row.get(id_col_name)) == str(id_value):
                row_idx = idx
                break
        if row_idx:
            updated_row = [updated_dict.get(h, "") for h in headers]
            ws.update(f"A{row_idx}", [updated_row])
            return True
    return False

def delete_row_from_sheet(worksheet_name, id_col_name, id_value):
    """Row ko permanently delete karta hai."""
    ws = get_worksheet(worksheet_name)
    if ws:
        data = ws.get_all_records()
        for idx, row in enumerate(data, start=2):
            if str(row.get(id_col_name)) == str(id_value):
                ws.delete_rows(idx)
                return True
    return False
