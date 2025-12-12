from data_extraction.utils import default_logger as logger
import copy
import math
from typing import Dict, Any, List, Set, Union
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import pandas as pd
from .watch import WatchFiles
from .barcode_printer import print_barcode
from .config import settings

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response Models
class BarcodeRequest(BaseModel):
    username: str = Field(..., description="Username to print on barcode")
    password: str = Field(..., description="Password to print on barcode")
    printer: str = Field(..., description="Printer name (e.g., 'Ground Floor', '1st Floor', '2nd Floor')")


class BarcodeResponse(BaseModel):
    status: str
    message: str


class HealthResponse(BaseModel):
    status: str
    service: str
    data_loaded: bool


class UsersNamesResponse(BaseModel):
    status: str


# Initialize watcher
try:
    watcher = WatchFiles()
    watcher.start_watching()
    logger.info("File watcher initialized and started")
except Exception as e:
    logger.error(f"Failed to initialize file watcher: {e}", exc_info=True)
    watcher = None


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests."""
    logger.info(f"{request.method} {request.url.path} - Client: {request.client.host if request.client else 'unknown'}")
    response = await call_next(request)
    logger.debug(f"Response status: {response.status_code}")
    return response


# Utility functions
def merge_names(data: Dict[str, Any], names_dict: Dict[str, str]) -> Dict[str, Any]:
    new_data = copy.deepcopy(data)
    for username, user_data in new_data.items():
        if username in names_dict:
            user_data['name'] = names_dict[username]
        else:
            user_data['name'] = 'Unknown'
    return new_data


def clean_nan_values(data: Any) -> Any:
    if isinstance(data, dict):
        return {key: clean_nan_values(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [clean_nan_values(item) for item in data]
    elif isinstance(data, float) and (math.isnan(data) or math.isinf(data)):
        return None
    else:
        return data


# API Endpoints
@app.get('/health', response_model=HealthResponse)
def health_check() -> HealthResponse:
    data_loaded = watcher is not None and (
        bool(watcher.cdhdr_data) or 
        bool(watcher.ltap_data) or 
        bool(watcher.bflow_monitor_data) or 
        bool(watcher.shipment_workl_data)
    )
    
    return HealthResponse(
        status="healthy" if watcher is not None else "unhealthy",
        service="CVNS Dashboard API",
        data_loaded=data_loaded
    )


@app.get('/data_cdhdr')
def get_packing_data() -> Dict[str, Any]:
    try:
        if watcher is None:
            raise HTTPException(status_code=503, detail="File watcher not initialized")
        
        if not watcher.cdhdr_data:
            logger.warning("CDHDR data is empty")
            return {}
        
        result = merge_names(watcher.cdhdr_data, watcher.users_name)
        logger.debug(f"Returning CDHDR data: {len(result)} entries")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting packing data: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get('/data_ltap')
def get_picking_data() -> Dict[str, Any]:
    try:
        if watcher is None:
            raise HTTPException(status_code=503, detail="File watcher not initialized")
        
        if not watcher.ltap_data:
            logger.warning("LTAP data is empty")
            return {}
        
        result = merge_names(watcher.ltap_data, watcher.users_name)
        logger.debug(f"Returning LTAP data: {len(result)} entries")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting picking data: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get('/data_deliveries_dashboard')
def get_deliveries_dashboard_data() -> Dict[str, Any]:
    try:
        if watcher is None:
            raise HTTPException(status_code=503, detail="File watcher not initialized")
        
        if not watcher.deliveries_dashboard_data:
            logger.warning("DELIVERIES DASHBOARD data is empty")
            return {}
        
        result = watcher.deliveries_dashboard_data
        logger.debug(f"Returning DELIVERIES DASHBOARD data: {len(result)} entries")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting deliveries dashboard data: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get('/data_hu_dashboard')
def get_hu_dashboard_data() -> Dict[str, Any]:
    try:
        if watcher is None:
            raise HTTPException(status_code=503, detail="File watcher not initialized")
        
        if not watcher.hu_dashboard_data:
            logger.warning("HU DASHBOARD data is empty")
            return {}
        
        result = watcher.hu_dashboard_data
        logger.debug(f"Returning HU DASHBOARD data: {len(result)} entries")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting hu dashboard data: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get('/data_lines_dashboard')
def get_lines_dashboard_data() -> Dict[str, Any]:
    try:
        if watcher is None:
            raise HTTPException(status_code=503, detail="File watcher not initialized")
        
        if not watcher.lines_dashboard_data:
            logger.warning("LINES DASHBOARD data is empty")
            return {}
        
        result = watcher.lines_dashboard_data
        logger.debug(f"Returning LINES DASHBOARD data: {len(result)} entries")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting lines dashboard data: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get('/data_deliveries_pgi_dashboard')
def get_deliveries_pgi_dashboard_data() -> Dict[str, Any]:
    try:
        if watcher is None:
            raise HTTPException(status_code=503, detail="File watcher not initialized")
        
        if not watcher.deliveries_pgi_dashboard_data:
            logger.warning("DELIVERIES PGI DASHBOARD data is empty")
            return {}
        
        result = watcher.deliveries_pgi_dashboard_data
        logger.debug(f"Returning DELIVERIES PGI DASHBOARD data: {len(result)} entries")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting deliveries pgi dashboard data: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get('/data_hu_pgi_dashboard')
def get_hu_pgi_dashboard_data() -> Dict[str, Any]:
    try:
        if watcher is None:
            raise HTTPException(status_code=503, detail="File watcher not initialized")
        
        if not watcher.hu_pgi_dashboard_data:
            logger.warning("HU PGI DASHBOARD data is empty")
            return {}
        
        result = watcher.hu_pgi_dashboard_data
        logger.debug(f"Returning HU PGI DASHBOARD data: {len(result)} entries")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting hu pgi dashboard data: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get('/data_lines_pgi_dashboard')
def get_lines_pgi_dashboard_data() -> Dict[str, Any]:
    try:
        if watcher is None:
            raise HTTPException(status_code=503, detail="File watcher not initialized")
        
        if not watcher.lines_pgi_dashboard_data:
            logger.warning("LINES PGI DASHBOARD data is empty")
            return {}
        
        result = watcher.lines_pgi_dashboard_data
        logger.debug(f"Returning LINES PGI DASHBOARD data: {len(result)} entries")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting lines pgi dashboard data: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get('/users_names')
def get_all_users() -> Set[str]:
    try:
        if watcher is None:
            raise HTTPException(status_code=503, detail="File watcher not initialized")
        
        all_usernames = set(watcher.cdhdr_data.keys()) | set(watcher.ltap_data.keys())
        logger.debug(f"Returning {len(all_usernames)} unique usernames")
        return all_usernames
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting all users: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.post('/users_names', response_model=UsersNamesResponse)
def save_users_name(names_data: Dict[str, str]) -> UsersNamesResponse:
    try:
        if watcher is None:
            raise HTTPException(status_code=503, detail="File watcher not initialized")
        
        # Validate input
        if not isinstance(names_data, dict):
            raise HTTPException(status_code=400, detail="names_data must be a dictionary")
        
        if not names_data:
            raise HTTPException(status_code=400, detail="names_data cannot be empty")
        
        # Validate dictionary values are strings
        for username, name in names_data.items():
            if not isinstance(username, str) or not isinstance(name, str):
                raise HTTPException(status_code=400, detail="All keys and values must be strings")
        
        result = []
        for username, name in names_data.items():
            result.append({'user': username, 'name': name})
        
        df = pd.DataFrame(result)
        df.to_csv(watcher.users_name_path, index=False)
        
        # Reload user names
        watcher.load_users_name()
        
        logger.info(f"Saved {len(result)} user names to {watcher.users_name_path}")
        return UsersNamesResponse(status='success')
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving user names: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.post('/barcode', response_model=BarcodeResponse)
def request_barcode(barcode_request: BarcodeRequest) -> BarcodeResponse:
    try:
        success, message = print_barcode(
            barcode_request.username,
            barcode_request.password,
            barcode_request.printer
        )
        
        if success:
            logger.info(f"Barcode printed successfully for user: {barcode_request.username}")
            return BarcodeResponse(status='success', message=message)
        else:
            logger.error(f"Barcode printing failed: {message}")
            raise HTTPException(status_code=500, detail=message)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error printing barcode: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
