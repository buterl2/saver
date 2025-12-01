import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # Data folder configuration
    path_to_data = os.getenv("PATH_TO_DATA", "C:/Users/buterl2/OneDrive - Medtronic PLC/Desktop/newDash/data_extraction/data")

    # CORS configuration
    _cors_origins_str = os.getenv("CORS_ORIGINS", "*")
    cors_origins = _cors_origins_str.split(",") if _cors_origins_str else ["*"]

    # Printer configuration
    printer_ground_floor_ip = os.getenv("PRINTER_GROUND_FLOOR_IP", "")
    printer_1st_floor_ip = os.getenv("PRINTER_1ST_FLOOR_IP", "")
    printer_2nd_floor_ip = os.getenv("PRINTER_2ND_FLOOR_IP", "")
    printer_port = int(os.getenv("PRINTER_PORT", "0")) if os.getenv("PRINTER_PORT") else 0

    # Retry configuration
    file_load_retries = int(os.getenv("FILE_LOAD_RETRIES", "3"))
    file_load_retry_delay = float(os.getenv("FILE_LOAD_RETRY_DELAY", "1.0"))

    # Socket timeout configuration
    socket_timeout = float(os.getenv("SOCKET_TIMEOUT", "0.0"))

    # Label configuration
    label_width = int(os.getenv("LABEL_WIDTH", "0"))

    @property
    def printers_ip(self):
        return {
            "Ground Floor": self.printer_ground_floor_ip,
            "1st Floor": self.printer_1st_floor_ip,
            "2nd Floor": self.printer_2nd_floor_ip
        }

settings = Settings()