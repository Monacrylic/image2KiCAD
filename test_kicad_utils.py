import kicad_utils
# Input is a list of wires and components, where each of it is a dictionary.
# Ensure Device.kicad_sym and other files are in the same directory as this notebook.
temp_wires = [
    {"x": 121.92, "y": 67.31, "end_x": 156.21, "end_y": 67.31},

    # {"x": 133.35, "y": 53.34, "end_x": 142.24, "end_y": 53.34},
    # {"x": 133.35, "y": 77.47, "end_x": 133.35, "end_y": 67.31},
    # {"x": 133.35, "y": 59.69, "end_x": 133.35, "end_y": 53.34},
    # {"x": 157.48, "y": 77.47, "end_x": 157.48, "end_y": 77.47},
    # {"x": 157.48, "y": 53.34, "end_x": 149.86, "end_y": 53.34},
]  # Keeping it simple for now, can add width to it in the future
temp_components = [
    # {"lib_id": ":SW_DPST_x2", "x": 143.51, "y": 77.47, "angle":0, "reference_name": "SW1A"},
    {"lib_id": "Device:Ammeter_AC", "x": 133.35,
        "y": 64.77, "angle": 0, "reference_name": "BT1"},
    # {"lib_id": "Device:Ammeter_AC", "x": 133.35,
    #     "y": 64.77, "angle": 0, "reference_name": "BT1"},
    {"lib_id": "Device:R", "x": 146.05, "y": 53.34,
        "angle": 90, "reference_name": "R1"}
]
kicad_utils.create_kicad_sch_file(temp_wires, temp_components)
