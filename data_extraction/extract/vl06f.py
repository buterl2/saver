import data_extraction.config.config as config
from data_extraction.utils.sapsession import SAPSession
from datetime import datetime

def extract_vl06f():
    # INITIALIZE SAP SESSION
    extractor = SAPSession()

    # START TRANSACTION & CONFIGURE
    extractor.StartTransaction("VL06F")
    extractor.get_variant_user(config.VARIANT_USER)
    extractor.findById("wnd[0]/tbar[1]/btn[8]").press()
    extractor.findById("wnd[0]/usr/cntlGRID1/shellcont/shell").setCurrentCell(-1,"WADAT")
    extractor.findById("wnd[0]/usr/cntlGRID1/shellcont/shell").selectColumn("WADAT")
    extractor.findById("wnd[0]/tbar[1]/btn[40]").press()

    # SAVE
    extractor.save_to_folder("vl06f")