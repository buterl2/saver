from datetime import datetime
from data_extraction.transform.routes import transform_routes
from data_extraction.extract.ltap import extract_ltap
from data_extraction.transform.ltap import retrieve_deliveries, transform_ltap
from data_extraction.extract.hutolink import extract_hu_to_link, extract_huto_lnkhis
from data_extraction.extract.cdhdr import extract_cdhdr
from data_extraction.transform.hutolink import hu_to_link, huto_lnkhis
from data_extraction.transform.cdhdr import transform_cdhdr, cdhdr
from data_extraction.utils.keep_alive import keep_alive
from data_extraction.utils.retry import retry
from data_extraction.extract.vl06f import extract_vl06f
from data_extraction.transform.vl06f import vl06f
from data_extraction.extract.likp import extract_likp
from data_extraction.transform.likp import likp
from data_extraction.extract.hutolink_dashboard import hutolink_dashboard
from data_extraction.transform.hutolink_dashboard import hutolink_dashboard_transform

if __name__ == "__main__":
    while True:
        current_time = datetime.now().strftime('%H:%M:%S')
        current_day = datetime.now().weekday()

        # Check if it's a weekday (Monday-Friday) and within working hours
        if current_day < 5 and current_time > '08:00:00' and current_time < '23:30:00':
            retry(transform_routes)
            retry(extract_ltap)
            retry(retrieve_deliveries)
            retry(extract_hu_to_link)
            retry(extract_huto_lnkhis)
            retry(extract_cdhdr)
            retry(hu_to_link)
            retry(huto_lnkhis)
            retry(transform_ltap)
            retry(cdhdr)
            retry(transform_cdhdr)
            retry(extract_vl06f)
            retry(extract_likp)
            retry(likp)
            retry(vl06f)
            retry(hutolink_dashboard)
            retry(hutolink_dashboard_transform)
        else:
            retry(keep_alive)