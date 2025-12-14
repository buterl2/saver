from data_extraction.utils.sapsession import SAPSession
import time
from typing import Any

def keep_alive() -> None:
    alive = SAPSession()
    alive.StartTransaction('Z_TABU_DIS')
    time.sleep(120)