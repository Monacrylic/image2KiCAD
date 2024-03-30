# image2Kicad (WIP!)

[![License](https://img.shields.io/badge/license-GNU%20GPL-blue.svg)](https://github.com/monacrylic/image2KiCAD/blob/main/LICENSE)

![image](https://github.com/Monacrylic/image2KiCAD/assets/44057927/c160252f-aca2-48fd-b79f-009555edab22)
A potential KiCAD plugin <b>(Work in pogress!)</b> that aims to effortlessly convert images to editable KiCAD schematics. No more manual tedious manual copying of schematics from datasheets.

## Table of Contents

- [Introduction](#introduction)
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [Contributors](#contributors)
- [License](#license)

## Introduction

image2Kicad is an experimental python script with a GUI that utilizes GPT-4 to parse images into .kicad_sch files. 
At the moment the capanilities of the script are limited to circuits containing
- Batteries
- Resistors
- Capacitors
- LEDs
- (we're adding more components everyday)

<b> Note: This is still a WIP, and invokving the GPT API costs money! Be sure to set a limit on your API calls.</b>

## Installation

1. Clone the repository
2. Install the necessary python libraries
    ```bash
    pip install -r requirements.txt
    ```
3. Enter your OPENAI_API_KEY in sample_configuration.yaml and rename the file as configuration.yaml
4. Run the plugin.py script!

## Usage
![image](https://github.com/Monacrylic/image2KiCAD/assets/44057927/d439c594-fb4a-40e4-9919-bb4b01e05cad)
Run plugin.py and enter the necessary inputs:
1. Select a .png file containing the schematic (Only works for super simple circuits containing the components listed above for now.)
2. Select an empty.kicad_sch file
3. Click 'Append to schematic'

## Contributing
This plugin is in the very initial stages of prototyping (need to format and document the code). Any help is appreciated!

We're grateful for all pinoeering work done to make the KiCAD ecosystem. This plugin would be our little contribution to the amaing community of open-source develoers.


## Contributors
<a href="https://github.com/monacrylic/image2Kicad/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=monacrylic/image2Kicad" />
</a>

## License
[![License](https://img.shields.io/badge/license-GNU%20GPL-blue.svg)](https://github.com/monacrylic/image2KiCAD/blob/main/LICENSE)

