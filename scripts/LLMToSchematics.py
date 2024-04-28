# python3 -m pip install langchain==0.0.351
# python3 -m pip install -U openai             #(1.14.3)
# export OPENAI_API_KEY="..."

from typing import TypedDict
import os
import langchain
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain.chains import TransformChain
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain import globals
from langchain_core.runnables import chain
import base64
from langchain_core.output_parsers import JsonOutputParser

import yaml
import os

# Path to your config.yaml file
config_file_path = 'configuration.yaml'

# Read the YAML file
with open(config_file_path, 'r') as file:
    config = yaml.safe_load(file)

# Extract the OPENAI_API_KEY value
openai_api_key = config.get('OPENAI_API_KEY', None)
# Extract the GOOGLE_API key value
google_api_key = config.get('GOOGLE_API_KEY', None)

api_in_use = None


# Use openAI API key if available, else try google API key, else print error message
if google_api_key:
    # Set the environment variable
    os.environ['GOOGLE_API_KEY'] = google_api_key
    api_in_use = 'gemini'
    print('GOOGLE_API_KEY loaded successfully.')
elif openai_api_key:
    # Set the environment variable
    os.environ['OPENAI_API_KEY'] = openai_api_key
    api_in_use = 'openai'
    print('OPENAI_API_KEY loaded successfully.')

else:
    print('No API key found. Please provide an API key in the configuration file.')


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


class Wire(TypedDict):
    x: float
    y: float
    end_x: float
    end_y: float


class Component(TypedDict):
    lib_id: str
    x: float
    y: float
    angle: float
    reference: str
    value: str


class Connections(TypedDict):
    A_ref: str
    A_pin: int
    B_ref: str
    B_pin: int


class SchematicsInformation(BaseModel):
    """Information that describes the schematics"""
    detected_components: list[Component] = Field(
        description="list of dictionary containing the name,XY coordinates, angle and reference for a circuit component")
    component_connections: list[Connections] = Field(
        description="list of dictionaries containing the connections from one pin of a reference to the pin of another reference. for eg {'A_ref': 'R1', 'A_pin': 1, 'B_ref': 'R2', 'B_pin': 2} means pin 1 of R1 is connected to pin 2 of R2")


# Set verbose
globals.set_debug(True)


@chain
def image_model(inputs: dict):  # -> str | list[str] | dict:
    """Invoke model with image and prompt."""
    # choose model based on the API key
    if api_in_use == 'openai':
        model = ChatOpenAI(
            temperature=0.5, model="gpt-4-vision-preview", max_tokens=1024)
    elif api_in_use == 'gemini':
        model = ChatGoogleGenerativeAI(
            temperature=0.5, model="gemini-pro-vision")
    msg = model.invoke(
        [HumanMessage(
            content=[
                {"type": "text", "text": inputs["prompt"]},
                {"type": "text", "text": parser.get_format_instructions()},
                {"type": "image_url", "image_url": {
                    "url": f"data:image/png;base64,{inputs['image']}"}},
            ]
        )]
    )
    return msg.content


@chain
def text_model(inputs: dict):  # -> str | list[str] | dict:
    """Invoke model with image and prompt."""
    # choose model based on the API key
    if api_in_use == 'openai':
        model = ChatOpenAI(
            temperature=0.5, model="gpt-4-vision-preview", max_tokens=1024)
    elif api_in_use == 'gemini':
        model = ChatGoogleGenerativeAI(
            temperature=0.5, model="gemini-pro")
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
   - A list of components present on this schematic drawing, including their name in lowercase alphabet (like resistor, capacitor, switch etc), position on the image, and orientation (you may approaximate using pixel locations)
   - A list of connections made by the components, you must make sure all the referneces stays consistent throught your answer!
   Please just reply ONLY in JSON output and nothing else!
   """

    vision_chain = load_image_chain | image_model | parser
    return vision_chain.invoke({'image_path': f'{image_path}',
                                'prompt': vision_prompt})


def image_text_to_schematics(image_path: str, user_request: str) -> dict:
    # user_request = input("Describe your request:")
    vision_prompt = f"""
    Look at this image which contains current design of a circuit schematic diagram which the user is currently working on.
    The user has requested that {user_request}
    Please construct a circuit based on these information.
    You must make sure all the references stays consistent throught your answer.
    Please just reply ONLY in JSON output and nothing else!
    """

    vision_chain = load_image_chain | image_model | parser
    return vision_chain.invoke({'image_path': f'{image_path}',
                               'prompt': vision_prompt})


def text_to_schematics(user_request: str) -> dict:
    # user_request = input("Describe your request:")
    vision_prompt = f"""
    You are a helpful circuit designer,
    The user has requested that {user_request}
    Please construct a circuit based on these information.
    You must make sure all the referneces stays consistent throught your answer.
    Please just reply ONLY in JSON output and nothing else!
    """

    vision_chain = text_model | parser
    return vision_chain.invoke({'prompt': vision_prompt})
