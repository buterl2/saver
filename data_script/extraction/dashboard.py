"""
Main dashboard extraction workflow.

This module orchestrates the complete dashboard data extraction, transformation,
and processing workflow.
"""

from data_script.extraction.dashboard_modules.extraction import (
    extract_vl06f_for_dashboard,
    extract_likp_for_dashboard,
    extract_zorf_huto_link,
    extract_ltap_from_to_numbers
)

from data_script.extraction.dashboard_modules.transformation import (
    extract_bflow_routes,
    extract_deliveries,
    extract_to_number_from_zorf_huto_link_for_dashboard,
    convert_likp_for_dashboard,
    convert_vl06f_for_dashboard,
    convert_zorf_huto_link_for_dashboard,
    convert_ltap_to_numbers
)

from data_script.extraction.dashboard_modules.processing import (
    create_deliveries_all_floors,
    create_hu_all_floors,
    create_lines_all_floors,
    create_deliveries_all_floors_pgi,
    create_hu_all_floors_pgi,
    create_lines_all_floors_pgi,
    create_picking_hourly_dashboard
)

from data_script.utils.logger import setup_logger

# Set up logger
logger = setup_logger("dashboard_workflow")

if __name__ == "__main__":
    try:
        logger.info("Starting dashboard extraction workflow")
        
        # Extract VL06F data
        extract_vl06f_for_dashboard("dashboard", "vl06f_dashboard")
        convert_vl06f_for_dashboard()
        
        # Extract b_flow routes
        extract_bflow_routes()
        
        # Extract LIKP data
        extract_likp_for_dashboard("dashboard", "likp_dashboard")
        convert_likp_for_dashboard()
        
        # Extract deliveries
        extract_deliveries("vl06f_dashboard.csv", "vl06f_deliveries.csv")
        extract_deliveries("likp_dashboard.csv", "likp_deliveries.csv")
        
        # Extract ZORF HUTO LINK data
        extract_zorf_huto_link("ZORF_HU_TO_LINK", "vl06f_deliveries.csv", "dashboard", "zorf_hu_to_link_vl06f")
        extract_zorf_huto_link("ZORF_HU_TO_LINK", "likp_deliveries.csv", "dashboard", "zorf_hu_to_link_likp")
        extract_zorf_huto_link("ZORF_HUTO_LNKHIS", "likp_deliveries.csv", "dashboard", "zorf_huto_lnkhis_likp")
        convert_zorf_huto_link_for_dashboard()
        
        # Extract TO numbers
        extract_to_number_from_zorf_huto_link_for_dashboard()
        
        # Extract LTAP data from TO numbers
        extract_ltap_from_to_numbers("hu_to_link_likp_to_numbers.csv", "dashboard", "ltap_likp_to_numbers")
        extract_ltap_from_to_numbers("hu_to_link_vl06f_to_numbers.csv", "dashboard", "ltap_vl06f_to_numbers")
        extract_ltap_from_to_numbers("huto_lnkhis_likp_to_numbers.csv", "dashboard", "ltap_likp_to_numbers_two")
        convert_ltap_to_numbers()
        
        # Create JSON files
        create_deliveries_all_floors()
        create_hu_all_floors()
        create_lines_all_floors()
        create_deliveries_all_floors_pgi()
        create_hu_all_floors_pgi()
        create_lines_all_floors_pgi()
        create_picking_hourly_dashboard()
        
        logger.info("Dashboard extraction workflow completed successfully")
        
    except FileNotFoundError as e:
        logger.error(f"File not found error in dashboard workflow: {e}", exc_info=True)
        raise
    except KeyError as e:
        logger.error(f"Missing required column in dashboard workflow: {e}", exc_info=True)
        raise
    except ValueError as e:
        logger.error(f"Value error in dashboard workflow: {e}", exc_info=True)
        raise
    except Exception as e:
        logger.error(f"Unexpected error in dashboard extraction workflow: {e}", exc_info=True)
        raise

