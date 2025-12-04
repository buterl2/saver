from data_extraction.utils.convert import convert_to_csv
from data_extraction.utils.rename import rename
import data_extraction.config.config as config
import pandas as pd

def retrieve_deliveries():
    # CONVERT
    convert_to_csv("likp")

    # RENAME
    rename("likp", config.LIKP_DF)

    df = pd.read_csv(f"{config.OUTPUT_PATH}likp.csv")
    df["delivery"] = df["delivery"].fillna(0).astype(int)
    deliveries_df = df["delivery"].drop_duplicates()
    deliveries_df.to_csv(f"{config.OUTPUT_PATH}deliveries_likp.csv", index=False)

def likp():
    retrieve_deliveries()