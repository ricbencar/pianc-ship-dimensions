"""
# Vessel Characteristics Interpolator

## 1. Script Description

This Python script is a command-line tool designed to estimate a comprehensive set of ship characteristics based on a single known parameter (e.g., Deadweight Tonnage - DWT). It serves as a practical utility for maritime engineers, port planners, and naval architects who need to approximate vessel dimensions for preliminary design and analysis.

The script uses data tables published by PIANC (The World Association for Waterborne Transport Infrastructure) and employs a robust interpolation method to provide accurate estimates.

### Key Features:

-   **Interactive Interface:** Guides the user through selecting a database, vessel type, a known characteristic, and its value.
-   **Dual Database Support:** Allows users to choose between two key PIANC datasets: the modern WG235 (2022) and the foundational WG121 (2014).
-   **Advanced Interpolation:** Uses the Piecewise Cubic Hermite Interpolating Polynomial (PCHIP) method from the `SciPy` library for numeric data. This method is ideal as it preserves the monotonicity of the data, preventing unrealistic overshoots that can occur with other methods like spline interpolation.
-   **Intelligent Non-Numeric Handling:** For textual characteristics like `vessel_subtype`, the script identifies the closest existing data entry in the table and returns its value, providing a contextually relevant result.
-   **File Output:** Appends all calculations to a text file named `pianc-ship-dimensions.txt` for record-keeping and further use.

## 2. PIANC Database Sources

The script relies on datasets extracted from official PIANC reports. PIANC provides technical and scientific guidance for the sustainable development of waterborne transport infrastructure. These reports are critical global standards for the design of ports, harbors, and waterways.

-   **PIANC MarCom WG235 (2022):** This is the most recent and comprehensive dataset available. The working group's report, "Design Guidelines for Inland and Maritime Waterways and their Structures," provides an extensive appendix with data on the modern world fleet. This database is preferred for contemporary projects.
-   **PIANC MarCom WG121 (2014):** This dataset is from the report "Harbour Approach Channels – Design Guidelines." For many years, it was the benchmark for channel design. While some of its data may be superseded by WG235, it remains a valuable reference, especially for older vessel types or for comparative studies.

## 3. Usage Information

### Prerequisites

-   Python 3.x
-   The following Python libraries: `pandas`, `numpy`, `scipy`. These can be installed using pip:
    ```
    pip install pandas numpy scipy
    ```

### Setup

1.  Place the script `pianc-ship-dimensions.py` in a directory.
2.  Create two text files in the **same directory**:
    -   `wg235_database.txt`: This file must contain the ship data from PIANC WG235, formatted as a Python dictionary.
    -   `wg121_database.txt`: This file must contain the ship data from PIANC WG121, also formatted as a Python dictionary.

### Execution

1.  Open a terminal or command prompt.
2.  Navigate to the directory containing the script and data files.
3.  Run the script using the command:
    ```
    python pianc-ship-dimensions.py
    ```
4.  Follow the interactive prompts to:
    -   Select the database (WG235 or WG121).
    -   Choose a vessel type from the provided list.
    -   Select the characteristic you know (e.g., `dwt`).
    -   Enter the known value for that characteristic.
5.  The script will display the interpolated results on the screen and save them to `pianc-ship-dimensions.txt`.

## 4. Available Vessel Types and Parameters

The parameters available for interpolation depend on the selected database and vessel type.

### PIANC WG235 (2022) Parameters 

-   **Common Parameters:** `vessel_subtype`, `dwt`, `loa_max`, `lbp_max`, `b_max`, `t_fully_laden_max`, `loa`, `lbp`, `b`, `t_fully_laden`, `moulded_depth`, `air_draft_ballast`, `cb`, `displacement_fully_laden`, `min_lateral_windage_fully_loaded`, `max_lateral_windage_in_ballast`, `longitudinal_windage_fully_loaded`, `longitudinal_windage_in_ballast`.
-   **Vessel Types:**
    -   Crude Oil & Larger Product Tankers (`cargo_capacity`)
    -   Product, Chemical and Dual Product Tankers (`cargo_capacity`)
    -   LNG Carriers (`cargo_capacity`)
    -   LPG Carriers (`cargo_capacity`)
    -   Container Ships (Post-Panamax & Panamax & smaller) (`cargo_capacity_(teu)`)
    -   General Cargo Vessels (`cargo_capacity_(gt)`)
    -   Refrigerated Cargo (`cargo_capacity_(gt)`)
    -   Car Carriers (`cargo_capacity_(cars)`)
    -   Ferries (`gt`, `cargo_capacity_(passengers)`)
    -   Cruise Liners (`gt`, `cargo_capacity_(passengers)`)
    -   Fishing Vessels > 200 GT (`gt`, `cargo_capacity`)

### PIANC WG121 (2014) Parameters 

-   **Common Parameters:** `DWT (t)`, `Loa (m)`, `lbp (m)`, `B (m)`, `T Laden (m)`, `Cb`, `dm Fully Laden (t)`, `Lateral Windage Fully Loaded (m2)`, `Lateral Windage In Ballast (m2)`.
-   **Common Parameters:** `DWT (t)`, `Loa (m)`, `lbp (m)`, `B (m)`, `T Laden (m)`, `Cb`, `dm Fully Laden (t)`, `Lateral Windage Fully Loaded (m2)`, `Lateral Windage In Ballast (m2)`.
-   **Vessel Types:**
    -   Tankers (ULCC, VLCC, and standard)
    -   Product and Chemical Tankers
    -   Bulk Carriers /OBOs
    -   LNG Carriers (Prismatic, Spheres, Moss) (`Capacity` in m³)
    -   LPG Carriers
    -   Container Ships (Post-Panamax, Panamax) (`Capacity` in TEU)
    -   Freight RoRo Ships (`Capacity` in lane meters/trailers)
    -   Cargo Vessels
    -   Car Carriers (`Capacity` in number of cars)
    -   Ferries & Fast Ferries (multihull)
    -   Cruise Liners (Post Panamax, Panamax)
    -   Fishing Vessels (Ocean-going, Coastal)
    -   Motor Yachts, Motor Boats, Sailing Yachts, Sailing Boats

## 5. Bibliography

[1] PIANC. (2022). *Design Guidelines for Inland and Maritime Waterways and their Structures* (Report No. 235). PIANC General Secretariat. 
[2] PIANC. (2014). *Harbour Approach Channels – Design Guidelines* (Report No. 121). PIANC General Secretariat. 
"""

# Import necessary libraries
import pandas as pd  # Used for data manipulation and analysis, primarily with its DataFrame structure.
import numpy as np   # Used for numerical operations, especially for handling 'np.nan' values in the data files.
from scipy.interpolate import PchipInterpolator  # The specific interpolation function used for its shape-preserving qualities.
import warnings      # Used to suppress non-critical warnings from pandas for a cleaner user experience.

def get_all_datasets():
    """
    Loads ship data from the two PIANC database text files ('wg235_database.txt' and 'wg121_database.txt').
    It parses these files, which are formatted as Python dictionaries, and constructs pandas DataFrames
    for each vessel type within each database.

    Returns:
        dict or None: A nested dictionary structure containing the DataFrames for both datasets,
                      e.g., {'PIANC WG235 (2022)': {'VesselType1': df1, ...}, ...}.
                      Returns None if the database files cannot be found or parsed.
    """
    # Suppress a specific pandas FutureWarning related to DataFrame concatenation,
    # which is not relevant to the user and clutters the output.
    warnings.simplefilter(action='ignore', category=FutureWarning)

    def load_data_from_file(filename):
        """
        A helper function to read a text file and execute its content as Python code.
        This is used to parse the database files, which are stored as string
        representations of Python dictionaries.

        Args:
            filename (str): The path to the text file.

        Returns:
            dict: The dictionary object loaded from the file.
        """
        with open(filename, 'r') as f:
            content = f.read()
        
        # A local scope to safely execute the file content in.
        local_scope = {}
        # Execute the code from the file. 'np' is passed as a global variable
        # so that `np.nan` values in the file are correctly interpreted as numpy's Not-a-Number.
        exec(content, {'np': np}, local_scope)
        
        # Assumes the first variable defined in the file is the data dictionary.
        var_name = list(local_scope.keys())[0]
        return local_scope[var_name]

    # --- Main Data Loading ---
    try:
        # Load the raw dictionary data from each file.
        wg235_data = load_data_from_file('wg235_database.txt')
        wg121_data = load_data_from_file('wg121_database.txt')
    except FileNotFoundError as e:
        # Provide a user-friendly error message if a database file is missing.
        print(f"Error: Database file not found - {e}.")
        print("Please ensure 'wg121_database.txt' and 'wg235_database.txt' are in the same directory as the script.")
        return None
    except Exception as e:
        # Catch other potential errors during file loading/parsing.
        print(f"An error occurred while loading or parsing the database files: {e}")
        return None

    # --- DataFrame Creation for WG235 ---
    data_map_wg235 = {}
    for vessel_type, data in wg235_data.items():
        try:
            # Convert each vessel's dictionary of lists into a pandas DataFrame.
            df = pd.DataFrame(data)
            data_map_wg235[vessel_type] = df
        except ValueError as e:
            # If DataFrame creation fails, it's often due to mismatched list lengths in the source data.
            # This detailed error message helps in debugging the source text file.
            print(f"Error creating DataFrame for {vessel_type} in WG235: {e}")
            print("This is likely due to mismatched list lengths in the source file.")
            for k, v in data.items():
                print(f"  - Parameter '{k}': has {len(v)} items")

    # --- DataFrame Creation for WG121 ---
    data_map_wg121 = {}
    for vessel_type, data in wg121_data.items():
        try:
            # Repeat the process for the second database.
            df = pd.DataFrame(data)
            data_map_wg121[vessel_type] = df
        except ValueError as e:
            print(f"Error creating DataFrame for {vessel_type} in WG121: {e}")
            print("This is likely due to mismatched list lengths in the source file.")
            for k, v in data.items():
                print(f"  - Parameter '{k}': has {len(v)} items")

    # Return the final structured dictionary of DataFrames.
    return {
        'PIANC WG235 (2022)': data_map_wg235,
        'PIANC WG121 (2014)': data_map_wg121
    }

def interpolate_ship_characteristics(ship_df, known_char, known_value):
    """
    Performs the core logic of the script. It takes a DataFrame for a specific ship type
    and a known characteristic value, then interpolates all other numeric characteristics.
    For non-numeric fields, it finds the value from the most similar vessel in the dataset.

    Args:
        ship_df (pd.DataFrame): The DataFrame containing the data for the selected vessel type.
        known_char (str): The name of the characteristic (column) with a known value.
        known_value (float): The user-provided value for the known characteristic.

    Returns:
        dict or None: A dictionary containing all the interpolated and looked-up characteristics.
                      Returns None if interpolation cannot be performed (e.g., input out of range).
    """
    # --- Input Validation ---
    if known_char not in ship_df.columns:
        print(f"Error: Characteristic '{known_char}' not found for this vessel type.")
        return None

    # Check if the known characteristic has enough data to be used for interpolation.
    valid_range_series = ship_df[known_char].dropna()
    if valid_range_series.empty or len(valid_range_series) < 2:
        print(f"Error: Not enough valid data for '{known_char}' in this vessel type to perform interpolation.")
        return None

    # Check if the user's value is within the range of the dataset. Extrapolation is disabled.
    min_val, max_val = valid_range_series.min(), valid_range_series.max()
    if not (min_val <= known_value <= max_val):
        print(f"\n--- CALCULATION ABORTED: INPUT OUT OF RANGE ---")
        print(f"The provided value for '{known_char}' ({known_value}) is outside the valid data range of [{min_val}, {max_val}].")
        print("Please provide a value within the specified range.")
        return None

    # --- Data Preparation ---
    x_col = known_char
    # Create a working copy, remove rows where the known characteristic is null, and sort by it.
    interp_df = ship_df.dropna(subset=[x_col]).copy()
    interp_df = interp_df.sort_values(by=x_col)
    
    # **Key Logic for Non-Numeric Data**: Find the index of the row in the original DataFrame
    # that is numerically closest to the user's input value. This index will be used to
    # look up text-based values like 'vessel_subtype'.
    closest_row_index = interp_df.iloc[(interp_df[x_col] - known_value).abs().argsort()[:1]].index[0]
    
    # The dataset sometimes contains duplicate values for the independent variable (e.g., two ships
    # with the exact same DWT). To create a valid function for interpolation, these duplicates
    # are resolved by taking the mean of their dependent variables.
    numeric_cols = [col for col in interp_df.columns if pd.api.types.is_numeric_dtype(interp_df[col])]
    interp_df_numeric = interp_df[numeric_cols]
    interp_df_grouped = interp_df_numeric.groupby(x_col).mean().reset_index()

    if len(interp_df_grouped) < 2:
        print(f"Error: Not enough unique data points (need at least 2) for '{known_char}' after cleaning.")
        return None
    
    # --- Interpolation Loop ---
    final_results = {col: 'N/A' for col in ship_df.columns}

    # Iterate through every characteristic (column) in the original DataFrame.
    for col in ship_df.columns:
        if col == x_col:
            # The known characteristic is set directly to the user's input value.
            final_results[col] = known_value
            continue

        if pd.api.types.is_numeric_dtype(ship_df[col]):
            # This block handles numeric columns that need to be interpolated.
            temp_df = interp_df_grouped[[x_col, col]].dropna()
            
            # Interpolation requires at least two data points.
            if len(temp_df) < 2:
                final_results[col] = 'N/A (Insufficient data)'
                continue
            
            # Create the PCHIP interpolator object. Extrapolate is set to False to prevent
            # guessing values outside the dataset's range.
            interpolator = PchipInterpolator(temp_df[x_col], temp_df[col], extrapolate=False)
            interpolated_value = float(interpolator(known_value))
            
            # Certain values (like TEU or number of cars) should be integers.
            integer_columns = [
                'Capacity', 'cargo_capacity_(teu)', 'cargo_capacity_(cars)'
            ]
            if col in integer_columns or 'passengers' in col:
                final_results[col] = int(round(interpolated_value))
            else:
                # Other values are rounded to two decimal places for readability.
                final_results[col] = round(interpolated_value, 2)
        else:
            # This block handles non-numeric (text) columns.
            # It retrieves the value from the single closest row identified earlier.
            value_from_closest_row = ship_df.loc[closest_row_index, col]
            if pd.notna(value_from_closest_row):
                final_results[col] = value_from_closest_row
            else:
                final_results[col] = 'No data available'
            
    return final_results

def main():
    """
    The main function that drives the user interface of the script.
    It manages the program flow, including database selection, vessel type selection,
    and input of known parameters. It then calls the interpolation function and
    formats the results for printing to the console and a text file.
    """
    # --- Initial Setup and Welcome ---
    print("--- PIANC Vessel Characteristics Interpolator (PCHIP Method) ---")
    print("This script reads data from 'wg121_database.txt' and 'wg235_database.txt'.")
    
    all_datasets = get_all_datasets()
    if not all_datasets:
        print("\nCritical Error: Could not load datasets. Exiting program.")
        return

    # --- Database Selection ---
    print(f"\nPlease choose which dataset you wish to use:")
    dataset_keys = list(all_datasets.keys())
    for i, name in enumerate(dataset_keys, 1):
        print(f"  {i}. {name}")

    try:
        choice = int(input("Select dataset (number): "))
        selected_key = dataset_keys[choice - 1] # `selected_key` holds the database name for the output header.
        data_map = all_datasets[selected_key]
    except (ValueError, IndexError):
        print("Invalid selection. Exiting.")
        return

    print(f"\nSuccessfully loaded dataset: {selected_key}")

    # --- Main Interaction Loop ---
    while True:
        # --- Vessel Type Selection ---
        print("\nAvailable vessel types in this dataset:")
        ship_type_keys = list(data_map.keys())
        for i, ship_type in enumerate(ship_type_keys, 1):
            print(f"  {i}. {ship_type}")

        try:
            choice = int(input("Select a vessel type (number): "))
            ship_type_key = ship_type_keys[choice - 1]
            selected_df = data_map[ship_type_key]
        except (ValueError, IndexError):
            print("Invalid selection. Please try again.")
            continue

        # --- Known Characteristic Selection ---
        print(f"\nAvailable characteristics for '{ship_type_key}':")
        # Only show numeric characteristics with at least 2 data points, as these are the only ones usable for interpolation.
        available_chars = [col for col in selected_df.columns if pd.api.types.is_numeric_dtype(selected_df[col]) and selected_df[col].notna().sum() > 1]
        for i, char in enumerate(available_chars, 1):
            print(f"  {i}. {char}")

        if not available_chars:
            print("No characteristics available for interpolation for this vessel type.")
            continue

        try:
            choice = int(input("Select the characteristic you know (number): "))
            known_char = available_chars[choice - 1]
        except (ValueError, IndexError):
            print("Invalid selection. Please try again.")
            continue
        
        # --- Value Input with Validation ---
        while True:
            try:
                known_value_str = input(f"Enter the value for {known_char}: ")
                known_value = float(known_value_str)
                break
            except ValueError:
                print("Invalid input. Please enter a valid number.")

        # --- Calculation and Output ---
        results = interpolate_ship_characteristics(selected_df, known_char, known_value)

        if results:
            # Create a formatted header and footer for clean output.
            header = f"\n--- '{ship_type_key}' with {known_char} = {known_value} (based on {selected_key} database) ---\n"
            footer = "----------------------------------------------------------------------------------------------------------------\n"
            
            # Print to console
            print(header, end="")
            for char, value in results.items():
                if value != 'N/A (Insufficient data)':
                    print(f"  - {char.ljust(45)}: {value}")
            print(footer, end="")

            # Append to file
            try:
                # 'a' mode appends to the file. 'utf-8' encoding is specified for broad compatibility.
                with open("pianc-ship-dimensions.txt", "a", encoding="utf-8") as f:
                    f.write(header)
                    for char, value in results.items():
                        if value != 'N/A (Insufficient data)':
                            f.write(f"  - {char.ljust(45)}: {value}\n")
                    f.write(footer)
                print("Results have been appended to pianc-ship-dimensions.txt")
            except IOError as e:
                print(f"\nError: Could not write results to file. {e}")
        
        # --- Loop Control ---
        again = input("\nPerform another calculation? (yes/no): ").lower()
        if again not in ['yes', 'y']:
            break

    print("\nProgram finished.")

# This standard Python construct ensures that the main() function is called only when the script is executed directly.
if __name__ == "__main__":
    main()