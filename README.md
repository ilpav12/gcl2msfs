# MSFS Avionics Framework Garmin Electronic Checklist File Converter

This is a simple tool to convert a Garmin Electronic Checklist file to a XML file that can be used with the MSFS Avionics Framework as described in the [documentation](https://microsoft.github.io/msfs-avionics-mirror/2024/docs/g3000/features/electronic-checklists/)

## Usage
1. Acquire a Garmin Electronic Checklist file (`.gcl`).
2. Get the Checklist Editor (Checkset) software from Garmin.
3. Open the `.gcl` file in the Checklist Editor and then export it to `.json` it by clicking on `File` -> `Export JSON`.
4. Run the `gcl2msfs.py` script with the path to the `.json` file as first argument and the path to the output `.xml` file as second argument.
5. The output `.xml` file can now be used with the MSFS Avionics Framework.

## Current limitation:
The Avionics Framework currently does not support the following features of the Garmin Electronic Checklist:
- Font size
- Special characters from the Garmin font
- Images
- Alerts
