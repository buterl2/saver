from data_extraction.utils.convert import convert_to_csv, convert_to_json
from data_extraction.utils.rename import rename
import data_extraction.config.config as config
import pandas as pd
from collections import defaultdict
from data_extraction.utils import default_logger as logger

def retrieve_deliveries():
    # CONVERT
    convert_to_csv("ltap")

    # RENAME
    rename("ltap", config.LTAP_DF)

    # EXTRACT DELIVERIES
    df = pd.read_csv(f"{config.OUTPUT_PATH}ltap.csv")
    #df["actual_quantity"] = df["actual_quantity"].fillna(0).astype(int)
    df["delivery"] = df["delivery"].fillna(0).astype(int)
    deliveries_df = df["delivery"].drop_duplicates()
    deliveries_df.to_csv(f"{config.OUTPUT_PATH}deliveries.csv", index=False)
    logger.info("Deliveries were successfully extracted")

FLOOR_MAPPING = {area: floor for floor, areas in config.FLOORS.items() for area in areas}

def get_productivity_color(value, thresholds):
    if value < thresholds[0]:
        return "red"
    elif value < thresholds[1]:
        return "orange"
    elif value < thresholds[2]:
        return "green"
    else:
        return "purple"

def load_and_combine_data():
    hu_to_link = pd.read_csv(f"{config.OUTPUT_PATH}hu_to_link.csv")
    huto_lnkhis = pd.read_csv(f"{config.OUTPUT_PATH}huto_lnkhis.csv")
    routes = pd.read_csv(f"{config.OUTPUT_PATH}routes.csv")

    combined = pd.concat([hu_to_link, huto_lnkhis], ignore_index=True)
    combined = combined.merge(routes, on="route", how="left")
    combined = combined.drop_duplicates(subset="document", keep="first")
    logger.info("HU-TO-LINK and ROUTES files were combined successfully")
    return combined

def prepare_ltap_data(combined):
    ltap = pd.read_csv(f"{config.OUTPUT_PATH}ltap.csv")
    ltap["actual_quantity"] = pd.to_numeric(ltap["actual_quantity"], errors="coerce").fillna(0).astype(int)
    ltap["delivery"] = ltap["delivery"].fillna(0).astype(int)

    ltap = ltap.merge(combined, left_on="delivery", right_on="document", how="left")

    # DROP COLUMNS IF THEY EXIST
    cols_to_drop = ["material_description", "material", "batch", "document", "route"]
    ltap = ltap.drop(columns=[col for col in cols_to_drop if col in ltap.columns])

    # FILTER OUT UNKNOWN FLOWS
    ltap["flow"] = ltap["flow"].fillna("unknown")
    ltap = ltap[ltap["flow"] != "unknown"].copy()

    # TRANSFORMATIONS
    ltap["flow"] = ltap["flow"].replace("y2", "a_flow")
    ltap["floor"] = ltap["picking_area"].map(FLOOR_MAPPING)
    ltap["hour"] = ltap["confirmation_time"].str.slice(0, 2)

    logger.info("LTAP data successfully prepared")

    return ltap

def calculate_hourly_productivity(ltap):
    lines_per_hour = ltap.groupby(["user", "floor", "flow", "hour"]).size()

    nested_dict = defaultdict(lambda: defaultdict(lambda: defaultdict(dict)))
    total_hours = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))

    for (user, floor, flow, hour), count in lines_per_hour.items():
        # CALCUATE ADJUSTED COUNT FOR BREAKS
        if hour in config.BREAKS:
            adjusted_count = count / config.BREAKS[hour]
            total_hours[user][floor][flow] += config.BREAKS[hour]
        else:
            adjusted_count = count
            total_hours[user][floor][flow] += 1

        # DETERMINE PRODUCTIVITY COLOR
        thresholds = config.PRODUCTIVITY_THRESHOLDS[floor]
        color = get_productivity_color(adjusted_count, thresholds)
        
        nested_dict[user][floor][flow][hour] = {
            "count": int(count),
            "productivity_color": color
        }

    logger.info("Hourly productivity (LTAP) calculated successfully")
    
    return nested_dict, total_hours

def calculate_aggregate_metrics(ltap, nested_dict, total_hours, lines_per_user):
    for (user, floor, flow), lines_picked in lines_per_user.items():
        hours_worked = total_hours[user][floor][flow]
        productivity = lines_picked / hours_worked if hours_worked > 0 else 0

        # CALCULATE ITEMS PICKED
        items_picked = ltap.loc[
            (ltap["user"] == user) & 
            (ltap["floor"] == floor) &
            (ltap["flow"] == flow),
            "actual_quantity"
        ].sum()

        ratio = items_picked / lines_picked if lines_picked > 0 else 0

        # GET PRODUCITIVITY COLOR FOR AGGREGATE
        thresholds = config.PRODUCTIVITY_THRESHOLDS[floor]
        color = get_productivity_color(productivity, thresholds)

        # UPDATE NESTED DICTIONARY
        nested_dict[user][floor][flow]["hours_worked"] = hours_worked
        nested_dict[user][floor][flow]["productivity"] = round(productivity, 2)
        nested_dict[user][floor][flow]["productivity_color"] = color
        nested_dict[user][floor][flow]["items_picked"] = int(items_picked)
        nested_dict[user][floor][flow]["lines_picked"] = int(lines_picked)
        nested_dict[user][floor][flow]["ratio"] = round(ratio, 2)

    logger.info("Aggregate metrics (LTAP) calculated successfully")

def transform_ltap():
    # LOAD AND COMBINE SUPPORTING DATA
    combined = load_and_combine_data()

    # PREPARE LTAP DATA
    ltap = prepare_ltap_data(combined)

    # CALCULATE GROUPED METRICS
    lines_per_user = ltap.groupby(["user", "floor", "flow"]).size()

    # CALCULATE HOURLY PRODUCTIVITY
    nested_dict, total_hours = calculate_hourly_productivity(ltap)

    # CALCULATE AGGREGATE METRICS
    calculate_aggregate_metrics(ltap, nested_dict, total_hours, lines_per_user)

    # CONVERT NESTED DICT TO REGULAR DICT FOR JSON SERIALIZATION
    result = {k: {k2: {k3: dict(v3) for k3, v3 in v2.items()}
                for k2, v2 in v.items()}
            for k, v in nested_dict.items()}

    # SAVE TO JSON
    convert_to_json("total_per_floor_per_flow_picks_per_hour", result)