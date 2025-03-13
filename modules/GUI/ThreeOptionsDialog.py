from enum import Enum
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt, QRect

from modules.GUI.GUIColors import GUIColors as Colors
from modules.GUI.GUICustomWidgets import GUICustomWidgets as Widgets

class DialogDimensions(Enum):
    """Enum for dialog dimensions."""
    WIDTH = 600
    HEIGHT = 180

    @staticmethod
    def rect():
        """Returns a QRect object with the specified width and height."""
        return QRect(0, 0, DialogDimensions.WIDTH.value, DialogDimensions.HEIGHT.value)

class ThreeOptionsDialog(QDialog):
    """Dialog with three options for the user to choose from. Returns 1, 2, or 3 depending on the button clicked."""
    def __init__(self, parent: QWidget, title: str, message: str, options: str):
        super().__init__(parent)

        self.setWindowTitle(title)
        
        # Center the dialog on the screen
        dialog_rect = DialogDimensions.rect()
        dialog_rect.moveCenter(parent.geometry().center())
        self.setGeometry(dialog_rect)

        # Create widgets
        self.label = Widgets.create_label(self, message)
        self.label.setWordWrap(True)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.button_1 = Widgets.create_button(self, options[0])
        self.button_2 = Widgets.create_button(self, options[1])
        self.button_3 = Widgets.create_button(self, options[2])

        # Connect button actions
        self.button_1.clicked.connect(lambda: self.done(1))
        self.button_2.clicked.connect(lambda: self.done(2))
        self.button_3.clicked.connect(lambda: self.done(3))

        # Set layouts
        layout_v = QVBoxLayout()
        layout_h = QHBoxLayout()
        
        layout_h.addWidget(self.button_1)
        layout_h.addWidget(self.button_2)
        layout_h.addWidget(self.button_3)

        layout_v.addWidget(self.label)
        layout_v.addLayout(layout_h)
        
        self.setLayout(layout_v)
        self.setStyleSheet(f"background-color: {Colors.DEEP_PURPLE};")