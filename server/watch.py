import os
import json
from data_extraction.utils import default_logger as logger
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
import pandas as pd
from .config import settings

load_dotenv()

class WatchFiles:
    """Monitor and load data files from the configured data folder."""
    
    def __init__(self):
        """Initialize the file watcher and load initial data."""
        self.data_folder_path = settings.path_to_data
        
        # Validate data folder path
        if not self.data_folder_path:
            logger.error("PATH_TO_DATA environment variable is not set")
            raise ValueError("PATH_TO_DATA environment variable is required")
        
        if not os.path.exists(self.data_folder_path):
            logger.error(f"Data folder does not exist: {self.data_folder_path}")
            raise FileNotFoundError(f"Data folder does not exist: {self.data_folder_path}")
        
        # Set up file paths
        self.cdhdr_data_path = os.path.join(self.data_folder_path, 'total_per_floor_packs_per_hour.json')
        self.ltap_data_path = os.path.join(self.data_folder_path, 'total_per_floor_per_flow_picks_per_hour.json')
        self.users_name_path = os.path.join(self.data_folder_path, 'users_name.csv')
        self.bflow_monitor_path = os.path.join(self.data_folder_path, 'bflow_monitor.json')
        self.shipment_workl_path = os.path.join(self.data_folder_path, 'shipment_workl.json')
        
        # Initialize data storage
        self.users_name: Dict[str, str] = {}
        self.cdhdr_data: Dict[str, Any] = {}
        self.ltap_data: Dict[str, Any] = {}
        self.bflow_monitor_data: Dict[str, Any] = {}
        self.shipment_workl_data: Dict[str, Any] = {}
        
        # Load initial data
        self.load_cdhdr()
        self.load_ltap()
        self.load_users_name()
        self.load_bflow_monitor()
        self.load_shipment_workl()
        
        logger.info("WatchFiles initialized successfully")
    
    def _load_file_with_retry(self, file_path: str, file_type: str = 'json') -> Optional[Any]:
        """
        Generic method to load a file with retry logic.
        
        Args:
            file_path: Path to the file to load
            file_type: Type of file ('json' or 'csv')
            
        Returns:
            Loaded data or None if loading failed
        """
        retries = settings.file_load_retries
        delay = settings.file_load_retry_delay
        
        for attempt in range(retries):
            try:
                if not os.path.exists(file_path):
                    if file_type == 'json':
                        logger.warning(f"File does not exist: {file_path}, returning empty dict")
                        return {}
                    return None
                
                # Check file size (basic validation)
                file_size = os.path.getsize(file_path)
                if file_size == 0:
                    logger.warning(f"File is empty: {file_path}")
                    return {} if file_type == 'json' else None
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    if file_type == 'json':
                        data = json.load(f)
                        logger.debug(f"Successfully loaded JSON file: {file_path}")
                        return data
                    else:
                        # For CSV files, return the file handle or path
                        return file_path
                        
            except json.JSONDecodeError as e:
                logger.warning(f"JSON decode error on attempt {attempt + 1}/{retries} for {file_path}: {e}")
                if attempt < retries - 1:
                    time.sleep(delay)
                else:
                    logger.error(f"Failed to load JSON file after {retries} attempts: {file_path}")
                    return {}
                    
            except FileNotFoundError as e:
                logger.warning(f"File not found on attempt {attempt + 1}/{retries}: {file_path}")
                if attempt < retries - 1:
                    time.sleep(delay)
                else:
                    logger.error(f"File not found after {retries} attempts: {file_path}")
                    return {} if file_type == 'json' else None
                    
            except PermissionError as e:
                logger.error(f"Permission denied reading file: {file_path}: {e}")
                return {} if file_type == 'json' else None
                
            except Exception as e:
                logger.error(f"Unexpected error loading file {file_path}: {e}", exc_info=True)
                if attempt < retries - 1:
                    time.sleep(delay)
                else:
                    return {} if file_type == 'json' else None
        
        return {} if file_type == 'json' else None
    
    def _load_json_file(self, file_path: str, default_value: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Load a JSON file with retry logic.
        
        Args:
            file_path: Path to the JSON file
            default_value: Default value to return if file doesn't exist (default: empty dict)
            
        Returns:
            Loaded JSON data as dictionary
        """
        if default_value is None:
            default_value = {}
        
        data = self._load_file_with_retry(file_path, file_type='json')
        if data is None:
            return default_value
        return data
    
    def load_cdhdr(self) -> None:
        """Load CDHDR data from JSON file."""
        logger.info(f"Loading CDHDR data from {self.cdhdr_data_path}")
        self.cdhdr_data = self._load_json_file(self.cdhdr_data_path, {})
        logger.info(f"CDHDR data loaded: {len(self.cdhdr_data)} entries")
    
    def load_ltap(self) -> None:
        """Load LTAP data from JSON file."""
        logger.info(f"Loading LTAP data from {self.ltap_data_path}")
        self.ltap_data = self._load_json_file(self.ltap_data_path, {})
        logger.info(f"LTAP data loaded: {len(self.ltap_data)} entries")
    
    def load_users_name(self) -> None:
        """Load user names from CSV file."""
        logger.info(f"Loading user names from {self.users_name_path}")
        try:
            if not os.path.exists(self.users_name_path):
                logger.info(f"User names file does not exist, creating empty file: {self.users_name_path}")
                df = pd.DataFrame(columns=['user', 'name'])
                df.to_csv(self.users_name_path, index=False)
                self.users_name = {}
            else:
                df = pd.read_csv(self.users_name_path)
                self.users_name = df.set_index('user')['name'].to_dict()
                logger.info(f"User names loaded: {len(self.users_name)} entries")
        except Exception as e:
            logger.error(f"Error loading user names: {e}", exc_info=True)
            self.users_name = {}
    
    def load_bflow_monitor(self) -> None:
        """Load B-Flow monitor data from JSON file."""
        logger.info(f"Loading B-Flow monitor data from {self.bflow_monitor_path}")
        self.bflow_monitor_data = self._load_json_file(self.bflow_monitor_path, {})
        logger.info(f"B-Flow monitor data loaded: {len(self.bflow_monitor_data)} entries")
    
    def load_shipment_workl(self) -> None:
        """Load shipment worklist data from JSON file."""
        logger.info(f"Loading shipment worklist data from {self.shipment_workl_path}")
        self.shipment_workl_data = self._load_json_file(self.shipment_workl_path, {})
        logger.info(f"Shipment worklist data loaded: {len(self.shipment_workl_data)} entries")
    
    def start_watching(self) -> None:
        """Start watching the data folder for file changes."""
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
        """Handle file system events for watched files."""
        
        def __init__(self, watcher: 'WatchFiles'):
            """Initialize the file change handler."""
            self.watcher = watcher
            logger.debug("FileChangeHandler initialized")
        
        def on_modified(self, event) -> None:
            """Handle file modification events."""
            try:
                if event.src_path == self.watcher.cdhdr_data_path:
                    logger.info("CDHDR file modified, reloading...")
                    self.watcher.load_cdhdr()
                elif event.src_path == self.watcher.ltap_data_path:
                    logger.info("LTAP file modified, reloading...")
                    self.watcher.load_ltap()
                elif event.src_path == self.watcher.users_name_path:
                    logger.info("User names file modified, reloading...")
                    self.watcher.load_users_name()
                elif event.src_path == self.watcher.bflow_monitor_path:
                    logger.info("B-Flow monitor file modified, reloading...")
                    self.watcher.load_bflow_monitor()
                elif event.src_path == self.watcher.shipment_workl_path:
                    logger.info("Shipment worklist file modified, reloading...")
                    self.watcher.load_shipment_workl()
            except Exception as e:
                logger.error(f"Error handling file modification: {e}", exc_info=True)
