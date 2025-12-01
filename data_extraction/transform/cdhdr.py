from data_extraction.utils.convert import convert_to_csv, convert_to_json
from data_extraction.utils.rename import rename
import data_extraction.config.config as config
import pandas as pd
from collections import defaultdict
from data_extraction.utils import default_logger as logger

def cdhdr():
    # CONVERT
    convert_to_csv("cdhdr")

    # RENAME
    rename("cdhdr", config.CDHDR_DF)

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
    cdhdr_df = pd.read_csv(f"{config.OUTPUT_PATH}cdhdr.csv")
    users = pd.read_csv(f"{config.OUTPUT_PATH}users_floor.csv")

    combined = cdhdr_df.merge(users, on="user", how="left")
    combined = combined.drop_duplicates(subset="object_value", keep="first")

    logger.info("CDHDR and USERS files were combined successfully")
    return combined

def prepare_cdhdr_data(combined):
    combined["datetime"] = pd.to_datetime(
        combined["date"] + " " + combined["time"],
        format="%d.%m.%Y %H:%M:%S",
        errors="coerce"
    )
    combined["datetime"] += pd.DateOffset(hours=1)
    combined["hour"] = combined["datetime"].dt.strftime("%H")
    combined = combined.drop(columns="datetime")

    logger.info("CDHDR data successfully prepared")

    return combined

def calculate_hourly_productivity(cdhdr_df):
    packing_per_hour = cdhdr_df.groupby(["user", "floor", "hour"]).size()

    # USE DEFAULTDICT TO SIMPLIFY NESTED DICT CREATION
    nested_dict = defaultdict(lambda: defaultdict(dict))
    total_hours = defaultdict(lambda: defaultdict(int))

    for (user, floor, hour), count in packing_per_hour.items():
        # CALCULATE ADJUSTED COUNT FOR BREAKS
        if hour in config.BREAKS:
            adjusted_count = count / config.BREAKS[hour]
            total_hours[user][floor] += config.BREAKS[hour]
        else:
            adjusted_count = count
            total_hours[user][floor] += 1

        # DETERMINE PRODUCTIVITY COLOR
        thresholds = config.PACKING_THRESHOLDS[floor]
        color = get_productivity_color(adjusted_count, thresholds)

        nested_dict[user][floor][hour] = {
            "count": int(count),
            "productivity_color": color
        }
    
    logger.info("Hourly productivity (CDHDR) calculated successfully")

    return nested_dict, total_hours

def calculate_aggregate_metrics(nested_dict, total_hours, packing_per_user):
    for (user, floor), boxes_packed in packing_per_user.items():
        hours_worked = total_hours[user][floor]
        productivity = boxes_packed / hours_worked if hours_worked > 0 else 0

        # GET PRODUCTIVITY COLOR FOR AGGREGATE
        thresholds = config.PACKING_THRESHOLDS[floor]
        color = get_productivity_color(productivity, thresholds)

        # UPDATE NESTED DICTIONARY
        nested_dict[user][floor]["hours_worked"] = hours_worked
        nested_dict[user][floor]["productivity"] = round(productivity, 2)
        nested_dict[user][floor]["productivity_color"] = color
        nested_dict[user][floor]["boxes_packed"] = int(boxes_packed)

    logger.info("Aggregate metrics (CDHDR) calculated successfully")

def transform_cdhdr():
    # LOAD AND COMBINE DATA
    combined = load_and_combine_data()

    # PREPARE CDHDR DATA
    cdhdr = prepare_cdhdr_data(combined)

    # CALCULATE GROUPED METRICS
    packing_per_user = cdhdr.groupby(["user", "floor"]).size()

    # CALCULATE HOURLY PRODUCTIVITY
    nested_dict, total_hours = calculate_hourly_productivity(cdhdr)

    # CALCULATE AGGREGATE METRICS
    calculate_aggregate_metrics(nested_dict, total_hours, packing_per_user)

    # CONVERT NESTED DICT TO REGULAR DICT FOR JSON SERIALIZATION
    result = {k: {k2: dict(v2) for k2, v2 in v.items()} 
              for k, v in nested_dict.items()}
    
    # SAVE TO JSON
    convert_to_json('total_per_floor_packs_per_hour', result)