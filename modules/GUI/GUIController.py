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
        
    def load_samba_settings(self):
        """Loads the SAMBA share settings relevant to the PS2 into the GUI."""
        
        # Stop the SAMBA service when initializing the Manager
        self.samba_manager.stop_server()
        
       # NetBIOS name
        netbios_name = self.samba_manager.get_netbios_name()
        
        # Set the NetBIOS name in the GUI
        line_edit = self.gui.findChild(QLineEdit, WN.NETBIOS_LINE_EDIT.value)
        line_edit.setText(netbios_name)
        
        # Check PS2 share settings
        try:
            self.samba_manager.check_ps2_share_settings()
        
        except TagNotFound:
            self.log("ERRO: Seu SAMBA não está configurado para compartilhar arquivos com o PS2. Vamos configurar isso pra você agora.")
            
            self.samba_manager.create_default_ps2_share_config()
            self.log("Configuração padrão criada.")
        
        except SettingNotFound as e:
            self.log(f"ERRO: {e.error_message}\nO valor padrão dessa configuração e das demais será adicionado.")
            
            if e.setting_name != "path":
                # If the missing setting is not the path, we will add the default configurations and add the found path to it later
                path = self.samba_manager.get_ps2_share_folder_path()
                
                self.samba_manager.create_default_ps2_share_config()
                
                self.samba_manager.set_ps2_share_folder_path(path)
                self.log("Configuração padrão criada.")
            else:
                # If the missing setting is the path, we will recreate the entire default configuration
                self.samba_manager.create_default_ps2_share_config()
                self.log("Configuração padrão criada.")
        
        # At this point, we have the global and the PS2 share settings checked and created if necessary
        # Now we can check if the PS2 share folder exists
        
        if not self.samba_manager.check_ps2_share_folder_exists():
            self.log("ERRO: A pasta compartilhada do PS2 não existe.")
            
            # Adicionar código para criar a pasta compartilhada do PS2
        
        # Now we can check if the PS2 share folder is writable and readable
        if not self.samba_manager.check_ps2_share_folder_rw():
            self.log("ERRO: A pasta compartilhada do PS2 não possui permissão de leitura e escrita.")
            
            # Adicionar código para criar a pasta compartilhada do PS2
        
        # At this point, we have the global and the PS2 share settings checked and created if necessary
        # Now let's load the remaining settings into the GUI
        
        # PS2 share name
        ps2_share_name = self.samba_manager.PS2_SHARE_NAME
                
        # Set the PS2 share path in the GUI
        share_name_label = self.gui.findChild(QLabel, WN.SHARE_NAME_LABEL.value)
        share_name_label.setText(ps2_share_name)
        
        # PS2 share folder path
        ps2_share_folder_path = self.samba_manager.get_ps2_share_folder_path()
        
        # Set the PS2 share path in the GUI
        share_folder_path_label = self.gui.findChild(QLabel, WN.SHARE_FOLDER_PATH.value)
        share_folder_path_label.setText(ps2_share_folder_path)
        
        # Update the server status
        server_status = self.samba_manager.get_server_status()
        self.__update_server_status(server_status)
        
    def __update_server_status(self, status: bool) -> None:
        """Updates the server status label in the GUI."""

        status_label = self.gui.findChild(QLabel, WN.SERVER_STATUS_LABEL.value)
        if status:
            status_label.setText("ATIVO")
        else:
            status_label.setText("INATIVO")

    def log(self, text: str):
        """Logs a message to the log display widget."""
        
        self.log_display_widget.appendPlainText(f"\n{text}")

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
            
            sys.exit(1)
            
        