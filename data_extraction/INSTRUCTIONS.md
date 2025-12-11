# We need to create the files with data necessary for a dashboard.
First file will be:
### lines_all_floors.json
 - We will need use data from 'vl06f_dashboard.csv', 'ltap_vl06f_to_numbers.csv' files
 - You need to follow already the style of coding I used in 'dashboard.py' file
 - Values from delivery column from vl06f_dashboard have to be made into integers
 - If you need any clarification before we start, let me know.
 - floors mapping will be done like this:
 ```
 if source_bin value starts with:
 * 'F' or 'L' or 'X' - that's ground_floor
 * 'N' - that's first_floor
 * 'Y' or 'O' or 'W' - that's second_floor
 if a hu has more than just one floor, we count it for all the floors that we found, it means that hu has to be picked from multiple floors 
 ```
 - Format of the json will be like this:
 
 ````
 date (format dd.mm.yyyy) - data will be taken from column 'gi_date':
    ground_floor (floor can be determined by taking the value from 'delivery' and looking it up in the ltap.. file, by finding the same value in the 'destination_bin' column, and looking in the 'source_bin' column to see what kind of locations we have [a delivery can be found in one or more files, so we need to search all files to make sure we find everything, and it can also be on multiple rows, we we need to take in account all rows]):
        picked (here we will count how many lines are picked by taking each unique value from 'delivery' column from vl06f_dashboard, and we will go into ltap.. file and we will find all the rows that have this value in the 'destination_bin' column and if a row has a value in 'confirmation_date' column, it means it's picked, if not, and the row is empty in that column, then it's not picked. even if a delivery has multiple rows, we count each row individually, even if 2 of them are picked and 3 of them are not picked, we count as 2 picked and 3 not picked):
            amount_of_lines (count of how many lines have in column 'confirmation_date' a value): 0 (the number)
        not_picked:
            amount_of_lines (count of how many lines have in column 'confirmation_date' nothing): 0
    first_floor:
        picked (here we will count how many lines are picked by taking each unique value from 'delivery' column from vl06f_dashboard, and we will go into ltap.. file and we will find all the rows that have this value in the 'destination_bin' column and if a row has a value in 'confirmation_date' column, it means it's picked, if not, and the row is empty in that column, then it's not picked. even if a delivery has multiple rows, we count each row individually, even if 2 of them are picked and 3 of them are not picked, we count as 2 picked and 3 not picked):
            amount_of_lines (count of how many lines have in column 'confirmation_date' a value): 0 (the number)
        not_picked:
            amount_of_lines (count of how many lines have in column 'confirmation_date' nothing): 0
    second_floor:
        picked (here we will count how many lines are picked by taking each unique value from 'delivery' column from vl06f_dashboard, and we will go into ltap.. file and we will find all the rows that have this value in the 'destination_bin' column and if a row has a value in 'confirmation_date' column, it means it's picked, if not, and the row is empty in that column, then it's not picked. even if a delivery has multiple rows, we count each row individually, even if 2 of them are picked and 3 of them are not picked, we count as 2 picked and 3 not picked):
            amount_of_lines (count of how many lines have in column 'confirmation_date' a value): 0 (the number)
        not_picked:
            amount_of_lines (count of how many lines have in column 'confirmation_date' nothing): 0
    picked (here we will start to count a total, so not individual per floor, but a total):
        amount_of_lines: 0
    not_picked (here we will start to count a total, so not individual per floor, but a total):
        amount_of_lines: 0
 ````
