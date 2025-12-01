import data_extraction.config.config as config
from data_extraction.utils.sapsession import SAPSession
from datetime import datetime

def extract_cdhdr():
    # TODAY'S DATE & TIME
    today = datetime.now().strftime("%d.%m.%Y")

    # INITIALIZE SAP SESSION
    extractor = SAPSession()

    # START TRANSACTION & CONFIGURE
    extractor.StartTransaction("Z_TABU_DIS")
    extractor.enter_table("CDHDR")
    extractor.checkbox_selection(config.CDHDR_CHECKBOX_SELECTIONS)
    extractor.findById('wnd[0]/usr/ctxtI5-LOW').text = today
    extractor.findById("wnd[0]/usr/ctxtI7-LOW").text = "ZORF_BOX_CLOSING"
    extractor.findById("wnd[0]/usr/btn%_I4_%_APP_%-VALU_PUSH").press()
    extractor.findById("wnd[1]/tbar[0]/btn[23]").press()
    extractor.findById("wnd[2]/usr/ctxtDY_PATH").text = config.OUTPUT_PATH
    extractor.findById("wnd[2]/usr/ctxtDY_FILENAME").text = "users.csv"
    extractor.findById("wnd[2]/tbar[0]/btn[0]").press()
    extractor.findById("wnd[1]/tbar[0]/btn[8]").press()
    extractor.findById("wnd[0]/tbar[1]/btn[8]").press()

    # SAVE
    extractor.save_to_folder("cdhdr")