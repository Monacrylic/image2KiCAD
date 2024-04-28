import sys


from PyQt6.QtWidgets import (QApplication, QWidget, QLabel, QVBoxLayout, QPushButton, QFileDialog, QCheckBox, QTextEdit, QComboBox, QTableWidget,
                             QTableWidgetItem, QVBoxLayout, QCompleter)
from PyQt6.QtCore import Qt
import json
from PyQt6.QtWidgets import QSpacerItem, QSizePolicy
from scripts.image_to_schematic import create_kicad_sch_file, get_json_from_image, get_json_from_image_and_text, get_json_from_text, add_components_to_schematic, add_wires_to_schematic
import time
import threading
import uuid


class CustomCompleter(QCompleter):
    def __init__(self, items, parent=None):
        super().__init__(items, parent)
        self.setFilterMode(Qt.MatchFlag.MatchContains)
        self.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)

    def splitPath(self, path):
        pattern = path.lower()
        matches = [x for x in self.model().stringList()
                   if pattern in x.lower()]
        return matches


class ComponentEditor(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.data = []  # To store the JSON data
        self.json_filepath = ""
        self.items = []

    def initUI(self):
        self.setWindowTitle('Component Editor')
        self.setGeometry(200, 200, 800, 400)
        layout = QVBoxLayout()
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(
            ['Lib ID', 'Lib ID GPT', 'Reference', 'Value', 'X', 'Y'])
        layout.addWidget(self.table)
        self.setLayout(layout)
        # Set the column widths, making 'Lib ID' column wider
        # Set width of 'Lib ID' column to 200 pixels
        self.table.setColumnWidth(0, 250)
        self.table.setColumnWidth(1, 100)  # Adjust as necessary
        self.table.setColumnWidth(2, 100)
        self.table.setColumnWidth(3, 100)
        self.table.setColumnWidth(4, 50)
        self.table.setColumnWidth(5, 50)

    def load_json(self, filepath):
        with open(filepath, 'r') as file:
            self.data = json.load(file)
        self.json_filepath = filepath
        self.load_component_data(self.data['detected_components'])

    def load_symbols(self, filepath):
        with open(filepath, 'r') as file:
            symbol_data = json.load(file)
            for library in symbol_data['symbols']:
                for symbol in library['symbols']:
                    self.items.append(f"{library['lib']}:{symbol}")
        self.items.sort()

    def load_component_data(self, components):
        if not self.items:  # Load symbols if not already loaded
            self.load_symbols('symbol_data.json')
        self.items.sort()
        self.table.setRowCount(len(components))
        for row, component in enumerate(components):
            # Adjust the order of items based on the new header
            self.table.setItem(row, 0, QTableWidgetItem(component['lib_id']))
            self.table.setItem(
                row, 1, QTableWidgetItem(component['lib_id_gpt']))
            self.table.setItem(
                row, 2, QTableWidgetItem(component['reference']))
            self.table.setItem(row, 3, QTableWidgetItem(component['value']))
            self.table.setItem(row, 4, QTableWidgetItem(str(component['x'])))
            self.table.setItem(row, 5, QTableWidgetItem(str(component['y'])))

            # Lib ID is now the first column, so we need to adjust the combo box setup
            combo = QComboBox()
            combo.setEditable(True)
            completer = CustomCompleter(self.items)
            combo.setCompleter(completer)
            combo.addItems(self.items)
            combo.setCurrentText(component['lib_id'])
            combo.currentIndexChanged.connect(
                lambda index, row=row, combo=combo: self.update_lib_id(row, combo.currentText()))
            # Set combo in the first column for Lib ID
            self.table.setCellWidget(row, 0, combo)

    def update_lib_id(self, row, value):
        # Update in-memory JSON data
        self.data['detected_components'][row]['lib_id'] = value
        print(f"Updated lib_id for row {row} to {value}")
        self.save_json(self.json_filepath)

    def save_json(self, filepath):
        with open(filepath, 'w') as file:
            json.dump(self.data, file, indent=4)


class Image2KiCAD(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.image_path = None
        self.kicad_schematic_path = None

        self.editor = ComponentEditor()  # Initializing the editor here
        self.containsTextPrompt = False

    def initUI(self):
        self.setWindowTitle('Image2KiCAD')
        self.setGeometry(100, 100, 400, 250)

        layout = QVBoxLayout()

        # Add status label
        self.status_label = QLabel('Status: Idle')
        layout.addWidget(self.status_label)

        self.setLayout(layout)

        # Add title
        title_label = QLabel('Image2KiCAD')
        title_label.setStyleSheet('font-size: 24px; font-weight: bold;')
        layout.addWidget(title_label)

        # Add circuit image selection
        self.file1_label = QLabel('Select Circuit Image (.png/.jpg/.jpeg):')
        layout.addWidget(self.file1_label)

        # Add file selection button
        self.file1_button = QPushButton('Browse')
        self.file1_button.clicked.connect(self.select_file1)
        layout.addWidget(self.file1_button)

        # Add a QLineEdit for input text (e.g., name of the output file)
        self.input_prompt_field = QTextEdit(self)
        self.input_prompt_field.setPlaceholderText(
            'Enter Any Additional Instructions...')
        self.input_prompt_field.setMinimumHeight(100)
        self.input_prompt_field.textChanged.connect(self.check_text_content)
        layout.addWidget(self.input_prompt_field)

        # Add a checkbox to create a new schematic
        self.new_schematic_checkbox = QCheckBox(
            "Create new Kicad schematic file")
        self.new_schematic_checkbox.setChecked(False)
        self.new_schematic_checkbox.stateChanged.connect(
            self.new_kicad_schematic)
        layout.addWidget(self.new_schematic_checkbox)

        # Add KiCAD schematic selection
        self.file2_label = QLabel(
            'Select existing KiCAD schematic file (experimental):')
        layout.addWidget(self.file2_label)

        # Add file selection button
        self.file2_button = QPushButton('Browse')
        self.file2_button.clicked.connect(self.select_file2)
        layout.addWidget(self.file2_button)

        # Add a vertical spacer
        vertical_spacer = QSpacerItem(
            20, 50, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        layout.addItem(vertical_spacer)

        # Add instruction label
        self.instruction_label = QLabel(
            'Select files or provide prompt to proceed.')
        self.instruction_label.setStyleSheet(
            'font-size: 18px; font-weight: bold; color: Red;')
        layout.addWidget(self.instruction_label)

        # add checkbox for add wires (default: checked)
        self.addwires_checkbox = QCheckBox('Add Wires (experimental)')
        self.addwires_checkbox.setChecked(True)
        layout.addWidget(self.addwires_checkbox)

        # Add append button
        self.append_button = QPushButton('Append to Schematic')
        self.append_button.clicked.connect(self.append_to_schematic)
        self.append_button.setEnabled(False)
        layout.addWidget(self.append_button)

        # Add title
        JSON2KiCad_title_label = QLabel('JSON2KiCAD')
        JSON2KiCad_title_label.setStyleSheet(
            'font-size: 24px; font-weight: bold;')
        layout.addWidget(JSON2KiCad_title_label)

        # Edit Component Mapping
        self.open_editor_button = QPushButton('Edit Component Mapping JSON')
        self.open_editor_button.clicked.connect(self.select_json_file_editor)
        layout.addWidget(self.open_editor_button)

        # Create schematic from JSON
        self.json_to_kicad_button = QPushButton(
            'Create schematic file from JSON')
        self.json_to_kicad_button.clicked.connect(self.json_to_kicad)
        layout.addWidget(self.json_to_kicad_button)

    def select_file1(self):
        file1, _ = QFileDialog.getOpenFileName(self, 'Select File 1')
        if file1:
            self.file1_button.setText(f'{file1} selected')
            self.image_path = file1
            # self.check_files_selected()
            self.check_input_satisfied()

    def new_kicad_schematic(self):
        # if the checkbox is checked, hide the file2 selection
        if self.new_schematic_checkbox.isChecked():
            self.file2_button.hide()
            self.file2_label.hide()
            self.kicad_schematic_path = None
            # self.check_files_selected()
            self.check_input_satisfied()
        else:
            self.file2_button.show()
            self.file2_label.show()
            # self.check_files_selected()
            self.check_input_satisfied()

    def select_file2(self):
        file2, _ = QFileDialog.getOpenFileName(self, 'Select File 2')
        if file2:
            self.file2_button.setText(f'{file2} selected')
            self.kicad_schematic_path = file2
            # self.check_files_selected()
            self.check_input_satisfied()

    def check_text_content(self):
        text_content = self.input_prompt_field.toPlainText()
        if text_content.strip():  # Check if text is not just whitespace
            # print("Text field is not empty.")
            # Here you can enable buttons or trigger other actions
            self.containsTextPrompt = True
        else:
            # print("Text field is empty.")
            self.containsTextPrompt = False

        self.check_input_satisfied()

    def check_files_selected(self):
        if ((self.image_path is not None) and self.kicad_schematic_path is not None) or ((self.image_path is not None) and self.new_schematic_checkbox.isChecked()):
            self.instruction_label.setText('All set!')
            self.append_button.setEnabled(True)

    def check_input_satisfied(self):
        # This function checks if user has correctly entered the required input fields
        # User should suppli at least one (or both) of the following:
        # - Provide Path to Image
        # - Provide Custom Prompt
        # lastly, it will check the logic for whether kicad schematic path is selected

        input_satisfied = (
            self.image_path is not None) or self.containsTextPrompt
        output_satisfied = (
            self.kicad_schematic_path is not None) or self.new_schematic_checkbox.isChecked()
        if input_satisfied and output_satisfied:
            self.instruction_label.setText('All set!')
            self.instruction_label.setStyleSheet(
                'font-size: 18px; font-weight: bold; color: rgb(0, 255, 0);')
            self.append_button.setEnabled(True)
        else:
            self.instruction_label.setText(
                'Select files or provide prompt to proceed.')
            self.instruction_label.setStyleSheet(
                'font-size: 18px; font-weight: bold; color: Red;')
            self.append_button.setEnabled(False)

    def append_to_schematic(self):
        self.status_label.setText('Status: Processing...')
        self.append_button.setEnabled(False)
        # Start a new thread for processing
        threading.Thread(target=self.process_schematic).start()

    def process_schematic(self):
        # Call your processing functions here
        # For example:
        if (self.image_path is not None) and (not self.containsTextPrompt):
            gpt_result = get_json_from_image(self.image_path)
        elif (self.image_path is None) and (self.containsTextPrompt):
            gpt_result = get_json_from_text(
                self.input_prompt_field.toPlainText())
        elif (self.image_path is not None) and (self.containsTextPrompt):
            gpt_result = get_json_from_image_and_text(
                self.image_path, self.input_prompt_field.toPlainText())

        # TODO: Open ComponentEditor.load_json('result.json') 

        # if new schematic is selected, create a new schematic
        if self.new_schematic_checkbox.isChecked():
            self.kicad_schematic_path = create_kicad_sch_file(
                components=None, wires=None, new_file_name=None)

        # Add components to schematic
        schematic_path = add_components_to_schematic(
            path_to_json='result.json', kicad_schematic_path=self.kicad_schematic_path)

        if self.addwires_checkbox.isChecked():
            add_wires_to_schematic(
                path_to_json='result.json', kicad_schematic_path=self.kicad_schematic_path)
        # Update status after processing completes
        self.status_label.setText(
            f'Status: Done. Created {self.kicad_schematic_path}')
        self.append_button.setEnabled(True)



    def json_to_kicad(self):
        curr_json_file, _ = QFileDialog.getOpenFileName(
            self, 'Select JSON File')
        if curr_json_file:
            # if new schematic is selected, create a new schematic
            self.status_label.setText('Status: Processing...')
            threading.Thread(target=self.make_schematic,
                             args=(curr_json_file,)).start()

    def make_schematic(self, curr_json_file):
        self.kicad_schematic_path = create_kicad_sch_file(
            components=None, wires=None, new_file_name=None)
        # Add components to schematic
        schematic_path = add_components_to_schematic(
            path_to_json=curr_json_file, kicad_schematic_path=self.kicad_schematic_path)

        if self.addwires_checkbox.isChecked():
            add_wires_to_schematic(
                path_to_json=curr_json_file, kicad_schematic_path=self.kicad_schematic_path)
        # Update status after processing completes
        self.status_label.setText(f'Status: Done {self.kicad_schematic_path}')

    def select_json_file_editor(self):
        curr_json_file, _ = QFileDialog.getOpenFileName(
            self, 'Select JSON File')
        if curr_json_file:
            self.open_component_editor(curr_json_file)

    def open_component_editor(self, json_filepath):
        self.editor.load_json(json_filepath)
        self.editor.show()
