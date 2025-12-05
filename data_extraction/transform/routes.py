import data_extraction.config.config as config
import pandas as pd

def transform_routes(): 
    df = pd.read_excel(f"{config.OUTPUT_PATH}routes.xlsx")
    df.to_csv(f"{config.OUTPUT_PATH}routes.csv", index=False) 