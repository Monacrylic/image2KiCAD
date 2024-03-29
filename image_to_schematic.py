
from LLMToSchematics import image_to_schematics
import json
import kicad_utils
import skip

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
            horizontal_segment = {'x': segment['x'], 'y': segment['y'], 'end_x': segment['end_x'], 'end_y': segment['y']}
            vertical_segment = {'x': segment['end_x'], 'y': segment['y'], 'end_x': segment['end_x'], 'end_y': segment['end_y']}
            new_wire_list.append(horizontal_segment)
            new_wire_list.append(vertical_segment)
        else:
            new_wire_list.append(segment)  # Keep non-diagonal segments unchanged
    return new_wire_list
####################################################################################

def get_json_from_image(image_path):
    result= image_to_schematics(image_path)
    with open('result.json', 'w') as f:
        json.dump(result, f, indent=4)
    return result

def add_components_to_schematic(path_to_json = 'result.json', kicad_schematic_path = "testProject/testProject.kicad_sch"):
    with open('result.json', 'r') as f:
        result = json.load(f)
    
    # Populate the list of components
    list_of_component_dict =[]
    for symbol in result["detected_components"]:
        # Add the component to the list
        list_of_component_dict.append({"lib_id": kicad_utils.match_libId(symbol["lib_id"]), "x": symbol["x"], "y": symbol["y"], "angle": symbol["angle"], "reference_name": symbol["reference"]})
    
    # Modify the kicad schematic file
    kicad_utils.modify_kicad_sch_file(components = list_of_component_dict, file_path=kicad_schematic_path)




def add_wires_to_schematic(path_to_json = 'result.json', kicad_schematic_path = "testProject/testProject.kicad_sch"):
    with open('result.json', 'r') as f:
        result = json.load(f)
    
    # Load kicad schematic file into skip schematic
    schem = skip.Schematic(kicad_schematic_path)
    wire_list = []

    # make a copy of detected connections
    all_connections = result["component_connections"].copy()

    # Iterate through the list of generated components in kicad shematic
    for curr_component in schem.symbol:
        print(curr_component.property.Reference.value)
        curr_component_ref = curr_component.property.Reference.value
    #   iterate through the list of detected connections
        for curr_connection in all_connections:
            # if curr component is compA in curr connection
            if curr_connection['componentA_reference'] == curr_component_ref:
                curr_component_A_pin = curr_component.pin[curr_connection['componentA_pin']-1]
                #find component B
                curr_component_B = find_component_in_schem(curr_connection['componentB_reference'], schem)
                curr_component_B_pin = curr_component_B.pin[curr_connection['componentB_pin']-1]
                # add a wire to connect
                wire_list.append({"x": curr_component_A_pin.location.x, "y": curr_component_A_pin.location.y, "end_x": curr_component_B_pin.location.x, "end_y":curr_component_B_pin.location.y})

    new_wire_list = split_diagonal_segments(wire_list)
    kicad_utils.modify_kicad_sch_file(wires= new_wire_list, file_path=kicad_schematic_path)