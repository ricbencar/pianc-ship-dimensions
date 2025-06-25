import csv
import numpy as np
import pandas as pd

def to_numeric_or_nan(value):
    """
    Converts a value to a float if possible. If the value contains characters
    that indicate it is a range or a non-numeric identifier (e.g., '/', '-'),
    it is preserved as a string. Correctly handles thousands separators.
    """
    if value is None:
        return np.nan
    
    value_str = str(value).strip()
    if not value_str:
        return np.nan

    # Preserve values that are clearly not single numeric entries (e.g., ranges, identifiers)
    if '/' in value_str or '-' in value_str:
        return value_str

    try:
        # Remove thousands separators and convert to float
        cleaned_str = value_str.replace(',', '')
        return float(cleaned_str)
    except (ValueError, TypeError):
        # If conversion fails, return the original string
        return value_str

def clean_header(header_str):
    """Cleans and standardizes a single header string."""
    return header_str.strip()

# --- Main Script Logic ---
wg235_data = {}
ship_type_order = []  # This list will maintain the original order from the file
current_headers = []
last_header_map = {} # To store the header order for each ship type block
last_ship_type = None # To carry over the ship type for rows with an empty first column

with open('wg235.csv', 'r', encoding='utf-8', errors='ignore') as f:
    reader = csv.reader(f, delimiter=',')
    for row in reader:
        # Skip rows that are completely empty or are comment/separator lines
        if not row or not any(field.strip() for field in row) or row[0].strip().startswith(';'):
            continue

        first_cell = row[0].strip()
        
        # A row is a header if 'Type' is in the first cell and 'DWT' or 'GT' is in the row.
        is_header = 'Type' in first_cell and any('DWT' in h or 'GT' in h for h in row)
        
        if is_header:
            raw_headers = [clean_header(h) for h in row]
            counts = {}
            current_headers = []
            for h in raw_headers:
                if h in counts:
                    counts[h] += 1
                    current_headers.append(f"{h}_{counts[h]}")
                else:
                    counts[h] = 0
                    current_headers.append(h)
            last_ship_type = None  # Invalidate the last ship type after finding a new header
            continue
        
        if not current_headers:
            continue

        # This logic ensures that the ship type from a previous row is carried over
        # if the current row's first cell is blank. It also handles cases where a new
        # type is introduced mid-block (as happens with the broken "Product, Chemical..." entry).
        ship_type = first_cell if first_cell else last_ship_type
        if not ship_type:
            continue
        last_ship_type = ship_type

        # Initialize the data structures for a newly encountered ship type
        if ship_type not in wg235_data:
            ship_type_order.append(ship_type)
            wg235_data[ship_type] = {}
            # Associate the current set of headers with this new ship type
            last_header_map[ship_type] = list(current_headers)

        # Use the headers that were most recently parsed and associated with this block
        headers_for_this_row = last_header_map.get(ship_type, current_headers)

        for i, header_key in enumerate(headers_for_this_row):
            if i >= len(row):
                continue
            
            if header_key == 'Type':
                continue

            if header_key not in wg235_data[ship_type]:
                wg235_data[ship_type][header_key] = []
            
            value = row[i]
            wg235_data[ship_type][header_key].append(value)

# --- Post-processing and Formatting ---
final_wg235_data = {}
for ship_type in ship_type_order:
    raw_data = wg235_data.get(ship_type, {})
    if not raw_data:
        continue
    
    processed_dict = {}
    
    # Find the maximum number of data points for any attribute of this ship type
    max_len = 0
    if raw_data.values():
       max_len = max(len(v) for v in raw_data.values())

    for key, values in raw_data.items():
        # Pad shorter lists with None to ensure all lists for a ship type have the same length
        padded_values = (values + [None] * max_len)[:max_len]
        processed_dict[key] = [to_numeric_or_nan(v) for v in padded_values]

    final_wg235_data[ship_type] = processed_dict

# --- Generate Final Output String ---
output_string = "wg235_data = {\n"

for ship_type in ship_type_order:
    if ship_type not in final_wg235_data:
        continue

    data = final_wg235_data[ship_type]
    output_string += f"    '{ship_type}': {{\n"
    
    key_order = [h for h in last_header_map.get(ship_type, data.keys()) if h != 'Type']
    
    for key in key_order:
        if key not in data:
            # Add empty list for keys that are in the header but had no data for this type
            output_string += f"        '{key}': [],\n"
            continue

        values = data[key]
        formatted_values = [f"np.nan" if pd.isnull(v) else repr(v) for v in values]
        output_string += f"        '{key}': [{', '.join(formatted_values)}],\n"
        
    output_string += "    },\n"
output_string += "}\n"

with open('wg235_database.txt', 'w', encoding='utf-8') as f:
    f.write(output_string)

print("The file 'wg235_database.txt' has been created successfully. All ship types and their full data have been extracted.")