# PIANC Vessel Characteristics Interpolation Tools

## 1. Project Description

This repository contains two engineering utilities for the estimation of ship characteristics based on key datasets published by PIANC (The World Association for Waterborne Transport Infrastructure). The tools are intended for use by maritime engineers, port planners, naval architects, and researchers in the preliminary design and analysis of maritime infrastructure.

The primary function of the scripts is to interpolate a comprehensive set of vessel parameters from a single known input value (e.g., Deadweight Tonnage). This is achieved using numerical methods applied to the official PIANC data tables, providing a repeatable and technically grounded basis for estimation.

The repository includes:
* **`pianc-ship-dimensions.py`**: A command-line interface (CLI) tool for interactive calculations and integration into automated workflows.
* **`pianc-ship-dimensions-gui.py`**: A graphical user interface (GUI) tool built with Tkinter for more accessible, visually-driven analysis.

## 2. Core Technology and Methodology

### 2.1. Data Sources

The estimators are built upon two authoritative PIANC datasets, which represent global standards in the design of ports and waterways. The data is stored in `wg121_database.txt` and `wg235_database.txt` as Python dictionaries.

1.  **PIANC MarCom Working Group 235 (2022):** This is the most current and comprehensive dataset, published in the report **"Ship Dimensions and Data for Design of Marine Infrastructure"**. It reflects the characteristics of the modern world fleet, including newer vessel classes, and is the recommended database for contemporary projects.

2.  **PIANC MarCom Working Group 121 (2014):** This foundational dataset originates from the report **"Harbour Approach Channels – Design Guidelines"**. While some data is superseded by WG235, it remains a critical reference for older vessel types, comparative analyses, or projects where historical design vessels are relevant.

### 2.2. Numerical Interpolation Method: PCHIP

For all numeric parameters, the scripts employ the **Piecewise Cubic Hermite Interpolating Polynomial (PCHIP)** method from the `scipy.interpolate` library.

This method is critically important for this application due to its **shape-preserving (monotonicity) properties**. In the context of ship dimensions, this ensures that the physical relationships present in the source data are maintained. For example, if the PIANC data shows that a ship's Length Overall (LoA) strictly increases with Deadweight Tonnage (DWT), the PCHIP interpolator guarantees the interpolated values will also follow this trend. This avoids the non-physical "overshoots" and oscillations that can be produced by other methods, such as standard cubic splines, thereby ensuring the plausibility of the engineering estimates.

### 2.3. Handling of Non-Numeric Data

For non-numeric (i.e., categorical or textual) characteristics such as `vessel_subtype`, a direct numerical interpolation is not feasible. The scripts address this using a nearest-neighbor lookup approach:

1.  The interpolation is performed on the numeric data based on the user's known input parameter and value.
2.  The algorithm then identifies the row in the source DataFrame where the value of the *known input parameter* is numerically closest to the user's input value.
3.  The categorical value from that specific row is then returned as the result.

## 3. Software Description

### 3.1. Command-Line Tool (`pianc-ship-dimensions.py`)

A Python script that provides an interactive command-line prompt to:
- Select the PIANC database (WG235 or WG121).
- Select the vessel type.
- Select a known characteristic to use as the input.
- Provide the value for the known characteristic.
- Display the full set of interpolated results to the console.
- Append all results to a log file (`pianc-ship-dimensions.txt`).

### 3.2. GUI Tool (`pianc-ship-dimensions-gui.py`)

A self-contained graphical application built using Python's standard `Tkinter` library.
-   **Database Selection:** Radio buttons to switch between WG235 and WG121 datasets.
-   **Dynamic Dropdowns:** Combobox menus for vessel type and characteristics are dynamically populated based on the selected database.
-   **Input/Output:** Features dedicated entry fields for the known value and a scrollable text area to display results.
-   **File Output:** A "Calculate" button triggers the interpolation and appends the results to `pianc-ship-dimensions.txt`.

## 4. Setup and Usage

### 4.1. Prerequisites

-   Python 3.x
-   Required Python libraries: `pandas`, `numpy`, `scipy`. These can be installed via `pip`:
    ```bash
    pip install pandas numpy scipy
    ```

### 4.2. File Structure

Ensure the following files are located in the same directory:
```
/your-project-folder
|-- pianc-ship-dimensions.py         (CLI tool)
|-- pianc-ship-dimensions-gui.py     (GUI tool)
|-- wg121_database.txt               (PIANC WG121 data)
|-- wg235_database.txt               (PIANC WG235 data)
```

### 4.3. Execution

-   **To run the Command-Line Tool:**
    ```bash
    python pianc-ship-dimensions.py
    ```
-   **To run the GUI Tool:**
    ```bash
    python pianc-ship-dimensions-gui.py
    ```

## 5. Compiling to a Standalone Executable

To distribute the GUI tool as a standalone `.exe` file that does not require users to have Python installed, PyInstaller can be used. A multi-step process involving a virtual environment and a `.spec` file is required to handle the `scipy` and `numpy` dependencies correctly.

**Step 1: Create a Virtual Environment**
A virtual environment isolates project dependencies.
```bash
# Navigate to your project folder
python -m venv venv
# Activate the environment
venv\Scripts\activate
```

**Step 2: Install Packages**
With the `(venv)` active, install the required libraries and PyInstaller.
```bash
pip install pandas numpy scipy pyinstaller
```

**Step 3: Generate the Initial .spec File**
Run a basic PyInstaller command to create a `.spec` file, which is a build recipe.
```bash
pyinstaller --noconsole --onefile pianc-ship-dimensions-gui.py
```

**Step 4: Modify the .spec File**
Open the generated `pianc-ship-dimensions-gui.spec` file. Locate the `a = Analysis(...)` section and modify it to include the `datas` and `hiddenimports` arguments. This ensures the database text files and required `scipy` sub-modules are bundled with the executable.
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

**Step 5: Build the Executable**
Run PyInstaller again, this time targeting the modified `.spec` file.
```bash
pyinstaller pianc-ship-dimensions-gui.spec
```

**Step 6: Locate the Executable**
The final `.exe` file will be located in the `dist` directory.

## 6. Available Vessel Data and Parameters

### 6.1. General Parameter Definitions

| Parameter | Definition | Units |
| :--- | :--- | :--- |
| **DWT** | Deadweight Tonnage: The weight of a vessel's cargo, fuel, water, crew, passengers, and stores. | tonnes |
| **GT** | Gross Tonnage: A non-dimensional measure of the overall internal volume of a vessel's enclosed spaces. | - |
| **Loa** | Length Overall: The maximum vessel length from its forward-most point to its aft-most point. | m |
| **lbp** | Length Between Perpendiculars: The length of a vessel along the summer load line. | m |
| **B** | Beam: The maximum width of the vessel. | m |
| **T** | Draught: The vertical distance from the waterline to the bottom of the hull (keel). The data refers to the maximum summer draught unless specified otherwise. | m |
| **Cb** | Block Coefficient: A dimensionless coefficient that indicates the shape of the hull below the waterline relative to a rectangular prism of the same length, beam, and draught. | - |
| **Displacement** | The total weight of the vessel and everything on board, equal to the weight of water it displaces. | tonnes |
| **Windage Area** | The projected plane area of the vessel's hull and superstructure above the waterline, used for calculating wind forces. Presented for both lateral (side) and longitudinal (frontal) aspects. | m² |

### 6.2. PIANC WG235 (2022) Data

**Vessel Types Available:**
- Crude Oil & Larger Product Tankers
- Product, Chemical and Dual Product Tankers
- LNG Carriers
- LPG Carriers
- Container Ships (Post-Panamax & Panamax & smaller)
- General Cargo Vessels
- Refrigerated Cargo
- Car Carriers
- Ferries
- Cruise Liners
- Fishing Vessels > 200 GT

**Parameters Available (by vessel type):**
- `vessel_subtype`, `dwt`, `loa_max`, `lbp_max`, `b_max`, `t_fully_laden_max`, `loa`, `lbp`, `b`, `t_fully_laden`, `moulded_depth`, `air_draft_ballast`, `cb`, `displacement_fully_laden`, `min_lateral_windage_fully_loaded`, `max_lateral_windage_in_ballast`, `longitudinal_windage_fully_loaded`, `longitudinal_windage_in_ballast`, `cargo_capacity` (m³ or GT), `cargo_capacity_(teu)`, `cargo_capacity_(cars)`, `cargo_capacity_(passengers)`

### 6.3. PIANC WG121 (2014) Data

**Vessel Types Available:**
- Tankers (ULCC, VLCC, standard)
- Product and Chemical Tankers
- Bulk Carriers / OBOs
- LNG Carriers (Prismatic, Spheres, Moss)
- LPG Carriers
- Container Ships (Post-Panamax, Panamax)
- Freight RoRo Ships
- Cargo Vessels
- Car Carriers
- Ferries & Fast Ferries (multihull)
- Cruise Liners (Post Panamax, Panamax)
- Fishing Vessels (Ocean-going, Coastal)
- Motor Yachts, Motor Boats, Sailing Yachts, Sailing Boats

**Parameters Available:**
- `DWT (t)`, `Loa (m)`, `lbp (m)`, `B (m)`, `T Laden (m)`, `Cb`, `dm Fully Laden (t)`, `Lateral Windage Fully Loaded (m2)`, `Lateral Windage In Ballast (m2)`, `Capacity` (m³, TEU, cars, lane meters/trailers)

## 7. Technical Literature and Citations

1.  **PIANC. (2022). *Ship Dimensions and Data for Design of Marine Infrastructure* (MarCom Working Group Report N° 235). PIANC General Secretariat.**
2.  **PIANC. (2014). *Harbour Approach Channels – Design Guidelines* (MarCom Working Group Report N° 121). PIANC General Secretariat.**
