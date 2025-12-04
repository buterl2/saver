from data_extraction.utils.sapsession import SAPSession
import data_extraction.config.config as config

def extract_hu_to_link():
    # INITIALIZE SAP SESSION
    extractor = SAPSession()

    # START TRANSACTION & CONFIGURE
    extractor.StartTransaction("Z_TABU_DIS")
    extractor.enter_table("ZORF_HU_TO_LINK")
    extractor.checkbox_selection(config.HUTOLINK_CHECKBOX_SELECTIONS)
    extractor.findById('wnd[0]/usr/ctxtI1-LOW').text = config.WAREHOUSE
    extractor.findById("wnd[0]/usr/btn%_I5_%_APP_%-VALU_PUSH").press()
    extractor.findById("wnd[1]/tbar[0]/btn[23]").press()
    extractor.findById("wnd[2]/usr/ctxtDY_FILENAME").text = "deliveries_likp.csv"
    extractor.findById("wnd[2]/usr/ctxtDY_FILENAME").caretPosition = 15
    extractor.findById("wnd[2]/tbar[0]/btn[0]").press()
    extractor.findById("wnd[1]/tbar[0]/btn[8]").press()
    extractor.findById("wnd[0]/tbar[1]/btn[8]").press()
    extractor.findById("wnd[0]/tbar[1]/btn[32]").press()
    extractor.findById("wnd[1]/usr/tabsG_TS_ALV/tabpALV_M_R1/ssubSUB_DYN0510:SAPLSKBH:0620/cntlCONTAINER2_LAYO/shellcont/shell").selectedRows = "0"
    extractor.findById("wnd[1]/usr/tabsG_TS_ALV/tabpALV_M_R1/ssubSUB_DYN0510:SAPLSKBH:0620/btnAPP_FL_SING").press()
    extractor.findById("wnd[1]/usr/tabsG_TS_ALV/tabpALV_M_R1/ssubSUB_DYN0510:SAPLSKBH:0620/cntlCONTAINER2_LAYO/shellcont/shell").selectedRows = "0"
    extractor.findById("wnd[1]/usr/tabsG_TS_ALV/tabpALV_M_R1/ssubSUB_DYN0510:SAPLSKBH:0620/btnAPP_FL_SING").press()
    extractor.findById("wnd[1]/usr/tabsG_TS_ALV/tabpALV_M_R1/ssubSUB_DYN0510:SAPLSKBH:0620/cntlCONTAINER1_LAYO/shellcont/shell").currentCellRow = 5
    extractor.findById("wnd[1]/usr/tabsG_TS_ALV/tabpALV_M_R1/ssubSUB_DYN0510:SAPLSKBH:0620/cntlCONTAINER1_LAYO/shellcont/shell").selectedRows = "5"
    extractor.findById("wnd[1]/usr/tabsG_TS_ALV/tabpALV_M_R1/ssubSUB_DYN0510:SAPLSKBH:0620/btnAPP_WL_SING").press()
    extractor.findById("wnd[1]/tbar[0]/btn[0]").press()

    # SAVE
    extractor.save_to_folder("hu_to_link_likp_hu_dashboard")

def extract_huto_lnkhis():
    # INITIALIZE SAP SESSION
    extractor = SAPSession()

    # START TRANSACTION & CONFIGURE
    extractor.StartTransaction("Z_TABU_DIS")
    extractor.enter_table("ZORF_HUTO_LNKHIS")
    extractor.checkbox_selection(config.HUTOLINK_CHECKBOX_SELECTIONS)
    extractor.findById('wnd[0]/usr/ctxtI1-LOW').text = config.WAREHOUSE
    extractor.findById("wnd[0]/usr/btn%_I5_%_APP_%-VALU_PUSH").press()
    extractor.findById("wnd[1]/tbar[0]/btn[23]").press()
    extractor.findById("wnd[2]/usr/ctxtDY_FILENAME").text = "deliveries_likp.csv"
    extractor.findById("wnd[2]/usr/ctxtDY_FILENAME").caretPosition = 19
    extractor.findById("wnd[2]/tbar[0]/btn[0]").press()
    extractor.findById("wnd[1]/tbar[0]/btn[8]").press()
    extractor.findById("wnd[0]/tbar[1]/btn[8]").press()
    extractor.findById("wnd[0]/tbar[1]/btn[32]").press()
    extractor.findById("wnd[1]/usr/tabsG_TS_ALV/tabpALV_M_R1/ssubSUB_DYN0510:SAPLSKBH:0620/cntlCONTAINER2_LAYO/shellcont/shell").selectedRows = "0"
    extractor.findById("wnd[1]/usr/tabsG_TS_ALV/tabpALV_M_R1/ssubSUB_DYN0510:SAPLSKBH:0620/btnAPP_FL_SING").press()
    extractor.findById("wnd[1]/usr/tabsG_TS_ALV/tabpALV_M_R1/ssubSUB_DYN0510:SAPLSKBH:0620/cntlCONTAINER2_LAYO/shellcont/shell").selectedRows = "0"
    extractor.findById("wnd[1]/usr/tabsG_TS_ALV/tabpALV_M_R1/ssubSUB_DYN0510:SAPLSKBH:0620/btnAPP_FL_SING").press()
    extractor.findById("wnd[1]/usr/tabsG_TS_ALV/tabpALV_M_R1/ssubSUB_DYN0510:SAPLSKBH:0620/cntlCONTAINER1_LAYO/shellcont/shell").currentCellRow = 5
    extractor.findById("wnd[1]/usr/tabsG_TS_ALV/tabpALV_M_R1/ssubSUB_DYN0510:SAPLSKBH:0620/cntlCONTAINER1_LAYO/shellcont/shell").selectedRows = "5"
    extractor.findById("wnd[1]/usr/tabsG_TS_ALV/tabpALV_M_R1/ssubSUB_DYN0510:SAPLSKBH:0620/btnAPP_WL_SING").press()
    extractor.findById("wnd[1]/tbar[0]/btn[0]").press()

    # SAVE
    extractor.save_to_folder("huto_lnkhis_likp_hu_dashboard")

def hutolink_dashboard():
    extract_hu_to_link()
    extract_huto_lnkhis()