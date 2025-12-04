import data_extraction.config.config as config
from data_extraction.utils.sapsession import SAPSession
from datetime import datetime

def extract_ltap_dashboard():

    # INITIALIZE SAP SESSION
    extractor = SAPSession()

    # START TRANSACTION & CONFIGURE
    extractor.StartTransaction("Z_TABU_DIS")
    extractor.enter_table("LTAP")
    extractor.checkbox_selection(config.LTAP_CHECKBOX_SELECTIONS)
    extractor.findById("wnd[0]/usr/ctxtI1-LOW").text = config.WAREHOUSE
    extractor.findById("wnd[0]/usr/btn%_I2_%_APP_%-VALU_PUSH").press()
    extractor.findById("wnd[1]/tbar[0]/btn[23]").press()
    extractor.findById("wnd[2]/usr/ctxtDY_FILENAME").text = "to_numbers.csv"
    extractor.findById("wnd[2]/usr/ctxtDY_FILENAME").caretPosition = 14
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

    # SAVE
    extractor.save_to_folder("ltap_dashboard")