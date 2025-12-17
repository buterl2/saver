from typing import Any
from data_script.utils.SAP import SAPSession
import data_script.config.constants as constant
from data_script.utils.logger import setup_logger
from data_script.utils.retry import retry_sap_operation

# Set up logger
logger = setup_logger("dashboard_extraction")

def _extract_vl06f_internal(folder: str, filename: str) -> None:
    """Internal extraction function (called by retry wrapper)"""
    logger.info(f"Starting VL06F extraction for dashboard, filename: {filename}, folder: {folder}")

    # Initialize SAP
    extractor = SAPSession()

    # Start transaction & configure it
    extractor.StartTransaction("VL06F")
    extractor.vl06f_dashboard(constant.VARIANT_VL06F_DASHBOARD)
    logger.info("Transaction executed successfully")

    # Save to folder
    extractor.save_to_folder(folder, filename)
    logger.info(f"Data saved to {filename}")

def extract_vl06f_for_dashboard(folder: str, filename: str) -> None:
    """
    Extract VL06F data for dashboard with automatic retry
    
    Args:
        folder: Output folder
        filename: Output filename
    """
    retry_sap_operation(
        lambda: _extract_vl06f_internal(folder, filename),
        func_name="extract_vl06f_for_dashboard"
    )

def _extract_likp_internal(folder: str, filename: str) -> None:
    """Internal extraction function (called by retry wrapper)"""
    logger.info(f"Starting LIKP extraction for dashboard, filename: {filename}, folder: {folder}")

    # Get today's date at function execution time
    # This captures the date when extraction starts, not when the scheduler started
    # get_today() calls datetime.now() each time, so it's always current
    today = constant.get_today()

    # Initialize SAP
    extractor = SAPSession()

    # Start transaction & configure it
    extractor.StartTransaction("Z_TABU_DIS")
    extractor.table("LIKP")
    extractor.checkbox_selection(constant.LIKP_CHECKBOX)
    extractor.findById("wnd[0]/usr/btn%_I6_%_APP_%-VALU_PUSH").press()
    extractor.findById("wnd[1]/tbar[0]/btn[23]").press()
    extractor.findById("wnd[2]/usr/ctxtDY_PATH").text = f"{constant.OUTPUT_PATH}/misc"
    extractor.findById("wnd[2]/usr/ctxtDY_FILENAME").text = "bflow_routes.csv"
    extractor.findById("wnd[2]/usr/ctxtDY_FILENAME").caretPosition = 16
    extractor.findById("wnd[2]/tbar[0]/btn[0]").press()
    extractor.findById("wnd[1]/tbar[0]/btn[8]").press()
    extractor.findById("wnd[0]/usr/ctxtI8-LOW").text = str(constant.WAREHOUSE)
    extractor.findById("wnd[0]/usr/ctxtI9-LOW").text = today
    extractor.findById("wnd[0]/usr/ctxtI9-LOW").setFocus()
    extractor.findById("wnd[0]/usr/ctxtI9-LOW").caretPosition = 10
    extractor.findById("wnd[0]").sendVKey(0)
    extractor.findById("wnd[0]/tbar[1]/btn[8]").press()
    logger.info("Transaction executed successfully")

    # Save to folder
    extractor.save_to_folder(folder, filename)
    logger.info(f"Data saved to {filename}")

def extract_likp_for_dashboard(folder: str, filename: str) -> None:
    """
    Extract LIKP data for dashboard with automatic retry
    
    Args:
        folder: Output folder
        filename: Output filename
    """
    retry_sap_operation(
        lambda: _extract_likp_internal(folder, filename),
        func_name="extract_likp_for_dashboard"
    )

def _extract_zorf_huto_link_internal(transaction: str, input_file: str, folder: str, filename: str) -> None:
    """Internal extraction function (called by retry wrapper)"""
    logger.info(f"Starting {transaction} extraction, input_file: {input_file}, filename: {filename}, folder: {folder}")

    # Initialize SAP
    extractor = SAPSession()

    # Start transaction & configure it
    extractor.StartTransaction("Z_TABU_DIS")
    extractor.table(transaction)
    extractor.checkbox_selection(constant.HUTOLINK_CHECKBOX)
    extractor.findById('wnd[0]/usr/ctxtI1-LOW').text = str(constant.WAREHOUSE)
    extractor.findById("wnd[0]/usr/btn%_I5_%_APP_%-VALU_PUSH").press()
    extractor.findById("wnd[1]/tbar[0]/btn[23]").press()
    extractor.findById("wnd[2]/usr/ctxtDY_PATH").text = f"{constant.OUTPUT_PATH}/{folder}"
    extractor.findById("wnd[2]/usr/ctxtDY_FILENAME").text = input_file
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
    logger.info("Transaction executed successfully")

    # Save to folder
    extractor.save_to_folder(folder, filename)
    logger.info(f"Data saved to {filename}")

def extract_zorf_huto_link(transaction: str, input_file: str, folder: str, filename: str) -> None:
    """
    Extract ZORF HUTO LINK data for dashboard with automatic retry
    
    Args:
        transaction: Transaction name
        input_file: Input filename for delivery selection
        folder: Output folder
        filename: Output filename
    """
    retry_sap_operation(
        lambda: _extract_zorf_huto_link_internal(transaction, input_file, folder, filename),
        func_name="extract_zorf_huto_link"
    )

def _extract_ltap_from_to_numbers_internal(file: str, folder: str, filename: str) -> None:
    """Internal extraction function (called by retry wrapper)"""
    logger.info(f"Starting LTAP extraction from TO numbers, file: {file}, filename: {filename}, folder: {folder}")

    # Initialize SAP
    extractor = SAPSession()

    # Start transaction & configure it
    extractor.StartTransaction("Z_TABU_DIS")
    extractor.table("LTAP")
    extractor.checkbox_selection(constant.LTAP_CHECKBOX)
    extractor.findById("wnd[0]/usr/ctxtI1-LOW").text = str(constant.WAREHOUSE)
    extractor.findById("wnd[0]/usr/ctxtI1-LOW").caretPosition = 3
    extractor.findById("wnd[0]/usr/btn%_I2_%_APP_%-VALU_PUSH").press()
    extractor.findById("wnd[1]/tbar[0]/btn[23]").press()
    extractor.findById("wnd[2]/usr/ctxtDY_PATH").text = f"{constant.OUTPUT_PATH}/{folder}"
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
    logger.info("Transaction executed successfully")

    # Save to folder
    extractor.save_to_folder(folder, filename)
    logger.info(f"Data saved to {filename}")

def extract_ltap_from_to_numbers(file: str, folder: str, filename: str) -> None:
    """
    Extract LTAP data from TO numbers for dashboard with automatic retry
    
    Args:
        file: Input file with TO numbers
        folder: Output folder
        filename: Output filename
    """
    retry_sap_operation(
        lambda: _extract_ltap_from_to_numbers_internal(file, folder, filename),
        func_name="extract_ltap_from_to_numbers"
    )

