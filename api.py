import sys
from scripts import image_to_schematic
from typing import Union
from fastapi import FastAPI

app = FastAPI()

def generate_schematic(textprompt):
    # Generate the JSON file through LLM
    image_to_schematic.get_json_from_text(textprompt)
    
    # Run local processing
    sch_path = image_to_schematic.make_schematic_from_JSON()

    return sch_path

@app.get("/generate/{prompt}")
def generate_schematic_from_prompt(prompt: str):
    textprompt = prompt
    return generate_schematic(textprompt)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        textprompt = " ".join(sys.argv[1:])
        generate_schematic(textprompt)
      
    else:
        print("Please provide a string as input.")