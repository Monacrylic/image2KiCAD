import os
import re
import json
import Levenshtein
import yaml

config_file_path = 'configuration.yaml'

# Read the YAML file
with open(config_file_path, 'r') as file:
    config = yaml.safe_load(file)

symbol_library_path = config.get('symbol_library_path', None)


#--------------------------------Helper functions------------------------------
def extract_top_level_symbol_names(file_path):
    symbol_names = []
    with open(file_path, "r") as f:
        content = f.read()
        symbol_matches = re.findall(r'\(symbol\s+"([^"]+)"', content)
        previous_symbol = ""
        for symbol_match in symbol_matches:
            escaped_symbol = re.escape(previous_symbol) if previous_symbol else ""
            if bool(re.search(fr'{escaped_symbol}_\d+', symbol_match)):
                continue
            else:
                previous_symbol = symbol_match
                symbol_names.append(symbol_match)

    
    return symbol_names

#--------------------------------Helper functions------------------------------

class SymbolSearch:
    def __init__(self, symbol_data_path):
        self.symbol_data = load_symbol_data(symbol_data_path)
    
    def find_closest_matches(self, term, top_n=3):
        return find_closest_matches(term, self.symbol_data, top_n)

    def load_symbol_data(self, file_path):
        self.symbol_data = load_symbol_data(file_path)

    def create_symbol_data_json(self, directory_path, output_file):
        create_symbol_data_json(directory_path, output_file)

def create_symbol_data_json(directory_path, output_file):
    """
    Creates a JSON file containing symbol data for the given directory of KiCad symbol files.

    Parameters:
        directory_path (str): The path to the directory containing the KiCad symbol files.
        output_file (str): The path to the output JSON file.

    Returns:
        None
    """
    with open(output_file, "w") as json_file:
        json_file.write('{"symbols": [')
        first_symbol = True
        for filename in os.listdir(directory_path):
            if filename.endswith(".kicad_sym"):
                # Extract the library name from the file name
                libname= filename.split(".")[0]
                file_path = os.path.join(directory_path, filename)
                symbols = extract_top_level_symbol_names(file_path)
                if symbols:
                    if not first_symbol:
                        json_file.write(',')
                    json.dump({"lib": libname, "symbols": symbols}, json_file, indent=2)
                    first_symbol = False
        json_file.write(']}')


def load_symbol_data(file_path):
    """
    Load symbol data from a JSON file.

    Parameters:
        file_path (str): The path to the JSON file.

    Returns:
        dict: The symbol data loaded from the JSON file.
    """
    if not os.path.exists(file_path):
        create_symbol_data_json(directory_path= symbol_library_path, output_file= file_path)

    with open(file_path, "r") as f:
        symbol_data = json.load(f)
    return symbol_data

def find_closest_matches(term, symbol_data, top_n=3):
    """
    Find the closest matches for a given search term in a symbol data.

    Parameters:
        term (str): The search term to find matches for.
        symbol_data (dict): The symbol data containing the symbols to search through.
        top_n (int, optional): The number of closest matches to return. Defaults to 3.

    Returns:
        list: A list of tuples containing the closest matches. Each tuple contains the library name, symbol name, and the distance from the search term.
    """
    matches = []
    for lib_data in symbol_data["symbols"]:
        lib_name = lib_data["lib"]
        symbols = lib_data["symbols"]
        for symbol in symbols:
            distance = Levenshtein.distance(term.lower(), symbol.lower())
            matches.append((lib_name, symbol, distance))
    
    # Sort the matches based on distance
    sorted_matches = sorted(matches, key=lambda x: x[2])
    
    # Extract top N matches
    top_matches = sorted_matches[:top_n]
    
    # Create a list having "lib_name: symbol_name" format
    top_matches_list = [f"{match[0]}:{match[1]}" for match in top_matches]
    return top_matches_list

symbol_search = SymbolSearch("symbol_data.json")


