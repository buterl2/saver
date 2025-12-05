from data_extraction.transform.routes import transform_routes
from data_extraction.utils.sapsession import SAPSession
import data_extraction.config.config as config
from datetime import datetime
from data_extraction.utils.convert import convert_to_csv, convert_to_json
from data_extraction.utils.rename import rename
import pandas as pd
from collections import defaultdict
from data_extraction.utils.keep_alive import keep_alive
from data_extraction.utils.retry import retry

def extract_ltap_for_productivity():
    # Today's date
    today = datetime.now().strftime("%d.%m.%Y")
    
    # Initialize SAP
    extractor = SAPSession()

    # Start transaction & configure it
    extractor.StartTransaction("Z_TABU_DIS")
    extractor.enter_table("LTAP")
    extractor.checkbox_selection(config.LTAP_CHECKBOX_SELECTIONS)
    extractor.findById("wnd[0]/usr/ctxtI1-LOW").text = config.WAREHOUSE
    extractor.findById("wnd[0]/usr/ctxtI7-LOW").text = today
    extractor.findById("wnd[0]/tbar[1]/btn[8]").press()

    # Save to folder
    extractor.save_to_folder("picking_productivity_ltap")

def extract_hu_to_link_for_productivity():
    # Initialize SAP
    extractor = SAPSession()

    # Start transaction & configure it
    extractor.StartTransaction("Z_TABU_DIS")
    extractor.enter_table("ZORF_HU_TO_LINK")
    extractor.checkbox_selection(config.HUTOLINK_CHECKBOX_SELECTIONS)
    extractor.findById('wnd[0]/usr/ctxtI1-LOW').text = config.WAREHOUSE
    extractor.findById("wnd[0]/usr/btn%_I5_%_APP_%-VALU_PUSH").press()
    extractor.findById("wnd[1]/tbar[0]/btn[23]").press()
    extractor.findById("wnd[2]/usr/ctxtDY_PATH").text = config.OUTPUT_PATH
    extractor.findById("wnd[2]/usr/ctxtDY_FILENAME").text = "picking_productivity_deliveries.csv"
    extractor.findById("wnd[2]/tbar[0]/btn[0]").press()
    extractor.findById("wnd[1]/tbar[0]/btn[8]").press()
    extractor.findById("wnd[0]/tbar[1]/btn[8]").press()

    # Save to folder
    extractor.save_to_folder("picking_productivity_hu_to_link")

    # Start transaction & configure it
    extractor.StartTransaction("Z_TABU_DIS")
    extractor.enter_table("ZORF_HUTO_LNKHIS")
    extractor.checkbox_selection(config.HUTOLINK_CHECKBOX_SELECTIONS)
    extractor.findById('wnd[0]/usr/ctxtI1-LOW').text = config.WAREHOUSE
    extractor.findById("wnd[0]/usr/btn%_I5_%_APP_%-VALU_PUSH").press()
    extractor.findById("wnd[1]/tbar[0]/btn[23]").press()
    extractor.findById("wnd[2]/usr/ctxtDY_PATH").text = config.OUTPUT_PATH
    extractor.findById("wnd[2]/usr/ctxtDY_FILENAME").text = "picking_productivity_deliveries.csv"
    extractor.findById("wnd[2]/tbar[0]/btn[0]").press()
    extractor.findById("wnd[1]/tbar[0]/btn[8]").press()
    extractor.findById("wnd[0]/tbar[1]/btn[8]").press()

    # Save to folder
    extractor.save_to_folder("picking_productivity_huto_lnkhis")

def extract_cdhdr_for_productivity():
    # Today's date
    today = datetime.now().strftime("%d.%m.%Y")

    # Initialize SAP
    extractor = SAPSession()

    # Start transaction & configure it
    extractor.StartTransaction("Z_TABU_DIS")
    extractor.enter_table("CDHDR")
    extractor.checkbox_selection(config.CDHDR_CHECKBOX_SELECTIONS)
    extractor.findById('wnd[0]/usr/ctxtI5-LOW').text = today
    extractor.findById("wnd[0]/usr/ctxtI7-LOW").text = "ZORF_BOX_CLOSING"
    extractor.findById("wnd[0]/usr/btn%_I4_%_APP_%-VALU_PUSH").press()
    extractor.findById("wnd[1]/tbar[0]/btn[23]").press()
    extractor.findById("wnd[2]/usr/ctxtDY_PATH").text = config.OUTPUT_PATH
    extractor.findById("wnd[2]/usr/ctxtDY_FILENAME").text = "users.csv"
    extractor.findById("wnd[2]/tbar[0]/btn[0]").press()
    extractor.findById("wnd[1]/tbar[0]/btn[8]").press()
    extractor.findById("wnd[0]/tbar[1]/btn[8]").press()

    # Save to folder
    extractor.save_to_folder("packing_productivity_cdhdr")

def retrieve_deliveries_from_ltap():
    convert_to_csv("picking_productivity_ltap")
    rename("picking_productivity_ltap", config.LTAP_DF)

    # Extract deliveries
    ltap_df = pd.read_csv(f"{config.OUTPUT_PATH}picking_productivity_ltap.csv")
    ltap_df["delivery"] = ltap_df["delivery"].fillna(0).astype(int)
    deliveries_df = ltap_df["delivery"].drop_duplicates()
    deliveries_df.to_csv(f"{config.OUTPUT_PATH}picking_productivity_deliveries.csv", index=False)

def convert_hu_to_link_for_productivity():
    convert_to_csv("picking_productivity_hu_to_link")
    convert_to_csv("picking_productivity_huto_lnkhis")

    rename("picking_productivity_hu_to_link", config.HU_TO_LINK_DF)
    rename("picking_productivity_huto_lnkhis", config.HU_TO_LINK_DF)

def convert_cdhdr_for_productivity():
    convert_to_csv("packing_productivity_cdhdr")

    rename("packing_productivity_cdhdr", config.CDHDR_DF)

def load_and_combine_hutolnk_routes():
    hu_to_link = pd.read_csv(f"{config.OUTPUT_PATH}picking_productivity_hu_to_link.csv")
    huto_lnkhis = pd.read_csv(f"{config.OUTPUT_PATH}picking_productivity_huto_lnkhis.csv")
    routes = pd.read_csv(f"{config.OUTPUT_PATH}routes.csv")

    combined = pd.concat([hu_to_link, huto_lnkhis], ignore_index=True)
    combined = combined.merge(routes, on="route", how="left")
    combined = combined.drop_duplicates(subset="document", keep="first")

    return combined

def load_and_combine_cdhdr_users():
    cdhdr = pd.read_csv(f"{config.OUTPUT_PATH}packing_productivity_cdhdr.csv")
    users = pd.read_csv(f"{config.OUTPUT_PATH}users_floor.csv")

    combined = cdhdr.merge(users, on="user", how="left")
    combined = combined.drop_duplicates(subset="object_value", keep="first")

    return combined

def prepare_ltap_data(combined):
    ltap = pd.read_csv(f"{config.OUTPUT_PATH}picking_productivity_ltap.csv")
    ltap["actual_quantity"] = pd.to_numeric(ltap["actual_quantity"], errors="coerce").fillna(0).astype(int)
    ltap["delivery"] = ltap["delivery"].fillna(0).astype(int)

    ltap = ltap.merge(combined, left_on="delivery", right_on="document", how="left")

    # Filter out unknown flows
    ltap["flow"] = ltap["flow"].fillna("unknown")
    ltap = ltap[ltap["flow"] != "unknown"].copy()

    # Transformations
    ltap["flow"] = ltap["flow"].replace("y2", "a_flow")
    ltap["floor"] = ltap["picking_area"].map(FLOOR_MAPPING)
    ltap["hour"] = ltap["confirmation_time"].str.slice(0, 2)

    return ltap

def prepare_cdhdr_data(combined):
    combined["datetime"] = pd.to_datetime(combined["date"] + " " + combined["time"], format="%d.%m.%Y %H:%M:%S", errors="coerce")
    combined["datetime"] += pd.DateOffset(hours=1)
    combined["hour"] = combined["datetime"].dt.strftime("%H")
    combined = combined.drop(columns="datetime")

    return combined

def get_productivity_color(value, thresholds):
    if value < thresholds[0]:
        return "red"
    elif value < thresholds[1]:
        return "orange"
    elif value < thresholds[2]:
        return "green"
    else:
        return "purple"

def calculate_picking_hourly_productivity(ltap):
    lines_per_hour = ltap.groupby(["user", "floor", "flow", "hour"]).size()

    nested_dict = defaultdict(lambda: defaultdict(lambda: defaultdict(dict)))
    total_hours = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))

    for (user, floor, flow, hour), count in lines_per_hour.items():
        # Calculate adjusted count for breaks
        if hour in config.BREAKS:
            adjusted_count = count / config.BREAKS[hour]
            total_hours[user][floor][flow] += config.BREAKS[hour]
        else:
            adjusted_count = count
            total_hours[user][floor][flow] += 1
        
        # Determine productivity color
        thresholds = config.PRODUCTIVITY_THRESHOLDS[floor]
        color = get_productivity_color(adjusted_count, thresholds)

        nested_dict[user][floor][flow][hour] = {
            "count": int(count),
            "productivity_color": color
        }

    return nested_dict, total_hours

def calculate_hourly_packing_productivity(cdhdr):
    packing_per_hour = cdhdr.groupby(["user", "floor", "hour"]).size()

    nested_dict = defaultdict(lambda: defaultdict(dict))
    total_hours = defaultdict(lambda: defaultdict(int))

    for (user, floor, hour), count in packing_per_hour.items():
        # Calculate adjusted count for breaks
        if hour in config.BREAKS:
            adjusted_count = count / config.BREAKS[hour]
            total_hours[user][floor] += config.BREAKS[hour]
        else:
            adjusted_count = count
            total_hours[user][floor] += 1

        # Determine productivity color
        thresholds = config.PACKING_THRESHOLDS[floor]
        color = get_productivity_color(adjusted_count, thresholds)

        nested_dict[user][floor][hour] = {
            "count": int(count),
            "productivity_color": color
        }
    
    return nested_dict, total_hours

def calculate_picking_aggregate_metrics(ltap, nested_dict, total_hours, lines_per_user):
    for (user, floor, flow), lines_picked in lines_per_user.items():
        hours_worked = total_hours[user][floor][flow]
        productivity = lines_picked / hours_worked if hours_worked > 0 else 0

        # Calculate items picked
        items_picked = ltap.loc[(ltap["user"] == user) & (ltap["floor"] == floor) & (ltap["flow"] == flow), "actual_quantity"].sum()

        ratio = items_picked / lines_picked if lines_picked > 0 else 0

        # Get productivity color for aggregate
        thresholds = config.PRODUCTIVITY_THRESHOLDS[floor]
        color = get_productivity_color(productivity, thresholds)

        # Update nested dictionary
        nested_dict[user][floor][flow]["hours_worked"] = hours_worked
        nested_dict[user][floor][flow]["productivity"] = round(productivity, 2)
        nested_dict[user][floor][flow]["productivity_color"] = color
        nested_dict[user][floor][flow]["items_picked"] = int(items_picked)
        nested_dict[user][floor][flow]["lines_picked"] = int(lines_picked)
        nested_dict[user][floor][flow]["ratio"] = round(ratio, 2)

def calculate_packing_aggregate_metrics(nested_dict, total_hours, packing_per_user):
    for (user, floor), boxes_packed in packing_per_user.items():
        hours_worked = total_hours[user][floor]
        productivity = boxes_packed / hours_worked if hours_worked > 0 else 0

        # Get productivity color for aggregate
        thresholds = config.PACKING_THRESHOLDS[floor]
        color = get_productivity_color(productivity, thresholds)

        # Update nested dictionary
        nested_dict[user][floor]["hours_worked"] = hours_worked
        nested_dict[user][floor]["productivity"] = round(productivity, 2)
        nested_dict[user][floor]["productivity_color"] = color
        nested_dict[user][floor]["boxes_packed"] = int(boxes_packed)

if __name__ == "__main__":
    while True:
        current_time = datetime.now().strftime('%H:%M:%S')
        current_day = datetime.now().weekday()

        if current_day < 5 and current_time > '08:00:00' and current_time < '23:30:00':
            retry(transform_routes)
            retry(extract_ltap_for_productivity)
            retry(retrieve_deliveries_from_ltap)
            retry(extract_hu_to_link_for_productivity)
            retry(extract_cdhdr_for_productivity)
            retry(convert_hu_to_link_for_productivity)
            
            # Load and combine supporting data
            combined = retry(load_and_combine_hutolnk_routes)

            # Get floor mapping
            FLOOR_MAPPING = {area: floor for floor, areas in config.FLOORS.items() for area in areas}

            # Prepare LTAP data
            ltap = prepare_ltap_data(combined)

            # Calculate grouped metrics
            lines_per_user = ltap.groupby(["user", "floor", "flow"]).size()

            # Calculate hourly productivity
            nested_dict, total_hours = calculate_picking_hourly_productivity(ltap)

            # Calculate aggregate metrics
            calculate_picking_aggregate_metrics(ltap, nested_dict, total_hours, lines_per_user)

            # Convert nested dict to regular dict for JSON serialization
            result = {k: {k2: {k3: dict(v3) for k3, v3 in v2.items()} for k2, v2 in v.items()} for k, v in nested_dict.items()}

            # Save to JSON
            convert_to_json("total_per_floor_per_flow_picks_per_hour", result)

            retry(convert_cdhdr_for_productivity)

            # Load and combine supporting data
            combined = retry(load_and_combine_cdhdr_users)

            # Prepare CDHDR data
            cdhdr = prepare_cdhdr_data(combined)

            # Calculate grouped metrics
            packing_per_user = cdhdr.groupby(["user", "floor"]).size()

            # Calculate hourly productivity
            nested_dict, total_hours = calculate_hourly_packing_productivity(cdhdr)

            # Calculate aggregate metrics
            calculate_packing_aggregate_metrics(nested_dict, total_hours, packing_per_user)

            # Convert nested dict to regular dict for JSON serialization
            result = {k: {k2: dict(v2) for k2, v2 in v.items()} for k, v in nested_dict.items()}

            # Save to JSON
            convert_to_json("total_per_floor_packs_per_hour", result)
        else:
            retry(keep_alive)