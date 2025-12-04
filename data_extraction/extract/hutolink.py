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
    extractor.findById("wnd[2]/usr/ctxtDY_PATH").text = config.OUTPUT_PATH
    extractor.findById("wnd[2]/usr/ctxtDY_FILENAME").text = "deliveries.csv"
    extractor.findById("wnd[2]/tbar[0]/btn[0]").press()
    extractor.findById("wnd[1]/tbar[0]/btn[8]").press()
    extractor.findById("wnd[0]/tbar[1]/btn[8]").press()

    # SAVE
    extractor.save_to_folder("hu_to_link")

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
    extractor.findById("wnd[2]/usr/ctxtDY_PATH").text = config.OUTPUT_PATH
    extractor.findById("wnd[2]/usr/ctxtDY_FILENAME").text = "deliveries.csv"
    extractor.findById("wnd[2]/tbar[0]/btn[0]").press()
    extractor.findById("wnd[1]/tbar[0]/btn[8]").press()
    extractor.findById("wnd[0]/tbar[1]/btn[8]").press()

    # SAVE
    extractor.save_to_folder("huto_lnkhis")