from data_extraction.utils.convert import convert_to_csv
from data_extraction.utils.rename import rename
import data_extraction.config.config as config
import pandas as pd

def hu_to_link():
    # CONVERT
    convert_to_csv("hu_to_link")

    # RENAME
    rename("hu_to_link", config.HU_TO_LINK_DF)

def huto_lnkhis():
    # CONVERT
    convert_to_csv("huto_lnkhis")

    # RENAME
    rename("huto_lnkhis", config.HU_TO_LINK_DF)