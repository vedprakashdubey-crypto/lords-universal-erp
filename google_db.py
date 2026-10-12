from google.oauth2.service_account import Credentials
import gspread
import pandas as pd
import streamlit as st

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
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
      sheet_id = "1liU4QesdM_8Qtn3tW1_9QGkU1_CQr0Ga6LHwg7Bwb9g"
      sheet = client.open_by_key(sheet_id)
      try:
        return sheet.worksheet(sheet_name)
      except gspread.exceptions.WorksheetNotFound:
        headers = {
            "Assets": [
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
            ],
            "Users": ["Email", "Password", "Role", "Name"],
            "Activity_Logs": [
                "Timestamp",
                "User Email",
                "Action",
                "Asset Code",
                "Details",
            ],
            "Settings": ["Key", "Value"],
        }
        ws = sheet.add_worksheet(title=sheet_name, rows=100, cols=30)
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
    try:
      headers = ws.row_values(1)
      if not headers:
        headers = list(row_data_dict.keys())
        ws.append_row(headers)
      else:
        # Check and add missing columns to Row 1
        needed_keys = list(row_data_dict.keys())
        for k in needed_keys:
          if k not in headers:
            headers.append(k)
            ws.update_cell(1, len(headers), k)

      row_to_append = [str(row_data_dict.get(h, "")) for h in headers]
      ws.append_row(row_to_append)
      st.cache_data.clear()
      return True
    except Exception as e:
      st.error(f"Error appending row: {e}")
      return False
  return False


def update_row_in_sheet(worksheet_name, id_col_name, id_value, updated_dict):
  ws = get_worksheet(worksheet_name)
  if ws:
    try:
      headers = ws.row_values(1)

      # 1. AUTO-HEADER EXPANSION: Agar sheet me naye columns missing hain to khud add kar dega
      needed_keys = list(updated_dict.keys())
      missing_headers = [k for k in needed_keys if k not in headers]
      if missing_headers:
        for new_col in missing_headers:
          headers.append(new_col)
          ws.update_cell(1, len(headers), new_col)

      # 2. MATCH ROW
      data = ws.get_all_records()
      row_idx = None
      for idx, row in enumerate(data, start=2):
        if str(row.get(id_col_name)).strip() == str(id_value).strip():
          row_idx = idx
          break

      # 3. WRITE UPDATED DATA
      if row_idx:
        updated_row = [str(updated_dict.get(h, "")) for h in headers]
        # Range safe update
        ws.update(
            range_name=f"A{row_idx}",
            values=[updated_row],
            value_input_option="USER_ENTERED",
        )
        st.cache_data.clear()
        return True
      else:
        st.error(f"Row with {id_col_name} = {id_value} not found.")
        return False
    except Exception as e:
      st.error(f"Error updating sheet: {e}")
      return False
  return False


def delete_row_from_sheet(worksheet_name, id_col_name, id_value):
  ws = get_worksheet(worksheet_name)
  if ws:
    try:
      data = ws.get_all_records()
      for idx, row in enumerate(data, start=2):
        if str(row.get(id_col_name)).strip() == str(id_value).strip():
          ws.delete_rows(idx)
          st.cache_data.clear()
          return True
    except Exception:
      return False
  return False
