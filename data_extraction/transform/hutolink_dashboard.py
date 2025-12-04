from data_extraction.utils.convert import convert_to_csv
from data_extraction.utils.rename import rename
import data_extraction.config.config as config
import pandas as pd
from datetime import datetime
import json
from data_extraction.extract.ltap_dashboard import extract_ltap_dashboard
from data_extraction.extract.hutolink_likp_dashboard import hutolink_dashboard

def retrieve_to_number():
    # CONVERT
    convert_to_csv("hu_to_link_dashboard", dtype={"Handling Unit": "str"})
    convert_to_csv("huto_lnkhis_dashboard", dtype={"Handling Unit": "str"})

    # RENAME
    rename("hu_to_link_dashboard", config.HU_TO_LINK_DASHBOARD_DF, dtype={"Handling Unit": "str"})
    rename("huto_lnkhis_dashboard", config.HU_TO_LINK_DASHBOARD_DF, dtype={"Handling Unit": "str"})

    # EXTRACT UNIQUE to_number VALUES FROM BOTH FILES
    df1 = pd.read_csv(f"{config.OUTPUT_PATH}hu_to_link_dashboard.csv")
    df2 = pd.read_csv(f"{config.OUTPUT_PATH}huto_lnkhis_dashboard.csv")

    # COMBINE to_number COLUMNS FROM BOTH DATAFRAMES
    all_to_numbers = pd.concat([df1["to_number"], df2["to_number"]], ignore_index=True)
    unique_to_numbers = all_to_numbers.drop_duplicates()

    # SAVE TO CSV
    unique_to_numbers.to_csv(f"{config.OUTPUT_PATH}to_numbers.csv", index=False)

def convert_hu_to_link_likp():
    # CONVERT
    convert_to_csv("hu_to_link_likp_hu_dashboard", dtype={"Handling Unit": "str"})
    convert_to_csv("huto_lnkhis_likp_hu_dashboard", dtype={"Handling Unit": "str"})

    # RENAME
    rename("hu_to_link_likp_hu_dashboard", config.HU_TO_LINK_LIKP_DASHBOARD_DF, dtype={"Handling Unit": "str"})
    rename("huto_lnkhis_likp_hu_dashboard", config.HU_TO_LINK_LIKP_DASHBOARD_DF, dtype={"Handling Unit": "str"})

def get_likp_hu_count():
    try:
        df1 = pd.read_csv(f"{config.OUTPUT_PATH}hu_to_link_likp_hu_dashboard.csv", dtype={"hu": "str"})
        df2 = pd.read_csv(f"{config.OUTPUT_PATH}huto_lnkhis_likp_hu_dashboard.csv", dtype={"hu": "str"})
        
        # COMBINE HU COLUMNS FROM BOTH FILES
        all_hu = pd.concat([df1["hu"], df2["hu"]], ignore_index=True)
        
        # COUNT UNIQUE VALUES
        return all_hu.nunique()
    except FileNotFoundError:
        return 0

def add_to_number_to_vl06f():
    # READ VL06F
    vl06f_df = pd.read_csv(f"{config.OUTPUT_PATH}vl06f.csv", dtype={"hu": "str"})

    # READ DASHBOARD FILES
    hu_to_link_df = pd.read_csv(f"{config.OUTPUT_PATH}hu_to_link_dashboard.csv", dtype={"hu": "str"})
    huto_lnkhis_df = pd.read_csv(f"{config.OUTPUT_PATH}huto_lnkhis_dashboard.csv", dtype={"hu": "str"})

    # REMOVE LEADING "00" FROM HU IN DASHBOARD FILES
    hu_to_link_df["hu_normalized"] = hu_to_link_df["hu"].astype(str).str.lstrip("0")
    huto_lnkhis_df["hu_normalized"] = huto_lnkhis_df["hu"].astype(str).str.lstrip("0")

    # COMBINE BOTH DASHBOARD FILES
    combined_dashboard = pd.concat([hu_to_link_df, huto_lnkhis_df], ignore_index=True)

    # GROUP BY HU AND CONCATENATE MULTIPLE to_number VALUES
    hu_to_number_map = combined_dashboard.groupby("hu_normalized")["to_number"].apply(
        lambda x: ",".join(map(str, x.unique()))
    ).to_dict()

    # MAP to_number to VL06F
    vl06f_df["hu_normalized"] = vl06f_df["hu"].fillna("").astype(str).str.lstrip("0")
    vl06f_df["to_number"] = vl06f_df["hu_normalized"].map(hu_to_number_map).fillna("")

    # SET "0000" IF HU IS EMPTY
    vl06f_df.loc[vl06f_df["hu"].fillna("") == "", "to_number"] == "0000"

    # DROP TEMPORARY COLUMN
    vl06f_df = vl06f_df.drop(columns=["hu_normalized"])

    # SAVE UPDATED VL06F
    vl06f_df.to_csv(f"{config.OUTPUT_PATH}vl06f.csv", index=False)

    return vl06f_df

def add_status_hu_to_vl06f(vl06f_df):
    # READ LTAP DASHBOARD
    ltap_df = pd.read_csv(f"{config.OUTPUT_PATH}ltap_dashboard.csv")
    
    # CHECK WHICH to_numbers HAVE ALL ROWS WITH confirmation_date
    # Group by to_number and check if all rows have confirmation_date (not empty, not NaN)
    def check_all_confirmed(to_numbers):
        if pd.isna(to_numbers) or str(to_numbers).strip() == "" or str(to_numbers).strip() == "0000":
            return "not_released"
        
        # Split comma-separated to_numbers
        to_number_list = [str(tn).strip() for tn in str(to_numbers).split(",") if str(tn).strip()]
        
        # Check each to_number
        all_picked = True
        for tn in to_number_list:
            # Filter ltap for this to_number
            tn_rows = ltap_df[ltap_df["to_number"] == int(tn) if tn.isdigit() else None]
            
            if len(tn_rows) == 0:
                # If to_number not found in ltap, consider as not_picked
                all_picked = False
                break
            
            # Check if all rows have confirmation_date (not empty, not NaN)
            has_confirmation = tn_rows["confirmation_date"].notna() & (tn_rows["confirmation_date"].astype(str).str.strip() != "")
            if not has_confirmation.all():
                all_picked = False
                break
        
        return "picked" if all_picked else "not_picked"
    
    # APPLY STATUS LOGIC
    vl06f_df["status_hu"] = vl06f_df["to_number"].apply(check_all_confirmed)

    # SAVE UPDATED VL06F
    vl06f_df.to_csv(f"{config.OUTPUT_PATH}vl06f.csv", index=False)
    
    return vl06f_df

def prepare_hu_data():
    df = pd.read_csv(f"{config.OUTPUT_PATH}vl06f.csv", dtype={"hu": "str"})

    # PARSE gi_date to datetime
    df["gi_date_parsed"] = pd.to_datetime(df["gi_date"], format="%d.%m.%Y", errors="coerce")

    # GET TODAY'S DATE
    today = datetime.now().date()

    # FILTER INTO THREE GROUPS
    past_df = df[df["gi_date_parsed"].dt.date < today]
    today_df = df[df["gi_date_parsed"].dt.date == today]
    future_df = df[df["gi_date_parsed"].dt.date > today]

    return past_df, today_df, future_df

def process_hu_dataframe(df_group, add_likp_count=False):
    # HANDLE EMPTY DATAFRAME
    if df_group.empty:
        return {}
    
    # MAKE A COPY TO AVOID MODIFYING ORIGINAL
    df_work = df_group.copy()

    # EXTRACT HOUR FROM gi_time
    df_work["hour"] = pd.to_datetime(df_work["gi_time"], format="%H:%M:%S", errors="coerce").dt.hour

    # GROUP BY DATE, HOUR, AND STATUS - COUNT UNIQUE HU VALUES
    grouped = df_work.groupby(["gi_date_parsed", "hour", "status_hu"])["hu"].nunique().reset_index(name="count")

    # BUILD THE NESTED DICTIONARY STRUCTURE
    result = {}

    for _, row in grouped.iterrows():
        date_str = row["gi_date_parsed"].strftime("%d.%m.%Y")
        hour = int(row["hour"])
        status = row["status_hu"]

        # INITIALIZE DATE IF NEEDED
        if date_str not in result:
            result[date_str] = {}
        
        # INITIALIZE HOUR WITH ALL THREE STATUS AT 0
        if hour not in result[date_str]:
            result[date_str][hour] = {
                "picked": {"amount_of_hu": 0},
                "not_picked": {"amount_of_hu": 0},
                "not_released": {"amount_of_hu": 0}
            }
        
        # UPDATE THE COUNT FOR THE SPECIFIC STATUS
        count = int(row["count"])
        result[date_str][hour][status]["amount_of_hu"] = count
    
    # ADD hu_pgid IF REQUESTED
    if add_likp_count:
        likp_hu_count = get_likp_hu_count()
        # ADD TO EACH DATE IN THE RESULT
        for date_str in result:
            result[date_str]["hu_pgid"] = likp_hu_count

    return result

def save_hu_json(past_json, today_json, future_json):
    with open(f"{config.OUTPUT_PATH}hu_past.json", "w") as f:
        json.dump(past_json, f, indent=2)
    
    with open(f"{config.OUTPUT_PATH}hu_today.json", "w") as f:
        json.dump(today_json, f, indent=2)
    
    with open(f"{config.OUTPUT_PATH}hu_future.json", "w") as f:
        json.dump(future_json, f, indent=2)

def create_hu_json_files():
    # GET FILTERED DATAFRAMES
    past_df, today_df, future_df = prepare_hu_data()
    
    # PROCESS EACH DATAFRAME INTO JSON STRUCTURE
    past_json = process_hu_dataframe(past_df)
    today_json = process_hu_dataframe(today_df, add_likp_count=True)
    future_json = process_hu_dataframe(future_df)
    
    # SAVE TO FILES
    save_hu_json(past_json, today_json, future_json)

def ltap_dashboard():
    # CONVERT
    convert_to_csv("ltap_dashboard")

    # RENAME
    rename("ltap_dashboard", config.LTAP_DASHBOARD_DF)

def hutolink_dashboard_transform():
    retrieve_to_number()
    extract_ltap_dashboard()
    hutolink_dashboard()
    convert_hu_to_link_likp()
    ltap_dashboard()
    vl06f_df = add_to_number_to_vl06f()
    vl06f_df = add_status_hu_to_vl06f(vl06f_df)
    create_hu_json_files()