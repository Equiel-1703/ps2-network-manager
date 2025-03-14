from enum import Enum
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt, QRect, QRegularExpression
from PyQt6.QtGui import QRegularExpressionValidator

from modules.GUI.GUIColors import GUIColors as Colors
from modules.GUI.GUIFonts import GUIFonts as Fonts
from modules.GUI.GUICustomWidgets import GUICustomWidgets as Widgets

class DialogDimensions(Enum):
    """Enum for dialog dimensions."""
    WIDTH = 500
    HEIGHT = 200

    @staticmethod
    def rect():
        """Returns a QRect object with the specified width and height."""
        return QRect(0, 0, DialogDimensions.WIDTH.value, DialogDimensions.HEIGHT.value)

class CreateNewIPDialog(QDialog):
    """Dialog for adding a new IP address to a network interface.
    
    The class provides a method for retrieving the new IP address.
    """

    __ip:str = ""
    __mask:str = ""

    def __init__(self, parent: QWidget, interface:str):
        """Constructor for the CreateNewIPDialog class.
        
        Args:
            parent (QWidget): The parent widget for the dialog.
            interface (str): The name of the network interface to which the IP address will be added.
        """
        super().__init__(parent)

        self.setWindowTitle(f"Adicionar novo IP para a interface {interface}")
        
        # Center the dialog on the screen
        dialog_rect = DialogDimensions.rect()
        dialog_rect.moveCenter(parent.geometry().center())
        self.setGeometry(dialog_rect)

        # Create widgets
        self.label = Widgets.create_label(self, "Crie um novo IP para a interface selecionada")
        self.label.setWordWrap(True)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Create a QLineEdit for IP address input
        self.ip_input = Widgets.create_line_edit(self, "Digite o novo IP (ex: 192.162.1.10)")
        self.ip_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        ip_mask_regex = QRegularExpression(
            r"^(25[0-5]|2[0-4][0-9]|1?[0-9]?[0-9])\."
            r"(25[0-5]|2[0-4][0-9]|1?[0-9]?[0-9])\."
            r"(25[0-5]|2[0-4][0-9]|1?[0-9]?[0-9])\."
            r"(25[0-5]|2[0-4][0-9]|1?[0-9]?[0-9])$"
        )
        self.ip_input.setValidator(QRegularExpressionValidator(ip_mask_regex, self))

        # Create a QLineEdit for subnet mask input
        self.subnet_mask_input = Widgets.create_line_edit(self, "Digite a máscara de sub-rede (ex: 255.255.255.0)")
        self.subnet_mask_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.subnet_mask_input.setValidator(QRegularExpressionValidator(ip_mask_regex, self))
        
        # Create buttons        
        self.button_ok = Widgets.create_button(self, "OK")
        self.button_cancel = Widgets.create_button(self, "Cancelar")

        # Connect button actions
        self.button_ok.clicked.connect(self.__validate)
        self.button_cancel.clicked.connect(self.reject)

        # Set layouts
        layout_v = QVBoxLayout()
        
        buttons_layout = QHBoxLayout()
        
        buttons_layout.addWidget(self.button_ok)
        buttons_layout.addWidget(self.button_cancel)

        layout_v.addWidget(self.label)
        layout_v.addWidget(self.ip_input)
        layout_v.addWidget(self.subnet_mask_input)
        layout_v.addLayout(buttons_layout)
        
        layout_v.setSpacing(15)
        
        self.setLayout(layout_v)
        self.setStyleSheet(f"background-color: {Colors.DEEP_PURPLE};")
    
    def __validate(self) -> None:
        """Validates the IP and Mask address entered by the user."""
        
        ip = self.ip_input.text()
        mask = self.subnet_mask_input.text()
        
        if not ip:
            QMessageBox.warning(self, "IP", "Por favor, digite um IP válido.")
            return
        
        if not mask:
            QMessageBox.warning(self, "Máscara", "Por favor, digite uma máscara de sub-rede válida.")
            return
        
        # If the IP and Mask are valid, save them and accept the dialog
        self.__ip = ip
        self.__mask = mask
        
        self.accept()
    
    def get_ip(self) -> str:
        """Returns the last valid IP address entered by the user."""
        
        return self.__ip
    
    def get_mask(self) -> str:
        """Returns the last valid subnet mask entered by the user."""
        
        return self.__mask
    