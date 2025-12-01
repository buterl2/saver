from data_extraction.utils.sapsession import SAPSession
import time

def keep_alive():
    alive = SAPSession()
    alive.StartTransaction('Z_TABU_DIS')
    time.sleep(120)