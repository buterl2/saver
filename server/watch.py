import os
import json
from data_extraction.utils import default_logger as logger
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
import pandas as pd
from server.config import settings

class WatchFiles:
    def __init__(self):
        self.data_folder_path = settings.path_to_data

        # VALIDATE DATA FOLDER PATH
        if not self.data_folder_path:
            logger.error("PATH_TO_DATA environment variable is not set")
            raise ValueError("PATH_TO_DATA environment variable is required")

        if not os.path.exists(self.data_folder_path):
            logger.error(f"Data folder does not exists: {self.data_folder_path}")
            raise ValueError(f"Data folder does not exist: {self.data_folder_path}")
        
        # SET UP FILE PATHS
        self.cdhdr_data_path = os.path.join(self.data_folder_path, "total_per_floor_packs_per_hour.json")
        self.ltap_data_path = os.path.join(self.data_folder_path, "total_per_floor_per_flow_picks_per_hour.json")
        self.deliveries_dashboard_data_path = os.path.join(self.data_folder_path, "deliveries_all_floors.json")
        self.hu_dashboard_data_path = os.path.join(self.data_folder_path, "hu_all_floors.json")
        self.lines_dashboard_data_path = os.path.join(self.data_folder_path, "lines_all_floors.json")
        self.deliveries_pgi_dashboard_data_path = os.path.join(self.data_folder_path, "deliveries_all_floors_pgi.json")
        self.hu_pgi_dashboard_data_path = os.path.join(self.data_folder_path, "hu_all_floors_pgi.json")
        self.lines_pgi_dashboard_data_path = os.path.join(self.data_folder_path, "lines_all_floors_pgi.json")
        self.users_name_path = os.path.join(self.data_folder_path, "users_name.csv")

        # INITIALIZE DATA STORAGE
        self.users_name = {}
        self.cdhdr_data = {}
        self.ltap_data = {}
        self.deliveries_dashboard_data = {}
        self.hu_dashboard_data = {}
        self.lines_dashboard_data = {}
        self.deliveries_pgi_dashboard_data = {}
        self.hu_pgi_dashboard_data = {}
        self.lines_pgi_dashboard_data = {}

        # LOAD INITIAL DATA
        self.load_cdhdr()
        self.load_ltap()
        self.load_deliveries_dashboard()
        self.load_hu_dashboard()
        self.load_lines_dashboard()
        self.load_deliveries_pgi_dashboard()
        self.load_hu_pgi_dashboard()
        self.load_lines_pgi_dashboard()
        self.load_users_name()

        logger.info("WatchFiles initialized successfully")
    
    def _load_file_with_retry(self, file_path, file_type="json"):
        retries = settings.file_load_retries
        delay = settings.file_load_retry_delay

        for attempt in range(retries):
            try:
                if not os.path.exists(file_path):
                    if file_type == "json":
                        logger.warning(f"File does not exist: {file_path}, returning empty dict")
                        return {}
                    return None

                # CHECK FILE SIZE (BASIC VALIDATION)
                file_size = os.path.getsize(file_path)
                if file_size == 0:
                    logger.warning(f"File is empty: {file_path}")
                    return {} if file_type == "json" else None

                with open(file_path, "r", encoding="utf-8") as f:
                    if file_type == "json":
                        data = json.load(f)
                        logger.debug(f"Successfully loaded JSON file: {file_path}")
                        return data
                    else:
                        return file_path

            except json.JSONDecodeError as e:
                logger.warning(f"JSON decode error on attempt {attempt + 1}/{retries} for {file_path}: {e}")
                if attempt < retries - 1:
                    time.sleep(delay)
                else:
                    logger.error(f"Failed to load JSON after {retries} attempts: {file_path}")
                    return {}

            except FileNotFoundError as e:
                logger.warning(f"File not found on attempt {attempt + 1}/{retries}: {file_path}")
                if attempt < retries - 1:
                    time.sleep(delay)
                else:
                    logger.error(f"File not found after {retries} attempts: {file_path}")
                    return {} if file_type == "json" else None

            except PermissionError as e:
                logger.error(f"Permission denied reading file: {file_path}: {e}")
                return {} if file_type == "json" else None

            except Exception as e:
                logger.error(f"Unexpected error loading file {file_path}: {e}", exc_info=True)
                if attempt < retries - 1:
                    time.sleep(delay)
                else:
                    return {} if file_type == "json" else None

        return {} if file_type == "json" else None

    def _load_json_file(self, file_path, default_value=None):
        if default_value is None:
            default_value = {}
        
        data = self._load_file_with_retry(file_path, file_type="json")
        if data is None:
            return default_value
        return data

    def load_cdhdr(self):
        logger.info(f"Loading CDHDR data from {self.cdhdr_data_path}")
        self.cdhdr_data = self._load_json_file(self.cdhdr_data_path, {})
        logger.info(f"CDHDR data loaded {len(self.cdhdr_data)} entries")
    
    def load_ltap(self):
        logger.info(f"Loading LTAP data from {self.ltap_data_path}")
        self.ltap_data = self._load_json_file(self.ltap_data_path, {})
        logger.info(f"LTAP data loaded {len(self.ltap_data)} entries")

    def load_deliveries_dashboard(self):
        logger.info(f"Loading DELIVERIES DASHBOARD data from {self.deliveries_dashboard_data_path}")
        self.deliveries_dashboard_data = self._load_json_file(self.deliveries_dashboard_data_path, {})
        logger.info(f"DELIVERIES DASHBOARD data loaded {len(self.deliveries_dashboard_data)} entries")

    def load_hu_dashboard(self):
        logger.info(f"Loading HU DASHBOARD data from {self.hu_dashboard_data_path}")
        self.hu_dashboard_data = self._load_json_file(self.hu_dashboard_data_path, {})
        logger.info(f"HU DASHBOARD data loaded {len(self.hu_dashboard_data)} entries")

    def load_lines_dashboard(self):
        logger.info(f"Loading LINES DASHBOARD data from {self.lines_dashboard_data_path}")
        self.lines_dashboard_data = self._load_json_file(self.lines_dashboard_data_path, {})
        logger.info(f"LINES DASHBOARD data loaded {len(self.lines_dashboard_data)} entries")
    
    def load_deliveries_pgi_dashboard(self):
        logger.info(f"Loading DELIVERIES PGI DASHBOARD data from {self.deliveries_pgi_dashboard_data_path}")
        self.deliveries_pgi_dashboard_data = self._load_json_file(self.deliveries_pgi_dashboard_data_path, {})
        logger.info(f"DELIVERIES PGI DASHBOARD data loaded {len(self.deliveries_pgi_dashboard_data)} entries")
    
    def load_hu_pgi_dashboard(self):
        logger.info(f"Loading HU PGI DASHBOARD data from {self.hu_pgi_dashboard_data_path}")
        self.hu_pgi_dashboard_data = self._load_json_file(self.hu_pgi_dashboard_data_path, {})
        logger.info(f"HU PGI DASHBOARD data loaded {len(self.hu_pgi_dashboard_data)} entries")

    def load_lines_pgi_dashboard(self):
        logger.info(f"Loading LINES PGI DASHBOARD data from {self.lines_pgi_dashboard_data_path}")
        self.lines_pgi_dashboard_data = self._load_json_file(self.lines_pgi_dashboard_data_path, {})
        logger.info(f"LINES PGI DASHBOARD data loaded {len(self.lines_pgi_dashboard_data)} entries")

    def load_users_name(self):
        logger.info(f"Loading user names from {self.users_name_path}")
        try:
            if not os.path.exists(self.users_name_path):
                logger.info(f"User names file does not exist, creating empty file: {self.users_name_path}")
                df = pd.DataFrame(columns=["user", "name"])
                df.to_csv(self.users_name_path, index=False)
                self.users_name = {}
            else:
                df = pd.read_csv(self.users_name_path)
                self.users_name = df.set_index("user")["name"].to_dict()
                logger.info(f"User names loaded: {len(self.users_name)} entries")
        except Exception as e:
            logger.error(f"Error loading user names: {e}", exc_info=True)
            self.users_name = {}

    def start_watching(self):
        try:
            event_handler = self.FileChangeHandler(self)
            self.observer = Observer()
            self.observer.schedule(event_handler, self.data_folder_path, recursive=False)
            self.observer.start()
            logger.info(f"Started watching data folder: {self.data_folder_path}")
        except Exception as e:
            logger.error(f"Error starting file watcher: {e}", exc_info=True)
            raise

    class FileChangeHandler(FileSystemEventHandler):
        def __init__(self, watcher):
            self.watcher = watcher
            logger.debug("FileChangeHandler initialized")

        def on_modified(self, event):
            try:
                if event.src_path == self.watcher.cdhdr_data_path:
                    logger.info("CDHDR file modified, reloading...")
                    self.watcher.load_cdhdr()
                elif event.src_path == self.watcher.ltap_data_path:
                    logger.info("LTAP file modified, reloading...")
                    self.watcher.load_ltap()
                elif event.src_path == self.watcher.deliveries_dashboard_data_path:
                    logger.info("DELIVERIES DASHBOARD file modified, reloading...")
                    self.watcher.load_deliveries_dashboard()
                elif event.src_path == self.watcher.hu_dashboard_data_path:
                    logger.info("HU DASHBOARD file modified, reloading...")
                    self.watcher.load_hu_dashboard()
                elif event.src_path == self.watcher.lines_dashboard_data_path:
                    logger.info("LINES DASHBOARD file modified, reloading...")
                    self.watcher.load_lines_dashboard()
                elif event.src_path == self.watcher.deliveries_pgi_dashboard_data_path:
                    logger.info("DELIVERIES PGI DASHBOARD file modified, reloading...")
                    self.watcher.load_deliveries_pgi_dashboard()
                elif event.src_path == self.watcher.hu_pgi_dashboard_data_path:
                    logger.info("HU PGI DASHBOARD file modified, reloading...")
                    self.watcher.load_hu_pgi_dashboard()
                elif event.src_path == self.watcher.lines_pgi_dashboard_data_path:
                    logger.info("LINES PGI DASHBOARD file modified, reloading...")
                    self.watcher.load_lines_pgi_dashboard()
                elif event.src_path == self.watcher.users_name_path:
                    logger.info("User names file modified, reloading...")
                    self.watcher.load_users_name()
            except Exception as e:
                logger.error(f"Error handling file modification: {e}", exc_info=True)