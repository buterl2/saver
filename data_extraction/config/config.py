from pathlib import Path
import os
from dotenv import load_dotenv

project_root = Path(__file__).parent.parent.parent
env_path = project_root / ".env"
load_dotenv(dotenv_path=env_path, override=True)

# CHECKBOX SELECTIONS
LTAP_CHECKBOX_SELECTIONS = [
    (5, [0, 1, 2, 5, 6, 7]),
    (21, [4, 6, 18, 19, 20]),
    (20, [13, 14, 15, 17]),
    (17, [6, 7, 8]),
    (8, [20]),
    (20, []),
    (20, [9]),
    (9, [17]),
    (17, [16, 17])
]
HUTOLINK_CHECKBOX_SELECTIONS = [
    (5, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 21]),
    (14, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20])
]
CDHDR_CHECKBOX_SELECTIONS = [
    (0, [5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 17, 18])
]

# COLUMNS
LTAP_DF = {
    'Source Bin': 'source_bin', 'Conf.dt.': 'confirmation_date', 'Actual qty': 'actual_quantity', ' Actual qty': 'actual_quantity', 
    'User': 'user', 'PAr': 'picking_area', 'Material Description': 'material_description', 
    'Conf.t.': 'confirmation_time', 'Material': 'material', 'Dest. Bin': 'destination_bin', 'Delivery': 'delivery', 
    'Batch': 'batch'
}
HU_TO_LINK_DF = {
    'Document': 'document',
    'Route': 'route'
}
CDHDR_DF = {
    'Object': 'object',
    'Object Value': 'object_value',
    'Doc.Number': 'document_number',
    'User': 'user',
    'Date': 'date',
    'Time': 'time',
    'TCode': 'transaction_code'
}

# MISCS
FLOORS = {
    "ground_floor": ["3.L", "1.L", "2.L", "0.L", "0.C", "PA1", "PA5"],
    "first_floor": ["1.4", "1.1", "1.3", "1.2", "1.5", "2.N"],
    "second_floor": ["2.1", "2.3", "2.4", "2.2", "2.P"]
    }
BREAKS = {
    "09": 0.75,
    "10": 0.75,
    "11": 0.50,
    "13": 0.75,
    "16": 0.75,
    "17": 0.75,
    "19": 0.50,
    "21": 0.75
}
PRODUCTIVITY_THRESHOLDS = {
    "ground_floor": [34, 44, 54],
    "first_floor": [50, 60, 70],
    "second_floor": [50, 60, 70]
}

PACKING_THRESHOLDS = {
    "ground_floor": [27, 33, 35],
    "first_floor": [35, 45, 50],
    "second_floor": [35, 40, 50]
}

# GENERAL
WAREHOUSE = 266
ENCODING = 1100
MAX_RETRIES = 10
WAIT_SECONDS = 2

def get_output_path() -> str:
    env_path = os.getenv("PATH_TO_DATA")
    if env_path:
        path = Path(env_path)
    else:
        path = project_root / "data_extraction" / "data"

    path.mkdir(parents=True, exist_ok=True)

    path_str = str(path.resolve()).replace("\\", "/")

    if not path_str.endswith("/"):
        path_str += "/"

    return path_str

# OUTPUT PATH
OUTPUT_PATH = get_output_path()