"""
Test script to print the CH REP shipping label.
Usage: python test_print_ch_rep.py <printer_name> [count]

Examples:
    python test_print_ch_rep.py "Ground Floor"
    python test_print_ch_rep.py "Ground Floor" 5
"""

import sys
from server.barcode_printer import print_ch_rep_label

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_print_ch_rep.py <printer_name> [count]")
        print('Available printer names: "Ground Floor", "1st Floor", "2nd Floor"')
        print('Count: Number of labels to print (default: 1)')
        sys.exit(1)
    
    printer_name = sys.argv[1]
    count = 1  # Default count
    
    if len(sys.argv) >= 3:
        try:
            count = int(sys.argv[2])
            if count < 1:
                print("Error: Count must be at least 1")
                sys.exit(1)
        except ValueError:
            print("Error: Count must be a valid integer")
            sys.exit(1)
    
    print(f"Printing {count} CH REP label(s) to printer: {printer_name}")
    
    success, message = print_ch_rep_label(printer_name, count)
    
    if success:
        print(f"✓ Success: {message}")
    else:
        print(f"✗ Error: {message}")
        sys.exit(1)

