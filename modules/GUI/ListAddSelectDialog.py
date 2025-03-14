from enum import Enum
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt, QRect

from modules.GUI.GUIColors import GUIColors as Colors
from modules.GUI.GUIFonts import GUIFonts as Fonts
from modules.GUI.GUICustomWidgets import GUICustomWidgets as Widgets
from modules.GUI.ListSelectDialog import ListSelectDialog

class ListAddSelectDialog(ListSelectDialog):
    """Dialog with a list of selectable options and a Add button for the user create its own option.
    
    The class provides a method for retrieving the selected option.
    
    The Add button allows the user to create a new option, which can be used to add items to the list.
    """
    
    def __init__(self, parent: QWidget, title: str, message:str, list: list[str]):
        """Constructor for the ListAddSelectDialog class.
        
        Args:
            parent (QWidget): The parent widget for the dialog.
            title (str): The title of the dialog.
            message (str): The message to display in the dialog.
            list (list[str]): A list of options to display in the dialog.
        """
        
        super().__init__(parent, title, message, list)

        # Create Add button
        self.button_add = Widgets.create_button(self, "Adicionar...")
        
        # Add button to layout
        layout = super().findChild(QHBoxLayout, ListSelectDialog.BUTTONS_H_LAYOUT)
        layout.addWidget(self.button_add)
    
    def set_add_button_action(self, action):
        """Set the action for the Add button.
        
        Args:
            action (PYQT_SLOT): The action to be executed when the Add button is clicked.
        """
        
        self.button_add.clicked.connect(action)
    
    def add_item_to_list(self, item: str):
        """Add an item to the list.
        
        Args:
            item (str): The item to be added to the list.
        """
        
        self.list_widget.addItem(item)