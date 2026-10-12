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
      return sheet.worksheet(sheet_name)
    except Exception as e:
      st.error(f"❌ Google Sheet Open Error: {e}")
      return None
  return None


# ==================== READ OPERATIONS ====================
def load_data_from_sheet(worksheet_name):
  ws = get_worksheet(worksheet_name)
  if ws:
    try:
      # Direct values get karke DataFrame banana (Robust & Zero Error)
      all_vals = ws.get_all_values()
      if len(all_vals) > 1:
        headers = all_vals[0]
        data = all_vals[1:]
        return pd.DataFrame(data, columns=headers)
      elif len(all_vals) == 1:
        return pd.DataFrame(columns=all_vals[0])
    except Exception as e:
      st.error(f"Read error: {e}")
      return pd.DataFrame()
  return pd.DataFrame()


# ==================== WRITE OPERATIONS ====================
def append_row_to_sheet(worksheet_name, row_data_dict):
  ws = get_worksheet(worksheet_name)
  if ws:
    try:
      headers = ws.row_values(1)
      row_to_append = [str(row_data_dict.get(h, "")) for h in headers]
      ws.append_row(row_to_append)
      st.cache_data.clear()
      return True
    except Exception as e:
      st.error(f"Append error: {e}")
      return False
  return False


def update_row_in_sheet(worksheet_name, id_col_name, id_value, updated_dict):
  ws = get_worksheet(worksheet_name)
  if ws:
    try:
      # Step 1: Ensure Grid size & Headers
      headers = ws.row_values(1)
      needed_cols = list(updated_dict.keys())
      missing = [c for c in needed_cols if c not in headers]

      if missing:
        # Sheet ke columns expand karein agar 26 se zyada ho rahe hain
        total_needed = len(headers) + len(missing)
        if ws.col_count < total_needed:
          ws.add_cols(total_needed - ws.col_count + 5)

        for new_col in missing:
          headers.append(new_col)
          ws.update_cell(1, len(headers), new_col)

      # Step 2: Row Find karein
      all_records = ws.get_all_records()
      row_idx = None
      for idx, row in enumerate(all_records, start=2):
        if str(row.get(id_col_name)).strip() == str(id_value).strip():
          row_idx = idx
          break

      # Step 3: Update Row
      if row_idx:
        updated_row = [str(updated_dict.get(h, "")) for h in headers]
        ws.update(
            values=[updated_row],
            range_name=f"A{row_idx}",
            value_input_option="USER_ENTERED",
        )
        st.cache_data.clear()
        return True
      else:
        st.error(f"Asset Code '{id_value}' sheet me nahi mila.")
        return False
    except Exception as e:
      st.error(f"Google Sheet Update Error: {e}")
      return False
  return False


def setup_sheet_columns_now():
  """Ek click me Google Sheet me 27 columns auto-create karne ka master function."""
  ws = get_worksheet("Assets")
  if ws:
    try:
      required_headers = [
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
      if ws.col_count < len(required_headers):
        ws.add_cols(len(required_headers) - ws.col_count + 5)

      # Update entire row 1 directly
      ws.update(
          values=[required_headers],
          range_name=f"A1:{chr(64 + len(required_headers)) if len(required_headers) <= 26 else 'AA'}1",
          value_input_option="USER_ENTERED",
      )
      st.cache_data.clear()
      return True
    except Exception as e:
      st.error(f"Header sync error: {e}")
      return False
  return False
