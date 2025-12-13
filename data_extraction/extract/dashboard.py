from data_extraction.utils.sapsession import SAPSession
import data_extraction.config.config as config
from data_extraction.utils.convert import convert_to_csv
from data_extraction.utils.rename import rename
import pandas as pd
from datetime import datetime
import json

def extract_vl06f_for_dashboard():
    # Initialize SAP
    extractor = SAPSession()

    # Start transaction & configure it
    extractor.StartTransaction("VL06F")
    extractor.vl06f_dashboard(config.VARIANT_VL06F_DASHBOARD)

    # Save to folder
    extractor.save_to_folder("vl06f_dashboard")

def extract_likp_for_dashboard():
    # Today's date
    today = datetime.now().strftime("%d.%m.%Y")

    # Initialize SAP
    extractor = SAPSession()

    # Start transaction & configure it
    extractor.StartTransaction("Z_TABU_DIS")
    extractor.enter_table("LIKP")
    extractor.checkbox_selection(config.LIKP_CHECKBOX_SELECTIONS)
    extractor.findById("wnd[0]/usr/btn%_I6_%_APP_%-VALU_PUSH").press()
    extractor.findById("wnd[1]/tbar[0]/btn[23]").press()
    extractor.findById("wnd[2]/usr/ctxtDY_PATH").text = config.OUTPUT_PATH
    extractor.findById("wnd[2]/usr/ctxtDY_FILENAME").text = "bflow_routes.csv"
    extractor.findById("wnd[2]/usr/ctxtDY_FILENAME").caretPosition = 16
    extractor.findById("wnd[2]/tbar[0]/btn[0]").press()
    extractor.findById("wnd[1]/tbar[0]/btn[8]").press()
    extractor.findById("wnd[0]/usr/ctxtI8-LOW").text = config.WAREHOUSE
    extractor.findById("wnd[0]/usr/ctxtI9-LOW").text = '12.12.2025' # CHANGEBACK
    extractor.findById("wnd[0]/usr/ctxtI9-LOW").setFocus()
    extractor.findById("wnd[0]/usr/ctxtI9-LOW").caretPosition = 10
    extractor.findById("wnd[0]").sendVKey(0)
    extractor.findById("wnd[0]/tbar[1]/btn[8]").press()

    # Save to folder
    extractor.save_to_folder("likp_dashboard")

def extract_zorf_huto_link_vl06f():
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
    extractor.findById("wnd[2]/usr/ctxtDY_FILENAME").text = "vl06f_deliveries.csv"
    extractor.findById("wnd[2]/tbar[0]/btn[0]").press()
    extractor.findById("wnd[1]/tbar[0]/btn[8]").press()
    extractor.findById("wnd[0]/tbar[1]/btn[8]").press()
    extractor.findById("wnd[0]/tbar[1]/btn[32]").press()
    extractor.findById("wnd[1]/usr/tabsG_TS_ALV/tabpALV_M_R1/ssubSUB_DYN0510:SAPLSKBH:0620/cntlCONTAINER1_LAYO/shellcont/shell").currentCellRow = 2
    extractor.findById("wnd[1]/usr/tabsG_TS_ALV/tabpALV_M_R1/ssubSUB_DYN0510:SAPLSKBH:0620/cntlCONTAINER1_LAYO/shellcont/shell").selectedRows = "2"
    extractor.findById("wnd[1]/usr/tabsG_TS_ALV/tabpALV_M_R1/ssubSUB_DYN0510:SAPLSKBH:0620/btnAPP_WL_SING").press()
    extractor.findById("wnd[1]/usr/tabsG_TS_ALV/tabpALV_M_R1/ssubSUB_DYN0510:SAPLSKBH:0620/cntlCONTAINER1_LAYO/shellcont/shell").currentCellRow = 3
    extractor.findById("wnd[1]/usr/tabsG_TS_ALV/tabpALV_M_R1/ssubSUB_DYN0510:SAPLSKBH:0620/cntlCONTAINER1_LAYO/shellcont/shell").selectedRows = "3"
    extractor.findById("wnd[1]/usr/tabsG_TS_ALV/tabpALV_M_R1/ssubSUB_DYN0510:SAPLSKBH:0620/btnAPP_WL_SING").press()
    extractor.findById("wnd[1]/usr/tabsG_TS_ALV/tabpALV_M_R1/ssubSUB_DYN0510:SAPLSKBH:0620/cntlCONTAINER1_LAYO/shellcont/shell").currentCellRow = 8
    extractor.findById("wnd[1]/usr/tabsG_TS_ALV/tabpALV_M_R1/ssubSUB_DYN0510:SAPLSKBH:0620/cntlCONTAINER1_LAYO/shellcont/shell").selectedRows = "8"
    extractor.findById("wnd[1]/usr/tabsG_TS_ALV/tabpALV_M_R1/ssubSUB_DYN0510:SAPLSKBH:0620/btnAPP_WL_SING").press()
    extractor.findById("wnd[1]/tbar[0]/btn[0]").press()

    # Save to folder
    extractor.save_to_folder("zorf_hu_to_link_vl06f")

    # Start transaction & configure it
    """extractor.StartTransaction("Z_TABU_DIS")
    extractor.enter_table("ZORF_HUTO_LNKHIS")
    extractor.checkbox_selection(config.HUTOLINK_CHECKBOX_SELECTIONS)
    extractor.findById('wnd[0]/usr/ctxtI1-LOW').text = config.WAREHOUSE
    extractor.findById("wnd[0]/usr/btn%_I5_%_APP_%-VALU_PUSH").press()
    extractor.findById("wnd[1]/tbar[0]/btn[23]").press()
    extractor.findById("wnd[2]/usr/ctxtDY_PATH").text = config.OUTPUT_PATH
    extractor.findById("wnd[2]/usr/ctxtDY_FILENAME").text = "vl06f_deliveries.csv"
    extractor.findById("wnd[2]/tbar[0]/btn[0]").press()
    extractor.findById("wnd[1]/tbar[0]/btn[8]").press()
    extractor.findById("wnd[0]/tbar[1]/btn[8]").press()
    extractor.findById("wnd[0]/tbar[1]/btn[32]").press()
    extractor.findById("wnd[1]/usr/tabsG_TS_ALV/tabpALV_M_R1/ssubSUB_DYN0510:SAPLSKBH:0620/cntlCONTAINER1_LAYO/shellcont/shell").currentCellRow = 2
    extractor.findById("wnd[1]/usr/tabsG_TS_ALV/tabpALV_M_R1/ssubSUB_DYN0510:SAPLSKBH:0620/cntlCONTAINER1_LAYO/shellcont/shell").selectedRows = "2"
    extractor.findById("wnd[1]/usr/tabsG_TS_ALV/tabpALV_M_R1/ssubSUB_DYN0510:SAPLSKBH:0620/btnAPP_WL_SING").press()
    extractor.findById("wnd[1]/usr/tabsG_TS_ALV/tabpALV_M_R1/ssubSUB_DYN0510:SAPLSKBH:0620/cntlCONTAINER1_LAYO/shellcont/shell").currentCellRow = 3
    extractor.findById("wnd[1]/usr/tabsG_TS_ALV/tabpALV_M_R1/ssubSUB_DYN0510:SAPLSKBH:0620/cntlCONTAINER1_LAYO/shellcont/shell").selectedRows = "3"
    extractor.findById("wnd[1]/usr/tabsG_TS_ALV/tabpALV_M_R1/ssubSUB_DYN0510:SAPLSKBH:0620/btnAPP_WL_SING").press()
    extractor.findById("wnd[1]/usr/tabsG_TS_ALV/tabpALV_M_R1/ssubSUB_DYN0510:SAPLSKBH:0620/cntlCONTAINER1_LAYO/shellcont/shell").currentCellRow = 8
    extractor.findById("wnd[1]/usr/tabsG_TS_ALV/tabpALV_M_R1/ssubSUB_DYN0510:SAPLSKBH:0620/cntlCONTAINER1_LAYO/shellcont/shell").selectedRows = "8"
    extractor.findById("wnd[1]/usr/tabsG_TS_ALV/tabpALV_M_R1/ssubSUB_DYN0510:SAPLSKBH:0620/btnAPP_WL_SING").press()
    extractor.findById("wnd[1]/tbar[0]/btn[0]").press()

    # Save to folder
    extractor.save_to_folder("zorf_huto_lnkhis_vl06f")"""

def extract_zorf_huto_link_likp():
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
    extractor.findById("wnd[2]/usr/ctxtDY_FILENAME").text = "likp_deliveries.csv"
    extractor.findById("wnd[2]/tbar[0]/btn[0]").press()
    extractor.findById("wnd[1]/tbar[0]/btn[8]").press()
    extractor.findById("wnd[0]/tbar[1]/btn[8]").press()
    extractor.findById("wnd[0]/tbar[1]/btn[32]").press()
    extractor.findById("wnd[1]/usr/tabsG_TS_ALV/tabpALV_M_R1/ssubSUB_DYN0510:SAPLSKBH:0620/cntlCONTAINER1_LAYO/shellcont/shell").currentCellRow = 2
    extractor.findById("wnd[1]/usr/tabsG_TS_ALV/tabpALV_M_R1/ssubSUB_DYN0510:SAPLSKBH:0620/cntlCONTAINER1_LAYO/shellcont/shell").selectedRows = "2"
    extractor.findById("wnd[1]/usr/tabsG_TS_ALV/tabpALV_M_R1/ssubSUB_DYN0510:SAPLSKBH:0620/btnAPP_WL_SING").press()
    extractor.findById("wnd[1]/usr/tabsG_TS_ALV/tabpALV_M_R1/ssubSUB_DYN0510:SAPLSKBH:0620/cntlCONTAINER1_LAYO/shellcont/shell").currentCellRow = 3
    extractor.findById("wnd[1]/usr/tabsG_TS_ALV/tabpALV_M_R1/ssubSUB_DYN0510:SAPLSKBH:0620/cntlCONTAINER1_LAYO/shellcont/shell").selectedRows = "3"
    extractor.findById("wnd[1]/usr/tabsG_TS_ALV/tabpALV_M_R1/ssubSUB_DYN0510:SAPLSKBH:0620/btnAPP_WL_SING").press()
    extractor.findById("wnd[1]/usr/tabsG_TS_ALV/tabpALV_M_R1/ssubSUB_DYN0510:SAPLSKBH:0620/cntlCONTAINER1_LAYO/shellcont/shell").currentCellRow = 8
    extractor.findById("wnd[1]/usr/tabsG_TS_ALV/tabpALV_M_R1/ssubSUB_DYN0510:SAPLSKBH:0620/cntlCONTAINER1_LAYO/shellcont/shell").selectedRows = "8"
    extractor.findById("wnd[1]/usr/tabsG_TS_ALV/tabpALV_M_R1/ssubSUB_DYN0510:SAPLSKBH:0620/btnAPP_WL_SING").press()
    extractor.findById("wnd[1]/tbar[0]/btn[0]").press()

    # Save to folder
    extractor.save_to_folder("zorf_hu_to_link_likp")

    # Start transaction & configure it
    extractor.StartTransaction("Z_TABU_DIS")
    extractor.enter_table("ZORF_HUTO_LNKHIS")
    extractor.checkbox_selection(config.HUTOLINK_CHECKBOX_SELECTIONS)
    extractor.findById('wnd[0]/usr/ctxtI1-LOW').text = config.WAREHOUSE
    extractor.findById("wnd[0]/usr/btn%_I5_%_APP_%-VALU_PUSH").press()
    extractor.findById("wnd[1]/tbar[0]/btn[23]").press()
    extractor.findById("wnd[2]/usr/ctxtDY_PATH").text = config.OUTPUT_PATH
    extractor.findById("wnd[2]/usr/ctxtDY_FILENAME").text = "likp_deliveries.csv"
    extractor.findById("wnd[2]/tbar[0]/btn[0]").press()
    extractor.findById("wnd[1]/tbar[0]/btn[8]").press()
    extractor.findById("wnd[0]/tbar[1]/btn[8]").press()
    extractor.findById("wnd[0]/tbar[1]/btn[32]").press()
    extractor.findById("wnd[1]/usr/tabsG_TS_ALV/tabpALV_M_R1/ssubSUB_DYN0510:SAPLSKBH:0620/cntlCONTAINER1_LAYO/shellcont/shell").currentCellRow = 2
    extractor.findById("wnd[1]/usr/tabsG_TS_ALV/tabpALV_M_R1/ssubSUB_DYN0510:SAPLSKBH:0620/cntlCONTAINER1_LAYO/shellcont/shell").selectedRows = "2"
    extractor.findById("wnd[1]/usr/tabsG_TS_ALV/tabpALV_M_R1/ssubSUB_DYN0510:SAPLSKBH:0620/btnAPP_WL_SING").press()
    extractor.findById("wnd[1]/usr/tabsG_TS_ALV/tabpALV_M_R1/ssubSUB_DYN0510:SAPLSKBH:0620/cntlCONTAINER1_LAYO/shellcont/shell").currentCellRow = 3
    extractor.findById("wnd[1]/usr/tabsG_TS_ALV/tabpALV_M_R1/ssubSUB_DYN0510:SAPLSKBH:0620/cntlCONTAINER1_LAYO/shellcont/shell").selectedRows = "3"
    extractor.findById("wnd[1]/usr/tabsG_TS_ALV/tabpALV_M_R1/ssubSUB_DYN0510:SAPLSKBH:0620/btnAPP_WL_SING").press()
    extractor.findById("wnd[1]/usr/tabsG_TS_ALV/tabpALV_M_R1/ssubSUB_DYN0510:SAPLSKBH:0620/cntlCONTAINER1_LAYO/shellcont/shell").currentCellRow = 8
    extractor.findById("wnd[1]/usr/tabsG_TS_ALV/tabpALV_M_R1/ssubSUB_DYN0510:SAPLSKBH:0620/cntlCONTAINER1_LAYO/shellcont/shell").selectedRows = "8"
    extractor.findById("wnd[1]/usr/tabsG_TS_ALV/tabpALV_M_R1/ssubSUB_DYN0510:SAPLSKBH:0620/btnAPP_WL_SING").press()
    extractor.findById("wnd[1]/tbar[0]/btn[0]").press()

    # Save to folder
    extractor.save_to_folder("zorf_huto_lnkhis_likp")

def extract_ltap_from_to_numbers(file, filename):
    # Initialize SAP
    extractor = SAPSession()

    # Start transaction & configure it
    extractor.StartTransaction("Z_TABU_DIS")
    extractor.enter_table("LTAP")
    extractor.checkbox_selection(config.LTAP_CHECKBOX_SELECTIONS)
    extractor.findById("wnd[0]/usr/ctxtI1-LOW").text = config.WAREHOUSE
    extractor.findById("wnd[0]/usr/ctxtI1-LOW").caretPosition = 3
    extractor.findById("wnd[0]/usr/btn%_I2_%_APP_%-VALU_PUSH").press()
    extractor.findById("wnd[1]/tbar[0]/btn[23]").press()
    extractor.findById("wnd[2]/usr/ctxtDY_PATH").text = config.OUTPUT_PATH
    extractor.findById("wnd[2]/usr/ctxtDY_FILENAME").text = file
    extractor.findById("wnd[2]/usr/ctxtDY_FILENAME").caretPosition = 30
    extractor.findById("wnd[2]/tbar[0]/btn[0]").press()
    extractor.findById("wnd[2]/usr/btnBUTTON_1").press()
    extractor.findById("wnd[1]/tbar[0]/btn[8]").press()
    extractor.findById("wnd[0]/tbar[1]/btn[8]").press()
    extractor.findById("wnd[0]/tbar[1]/btn[32]").press()
    extractor.findById("wnd[1]/usr/tabsG_TS_ALV/tabpALV_M_R1/ssubSUB_DYN0510:SAPLSKBH:0620/cntlCONTAINER1_LAYO/shellcont/shell").currentCellRow = 2
    extractor.findById("wnd[1]/usr/tabsG_TS_ALV/tabpALV_M_R1/ssubSUB_DYN0510:SAPLSKBH:0620/cntlCONTAINER1_LAYO/shellcont/shell").selectedRows = "2"
    extractor.findById("wnd[1]/usr/tabsG_TS_ALV/tabpALV_M_R1/ssubSUB_DYN0510:SAPLSKBH:0620/btnAPP_WL_SING").press()
    extractor.findById("wnd[1]/tbar[0]/btn[0]").press()
    extractor.findById("wnd[0]/usr/cntlGRID1/shellcont/shell").setCurrentCell(-1,"QDATU")
    extractor.findById("wnd[0]/usr/cntlGRID1/shellcont/shell").selectColumn("QDATU")
    extractor.findById("wnd[0]/tbar[1]/btn[40]").press()

    # Save to folder
    extractor.save_to_folder(filename)

def extract_bflow_routes():
    routes_df = pd.read_csv(f"{config.OUTPUT_PATH}routes.csv")
    routes_df = routes_df.loc[routes_df["flow"] == "b_flow", "route"]

    routes_df.to_csv(f"{config.OUTPUT_PATH}bflow_routes.csv", index=False)

def extract_deliveries_from_vl06f_for_dashboard():
    # Extract deliveries
    vl06f_df = pd.read_csv(f"{config.OUTPUT_PATH}vl06f_dashboard.csv")
    vl06f_df["delivery"] = vl06f_df["delivery"].fillna(0).astype(int)
    deliveries_df = vl06f_df["delivery"].drop_duplicates()
    deliveries_df.to_csv(f"{config.OUTPUT_PATH}vl06f_deliveries.csv", index=False)

def extract_deliveries_from_likp_for_dashboard():
    # Extract deliveries
    likp_df = pd.read_csv(f"{config.OUTPUT_PATH}likp_dashboard.csv")
    likp_df["delivery"] = likp_df["delivery"].fillna(0).astype(int)
    deliveries_df = likp_df["delivery"].drop_duplicates()
    deliveries_df.to_csv(f"{config.OUTPUT_PATH}likp_deliveries.csv", index=False)

def extract_to_number_from_zorf_huto_link_for_dashboard():
    # Extract to_number
    hu_to_link_likp_df = pd.read_csv(f"{config.OUTPUT_PATH}zorf_hu_to_link_likp.csv")
    hu_to_link_vl06f_df = pd.read_csv(f"{config.OUTPUT_PATH}zorf_hu_to_link_vl06f.csv")
    huto_lnkhis_likp_df = pd.read_csv(f"{config.OUTPUT_PATH}zorf_huto_lnkhis_likp.csv")
    huto_lnkhis_vl06f_df = pd.read_csv(f"{config.OUTPUT_PATH}zorf_huto_lnkhis_vl06f.csv")

    hu_to_link_likp_df["to_number"] = hu_to_link_likp_df["to_number"].fillna(0).astype(int)
    hu_to_link_vl06f_df["to_number"] = hu_to_link_vl06f_df["to_number"].fillna(0).astype(int)
    huto_lnkhis_likp_df["to_number"] = huto_lnkhis_likp_df["to_number"].fillna(0).astype(int)
    huto_lnkhis_vl06f_df["to_number"] = huto_lnkhis_vl06f_df["to_number"].fillna(0).astype(int)

    to_number_df_one = hu_to_link_likp_df["to_number"].drop_duplicates()
    to_number_df_one.to_csv(f"{config.OUTPUT_PATH}hu_to_link_likp_to_numbers.csv", index=False)
    to_number_df_two = hu_to_link_vl06f_df["to_number"].drop_duplicates()
    to_number_df_two.to_csv(f"{config.OUTPUT_PATH}hu_to_link_vl06f_to_numbers.csv", index=False)
    to_number_df_three = huto_lnkhis_likp_df["to_number"].drop_duplicates()
    to_number_df_three.to_csv(f"{config.OUTPUT_PATH}huto_lnkhis_likp_to_numbers.csv", index=False)
    to_number_df_four = huto_lnkhis_vl06f_df["to_number"].drop_duplicates()
    to_number_df_four.to_csv(f"{config.OUTPUT_PATH}huto_lnkhis_vl06f_to_numbers.csv", index=False)

def convert_likp_for_dashboard():
    convert_to_csv("likp_dashboard")

    rename("likp_dashboard", config.LIKP_DF)

def convert_vl06f_for_dashboard():
    convert_to_csv("vl06f_dashboard", dtype={"Handling Unit": "str"})

    rename("vl06f_dashboard", config.VL06F_DF, dtype={"Handling Unit": "str"})

def convert_zorf_huto_link_for_dashboard():
    convert_to_csv("zorf_hu_to_link_likp", dtype={"Handling Unit": "str"})
    convert_to_csv("zorf_hu_to_link_vl06f", dtype={"Handling Unit": "str"})
    convert_to_csv("zorf_huto_lnkhis_likp", dtype={"Handling Unit": "str"})
    convert_to_csv("zorf_huto_lnkhis_vl06f", dtype={"Handling Unit": "str"})

    rename("zorf_hu_to_link_likp", config.ZORF_HUTO_LINK_DASHBOARD_DF, dtype={"Handling Unit": "str"})
    rename("zorf_hu_to_link_vl06f", config.ZORF_HUTO_LINK_DASHBOARD_DF, dtype={"Handling Unit": "str"})
    rename("zorf_huto_lnkhis_likp", config.ZORF_HUTO_LINK_DASHBOARD_DF, dtype={"Handling Unit": "str"})
    rename("zorf_huto_lnkhis_vl06f", config.ZORF_HUTO_LINK_DASHBOARD_DF, dtype={"Handling Unit": "str"})

def convert_ltap_to_numbers():
    convert_to_csv("ltap_likp_to_numbers")
    convert_to_csv("ltap_vl06f_to_numbers")
    convert_to_csv("ltap_likp_to_numbers_two")
    convert_to_csv("ltap_vl06f_to_numbers_two")

    rename("ltap_likp_to_numbers", config.LTAP_DASHBOARD_DF)
    rename("ltap_vl06f_to_numbers", config.LTAP_DASHBOARD_DF)
    rename("ltap_likp_to_numbers_two", config.LTAP_DASHBOARD_DF)
    rename("ltap_vl06f_to_numbers_two", config.LTAP_DASHBOARD_DF)

def determine_floor(source_bin):
    if pd.isna(source_bin) or source_bin == '':
        return []

    source_bin_str = str(source_bin).strip()
    if len(source_bin_str) == 0:
        return []

    first_char = source_bin_str[0].upper()
    floors = []

    if first_char in ["F", "L", "X"]:
        floors.append("ground_floor")
    if first_char == "N":
        floors.append("first_floor")
    if first_char in ["Y", "O", "W"]:
        floors.append("second_floor")

    return floors

def create_deliveries_all_floors():
    # Read vl06f_dashboard.csv
    vl06f_df = pd.read_csv(f"{config.OUTPUT_PATH}vl06f_dashboard.csv")
    
    # Convert delivery to int (handle NaN values)
    vl06f_df["delivery"] = vl06f_df["delivery"].fillna(0).astype(int)
    
    # Read all zorf files
    zorf_hu_to_link_likp_df = pd.read_csv(f"{config.OUTPUT_PATH}zorf_hu_to_link_likp.csv")
    zorf_hu_to_link_vl06f_df = pd.read_csv(f"{config.OUTPUT_PATH}zorf_hu_to_link_vl06f.csv")
    zorf_huto_lnkhis_likp_df = pd.read_csv(f"{config.OUTPUT_PATH}zorf_huto_lnkhis_likp.csv")
    zorf_huto_lnkhis_vl06f_df = pd.read_csv(f"{config.OUTPUT_PATH}zorf_huto_lnkhis_vl06f.csv")
    
    # Convert delivery to int in all zorf files
    zorf_hu_to_link_likp_df["delivery"] = zorf_hu_to_link_likp_df["delivery"].fillna(0).astype(int)
    zorf_hu_to_link_vl06f_df["delivery"] = zorf_hu_to_link_vl06f_df["delivery"].fillna(0).astype(int)
    zorf_huto_lnkhis_likp_df["delivery"] = zorf_huto_lnkhis_likp_df["delivery"].fillna(0).astype(int)
    zorf_huto_lnkhis_vl06f_df["delivery"] = zorf_huto_lnkhis_vl06f_df["delivery"].fillna(0).astype(int)
    
    # Combine all zorf files to create a mapping of delivery -> floors
    # We need to search all files for each delivery
    all_zorf_dfs = [
        zorf_hu_to_link_likp_df,
        zorf_hu_to_link_vl06f_df,
        zorf_huto_lnkhis_likp_df,
        zorf_huto_lnkhis_vl06f_df
    ]
    
    # Create a dictionary to store delivery -> set of floors
    delivery_to_floors = {}
    
    # Process each zorf file
    for zorf_df in all_zorf_dfs:
        for _, row in zorf_df.iterrows():
            delivery = int(row['delivery'])
            source_bin = row['source_bin']
            
            floors = determine_floor(source_bin)
            
            if delivery not in delivery_to_floors:
                delivery_to_floors[delivery] = set()
            
            delivery_to_floors[delivery].update(floors)
    
    # Initialize result dictionary
    result = {}
    
    # Process vl06f_dashboard.csv
    for _, row in vl06f_df.iterrows():
        delivery = int(row['delivery'])
        gi_date = row['gi_date']
        wm = str(row['wm']).strip().upper()
        
        # Skip if delivery is 0 or invalid
        if delivery == 0:
            continue
        
        # Skip if wm is not A, B, or C
        if wm not in ['A', 'B', 'C']:
            continue
        
        # Skip if gi_date is NaN or empty
        if pd.isna(gi_date) or gi_date == '':
            continue
        
        # Format date (assuming it's already in dd.mm.yyyy format, but ensure it is)
        try:
            # If date is in a different format, convert it
            if isinstance(gi_date, str):
                date_str = gi_date
            else:
                # If it's a datetime object, format it
                date_str = pd.to_datetime(gi_date).strftime("%d.%m.%Y")
        except:
            continue
        
        # Initialize date entry if not exists
        if date_str not in result:
            result[date_str] = {
                'ground_floor': {'a': {'amount_of_deliveries': 0}, 'b': {'amount_of_deliveries': 0}, 'c': {'amount_of_deliveries': 0}},
                'first_floor': {'a': {'amount_of_deliveries': 0}, 'b': {'amount_of_deliveries': 0}, 'c': {'amount_of_deliveries': 0}},
                'second_floor': {'a': {'amount_of_deliveries': 0}, 'b': {'amount_of_deliveries': 0}, 'c': {'amount_of_deliveries': 0}},
                'a': {'amount_of_deliveries': 0},
                'b': {'amount_of_deliveries': 0},
                'c': {'amount_of_deliveries': 0}
            }
        
        # Get floors for this delivery
        floors = delivery_to_floors.get(delivery, set())
        
        # If no floors found, skip this delivery (or you might want to handle it differently)
        if not floors:
            continue
        
        # Count this delivery for each floor it belongs to
        for floor in floors:
            # Increment floor-specific count
            result[date_str][floor][wm.lower()]['amount_of_deliveries'] += 1
        
        # Increment total count (count once per delivery, regardless of floors)
        result[date_str][wm.lower()]['amount_of_deliveries'] += 1
    
    # Convert sets to lists for JSON serialization and ensure we're counting unique deliveries per floor/status
    # Actually, we need to count unique deliveries, not just increment
    # Let me revise the approach to count unique deliveries
    
    # Re-initialize result to count unique deliveries
    result = {}
    
    # Process vl06f_dashboard.csv and track unique deliveries
    for _, row in vl06f_df.iterrows():
        delivery = int(row['delivery'])
        gi_date = row['gi_date']
        wm = str(row['wm']).strip().upper()
        
        # Skip if delivery is 0 or invalid
        if delivery == 0:
            continue
        
        # Skip if wm is not A, B, or C
        if wm not in ['A', 'B', 'C']:
            continue
        
        # Skip if gi_date is NaN or empty
        if pd.isna(gi_date) or gi_date == '':
            continue
        
        # Format date
        try:
            if isinstance(gi_date, str):
                date_str = gi_date
            else:
                date_str = pd.to_datetime(gi_date).strftime("%d.%m.%Y")
        except:
            continue
        
        # Initialize date entry if not exists
        if date_str not in result:
            result[date_str] = {
                'ground_floor': {
                    'a': {'amount_of_deliveries': set()},
                    'b': {'amount_of_deliveries': set()},
                    'c': {'amount_of_deliveries': set()}
                },
                'first_floor': {
                    'a': {'amount_of_deliveries': set()},
                    'b': {'amount_of_deliveries': set()},
                    'c': {'amount_of_deliveries': set()}
                },
                'second_floor': {
                    'a': {'amount_of_deliveries': set()},
                    'b': {'amount_of_deliveries': set()},
                    'c': {'amount_of_deliveries': set()}
                },
                'a': {'amount_of_deliveries': set()},
                'b': {'amount_of_deliveries': set()},
                'c': {'amount_of_deliveries': set()}
            }
        
        # Get floors for this delivery
        floors = delivery_to_floors.get(delivery, set())
        
        # If no floors found, skip this delivery
        if not floors:
            continue
        
        # Add this delivery to each floor it belongs to
        for floor in floors:
            result[date_str][floor][wm.lower()]['amount_of_deliveries'].add(delivery)
        
        # Add to total count
        result[date_str][wm.lower()]['amount_of_deliveries'].add(delivery)
    
    # Convert sets to counts
    for date_str in result:
        for floor in ['ground_floor', 'first_floor', 'second_floor']:
            for status in ['a', 'b', 'c']:
                result[date_str][floor][status]['amount_of_deliveries'] = len(result[date_str][floor][status]['amount_of_deliveries'])
        
        for status in ['a', 'b', 'c']:
            result[date_str][status]['amount_of_deliveries'] = len(result[date_str][status]['amount_of_deliveries'])
    
    # Save to JSON file
    output_path = f"{config.OUTPUT_PATH}deliveries_all_floors.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=4, ensure_ascii=False)

def create_hu_all_floors():
    # Read vl06f_dashboard.csv with dtype str for hu column
    vl06f_df = pd.read_csv(f"{config.OUTPUT_PATH}vl06f_dashboard.csv", dtype={'hu': str})
    
    # Read all zorf files with dtype str for hu column
    zorf_hu_to_link_likp_df = pd.read_csv(f"{config.OUTPUT_PATH}zorf_hu_to_link_likp.csv", dtype={'hu': str})
    zorf_hu_to_link_vl06f_df = pd.read_csv(f"{config.OUTPUT_PATH}zorf_hu_to_link_vl06f.csv", dtype={'hu': str})
    zorf_huto_lnkhis_likp_df = pd.read_csv(f"{config.OUTPUT_PATH}zorf_huto_lnkhis_likp.csv", dtype={'hu': str})
    zorf_huto_lnkhis_vl06f_df = pd.read_csv(f"{config.OUTPUT_PATH}zorf_huto_lnkhis_vl06f.csv", dtype={'hu': str})
    
    # Read all ltap files
    ltap_likp_to_numbers_df = pd.read_csv(f"{config.OUTPUT_PATH}ltap_likp_to_numbers.csv")
    ltap_likp_to_numbers_two_df = pd.read_csv(f"{config.OUTPUT_PATH}ltap_likp_to_numbers_two.csv")
    ltap_vl06f_to_numbers_df = pd.read_csv(f"{config.OUTPUT_PATH}ltap_vl06f_to_numbers.csv")
    ltap_vl06f_to_numbers_two_df = pd.read_csv(f"{config.OUTPUT_PATH}ltap_vl06f_to_numbers_two.csv")
    
    # Combine all zorf files
    all_zorf_dfs = [
        zorf_hu_to_link_likp_df,
        zorf_hu_to_link_vl06f_df,
        zorf_huto_lnkhis_likp_df,
        zorf_huto_lnkhis_vl06f_df
    ]
    
    # Combine all ltap files
    all_ltap_dfs = [
        ltap_likp_to_numbers_df,
        ltap_likp_to_numbers_two_df,
        ltap_vl06f_to_numbers_df,
        ltap_vl06f_to_numbers_two_df
    ]
    
    # Create a mapping: hu (with leading zeros) -> set of (to_number, source_bin) tuples
    # This will help us quickly find all to_numbers and source_bins for a given HU
    hu_to_info = {}
    
    for zorf_df in all_zorf_dfs:
        for _, row in zorf_df.iterrows():
            hu = str(row['hu']).strip() if pd.notna(row['hu']) else ''
            to_number = row['to_number']
            source_bin = row['source_bin']
            
            if hu == '':
                continue
            
            if hu not in hu_to_info:
                hu_to_info[hu] = {'to_numbers': set(), 'source_bins': set()}
            
            if pd.notna(to_number):
                hu_to_info[hu]['to_numbers'].add(to_number)
            if pd.notna(source_bin):
                hu_to_info[hu]['source_bins'].add(source_bin)
    
    # Create a mapping: to_number -> list of confirmation_date values (to check if all have values)
    # We need to check ALL rows for each to_number in ALL ltap files
    to_number_to_confirmation_dates = {}
    
    for ltap_df in all_ltap_dfs:
        for _, row in ltap_df.iterrows():
            to_number = row['to_number']
            confirmation_date = row['confirmation_date']
            
            if pd.notna(to_number):
                if to_number not in to_number_to_confirmation_dates:
                    to_number_to_confirmation_dates[to_number] = []
                
                # Check if confirmation_date has a value (not NaN and not empty string)
                if pd.notna(confirmation_date) and str(confirmation_date).strip() != '':
                    to_number_to_confirmation_dates[to_number].append(True)
                else:
                    to_number_to_confirmation_dates[to_number].append(False)
    
    # Initialize result dictionary
    result = {}
    
    # Process vl06f_dashboard.csv
    for _, row in vl06f_df.iterrows():
        hu = str(row['hu']).strip() if pd.notna(row['hu']) else ''
        gi_date = row['gi_date']
        
        # Skip if hu is empty
        if hu == '':
            continue
        
        # Skip if gi_date is NaN or empty
        if pd.isna(gi_date) or gi_date == '':
            continue
        
        # Format date (assuming it's already in dd.mm.yyyy format, but ensure it is)
        try:
            if isinstance(gi_date, str):
                date_str = gi_date
            else:
                # If it's a datetime object, format it
                date_str = pd.to_datetime(gi_date).strftime("%d.%m.%Y")
        except:
            continue
        
        # Convert HU from vl06f format (without leading zeros) to zorf format (with leading zeros)
        # Add "00" prefix to match zorf files
        hu_with_zeros = f"00{hu}"
        
        # Find this HU in zorf files
        if hu_with_zeros not in hu_to_info:
            continue
        
        # Get all to_numbers for this HU
        to_numbers = hu_to_info[hu_with_zeros]['to_numbers']
        
        # Check if all to_numbers have confirmation_date in ALL their rows
        # If all to_numbers exist in ltap files AND all their rows have confirmation_date, it's picked
        # If any to_number is missing OR any row doesn't have confirmation_date, it's not_picked
        is_picked = True
        
        if len(to_numbers) == 0:
            # If no to_numbers found, we can't determine if it's picked
            continue
        
        for to_number in to_numbers:
            if to_number not in to_number_to_confirmation_dates:
                # If to_number not found in ltap files, it's not picked
                is_picked = False
                break
            
            # Check if ALL rows for this to_number have confirmation_date
            confirmation_statuses = to_number_to_confirmation_dates[to_number]
            if len(confirmation_statuses) == 0 or not all(confirmation_statuses):
                # If any row doesn't have confirmation_date, it's not picked
                is_picked = False
                break
        
        # Get floors from source_bins
        source_bins = hu_to_info[hu_with_zeros]['source_bins']
        floors = set()
        for source_bin in source_bins:
            floor_list = determine_floor(source_bin)
            floors.update(floor_list)
        
        # If no floors found, skip this HU
        if not floors:
            continue
        
        # Initialize date entry if not exists
        if date_str not in result:
            result[date_str] = {
                'ground_floor': {
                    'picked': {'amount_of_hu': set()},
                    'not_picked': {'amount_of_hu': set()}
                },
                'first_floor': {
                    'picked': {'amount_of_hu': set()},
                    'not_picked': {'amount_of_hu': set()}
                },
                'second_floor': {
                    'picked': {'amount_of_hu': set()},
                    'not_picked': {'amount_of_hu': set()}
                },
                'picked': {'amount_of_hu': set()},
                'not_picked': {'amount_of_hu': set()}
            }
        
        # Add this HU to each floor it belongs to
        picked_status = 'picked' if is_picked else 'not_picked'
        
        for floor in floors:
            result[date_str][floor][picked_status]['amount_of_hu'].add(hu)
        
        # Add to total count
        result[date_str][picked_status]['amount_of_hu'].add(hu)
    
    # Convert sets to counts
    for date_str in result:
        for floor in ['ground_floor', 'first_floor', 'second_floor']:
            result[date_str][floor]['picked']['amount_of_hu'] = len(result[date_str][floor]['picked']['amount_of_hu'])
            result[date_str][floor]['not_picked']['amount_of_hu'] = len(result[date_str][floor]['not_picked']['amount_of_hu'])
        
        result[date_str]['picked']['amount_of_hu'] = len(result[date_str]['picked']['amount_of_hu'])
        result[date_str]['not_picked']['amount_of_hu'] = len(result[date_str]['not_picked']['amount_of_hu'])
    
    # Save to JSON file
    output_path = f"{config.OUTPUT_PATH}hu_all_floors.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=4, ensure_ascii=False)

def create_lines_all_floors():
    # Read vl06f_dashboard.csv
    vl06f_df = pd.read_csv(f"{config.OUTPUT_PATH}vl06f_dashboard.csv")
    
    # Convert delivery to int (handle NaN values)
    vl06f_df["delivery"] = vl06f_df["delivery"].fillna(0).astype(int)
    
    # Read ltap_vl06f_to_numbers.csv (only this one file)
    ltap_vl06f_to_numbers_df = pd.read_csv(f"{config.OUTPUT_PATH}ltap_vl06f_to_numbers.csv")
    
    # Convert destination_bin to int to match with delivery
    ltap_vl06f_to_numbers_df["destination_bin"] = ltap_vl06f_to_numbers_df["destination_bin"].fillna(0).astype(int)
    
    # Get unique deliveries from vl06f_dashboard
    unique_deliveries = vl06f_df["delivery"].drop_duplicates()
    
    # Create a mapping: delivery -> gi_date from vl06f_dashboard
    # Each delivery should only have one date
    delivery_to_date = {}
    for _, row in vl06f_df.iterrows():
        delivery = int(row['delivery'])
        gi_date = row['gi_date']
        
        if delivery == 0:
            continue
        
        if pd.isna(gi_date) or gi_date == '':
            continue
        
        # Format date
        try:
            if isinstance(gi_date, str):
                date_str = gi_date
            else:
                date_str = pd.to_datetime(gi_date).strftime("%d.%m.%Y")
        except:
            continue
        
        # Store the date for this delivery
        if delivery not in delivery_to_date:
            delivery_to_date[delivery] = date_str
    
    # Initialize result dictionary
    result = {}
    
    # Process each unique delivery
    for delivery in unique_deliveries:
        if delivery == 0:
            continue
        
        # Get date for this delivery
        if delivery not in delivery_to_date:
            continue
        
        date_str = delivery_to_date[delivery]
        
        # Find all rows in ltap file where destination_bin matches this delivery
        matching_rows = ltap_vl06f_to_numbers_df[ltap_vl06f_to_numbers_df["destination_bin"] == delivery]
        
        if len(matching_rows) == 0:
            continue
        
        # Initialize date entry if not exists
        if date_str not in result:
            result[date_str] = {
                'ground_floor': {
                    'picked': {'amount_of_lines': 0},
                    'not_picked': {'amount_of_lines': 0}
                },
                'first_floor': {
                    'picked': {'amount_of_lines': 0},
                    'not_picked': {'amount_of_lines': 0}
                },
                'second_floor': {
                    'picked': {'amount_of_lines': 0},
                    'not_picked': {'amount_of_lines': 0}
                },
                'picked': {'amount_of_lines': 0},
                'not_picked': {'amount_of_lines': 0}
            }
        
        # Process each row individually
        for _, row in matching_rows.iterrows():
            source_bin = row['source_bin']
            confirmation_date = row['confirmation_date']
            
            # Determine floor from source_bin
            floors = determine_floor(source_bin)
            
            # If no floors found, skip this row
            if not floors:
                continue
            
            # Check if confirmation_date has a value (empty string = not_picked, same as NaN/None)
            is_picked = pd.notna(confirmation_date) and str(confirmation_date).strip() != ''
            picked_status = 'picked' if is_picked else 'not_picked'
            
            # Count this line for each floor it belongs to
            for floor in floors:
                result[date_str][floor][picked_status]['amount_of_lines'] += 1
            
            # Count in total
            result[date_str][picked_status]['amount_of_lines'] += 1
    
    # Save to JSON file
    output_path = f"{config.OUTPUT_PATH}lines_all_floors.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=4, ensure_ascii=False)

def create_deliveries_all_floors_pgi():
    # Today's date
    today = datetime.now().strftime("%d.%m.%Y")
    
    # Read likp_dashboard.csv
    likp_df = pd.read_csv(f"{config.OUTPUT_PATH}likp_dashboard.csv")
    
    # Convert delivery to int (handle NaN values)
    likp_df["delivery"] = likp_df["delivery"].fillna(0).astype(int)
    
    # Get unique deliveries from likp_dashboard.csv
    unique_deliveries = set(likp_df["delivery"].drop_duplicates())
    
    # Remove 0 deliveries
    unique_deliveries.discard(0)
    
    # Read zorf files
    zorf_hu_to_link_likp_df = pd.read_csv(f"{config.OUTPUT_PATH}zorf_hu_to_link_likp.csv")
    zorf_huto_lnkhis_likp_df = pd.read_csv(f"{config.OUTPUT_PATH}zorf_huto_lnkhis_likp.csv")
    
    # Convert delivery to int in zorf files
    zorf_hu_to_link_likp_df["delivery"] = zorf_hu_to_link_likp_df["delivery"].fillna(0).astype(int)
    zorf_huto_lnkhis_likp_df["delivery"] = zorf_huto_lnkhis_likp_df["delivery"].fillna(0).astype(int)
    
    # Combine zorf files
    all_zorf_dfs = [
        zorf_hu_to_link_likp_df,
        zorf_huto_lnkhis_likp_df
    ]
    
    # Create a dictionary to store delivery -> set of floors
    delivery_to_floors = {}
    
    # Process each zorf file
    for zorf_df in all_zorf_dfs:
        for _, row in zorf_df.iterrows():
            delivery = int(row['delivery'])
            source_bin = row['source_bin']
            
            # Skip if delivery is 0
            if delivery == 0:
                continue
            
            floors = determine_floor(source_bin)
            
            if delivery not in delivery_to_floors:
                delivery_to_floors[delivery] = set()
            
            delivery_to_floors[delivery].update(floors)
    
    # Initialize result dictionary
    result = {
        today: {
            'ground_floor': {'amount_of_deliveries_pgi': set()},
            'first_floor': {'amount_of_deliveries_pgi': set()},
            'second_floor': {'amount_of_deliveries_pgi': set()},
            'amount_of_deliveries_pgi': set()
        }
    }
    
    # Process each unique delivery from likp_dashboard.csv
    for delivery in unique_deliveries:
        # Get floors for this delivery from zorf files
        floors = delivery_to_floors.get(delivery, set())
        
        # If no floors found, skip this delivery
        if not floors:
            continue
        
        # Add this delivery to each floor it belongs to
        for floor in floors:
            result[today][floor]['amount_of_deliveries_pgi'].add(delivery)
        
        # Add to total count (unique deliveries across all floors)
        result[today]['amount_of_deliveries_pgi'].add(delivery)
    
    # Convert sets to counts
    result[today]['ground_floor']['amount_of_deliveries_pgi'] = len(result[today]['ground_floor']['amount_of_deliveries_pgi'])
    result[today]['first_floor']['amount_of_deliveries_pgi'] = len(result[today]['first_floor']['amount_of_deliveries_pgi'])
    result[today]['second_floor']['amount_of_deliveries_pgi'] = len(result[today]['second_floor']['amount_of_deliveries_pgi'])
    result[today]['amount_of_deliveries_pgi'] = len(result[today]['amount_of_deliveries_pgi'])
    
    # Save to JSON file
    output_path = f"{config.OUTPUT_PATH}deliveries_all_floors_pgi.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=4, ensure_ascii=False)

def create_hu_all_floors_pgi():
    # Today's date
    today = datetime.now().strftime("%d.%m.%Y")
    
    # Read zorf files with dtype str for hu column
    zorf_hu_to_link_likp_df = pd.read_csv(f"{config.OUTPUT_PATH}zorf_hu_to_link_likp.csv", dtype={'hu': str})
    zorf_huto_lnkhis_likp_df = pd.read_csv(f"{config.OUTPUT_PATH}zorf_huto_lnkhis_likp.csv", dtype={'hu': str})
    
    # Combine zorf files
    all_zorf_dfs = [
        zorf_hu_to_link_likp_df,
        zorf_huto_lnkhis_likp_df
    ]
    
    # Create a dictionary to store hu -> set of floors
    hu_to_floors = {}
    
    # Process each zorf file
    for zorf_df in all_zorf_dfs:
        for _, row in zorf_df.iterrows():
            hu = str(row['hu']).strip() if pd.notna(row['hu']) else ''
            source_bin = row['source_bin']
            
            # Skip if hu is empty
            if hu == '':
                continue
            
            floors = determine_floor(source_bin)
            
            if hu not in hu_to_floors:
                hu_to_floors[hu] = set()
            
            hu_to_floors[hu].update(floors)
    
    # Initialize result dictionary
    result = {
        today: {
            'ground_floor': {'amount_of_hu_pgi': set()},
            'first_floor': {'amount_of_hu_pgi': set()},
            'second_floor': {'amount_of_hu_pgi': set()},
            'amount_of_hu_pgi': set()
        }
    }
    
    # Process each unique HU
    for hu, floors in hu_to_floors.items():
        # If no floors found, skip this HU
        if not floors:
            continue
        
        # Add this HU to each floor it belongs to
        for floor in floors:
            result[today][floor]['amount_of_hu_pgi'].add(hu)
        
        # Add to total count (unique HUs across all floors)
        result[today]['amount_of_hu_pgi'].add(hu)
    
    # Convert sets to counts
    result[today]['ground_floor']['amount_of_hu_pgi'] = len(result[today]['ground_floor']['amount_of_hu_pgi'])
    result[today]['first_floor']['amount_of_hu_pgi'] = len(result[today]['first_floor']['amount_of_hu_pgi'])
    result[today]['second_floor']['amount_of_hu_pgi'] = len(result[today]['second_floor']['amount_of_hu_pgi'])
    result[today]['amount_of_hu_pgi'] = len(result[today]['amount_of_hu_pgi'])
    
    # Save to JSON file
    output_path = f"{config.OUTPUT_PATH}hu_all_floors_pgi.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=4, ensure_ascii=False)

def create_lines_all_floors_pgi():
    # Today's date
    today = datetime.now().strftime("%d.%m.%Y")
    
    # Read zorf files
    zorf_hu_to_link_likp_df = pd.read_csv(f"{config.OUTPUT_PATH}zorf_hu_to_link_likp.csv")
    zorf_huto_lnkhis_likp_df = pd.read_csv(f"{config.OUTPUT_PATH}zorf_huto_lnkhis_likp.csv")
    
    # Combine zorf files
    all_zorf_dfs = [
        zorf_hu_to_link_likp_df,
        zorf_huto_lnkhis_likp_df
    ]
    
    # Initialize result dictionary
    result = {
        today: {
            'ground_floor': {'amount_of_lines_pgi': 0},
            'first_floor': {'amount_of_lines_pgi': 0},
            'second_floor': {'amount_of_lines_pgi': 0},
            'amount_of_lines_pgi': 0
        }
    }
    
    # Process each row (each row represents a line)
    for zorf_df in all_zorf_dfs:
        for _, row in zorf_df.iterrows():
            source_bin = row['source_bin']
            
            # Determine floor from source_bin
            floors = determine_floor(source_bin)
            
            # If no floors found, skip this row
            if not floors:
                continue
            
            # Count this line for each floor it belongs to
            for floor in floors:
                result[today][floor]['amount_of_lines_pgi'] += 1
            
            # Count in total (each row is counted once in total, regardless of how many floors it belongs to)
            result[today]['amount_of_lines_pgi'] += 1
    
    # Save to JSON file
    output_path = f"{config.OUTPUT_PATH}lines_all_floors_pgi.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=4, ensure_ascii=False)

def create_picking_hourly_dashboard():
    # Read bflow_routes.csv to get valid routes
    bflow_routes_df = pd.read_csv(f"{config.OUTPUT_PATH}bflow_routes.csv")
    valid_routes = set(bflow_routes_df['route'].str.strip().str.upper())
    
    # Read picking_productivity_huto_lnkhis.csv and picking_productivity_hu_to_link.csv
    # Create a mapping: document -> route
    huto_lnkhis_df = pd.read_csv(f"{config.OUTPUT_PATH}picking_productivity_huto_lnkhis.csv")
    hu_to_link_df = pd.read_csv(f"{config.OUTPUT_PATH}picking_productivity_hu_to_link.csv")
    
    # Combine both dataframes and create document -> route mapping
    # Convert document to string/numeric for matching
    document_to_route = {}
    
    for _, row in huto_lnkhis_df.iterrows():
        document = row['document']
        route = str(row['route']).strip().upper() if pd.notna(row['route']) else ''
        if pd.notna(document) and route:
            # Convert document to same type as destination_bin (likely int or float)
            doc_value = int(float(document)) if pd.notna(document) else None
            if doc_value is not None:
                document_to_route[doc_value] = route
    
    for _, row in hu_to_link_df.iterrows():
        document = row['document']
        route = str(row['route']).strip().upper() if pd.notna(row['route']) else ''
        if pd.notna(document) and route:
            doc_value = int(float(document)) if pd.notna(document) else None
            if doc_value is not None:
                # Only add if not already present (or update if needed)
                document_to_route[doc_value] = route
    
    # Read picking_productivity_ltap.csv
    ltap_df = pd.read_csv(f"{config.OUTPUT_PATH}picking_productivity_ltap.csv")
    
    # Initialize result dictionary
    result = {}
    
    # Process each row in ltap_df
    for _, row in ltap_df.iterrows():
        destination_bin = row['destination_bin']
        confirmation_time = row['confirmation_time']
        
        # Skip if destination_bin is NaN or empty
        if pd.isna(destination_bin):
            continue
        
        # Convert destination_bin to int for matching
        try:
            dest_bin_value = int(float(destination_bin))
        except (ValueError, TypeError):
            continue
        
        # Look up route in document_to_route mapping
        if dest_bin_value not in document_to_route:
            continue
        
        route = document_to_route[dest_bin_value]
        
        # Check if route is in valid_routes
        if route not in valid_routes:
            continue
        
        # Extract hour from confirmation_time (format: HH:MM:SS)
        if pd.isna(confirmation_time) or confirmation_time == '':
            continue
        
        try:
            # Parse time string
            time_str = str(confirmation_time).strip()
            if ':' not in time_str:
                continue
            
            # Split by colon to get hours and minutes
            time_parts = time_str.split(':')
            if len(time_parts) < 2:
                continue
            
            hour = int(time_parts[0])
            minute = int(time_parts[1])
            
            # Group into 30-minute intervals
            # If minute < 30, use HH00, else use HH30
            if minute < 30:
                hour_key = f"{hour:02d}00"
            else:
                hour_key = f"{hour:02d}30"
            
            # Initialize hour entry if not exists
            if hour_key not in result:
                result[hour_key] = {'lines_picked': 0}
            
            # Count this line
            result[hour_key]['lines_picked'] += 1
            
        except (ValueError, IndexError, TypeError):
            continue
    
    # Sort by hour key for better readability
    sorted_result = dict(sorted(result.items()))
    
    # Save to JSON file
    output_path = f"{config.OUTPUT_PATH}picking_hourly_dashboard.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(sorted_result, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    """extract_vl06f_for_dashboard()
    print('1')
    convert_vl06f_for_dashboard()
    print('2')
    extract_bflow_routes()
    print('3')
    extract_likp_for_dashboard()
    print('4')
    convert_likp_for_dashboard()
    print('5')
    extract_deliveries_from_vl06f_for_dashboard()
    print('6')
    extract_deliveries_from_likp_for_dashboard()
    print('7')
    extract_zorf_huto_link_vl06f()
    print('8')
    extract_zorf_huto_link_likp()
    print('9')
    convert_zorf_huto_link_for_dashboard()
    print('10')
    extract_to_number_from_zorf_huto_link_for_dashboard()
    print('11')
    extract_ltap_from_to_numbers("hu_to_link_likp_to_numbers.csv", "ltap_likp_to_numbers")
    print('12')
    extract_ltap_from_to_numbers("hu_to_link_vl06f_to_numbers.csv", "ltap_vl06f_to_numbers")
    print('13')
    extract_ltap_from_to_numbers("huto_lnkhis_likp_to_numbers.csv", "ltap_likp_to_numbers_two")
    print('14')
    extract_ltap_from_to_numbers("huto_lnkhis_vl06f_to_numbers.csv", "ltap_vl06f_to_numbers_two")
    print('15')
    convert_ltap_to_numbers()
    print('16')
    create_deliveries_all_floors()
    print('17')
    create_hu_all_floors()
    print('18')
    create_lines_all_floors()
    print('19')
    create_deliveries_all_floors_pgi()
    print('20')
    create_hu_all_floors_pgi()
    print('21')
    create_lines_all_floors_pgi()
    print('22')"""
    create_picking_hourly_dashboard()