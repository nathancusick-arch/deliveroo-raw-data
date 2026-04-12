import streamlit as st
import pandas as pd
import io
from datetime import datetime, timedelta

st.title("Deliveroo Raw Data Mapper")

# ============================================================
# DATE LOGIC
# ============================================================

today = datetime.today()
last_monday = today - timedelta(days=today.weekday() + 7)
last_monday_str = last_monday.strftime("%d.%m.%y")
today_str = today.strftime("%d.%m.%y")

st.write(f"""
1. Upload the latest export file
2. Upload last week's Deliveroo Raw Data file
3. The tool will automatically remove previously reported audits
4. Download this week's Deliveroo Raw Data file
""")

# ============================================================
# COLUMN MAP
# ============================================================

COLUMN_MAP = {
    "ORDER": "order_internal_id",
    "CLIENT": "client_name",
    "VISIT": "internal_id",
    "SITE": "site_internal_id",
    "PREMISES": "site_name",
    "SITE CODE": "site_code",
    "DATE OF VISIT": "date_of_visit",
    "TIME OF VISIT": "time_of_visit",
    "RESULT": "primary_result",
    "What is your age?": "What is your age?",
    "What is the name of the restaurant/shop you made the purchase from?": [
        "What is the name of the restaurant/shop you made the purchase from?",
        "What is the name of the shop you made the purchase from?"
    ],
    "Please enter the  11-digit order number:": "Please enter the  11-digit order number:",
    "Please give details of the product that you purchased:": [
        "Please give details of the alcohol that you purchased:",
        "Please give details of the cigarettes that you purchased:",
        "Please give details of the e-cigarette that you purchased:",
        "Please give details of the CBD product that you purchased:",
        "Please give details of the age-restricted product you purchased:"
    ],
    "Did the rider ask for your ID?": "Did the rider ask for your ID?",
    "Did the rider check your ID?": "Did the rider check your ID?",
    "Did the rider ask for your date of birth?": "Did the rider ask for your date of birth?",
    "Did the rider hand you their phone to type in your date of birth?": "Did the rider hand you their phone to type in your date of birth?",
    "Did the rider hand over the product?": [
        "Did the rider hand over the alcohol?",
        "Did the rider hand over the cigarettes?",
        "Did the rider hand over the e-cigs?",
        "Did the rider hand over the CBD?"
    ],
    "Anything else important to note from your interaction with the rider?": "Anything else important to note from your interaction with the rider?",
    "What type of kit is the rider wearing?": "What type of kit is the rider wearing?",
    "If Deliveroo, which items are branded:": "If Deliveroo, which items are branded:",
    "If other, please provide details:": "If other, please provide details:",
    "What mode of transport was the rider using?": "What mode of transport was the rider using?",
    "Please provide details:": "Please provide details:",
    "Did the rider bring your delivery in a thermal bag?": "Did the rider bring your delivery in a thermal bag?",
    "Was there an age verification sticker on your order?": "Was there an age verification sticker on your order?",
    "Did the courier refer to the sticker?": "Did the courier refer to the sticker?",
    "Please use this space to explain anything unusual about your visit or to clarify any detail of your report:": "Please use this space to explain anything unusual about your visit or to clarify any detail of your report:",
    "Has the same rider delivered an age-restricted product to you and asked you for ID within the last month?": "Has the same rider delivered an age-restricted product to you and asked you for ID within the last month?",
    "Please describe the doorstep transaction:": "Please describe the doorstep transaction:",
    "Please confirm below whether or not you were asked for ID:": "Please confirm below whether or not you were asked for ID?"
}

# ============================================================
# MAPPING FUNCTION
# ============================================================

def map_value(row, mapping):
    if mapping is None:
        return ""
    if isinstance(mapping, list):
        vals = []
        for col in mapping:
            if col in row and pd.notna(row[col]):
                cleaned = str(row[col]).strip()
                if cleaned:
                    vals.append(cleaned)
        return " | ".join(vals)
    if isinstance(mapping, str):
        if mapping in row and pd.notna(row[mapping]):
            return str(row[mapping]).strip()
    return ""

# ============================================================
# FILE UPLOADERS
# ============================================================

export_file = st.file_uploader("Upload audits_basic_data_export.csv", type=["csv"])
previous_file = st.file_uploader(f"Upload Deliveroo Raw Data {last_monday_str}.csv", type=["csv"])

# ============================================================
# MAIN LOGIC (ONLY RUN IF BOTH FILES PROVIDED)
# ============================================================

if export_file is not None and previous_file is not None:

    df = pd.read_csv(export_file, dtype=str).fillna("")

    # FILTERS
    df = df[df["primary_result"].str.strip().str.lower() != "abort"]
    df = df[df["site_internal_id"] != "SITE224854"]

    # MAP TO FINAL FORMAT
    final_df = pd.DataFrame()
    for report_col, export_mapping in COLUMN_MAP.items():
        final_df[report_col] = df.apply(lambda row: map_value(row, export_mapping), axis=1)

    # REMOVE ALREADY REPORTED AUDITS
    prev_df = pd.read_csv(previous_file, dtype=str).fillna("")

    if "VISIT" not in prev_df.columns:
        st.error("The uploaded previous file is not valid. It must contain a 'VISIT' column.")
        st.stop()

    prev_ids = set(prev_df["VISIT"].astype(str).str.strip())
    final_df = final_df[~final_df["VISIT"].astype(str).str.strip().isin(prev_ids)]

    # PREVIEW
    st.subheader("Preview of Output")
    st.write(final_df)

    # DOWNLOAD
    output_buffer = io.BytesIO()
    final_df.to_csv(output_buffer, index=False, encoding="utf-8-sig")
    output_buffer.seek(0)

    st.download_button(
        label="Download Deliveroo Raw Data CSV",
        data=output_buffer,
        file_name=f"Deliveroo Raw Data {today_str}.csv",
        mime="text/csv"
    )

elif export_file is not None or previous_file is not None:
    st.warning("Please upload both files to generate the report.")
