from enum import Enum
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt, QRect

from modules.GUI.GUIColors import GUIColors as Colors
from modules.GUI.GUIFonts import GUIFonts as Fonts
from modules.GUI.GUICustomWidgets import GUICustomWidgets as Widgets

class DialogDimensions(Enum):
    """Enum for dialog dimensions."""
    WIDTH = 400
    HEIGHT = 500

    @staticmethod
    def rect():
        """Returns a QRect object with the specified width and height."""
        return QRect(0, 0, DialogDimensions.WIDTH.value, DialogDimensions.HEIGHT.value)

class ListSelectDialog(QDialog):
    """Dialog with a list of options for the user to choose from. 
    
    The class provides a method for retrieving the selected option.
    """
    
    BUTTONS_H_LAYOUT = "buttons_layout"
    
    def __init__(self, parent: QWidget, title: str, message:str, list: list[str]):
        """Constructor for the ListSelectDialog class.
        
        Args:
            parent (QWidget): The parent widget for the dialog.
            title (str): The title of the dialog.
            message (str): The message to display in the dialog.
            list (list[str]): A list of options to display in the dialog.
        """
        
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
        
        # Create a QListWidget
        self.list_widget = Widgets.create_selectable_list(self)
        self.list_widget.addItems(list)
        self.list_widget.setCurrentRow(0)  # Set the first item as selected by default
        
        # Create buttons        
        self.button_ok = Widgets.create_button(self, "OK")
        self.button_cancel = Widgets.create_button(self, "Cancelar")

        # Connect button actions
        self.button_ok.clicked.connect(self.accept)
        self.button_cancel.clicked.connect(self.reject)

        # Set layouts
        layout_v = QVBoxLayout()
        buttons_layout = QHBoxLayout()
        buttons_layout.setObjectName(self.BUTTONS_H_LAYOUT)
        
        buttons_layout.addWidget(self.button_ok)
        buttons_layout.addWidget(self.button_cancel)

        layout_v.addWidget(self.label)
        layout_v.addWidget(self.list_widget)
        layout_v.addLayout(buttons_layout)
        
        layout_v.setSpacing(15)
        
        self.setLayout(layout_v)
        self.setStyleSheet(f"background-color: {Colors.DEEP_PURPLE};")
        
    def get_selected_option(self) -> str:
        """Returns the selected option from the list.
        
        Returns:
            str: The selected option. If no option is selected, returns None.
        """
        
        selected_items = self.list_widget.selectedItems()
        if selected_items:
            return selected_items[0].text()
        else:
            return None