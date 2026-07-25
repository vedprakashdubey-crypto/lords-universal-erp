import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

@st.cache_resource
def get_gspread_client():
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
    client = get_gspread_client()
    if client:
        try:
            # Direct Sheet ID link se open karega (Zero Error Solution)
            sheet_id = "1liU4QesdM_8Qtn3tW1_9QGkU1_CQr0Ga6LHwg7Bwb9g"
            sheet = client.open_by_key(sheet_id)
            
            try:
                return sheet.worksheet(sheet_name)
            except gspread.exceptions.WorksheetNotFound:
                headers = {
                    "Assets": ["Asset Code", "Asset Name", "Category", "Brand", "Model", "Serial Number", "Processor", "RAM", "Storage", "Operating System", "MAC Address", "IP Address", "Purchase Date", "Invoice Number", "Vendor", "Purchase Cost", "Warranty Start", "Warranty End", "Current Location", "Assigned To", "Department", "Status", "Remarks"],
                    "Users": ["Email", "Password", "Role", "Name"],
                    "Activity_Logs": ["Timestamp", "User Email", "Action", "Asset Code", "Details"],
                    "Settings": ["Key", "Value"]
                }
                ws = sheet.add_worksheet(title=sheet_name, rows=100, cols=25)
                if sheet_name in headers:
                    ws.append_row(headers[sheet_name])
                return ws

        except Exception as e:
            st.error(f"❌ Google Sheet Open Error: {e}")
            return None
    return None

# ==================== CACHED READ OPERATIONS ====================

@st.cache_data(ttl=60)
def load_data_from_sheet(worksheet_name):
    ws = get_worksheet(worksheet_name)
    if ws:
        try:
            data = ws.get_all_records()
            return pd.DataFrame(data)
        except Exception:
            return pd.DataFrame()
    return pd.DataFrame()

# ==================== WRITE OPERATIONS ====================

def append_row_to_sheet(worksheet_name, row_data_dict):
    ws = get_worksheet(worksheet_name)
    if ws:
        headers = ws.row_values(1)
        if not headers:
            headers = list(row_data_dict.keys())
            ws.append_row(headers)
        row_to_append = [str(row_data_dict.get(h, "")) for h in headers]
        ws.append_row(row_to_append)
        st.cache_data.clear()
        return True
    return False

def update_row_in_sheet(worksheet_name, id_col_name, id_value, updated_dict):
    ws = get_worksheet(worksheet_name)
    if ws:
        data = ws.get_all_records()
        headers = ws.row_values(1)
        row_idx = None
        for idx, row in enumerate(data, start=2):
            if str(row.get(id_col_name)).strip() == str(id_value).strip():
                row_idx = idx
                break
        if row_idx:
            updated_row = [str(updated_dict.get(h, "")) for h in headers]
            ws.update(f"A{row_idx}", [updated_row])
            st.cache_data.clear()
            return True
    return False

def delete_row_from_sheet(worksheet_name, id_col_name, id_value):
    ws = get_worksheet(worksheet_name)
    if ws:
        data = ws.get_all_records()
        for idx, row in enumerate(data, start=2):
            if str(row.get(id_col_name)).strip() == str(id_value).strip():
                ws.delete_rows(idx)
                st.cache_data.clear()
                return True
    return False
