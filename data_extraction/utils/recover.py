from data_extraction.utils.sapsession import SAPSession
from data_extraction.utils import default_logger as logger

def recover_from_error():
    try:
        recover = SAPSession()
        for i in range(3):
            try:
                recover.findById("wnd[0]/tbar[0]/btn[3]").press()
            except:
                break
    except Exception as e:
        logger.warning(f"Recovery failed: {e}")