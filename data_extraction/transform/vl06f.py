from data_extraction.utils.convert import convert_to_csv
from data_extraction.utils.rename import rename
import data_extraction.config.config as config
import pandas as pd
from datetime import datetime
import json

def retrieve_deliveries():
    # CONVERT
    convert_to_csv("vl06f", dtype={"Handling Unit": "str"})

    # RENAME
    rename("vl06f", config.VL06F_DF, dtype={"Handling Unit": "str"})

    # EXTRACT DELIVERIES
    df = pd.read_csv(f"{config.OUTPUT_PATH}vl06f.csv", dtype={"hu": "str"})
    df["delivery"] = df["delivery"].fillna(0).astype(int)
    deliveries_df = df["delivery"].drop_duplicates()
    deliveries_df.to_csv(f"{config.OUTPUT_PATH}deliveries_vl06f.csv", index=False)

def retrieve_hu():
    # EXTRACT HU
    df = pd.read_csv(f"{config.OUTPUT_PATH}vl06f.csv", dtype={"hu": "str"})
    df["hu"] = df["hu"].fillna(0).astype(int)
    hu_df = df["hu"].drop_duplicates()
    hu_df.to_csv(f"{config.OUTPUT_PATH}hu_vl06f.csv", index=False)

def categorize_wm(wm_value):
    if wm_value == "C":
        return "picked"
    elif wm_value == "B":
        return "not_picked"
    else:
        return "not_released"

def prepare_vl06f_data():
    df = pd.read_csv(f"{config.OUTPUT_PATH}vl06f.csv", dtype={"hu": "str"})

    # PARSE gi_date to datetime
    df["gi_date_parsed"] = pd.to_datetime(df["gi_date"], format="%d.%m.%Y", errors="coerce")

    # TODAY'S DATE
    today = datetime.now().date()

    # FILTER INTO THREE GROUPS
    past_df = df[df["gi_date_parsed"].dt.date < today]
    today_df = df[df["gi_date_parsed"].dt.date == today]
    future_df = df[df["gi_date_parsed"].dt.date > today]

    return past_df, today_df, future_df

def get_likp_delivery_count():
    try:
        likp_df = pd.read_csv(f"{config.OUTPUT_PATH}deliveries_likp.csv")
        return likp_df["delivery"].nunique()
    except FileNotFoundError:
        return 0

def process_delivery_dataframe(df_group, add_likp_count=False):
    # HANDLE EMPTY DATAFRAME
    if df_group.empty:
        return {}
    
    # MAKE A COPY TO AVOID MODIFYING ORIGINAL
    df_work = df_group.copy()

    # EXTRACT HOUR FROM gi_time
    df_work["hour"] = pd.to_datetime(df_work["gi_time"], format="%H:%M:%S", errors="coerce").dt.hour

    # CATEGORIZE wm VALUES
    df_work["status"] = df_work["wm"].apply(categorize_wm)

    # GROUP BY DATE, HOUR, AND STATUS - COUNT ROWS
    grouped = df_work.groupby(["gi_date_parsed", "hour", "status"])["delivery"].nunique().reset_index(name="count")

    # BUILD THE NESTED DICTIONARY STRUCTURE
    result = {}

    for _, row in grouped.iterrows():
        date_str = row["gi_date_parsed"].strftime("%d.%m.%Y")
        hour = int(row["hour"])

        # INITIALIZE DATE IF NEEDED
        if date_str not in result:
            result[date_str] = {}
        
        # INITIALIZE HOUR WITH ALL THREE STATUS AT 0
        if hour not in result[date_str]:
            result[date_str][hour] = {
                "picked": {"amount_of_deliveries" : 0},
                "not_picked": {"amount_of_deliveries": 0},
                "not_released": {"amount_of_deliveries": 0}
            }
        
        # UPDATE THE COUNT FOR THE SPECIFIC STATUS
        status = row["status"]
        count = int(row["count"])
        result[date_str][hour][status]["amount_of_deliveries"] = count
    
    # ADD DELIVERIES PGID IF REQUESTED
    if add_likp_count:
        likp_count = get_likp_delivery_count()
        # ADD TO EACH DATE TO THE RESULT
        for date_str in result:
            result[date_str]["deliveries_pgid"] = likp_count

    return result

def save_deliveries_json(past_json, today_json, future_json):
    with open(f"{config.OUTPUT_PATH}deliveries_past.json", "w") as f:
        json.dump(past_json, f, indent=2)
    
    with open(f"{config.OUTPUT_PATH}deliveries_today.json", "w") as f:
        json.dump(today_json, f, indent=2)

    with open(f"{config.OUTPUT_PATH}deliveries_future.json", "w") as f:
        json.dump(future_json, f, indent=2)

def create_delivery_json_files():
    # GET FILTERED DATAFRAMES
    past_df, today_df, future_df = prepare_vl06f_data()

    # PROCESS EACH DATAFRAME INTO JSON STRUCUTRE
    past_json = process_delivery_dataframe(past_df)
    today_json = process_delivery_dataframe(today_df, add_likp_count=True)
    future_json = process_delivery_dataframe(future_df)

    # SAVE TO FILES
    save_deliveries_json(past_json, today_json, future_json)

def vl06f():
    retrieve_deliveries()
    retrieve_hu()
    create_delivery_json_files()