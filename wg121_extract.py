import csv
import numpy as np
from collections import defaultdict

def format_value(value):
    """
    Formats a single value for pretty printing.
    If it's np.nan, returns 'np.nan'.
    Otherwise, returns the string representation of the value.
    """
    if isinstance(value, float) and np.isnan(value):
        return 'np.nan'
    return str(value)

def wg121_extract(csv_file_path, output_file_path):
    """
    Reads ship data from a CSV file and writes it to a text file
    as a formatted Python dictionary, preserving the original column order and
    the order of ship types as they appear in the CSV.

    Args:
        csv_file_path (str): The path to the input CSV file.
        output_file_path (str): The path for the output text file.
    """
    # In Python 3.7+, defaultdict (like standard dict) preserves insertion order.
    # This ensures that ship types are not sorted alphabetically but rather
    # kept in the order they are encountered in the source CSV file.
    data = defaultdict(lambda: defaultdict(list))
    
    # This list will store the header names in their original order.
    parameter_headers = []

    try:
        # Use 'latin-1' encoding for broader compatibility with CSV files.
        with open(csv_file_path, mode='r', encoding='latin-1') as infile:
            reader = csv.reader(infile, delimiter=',')
            
            # Read the header row. These are the parameter names in order.
            # We skip the first column, which is the ship type identifier.
            all_headers = next(reader)
            parameter_headers = [h.strip() for h in all_headers[1:]]

            # Process each data row in the CSV
            for row in reader:
                # Ensure the row has content before processing
                if not row or not row[0].strip():
                    continue

                ship_type = row[0].strip()

                # Filter out any header-like rows that might be in the data
                if ship_type.lower() == 'type':
                    continue

                # The rest of the items are the parameter values
                values = row[1:]

                # Append each value to the correct list under its ship type and parameter.
                for i, value_str in enumerate(values):
                    # Ensure we don't process more values than we have headers for.
                    if i >= len(parameter_headers):
                        break
                        
                    parameter_name = parameter_headers[i]
                    clean_value_str = value_str.strip()
                    
                    if clean_value_str == '':
                        # If the cell is empty, represent it as Not a Number.
                        value = np.nan
                    elif parameter_name.lower() == 'unit' and clean_value_str:
                         # Handle the 'unit' column as a string.
                        value = clean_value_str
                    else:
                        try:
                            # Attempt to convert the value to a float.
                            value = float(clean_value_str)
                        except (ValueError, TypeError):
                            # If conversion fails, it's not a number.
                            value = np.nan
                    
                    data[ship_type][parameter_name].append(value)

    except FileNotFoundError:
        print(f"Error: The file '{csv_file_path}' was not found.")
        return
    except Exception as e:
        print(f"An error occurred while reading the CSV file: {e}")
        return

    # Write the formatted data structure to the output file
    try:
        with open(output_file_path, mode='w', encoding='utf-8') as outfile:
            outfile.write("wg121_data = {\n")

            ship_items = list(data.items())
            for i, (ship_type, params) in enumerate(ship_items):
                # Write the ship type key and start the inner dictionary
                outfile.write(f"    '{ship_type}': {{\n")
                
                param_lines = []
                # Iterate through the original headers to maintain parameter order
                for header in parameter_headers:
                    values = params.get(header, [])
                    
                    # Format each value in the list for output
                    formatted_values = []
                    for v in values:
                        if isinstance(v, str):
                             formatted_values.append(f"'{v}'") # Add quotes for strings
                        else:
                            formatted_values.append(format_value(v))

                    values_str = ", ".join(formatted_values)
                    
                    # Create the formatted line for the parameter with indentation
                    param_lines.append(f"        '{header}': [{values_str}]")

                # Join the parameter lines with ',\n' and write them to the file
                outfile.write(",\n".join(param_lines))
                outfile.write("\n")

                # Close the inner dictionary
                outfile.write("    }")

                # Add a comma and newline if it's not the last ship type
                if i < len(ship_items) - 1:
                    outfile.write(",\n")
                else:
                    outfile.write("\n")

            outfile.write("}\n")
        
        print(f"Data successfully extracted to '{output_file_path}'")

    except Exception as e:
        print(f"An error occurred while writing the output file: {e}")


if __name__ == '__main__':
    csv_input_file = 'wg121.csv'
    text_output_file = 'wg121_database.txt'
    wg121_extract(csv_input_file, text_output_file)
