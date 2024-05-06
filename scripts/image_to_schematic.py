
from scripts.LLMToSchematics import image_to_schematics, image_text_to_schematics, text_to_schematics
import json
import scripts.kicad_utils as kicad_utils
import skip
import uuid

from scripts.symbol_search import symbol_search

################################## HELPER FUNCTIONS ################################
# to be moved into respective files


def find_component_in_schem(component_reference, skip_schematic):
    for symbol in skip_schematic.symbol:
        if symbol.property.Reference.value == component_reference:
            return symbol


def split_diagonal_segments(wire_list):
    new_wire_list = []
    for segment in wire_list:
        # Check if the segment is diagonal
        if segment['x'] != segment['end_x'] and segment['y'] != segment['end_y']:
            # Split the diagonal segment into horizontal and vertical segments
            horizontal_segment = {
                'x': segment['x'], 'y': segment['y'], 'end_x': segment['end_x'], 'end_y': segment['y']}
            vertical_segment = {'x': segment['end_x'], 'y': segment['y'],
                                'end_x': segment['end_x'], 'end_y': segment['end_y']}
            new_wire_list.append(horizontal_segment)
            new_wire_list.append(vertical_segment)
        else:
            # Keep non-diagonal segments unchanged
            new_wire_list.append(segment)
    return new_wire_list


def scale_components(components, scaling_factor):
    # Find the minimum and maximum x and y coordinates
    min_x = min(component['x'] for component in components)
    min_y = min(component['y'] for component in components)
    
    # Scale the components
    scaled_components = []
    for component in components:
        scaled_x = min_x + (component['x'] - min_x) * scaling_factor
        scaled_y = min_y + (component['y'] - min_y) * scaling_factor
        scaled_component = component.copy()
        scaled_component['x'] = int(scaled_x)
        scaled_component['y'] = int(scaled_y)
        scaled_components.append(scaled_component)

    return scaled_components

def scale_components_in_relative_coordinates(components, scaling_factor):
    # Find the minimum and maximum x and y coordinates
    # Scale the components
    scaled_components = []
    for component in components:
        scaled_x = 20 + (component['x']) * scaling_factor
        scaled_y = 20 + (component['y']) * scaling_factor
        scaled_component = component.copy()
        scaled_component['x'] = int(scaled_x)
        scaled_component['y'] = int(scaled_y)
        scaled_components.append(scaled_component)
    
    return scaled_components



def match_libId(raw_libid: str):
    lib_id = raw_libid
    if raw_libid == "resistor" or raw_libid == "R" or raw_libid== "Resistor":
        lib_id = "Device:R"
    elif raw_libid == "capacitor" or raw_libid == "C" or raw_libid == "C_Small":
        lib_id = "Device:C"
    elif "battery" == raw_libid or "cell" == raw_libid or "BAT" == raw_libid:
        lib_id = "Device:Battery"
    elif "led" == raw_libid or "LED" == raw_libid:
        lib_id = "Device:LED"
    elif "switch" == raw_libid or "SW" == raw_libid or "switch_spst" == raw_libid:
        lib_id = "Switch:SW_SPST"
    else:
        lib_id = symbol_search.find_closest_matches(raw_libid)[0]

    return lib_id


####################################################################################

def get_json_from_image(image_path):
    result = image_to_schematics(image_path)
    for component in result['detected_components']:
        component['lib_id_gpt'] = component['lib_id']
        component['lib_id'] = match_libId(component['lib_id'])

    with open('result.json', 'w') as f:
        json.dump(result, f, indent=4)
    return result


def get_json_from_image_and_text(image_path, prompt):
    result = image_text_to_schematics(image_path, prompt)
    for component in result['detected_components']:
        component['lib_id_gpt'] = component['lib_id']
        component['lib_id'] = match_libId(component['lib_id'])
    with open('result.json', 'w') as f:
        json.dump(result, f, indent=4)
    return result


def get_json_from_text(prompt):
    result = text_to_schematics(prompt)
    for component in result['detected_components']:
        component['lib_id_gpt'] = component['lib_id']
        component['lib_id'] = match_libId(component['lib_id'])
    with open('result.json', 'w') as f:
        json.dump(result, f, indent=4)
    return result


def create_kicad_sch_file(components=None, wires=None, new_file_name=None):
    kicad_schematic_path = kicad_utils.create_kicad_sch_file(
        components=components, wires=wires, new_file_name=new_file_name)
    return kicad_schematic_path


def add_components_to_schematic(path_to_json='result.json', kicad_schematic_path=None):
    _kicad_schematic_path = kicad_schematic_path
    if (_kicad_schematic_path == None):
        _kicad_schematic_path = "temp_" + uuid.uuid4().hex + ".kicad_sch"

    with open('result.json', 'r') as f:
        result = json.load(f)

    # Populate the list of components
    list_of_component_dict = []
    for symbol in result["detected_components"]:
        # Add the component to the list
        list_of_component_dict.append({"lib_id": symbol["lib_id"], "x": symbol["x"], "y": symbol["y"],
                                      "angle": symbol["angle"], "reference_name": symbol["reference"], "value": symbol["value"]})

    # scaled_components = scale_components(list_of_component_dict, 0.2)
    scaled_components = scale_components_in_relative_coordinates(list_of_component_dict, 10)

    # Change angle t0 90 for all resistors having angle 0 and 0 for all resistors having angle 90
    for component in scaled_components:
        if component["lib_id"] == "Device:R":
            if component["angle"] == 0:
                component["angle"] = 90
            else:
                component["angle"] = 0

    # Modify the kicad schematic file
    kicad_utils.modify_kicad_sch_file(
        components=scaled_components, file_path=_kicad_schematic_path)
    return _kicad_schematic_path


def add_wires_to_schematic(path_to_json='result.json', kicad_schematic_path=None):
    with open('result.json', 'r') as f:
        result = json.load(f)

    # Load kicad schematic file into skip schematic
    schem = skip.Schematic(kicad_schematic_path)
    wire_list = []

    # make a copy of detected connections
    all_connections = result["component_connections"].copy()

    for curr_component in schem.symbol:
        print(curr_component.property.Reference.value)
        curr_component_ref = curr_component.property.Reference.value
        # Iterate through the list of detected connections
        for curr_connection in all_connections:
            # If curr component is compA in curr connection
            if curr_connection['A_ref'] == curr_component_ref:
                try:
                    curr_component_A_pin = curr_component.pin[curr_connection['A_pin'] - 1]
                    # Find component B
                    curr_component_B = find_component_in_schem(
                        curr_connection['B_ref'], schem)
                    curr_component_B_pin = curr_component_B.pin[curr_connection['B_pin'] - 1]
                    # Add a wire to connect

                    wire_list.append({"x": curr_component_A_pin.location.x, "y": curr_component_A_pin.location.y,
                                      "end_x": curr_component_B_pin.location.x, "end_y": curr_component_B_pin.location.y})
                except:
                    print("Skipped a wire")
                    continue
    new_wire_list = split_diagonal_segments(wire_list)
    kicad_utils.modify_kicad_sch_file(
        wires=new_wire_list, file_path=kicad_schematic_path)
