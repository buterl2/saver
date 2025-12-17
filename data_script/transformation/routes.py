import data_script.config.constants as constant
import pandas as pd
from data_script.utils.logger import setup_logger
from pathlib import Path

# Setup logger
logger = setup_logger("transforming_routes")

def transform_routes() -> None:
    """
    Transform routes Excel file to CSV format

    Raises:
        FileNotFoundError: If the Excel file doesn't exist
        Exception: For other transformation errors
    """
    excel_path = f"{constant.OUTPUT_PATH}/misc/routes.xlsx"
    csv_path = f"{constant.OUTPUT_PATH}/misc/routes.csv"

    try:
        logger.info("Started transforming routes file")

        # Check if Excel file exIsts
        if not Path(excel_path).exists():
            raise FileNotFoundError(f"Routes Excel file not found: {excel_path}")

        # Read Excel file
        df = pd.read_excel(excel_path)
        logger.debug(f"Read {len(df)} rows from routes.xlsx")

        # Ensure output directory exists
        Path(csv_path).parent.mkdir(parents=True, exist_ok=True)

        # Convert to CSV
        df.to_csv(csv_path, index=False)
        logger.debug(f"Routes file transformed successfully: {csv_path}")

    except FileNotFoundError as e:
        logger.error(f"Routes file not found: {e}")
        raise
    except pd.errors.EmptyDataError:
        logger.error(f"Routes Excel file is empty")
        raise
    except Exception as e:
        logger.error(F"Error transforming routes file: {e}", exc_info=True)
        raise