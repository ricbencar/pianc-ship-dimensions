"""
# PIANC Vessel Characteristics Interpolator - GUI Version

## 1. Script Description

This Python script provides a Graphical User Interface (GUI) for the PIANC Vessel
Characteristics Interpolator. It is built using Tkinter, Python's standard GUI library.

The application allows users to estimate a comprehensive set of ship characteristics
based on a single known parameter (e.g., Deadweight Tonnage - DWT).

### Key Features:

-   **Graphical User Interface:** An intuitive interface built with Tkinter, replacing the command-line prompts.
-   **Dual Database Support:** Allows users to choose between two key PIANC datasets:
    the modern WG235 (2022) and the foundational WG121 (2014) via radio buttons.
-   **Dynamic Dropdowns:** The lists of vessel types and characteristics automatically
    update based on the user's selections.
-   **Advanced Interpolation:** Uses the Piecewise Cubic Hermite Interpolating Polynomial
    (PCHIP) method from the `scipy` library for numeric data.
-   **Intelligent Non-Numeric Handling:** For textual characteristics, the script
    identifies the closest existing data entry and returns its value.
-   **Results Display:** Shows the interpolated results in a clear, scrollable text area.
-   **File Output:** Appends all calculations to a text file named
    `pianc-ship-dimensions.txt` for record-keeping.

## 2. Setup and Execution

### Prerequisites

-   Python 3.x
-   The following Python libraries: `pandas`, `numpy`, `scipy`. These can be installed using pip:
    ```
    pip install pandas numpy scipy
    ```

### Setup

1.  Save this script as a Python file (e.g., `pianc_gui.py`).
2.  Ensure the following two files are in the **same directory** as the script:
    -   `wg235_database.txt`: Contains the ship data from PIANC WG235 as a Python dictionary.
    -   `wg121_database.txt`: Contains the ship data from PIANC WG121 as a Python dictionary.

### Execution

1.  Run the script from your terminal:
    ```
    python pianc-ship-dimensions-gui.py
    ```
2.  The application window will appear. Use the controls to make your selections and
    get the interpolated ship dimensions.

### Compiling into a Standalone Executable (Optional)

To share this tool without requiring users to have Python installed, you can compile it into a single `.exe` file using PyInstaller. Due to the complexity of the `scipy` and `numpy` libraries, a robust multi-step process using a virtual environment and a custom `.spec` file is strongly recommended to ensure a successful build.

**Step 1: Create a Virtual Environment**

A virtual environment provides a clean, isolated space for the project.

1.  Open a command prompt and navigate to your project folder.
2.  Create the virtual environment (e.g., named `venv`):
    ```bash
    python -m venv venv
    ```
3.  Activate the environment:
    ```bash
    venv\Scripts\activate
    ```
    Your command prompt should now start with `(venv)`.

**Step 2: Install Packages**

With the `(venv)` active, install the necessary libraries and PyInstaller:

```bash
pip install pandas numpy scipy pyinstaller
```

**Step 3: Generate the Initial .spec File**

First, run a basic PyInstaller command to generate a `.spec` file. This file is a Python script that acts as a build recipe. We will modify it to ensure all libraries are included correctly.

```bash
pyinstaller --noconsole --onefile pianc-ship-dimensions-gui.py
```

This will create a file named `pianc-ship-dimensions-gui.spec` in your project folder.

**Step 4: Modify the .spec File**

Open the newly created `pianc-ship-dimensions-gui.spec` file in a text editor. You will need to make two important changes to the `Analysis` block:

1.  **Add the `datas`:** Tell PyInstaller to bundle your `.txt` database files.
2.  **Add `hiddenimports`:** Explicitly tell PyInstaller to include `scipy` sub-modules that it often fails to find automatically.

Locate the `a = Analysis(...)` section and modify it to look like this:

```python
a = Analysis(
    ['pianc-ship-dimensions-gui.py'],
    pathex=[],
    binaries=[],
    datas=[('wg121_database.txt', '.'), ('wg235_database.txt', '.')],
    hiddenimports=[
        'scipy.special',
        'scipy.special._cdflib',
        'scipy._lib.messagestream',
        'scipy._cyutility'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
```
Save and close the `.spec` file.

**Step 5: Build the Executable from the .spec file**

Now, run PyInstaller again, but this time, provide the name of your modified `.spec` file. This will build the executable using your custom recipe.

```bash
pyinstaller pianc-ship-dimensions-gui.spec
```

**Step 6: Find the Executable**

PyInstaller will create a `dist` folder. Your final, single-file executable will be inside this `dist` folder.

## 3. Bibliography

[1] PIANC. (2022). *Design Guidelines for Inland and Maritime Waterways and their Structures* (Report No. 235). PIANC General Secretariat.
[2] PIANC. (2014). *Harbour Approach Channels – Design Guidelines* (Report No. 121). PIANC General Secretariat.
"""

# Import necessary libraries
import tkinter as tk
from tkinter import ttk, messagebox, font
import pandas as pd
import numpy as np
from scipy.interpolate import PchipInterpolator
import warnings
import os
import sys

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# --- CORE LOGIC (This section is unchanged) ---
def get_all_datasets():
    warnings.simplefilter(action='ignore', category=FutureWarning)

    def load_data_from_file(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        local_scope = {}
        exec(content, {'np': np}, local_scope)
        var_name = list(local_scope.keys())[0]
        return local_scope[var_name]

    try:
        wg235_path = resource_path('wg235_database.txt')
        wg121_path = resource_path('wg121_database.txt')
        
        wg235_data = load_data_from_file(wg235_path)
        wg121_data = load_data_from_file(wg121_path)

    except FileNotFoundError as e:
        messagebox.showerror(
            "Database File Not Found",
            f"Error: {e}.\nPlease ensure 'wg121_database.txt' and 'wg235_database.txt' "
            "are in the same directory as the script."
        )
        return None
    except Exception as e:
        messagebox.showerror(
            "Database Load Error",
            f"An error occurred while loading or parsing the database files: {e}"
        )
        return None

    data_map_wg235 = {v_type: pd.DataFrame(data) for v_type, data in wg235_data.items()}
    data_map_wg121 = {v_type: pd.DataFrame(data) for v_type, data in wg121_data.items()}

    return {
        'PIANC WG235 (2022)': data_map_wg235,
        'PIANC WG121 (2014)': data_map_wg121
    }

def interpolate_ship_characteristics(ship_df, known_char, known_value):
    valid_range_series = ship_df[known_char].dropna()
    if valid_range_series.empty or len(valid_range_series) < 2:
        messagebox.showerror(
            "Interpolation Error",
            f"Not enough valid data for '{known_char}' in this vessel type to perform interpolation."
        )
        return None

    min_val, max_val = valid_range_series.min(), valid_range_series.max()
    if not (min_val <= known_value <= max_val):
        messagebox.showwarning(
            "Input Out of Range",
            f"The provided value for '{known_char}' ({known_value}) is outside the valid data "
            f"range of [{min_val}, {max_val}].\n\nPlease provide a value within this range."
        )
        return None

    x_col = known_char
    interp_df = ship_df.dropna(subset=[x_col]).copy().sort_values(by=x_col)
    
    closest_row_index = interp_df.iloc[(interp_df[x_col] - known_value).abs().argsort()[:1]].index[0]
    
    numeric_cols = [col for col in interp_df.columns if pd.api.types.is_numeric_dtype(interp_df[col])]
    interp_df_numeric = interp_df[numeric_cols]
    interp_df_grouped = interp_df_numeric.groupby(x_col).mean().reset_index()

    if len(interp_df_grouped) < 2:
        messagebox.showerror("Interpolation Error", f"Not enough unique data points for '{known_char}'.")
        return None
    
    final_results = {col: 'N/A' for col in ship_df.columns}

    for col in ship_df.columns:
        if col == x_col:
            final_results[col] = known_value
            continue

        if pd.api.types.is_numeric_dtype(ship_df[col]):
            temp_df = interp_df_grouped[[x_col, col]].dropna()
            if len(temp_df) < 2:
                final_results[col] = 'N/A (Insufficient data)'
                continue
            
            interpolator = PchipInterpolator(temp_df[x_col], temp_df[col], extrapolate=False)
            interpolated_value = float(interpolator(known_value))
            
            integer_columns = ['Capacity', 'cargo_capacity_(teu)', 'cargo_capacity_(cars)']
            if col in integer_columns or 'passengers' in col:
                final_results[col] = int(round(interpolated_value))
            else:
                final_results[col] = round(interpolated_value, 2)
        else:
            value_from_closest_row = ship_df.loc[closest_row_index, col]
            final_results[col] = value_from_closest_row if pd.notna(value_from_closest_row) else 'No data available'
            
    return final_results


# --- TKINTER GUI APPLICATION ---

class App(tk.Tk):
    """
    The main application class for the PIANC Interpolator GUI.
    """
    def __init__(self):
        super().__init__()

        # --- Load Data ---
        self.all_datasets = get_all_datasets()
        if not self.all_datasets:
            self.destroy()
            return

        # --- Window Configuration ---
        self.title("PIANC Vessel Characteristics Interpolator")
        self.geometry("1000x700")

        # --- Font and Style Configuration ---
        # Increased font size for better readability
        self.default_font = font.Font(family='Segoe UI', size=14) 
        self.title_font = font.Font(family='Segoe UI', size=14, weight='bold')
        self.text_font = font.Font(family='Consolas', size=14)

        # Configure styles for all ttk widgets
        style = ttk.Style(self)
        style.configure('.', font=self.default_font)
        style.configure("TLabel", padding=5)
        style.configure("TButton", padding=5)
        style.configure("TCombobox", padding=5)
        style.configure("TEntry", padding=5)
        style.configure("TLabelframe.Label", font=self.title_font)

        # ** NEW CODE: Set the font for the Combobox's dropdown list **
        # This targets the internal Listbox widget of all TCombobox widgets.
        self.option_add('*TCombobox*Listbox.font', self.default_font)


        # --- Member Variables ---
        self.db_name = tk.StringVar(value=list(self.all_datasets.keys())[0])
        self.vessel_type = tk.StringVar()
        self.known_char = tk.StringVar()
        self.known_value = tk.StringVar()

        # --- Create Widgets ---
        self._create_widgets()

        # --- Center the window on the screen ---
        self._center_window()

    def _center_window(self):
        """Centers the main window on the screen."""
        self.update_idletasks()
        
        window_width = self.winfo_width()
        window_height = self.winfo_height()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        
        self.geometry(f'{window_width}x{window_height}+{x}+{y}')

    def _create_widgets(self):
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        input_frame = ttk.LabelFrame(main_frame, text="Inputs", padding="10")
        input_frame.pack(fill=tk.X, expand=False)
        input_frame.columnconfigure(1, weight=1)

        ttk.Label(input_frame, text="Select Database:").grid(row=0, column=0, sticky=tk.W)
        db_frame = ttk.Frame(input_frame)
        db_frame.grid(row=0, column=1, sticky=tk.W)
        for i, name in enumerate(self.all_datasets.keys()):
            rb = ttk.Radiobutton(db_frame, text=name, variable=self.db_name, value=name, command=self._on_database_select)
            rb.pack(side=tk.LEFT, padx=5)

        ttk.Label(input_frame, text="Vessel Type:").grid(row=1, column=0, sticky=tk.W)
        self.vessel_combo = ttk.Combobox(input_frame, textvariable=self.vessel_type, state="readonly")
        self.vessel_combo.grid(row=1, column=1, sticky=tk.EW, pady=5)
        self.vessel_combo.bind("<<ComboboxSelected>>", self._on_vessel_select)

        ttk.Label(input_frame, text="Known Characteristic:").grid(row=2, column=0, sticky=tk.W)
        self.char_combo = ttk.Combobox(input_frame, textvariable=self.known_char, state="disabled")
        self.char_combo.grid(row=2, column=1, sticky=tk.EW, pady=5)

        ttk.Label(input_frame, text="Value:").grid(row=3, column=0, sticky=tk.W)
        self.value_entry = ttk.Entry(input_frame, textvariable=self.known_value, state="disabled")
        self.value_entry.grid(row=3, column=1, sticky=tk.EW, pady=5)

        controls_frame = ttk.Frame(main_frame)
        controls_frame.pack(fill=tk.X, pady=10)

        self.calc_button = ttk.Button(controls_frame, text="Calculate", command=self._calculate, state="disabled")
        self.calc_button.pack(side=tk.RIGHT)

        results_frame = ttk.LabelFrame(main_frame, text="Results", padding="10")
        results_frame.pack(fill=tk.BOTH, expand=True)

        self.results_text = tk.Text(results_frame, wrap=tk.WORD, height=15, font=self.text_font)
        self.results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # --- Create a right-click context menu for the results text area ---
        results_menu = tk.Menu(self.results_text, tearoff=0)
        results_menu.add_command(label="Copy", command=lambda: self.results_text.event_generate("<<Copy>>"))
        results_menu.add_command(label="Select All", command=lambda: self.results_text.tag_add(tk.SEL, "1.0", tk.END))

        def show_results_menu(event):
            # Disable 'Copy' if no text is selected
            if not self.results_text.tag_ranges(tk.SEL):
                results_menu.entryconfigure("Copy", state="disabled")
            else:
                results_menu.entryconfigure("Copy", state="normal")
            
            # Display the menu at the cursor's position
            results_menu.tk_popup(event.x_root, event.y_root)

        self.results_text.bind("<Button-3>", show_results_menu)
        # --- End of context menu code ---

        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.results_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.results_text.config(yscrollcommand=scrollbar.set)
        
        self._on_database_select()

    def _on_database_select(self, event=None):
        data_map = self.all_datasets[self.db_name.get()]
        self.vessel_combo['values'] = list(data_map.keys())
        self.vessel_combo.set('')
        self.char_combo.set('')
        self.known_value.set('')
        self.char_combo.config(state="disabled")
        self.value_entry.config(state="disabled")
        self.calc_button.config(state="disabled")

    def _on_vessel_select(self, event=None):
        db_name = self.db_name.get()
        vessel_key = self.vessel_type.get()
        if not vessel_key: return

        df = self.all_datasets[db_name][vessel_key]
        available_chars = [col for col in df.columns if pd.api.types.is_numeric_dtype(df[col]) and df[col].notna().sum() > 1]
        
        self.char_combo['values'] = available_chars
        self.char_combo.config(state="readonly")
        self.value_entry.config(state="normal")
        self.calc_button.config(state="normal")
        self.char_combo.set('')
        self.known_value.set('')

    def _calculate(self):
        db_name = self.db_name.get()
        vessel_key = self.vessel_type.get()
        char_key = self.known_char.get()
        value_str = self.known_value.get()

        if not all([db_name, vessel_key, char_key, value_str]):
            messagebox.showerror("Missing Input", "Please fill in all the fields before calculating.")
            return

        try:
            value_float = float(value_str)
        except ValueError:
            messagebox.showerror("Invalid Value", "Please enter a valid number for the value field.")
            return

        df = self.all_datasets[db_name][vessel_key]
        results = interpolate_ship_characteristics(df, char_key, value_float)

        if results:
            header = f"\n--- '{vessel_key}' with {char_key} = {value_float} (based on {db_name} database) ---\n"
            footer = "----------------------------------------------------------------------------------------------------------------\n"
            
            output_lines = []
            for char, value in results.items():
                if value != 'N/A (Insufficient data)':
                    output_lines.append(f"  - {char.ljust(45)}: {value}")
            
            output_str = header + "\n".join(output_lines) + "\n" + footer

            self.results_text.config(state="normal")
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, output_str)
            # The results_text widget is intentionally left in the 'normal' state
            # to allow for text selection and copying.

            self._write_to_file(output_str)

    def _write_to_file(self, content):
        """Appends the given content to the output text file."""
        output_filename = "pianc-ship-dimensions.txt"
        try:
            with open(output_filename, "a", encoding="utf-8") as f:
                f.write(content)
        except IOError as e:
            messagebox.showerror("File Write Error", f"Could not write results to file: {e}")

if __name__ == "__main__":
    app = App()
    app.mainloop()
