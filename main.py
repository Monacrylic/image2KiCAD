import os
from gui.gui import Image2KiCAD
import sys
from PyQt6.QtWidgets import QApplication

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Image2KiCAD()
    window.show()
    sys.exit(app.exec())

