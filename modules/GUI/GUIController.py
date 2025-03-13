import sys
from PyQt6.QtWidgets import *

from modules.SambaManager import SambaManager
from modules.GUI.GUIInterface import GUIInterface
from modules.GUI.WidgetsNames import WidgetsNames as WN
from modules.Exceptions import *

class PS2NetManagerGUIController:
    """This class handles the logic for events in the 'PS2 Network Manager' GUI."""
    
    def __init__(self, samba_manager: SambaManager, gui: GUIInterface, log_display_widget: QPlainTextEdit):
        """Initializes the GUI controller with a SambaManager instance."""
        
        self.samba_manager = samba_manager
        self.log_display_widget = log_display_widget
        self.gui = gui
        
    def log(self, text: str):
        """Logs a message to the log display widget."""
        
        self.log_display_widget.appendPlainText(f"\n{text}")
    
    def initialize_netbios_line_edit(self):
        """Initializes the NetBIOS name line edit with the current NetBIOS name."""
        
        netbios_name = self.samba_manager.get_netbios_name()
        
        netbios_line_edit = self.gui.findChild(QLineEdit, WN.NETBIOS_LINE_EDIT.value)
        netbios_line_edit.setText(netbios_name)
        
    def on_netbios_ok_clicked(self):
        """Handles the 'OK' button click event for the NetBIOS name dialog."""
        
        line_edit = self.gui.findChild(QLineEdit, WN.NETBIOS_LINE_EDIT.value)
        netbios_name = line_edit.text().strip()
        
        try:
            self.samba_manager.set_netbios_name(netbios_name)
        
        except ValueError as e:
            self.log(f"ERRO: {e}")
            
            # Put old NetBIOS name back
            line_edit.setText(self.samba_manager.get_netbios_name())
            
        except SambaServiceFailure as e:
            self.log(f"ERRO DE SERVIÇO: {e}")
            
            self.log("O nome foi alterado no arquivo de configuração, mas houve um erro ao reiniciar o serviço do SAMBA. Portanto, o novo nome ainda não está visível na rede.")        
        except Exception as e:
            self.log(f"ERRO DESCONHECIDO: {e}")
            
            # Put old NetBIOS name back
            sys.exit(1)
            
        