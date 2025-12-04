import data_extraction.config.config as config
from data_extraction.utils.sapsession import SAPSession
from datetime import datetime

def extract_likp():
    # TODAY'S DATE & TIME
    today = datetime.now().strftime("%d.%m.%Y")

    # INITIALIZE SAP SESSION
    extractor = SAPSession()

    # START TRANSACTION & CONFIGURE
    extractor.StartTransaction("Z_TABU_DIS")
    extractor.enter_table("LIKP")
    extractor.get_variant_name(config.VARIANT_NAME)
    extractor.findById("wnd[0]/usr/ctxtI7-LOW").text = today
    extractor.findById("wnd[0]/tbar[1]/btn[8]").press()

    # SAVE
    extractor.save_to_folder("likp")