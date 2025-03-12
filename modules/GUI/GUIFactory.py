from PyQt6.QtWidgets import *
from PyQt6.QtGui import QFont

from modules.GUI.GUIColors import GUIColors as GUC

class GUIFactory:
    """Factory class for creating generic GUI elements."""

    @staticmethod
    def create_hline(parent: QWidget, color: str, shadow: QFrame.Shadow = QFrame.Shadow.Sunken) -> QFrame:
        """Creates a horizontal line with the specified parent and color."""

        hline = QFrame(parent)
        hline.setFrameShape(QFrame.Shape.HLine)
        hline.setFrameShadow(shadow)
        hline.setStyleSheet(f"background-color: {color};")
        
        return hline

    @staticmethod
    def create_label(parent: QWidget, text: str, font: QFont, color: str) -> QLabel:
        """Creates a label with the specified parent, text, font and color."""

        label = QLabel(parent)
        label.setText(text)
        label.setFont(font)
        label.setStyleSheet(f"color: {color};")
        
        return label
    
    @staticmethod
    def create_button(parent: QWidget, text: str, font: QFont, bg_color: str, text_color: str) -> QPushButton:
        """Creates a button with the specified parent, text, font and colors."""
        
        button = QPushButton(parent)
        button.setText(text)
        button.setFont(font)
        
        P_TB = "2px"
        P_LR = "15px"
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg_color};
                color: {text_color};
                border: none;
                border-radius: 5px;
                padding: {P_TB} {P_LR};
            }}
            QPushButton:hover {{
                background-color: {GUC.enlight_color(bg_color, 0.1)};
            }}
        """)

        return button