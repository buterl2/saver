import socket
from data_script.utils.logger import setup_logger
from .config import settings

# Set up logger
logger = setup_logger("barcode_printer")

def generate_zpl_command(username, password):
    data = username + "\t" + password
    label_width = settings.label_width
    barcode_width = len(data) + 25
    x_position = (label_width - barcode_width) / 2
    zpl_command = (
        f"^XA^FO{x_position},5^BY2,3,100^BC,100,N,N,N,A^FD{username}\t{password}^FS"
        f"^FO{x_position},115^A0N,30,30^FDUsername: {username} Password:{password}^FS^XZ"
    )
    
    return zpl_command

def generate_ch_rep_zpl_command():
    """
    Generates ZPL command to replicate the CH REP shipping label exactly as shown in the photo.
    The label has:
    - Two separate boxes: one for "CH" and one for "REP"
    - Right section: Swiss address text positioned more to the right
    """
    label_width = settings.label_width
    
    # Box dimensions - make them larger and more prominent
    box_height = 70
    box_width = 100
    box_spacing = 5  # Small gap between the two boxes
    
    # Position of first box (CH)
    ch_box_x = 10
    ch_box_y = 10
    
    # Position of second box (REP) - separate box next to CH
    rep_box_x = ch_box_x + box_width + box_spacing
    rep_box_y = 10
    
    # Calculate text position inside each box (centered)
    ch_text_x = ch_box_x + 18  # Position CH text centered in its box
    ch_text_y = ch_box_y + 20
    rep_text_x = rep_box_x + 15  # Position REP text centered in its box
    rep_text_y = rep_box_y + 20
    
    # Address text position - moved much more to the right (after both boxes with more spacing)
    right_x = rep_box_x + box_width + 30
    right_y = 15
    
    # Build ZPL command with proper string concatenation - two separate boxes
    zpl_command = (
        "^XA"  # Start label
        f"^FO{ch_box_x},{ch_box_y}^GB{box_width},{box_height},4^FS"  # Draw separate black border box for CH
        f"^FO{ch_text_x},{ch_text_y}^A0N,45,45^FDCH^FS"  # Print "CH" in its own box
        f"^FO{rep_box_x},{rep_box_y}^GB{box_width},{box_height},4^FS"  # Draw separate black border box for REP
        f"^FO{rep_text_x},{rep_text_y}^A0N,45,45^FDREP^FS"  # Print "REP" in its own box
        f"^FO{right_x},{right_y}^A0N,25,25^FDMedtronic (Schweiz) AG,^FS"  # Address line 1
        f"^FO{right_x},{right_y + 25}^A0N,25,25^FDc/o Medtronic International Trading Sarl^FS"  # Address line 2
        f"^FO{right_x},{right_y + 50}^A0N,25,25^FDRoute du Molliau 31, 1131 Tolochenaz^FS"  # Address line 3
        f"^FO{right_x},{right_y + 75}^A0N,25,25^FDSwitzerland^FS"  # Address line 4
        "^XZ"  # End label
    )
    
    return zpl_command

def print_barcode(username, password, printer_name):
    # VALIDATE INPUTS
    if not username or not password:
        error_msg = 'Username and password are required'
        logger.error(error_msg)
        return False, error_msg

    if not printer_name:
        error_msg = 'Printer name is required'
        logger.error(error_msg)
        return False, error_msg

    # VALIDATE PRINTER NAME EXISTS
    printers_ip = settings.printers_ip
    if printer_name not in printers_ip:
        error_msg = f'Invalid printer name: {printer_name}. Available printers: {list(printers_ip.keys())}'
        logger.error(error_msg)
        return False, error_msg

    printer_ip = printers_ip[printer_name]
    printer_port = settings.printer_port
    socket_timeout = settings.socket_timeout

    logger.info(f'Attempting to print barcode to {printer_name} ({printer_ip}:{printer_port})')

    # GENERATE ZPL COMMAND
    try:
        zpl_command = generate_zpl_command(username, password)
    except Exception as e:
        error_msg = f'Error generating ZPL command: {e}'
        logger.error(error_msg, exc_info=True)
        return False, error_msg

    # CREATE SOCKET AND SEND COMMAND
    socket_obj = None
    try:
        socket_obj = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_obj.settimeout(socket_timeout)
        socket_obj.connect((printer_ip, printer_port))
        socket_obj.send(zpl_command.encode('utf-8'))
        logger.info(f'Successfully sent barcode print job to {printer_name}')
        return True, 'Barcode printer successfully'
    except socket.timeout:
        error_msg = f'Connection timeout while printing to {printer_name}'
        logger.error(error_msg)
        return False, error_msg
    except socket.gaierror as e:
        error_msg = f'DNS resolution error for printer {printer_name} ({printer_ip}): {e}'
        logger.error(error_msg)
        return False, error_msg
    except ConnectionRefusedError:
        error_msg = f'Connection refused by printer {printer_name} ({printer_ip}:{printer_port})'
        logger.error(error_msg)
        return False, error_msg
    except OSError as e:
        error_msg = f'Network error while printing to {printer_name}: {e}'
        logger.error(error_msg, exc_info=True)
        return False, error_msg
    except Exception as e:
        error_msg = f'Unexpected error while printing to {printer_name}: {e}'
        logger.error(error_msg, exc_info=True)
        return False, error_msg

    finally:
        if socket_obj:
            try:
                socket_obj.close()
            except Exception as e:
                logger.warning(f'Error closing socket: {e}')

def print_ch_rep_label(printer_name, count=1):
    """
    Prints the CH REP shipping label to the specified printer.
    
    Args:
        printer_name: Name of the printer (e.g., 'Ground Floor', '1st Floor', '2nd Floor')
        count: Number of labels to print (default: 1)
    
    Returns:
        tuple: (success: bool, message: str)
    """
    # VALIDATE PRINTER NAME
    if not printer_name:
        error_msg = 'Printer name is required'
        logger.error(error_msg)
        return False, error_msg

    # VALIDATE COUNT
    try:
        count = int(count)
        if count < 1:
            error_msg = 'Count must be at least 1'
            logger.error(error_msg)
            return False, error_msg
    except (ValueError, TypeError):
        error_msg = 'Count must be a valid integer'
        logger.error(error_msg)
        return False, error_msg

    # VALIDATE PRINTER NAME EXISTS
    printers_ip = settings.printers_ip
    if printer_name not in printers_ip:
        error_msg = f'Invalid printer name: {printer_name}. Available printers: {list(printers_ip.keys())}'
        logger.error(error_msg)
        return False, error_msg

    printer_ip = printers_ip[printer_name]
    printer_port = settings.printer_port
    socket_timeout = settings.socket_timeout

    logger.info(f'Attempting to print {count} CH REP label(s) to {printer_name} ({printer_ip}:{printer_port})')

    # GENERATE ZPL COMMAND
    try:
        zpl_command = generate_ch_rep_zpl_command()
    except Exception as e:
        error_msg = f'Error generating ZPL command: {e}'
        logger.error(error_msg, exc_info=True)
        return False, error_msg

    # CREATE SOCKET AND SEND COMMAND(S)
    socket_obj = None
    try:
        socket_obj = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_obj.settimeout(socket_timeout)
        socket_obj.connect((printer_ip, printer_port))
        
        # Send the ZPL command multiple times
        for i in range(count):
            socket_obj.send(zpl_command.encode('utf-8'))
            logger.info(f'Sent CH REP label {i+1}/{count} to {printer_name}')
        
        success_msg = f'CH REP label(s) printed successfully ({count} label(s))'
        logger.info(f'Successfully sent {count} CH REP label print job(s) to {printer_name}')
        return True, success_msg
    except socket.timeout:
        error_msg = f'Connection timeout while printing to {printer_name}'
        logger.error(error_msg)
        return False, error_msg
    except socket.gaierror as e:
        error_msg = f'DNS resolution error for printer {printer_name} ({printer_ip}): {e}'
        logger.error(error_msg)
        return False, error_msg
    except ConnectionRefusedError:
        error_msg = f'Connection refused by printer {printer_name} ({printer_ip}:{printer_port})'
        logger.error(error_msg)
        return False, error_msg
    except OSError as e:
        error_msg = f'Network error while printing to {printer_name}: {e}'
        logger.error(error_msg, exc_info=True)
        return False, error_msg
    except Exception as e:
        error_msg = f'Unexpected error while printing to {printer_name}: {e}'
        logger.error(error_msg, exc_info=True)
        return False, error_msg

    finally:
        if socket_obj:
            try:
                socket_obj.close()
            except Exception as e:
                logger.warning(f'Error closing socket: {e}')