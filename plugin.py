import sys
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QPushButton, QFileDialog

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

        title_label = QLabel('Image2KiCAD')
        title_label.setStyleSheet('font-size: 24px; font-weight: bold;')
        layout.addWidget(title_label)

        file1_label = QLabel('Select Circuit Image (.png):')
        layout.addWidget(file1_label)

        self.file1_button = QPushButton('Browse')
        self.file1_button.clicked.connect(self.select_file1)
        layout.addWidget(self.file1_button)

        file2_label = QLabel('Select target KiCAD file:')
        layout.addWidget(file2_label)

        self.file2_button = QPushButton('Browse')
        self.file2_button.clicked.connect(self.select_file2)
        layout.addWidget(self.file2_button)

        self.instruction_label = QLabel('Select files to proceed.')
        layout.addWidget(self.instruction_label)

        self.append_button = QPushButton('Append to Schematic')
        self.append_button.clicked.connect(self.append_to_schematic)
        layout.addWidget(self.append_button)

        self.status_label = QLabel('Status: Idle')
        layout.addWidget(self.status_label)

        self.setLayout(layout)

    def select_file1(self):
        file1, _ = QFileDialog.getOpenFileName(self, 'Select File 1')
        if file1:
            self.file1_button.setText(f'{file1} selected')
            self.image_path = file1
            self.check_files_selected()
        

    def select_file2(self):
        file2, _ = QFileDialog.getOpenFileName(self, 'Select File 2')
        if file2:
            self.file2_button.setText(f'{file2} selected')
            self.kicad_schematic_path = file2
            self.check_files_selected()

    def check_files_selected(self):
        if self.image_path is not None and self.kicad_schematic_path is not None:
            self.instruction_label.setText('All set!')

    def append_to_schematic(self):
        self.status_label.setText('Status: Processing...')
        # Add main functionality here
        
        self.status_label.setText('Status: Done')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Image2KiCAD()
    window.show()
    sys.exit(app.exec())