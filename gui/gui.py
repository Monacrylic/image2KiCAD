import sys
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QPushButton, QFileDialog, QCheckBox
from scripts.image_to_schematic import create_kicad_sch_file, get_json_from_image, add_components_to_schematic, add_wires_to_schematic
import time
import threading
import uuid

class Image2KiCAD(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.image_path = None
        self.kicad_schematic_path = None

    def initUI(self):
        self.setWindowTitle('Image2KiCAD')
        self.setGeometry(100, 100, 400, 250)

        layout = QVBoxLayout()

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

        # Add a checkbox to create a new schematic
        self.new_schematic_checkbox = QCheckBox("Create new Kicad schematic file")
        self.new_schematic_checkbox.setChecked(False)
        self.new_schematic_checkbox.stateChanged.connect(self.new_kicad_schematic)
        layout.addWidget(self.new_schematic_checkbox)


        # Add KiCAD schematic selection
        self.file2_label = QLabel('Select existing KiCAD schematic file (experimental):')
        layout.addWidget(self.file2_label)

        # Add file selection button
        self.file2_button = QPushButton('Browse')
        self.file2_button.clicked.connect(self.select_file2)
        layout.addWidget(self.file2_button)

        # Add instruction label
        self.instruction_label = QLabel('Select files to proceed.')
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

        # Add status label
        self.status_label = QLabel('Status: Idle')
        layout.addWidget(self.status_label)

        self.setLayout(layout)

    def select_file1(self):
        file1, _ = QFileDialog.getOpenFileName(self, 'Select File 1')
        if file1:
            self.file1_button.setText(f'{file1} selected')
            self.image_path = file1
            self.check_files_selected()

    def new_kicad_schematic(self):
        # if the checkbox is checked, hide the file2 selection
        if self.new_schematic_checkbox.isChecked():
            self.file2_button.hide()
            self.file2_label.hide()
            self.kicad_schematic_path = None
            self.check_files_selected()
        else:
            self.file2_button.show()
            self.file2_label.show()
            self.check_files_selected()

    def select_file2(self):
        file2, _ = QFileDialog.getOpenFileName(self, 'Select File 2')
        if file2:
            self.file2_button.setText(f'{file2} selected')
            self.kicad_schematic_path = file2
            self.check_files_selected()

    def check_files_selected(self):
        if ((self.image_path is not None) and self.kicad_schematic_path is not None) or ((self.image_path is not None) and self.new_schematic_checkbox.isChecked()):
            self.instruction_label.setText('All set!')
            self.append_button.setEnabled(True)

    def append_to_schematic(self):
        self.status_label.setText('Status: Processing...')
        self.append_button.setEnabled(False)
        # Start a new thread for processing
        threading.Thread(target=self.process_schematic).start()
    

    def process_schematic(self):
        # Call your processing functions here
        # For example:
        gpt_result = get_json_from_image(self.image_path)

        # if new schematic is selected, create a new schematic
        if self.new_schematic_checkbox.isChecked():
            self.kicad_schematic_path = create_kicad_sch_file(components=None, wires=None, new_file_name=None)

        # Add components to schematic
        schematic_path = add_components_to_schematic(path_to_json='result.json', kicad_schematic_path=self.kicad_schematic_path)

        if self.addwires_checkbox.isChecked():
            add_wires_to_schematic(path_to_json='result.json', kicad_schematic_path=self.kicad_schematic_path)
        # Update status after processing completes
        self.status_label.setText('Status: Done')
        self.append_button.setEnabled(True)