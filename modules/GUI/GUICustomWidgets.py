from PyQt6.QtWidgets import *
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

from modules.GUI.GUIFactory import GUIFactory
from modules.GUI.GUIColors import GUIColors as Colors
from modules.GUI.GUIFonts import GUIFonts as Fonts

class GUICustomWidgets:
    """This helper class contains static methods for creating custom GUI widgets for the 'PS2 Network Manager' GUI."""
    
    @staticmethod
    def create_label(parent: QWidget, text: str, font: QFont = Fonts.LIGHT_FONT) -> QLabel:
        """Creates a label with off white color. By default, the label uses the light font."""

        return GUIFactory.create_label(parent, text, font, Colors.OFF_WHITE)

    @staticmethod
    def create_button(parent: QWidget, text: str, bg_color: str = Colors.DEEP_MARINE) -> QPushButton:
        """Creates a button with the specified parent and text. By default, the button has a deep marine background color."""

        return GUIFactory.create_button(parent, text, Fonts.BOLD_FONT, bg_color, Colors.OFF_WHITE)
    
    @staticmethod
    def create_line_edit(parent: QWidget, placeholder: str = "") -> QLineEdit:
        """Creates a line edit with the specified parent and placeholder text."""
        
        line_field = QLineEdit(parent)
        line_field.setPlaceholderText(placeholder)
        line_field.setFont(Fonts.REGULAR_FONT)
        line_field.setStyleSheet(f"background-color: {Colors.DARK_LAVENDER}; color: {Colors.OFF_WHITE};")
        
        return line_field
    
    @staticmethod
    def create_hline(parent: QWidget, color: str = Colors.LIGHT_GOLD) -> QFrame:
        """Creates a horizontal line with the specified parent. It has a light gold color by default."""
        
        return GUIFactory.create_hline(parent, color)
    
    @staticmethod
    def create_selectable_list(parent: QWidget, font: QFont = Fonts.REGULAR_FONT) -> QListWidget:
        """Creates a selectable list with the specified parent. By default, it uses the regular font."""
        
        list_widget = QListWidget(parent)
        list_widget.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        list_widget.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        list_widget.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        list_widget.setFont(Fonts.REGULAR_FONT)
        
        list_widget.setStyleSheet(f"""
            QListWidget {{ 
                background-color: {Colors.OFF_WHITE}; 
                color: {Colors.OFF_BLACK}; 
            }}
            
            QListWidget::item:selected {{
                background-color: {Colors.DARK_LAVENDER}; 
                color: {Colors.OFF_WHITE}; 
            }}
        """)
        
        return list_widget
