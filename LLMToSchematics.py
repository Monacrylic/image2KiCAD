# python3 -m pip install langchain==0.0.351
# python3 -m pip install -U openai             #(1.14.3)
# export OPENAI_API_KEY="..."
import os
import langchain
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain.chains import TransformChain
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langchain import globals
from langchain_core.runnables import chain
import base64
from langchain_core.output_parsers import JsonOutputParser


def load_image(inputs: dict) -> dict:
    """Load image from file and encode it as base64."""
    image_path = inputs["image_path"]
  
    def encode_image(image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    image_base64 = encode_image(image_path)
    return {"image": image_base64}

    
load_image_chain = TransformChain(
    input_variables=["image_path"],
    output_variables=["image"],
    transform=load_image
)


# Define dictionary structure
from typing import TypedDict
class Wire(TypedDict):
    x: float
    y: float
    end_x: float
    end_y: float
# {"lib_id": "Switch:SW_DPST_x2", "x": 143.51, "y": 77.47, "angle":0, "reference_name": "SW1A"},
class Component(TypedDict):
    lib_id: str
    x: float
    y: float
    angle: float
    reference: str
    value: str
class Connections(TypedDict):
    componentA_reference: str
    componentA_pin: int
    componentB_reference: str
    componentB_pin: int


class SchematicsInformation(BaseModel):
    """Information that describes the schematics"""
    # symbol_count: int = Field(description="number of circuit symbols")
    detected_wires: list[Wire] = Field(description="list of dictionary containing beginning and end coordinates of the wire")
    detected_components: list[Component] = Field(description="list of dictionary containing the name,XY coordinates, angle and reference for a circuit component")
    component_connections: list[Connections] = Field(description="list of discitonaty containing the connections from one pin of a reference to the pin of another reference")
    
# Set verbose
globals.set_debug(True)

@chain
def image_model(inputs: dict):# -> str | list[str] | dict:
    """Invoke model with image and prompt."""
    model = ChatOpenAI(temperature=0.5, model="gpt-4-vision-preview", max_tokens=1024)
    msg = model.invoke(
        [HumanMessage(
            content=[
                {"type": "text", "text": inputs["prompt"]},
                {"type": "text", "text": parser.get_format_instructions()},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{inputs['image']}"}},
                ]
            )]
        )
    return msg.content

@chain
def text_model(inputs: dict):# -> str | list[str] | dict:
    """Invoke model with image and prompt."""
    model = ChatOpenAI(temperature=0.5, model="gpt-4-vision-preview", max_tokens=1024)
    msg = model.invoke(
        [HumanMessage(
            content=[
                {"type": "text", "text": inputs["prompt"]},
                {"type": "text", "text": parser.get_format_instructions()},
                ]
            )]
        )
    return msg.content

parser = JsonOutputParser(pydantic_object=SchematicsInformation)

# including start and end position on the image (you may approaximate using pixel locations)
# including their name, position on the image, and orientation (you may approaximate using pixel locations)
# Can you recognize and list all the electronic components on this schematic drawing and generate an netlist-like list of this diagram?
def image_to_schematics(image_path: str) -> dict:
   vision_prompt = """
   Given the image which contains a circuit schematic drawing, provide the following information:
   - A count of how many components are in the image
   - A list of wires present on this schematic drawing, including start and end position on the image (you may approaximate using pixel locations)
   - A list of components present on this schematic drawing, including their name, position on the image, and orientation (you may approaximate using pixel locations)
   - A list of connections made by the components, you must make sure all the referneces stays consistent throught your answer!
   Please just reply ONLY in JSON output and nothing else!
   """

   vision_chain = load_image_chain | image_model | parser
   return vision_chain.invoke({'image_path': f'{image_path}', 
                               'prompt': vision_prompt})

def image_text_to_schematics(image_path: str) -> dict:
    user_request = input("Describe your request:")
    vision_prompt = f"""
    Look at this image which contains current design of a circuit schematic diagram which the user is currently working on.
    The user has requested that {user_request}
    Please construct a circuit based on these information.
    You must make sure all the referneces stays consistent throught your answer.
    Please just reply ONLY in JSON output and nothing else!
    """

    vision_chain = load_image_chain | image_model | parser
    return vision_chain.invoke({'image_path': f'{image_path}', 
                               'prompt': vision_prompt})

def text_to_schematics() -> dict:
    user_request = input("Describe your request:")
    vision_prompt = f"""
    You are a helpful circuit designer,
    The user has requested that {user_request}
    Please construct a circuit based on these information.
    You must make sure all the referneces stays consistent throught your answer.
    Please just reply ONLY in JSON output and nothing else!
    """

    vision_chain = text_model | parser
    return vision_chain.invoke({'prompt': vision_prompt})

# result = get_image_informations("./circuit1.png")
# result = get_netlist_with_text("./incompleteCircuit.png")
result = text_to_schematics()
print(result)
print(type(result))