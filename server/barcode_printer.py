import socket
from data_extraction.utils import default_logger as logger
from .config import settings

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
        error_msg = f'Invalid printer name: {printer_name}. Available printers: {list[str](printers_ip.keys())}'
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