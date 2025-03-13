import sys
import os
from colorama import Fore
from PyQt6.QtWidgets import *

from modules.SambaManager import SambaManager
from modules.GUI.GUIInterface import GUIInterface
from modules.GUI.WidgetsNames import WidgetsNames as WN
from modules.GUI.ThreeOptionsDialog import ThreeOptionsDialog as TODialog
from modules.Exceptions import *

class PS2NetManagerGUIController:
    """This class handles the logic for events in the 'PS2 Network Manager' GUI."""
    
    def __init__(self, samba_manager: SambaManager, gui: GUIInterface, log_display_widget: QPlainTextEdit):
        """Initializes the GUI controller with a SambaManager instance."""
        
        self.samba_manager = samba_manager
        self.log_display_widget = log_display_widget
        self.gui = gui
        
    def load_samba_settings(self):
        """Loads the SAMBA share settings relevant to the PS2 sharing into the GUI."""
        
        # Stop the SAMBA service when initializing the Manager
        self.samba_manager.stop_server()
        
        # NetBIOS name
        netbios_name = self.samba_manager.get_netbios_name()
        
        # Load the NetBIOS name in the GUI
        line_edit = self.gui.findChild(QLineEdit, WN.NETBIOS_LINE_EDIT.value)
        line_edit.setText(netbios_name)
        
        # Check PS2 share settings
        try:
            self.samba_manager.check_ps2_share_settings()
        
        except TagNotFound:
            err_msg = "ERRO: O SAMBA não está configurado para compartilhar arquivos com o PS2. Vamos configurar isso pra você agora."
            
            self.log(err_msg)
            print(Fore.RED + err_msg)
            
            self.samba_manager.create_default_ps2_share_config()
            self.log("Configuração padrão criada.")
        
        except SettingNotFound as e:
            err_msg = f"ERRO: {e.error_message}\nPara garantir o funcionamento, todas as configurações do compartilhamento do PS2 serão recriadas."
            
            self.log(err_msg)
            print(Fore.RED + err_msg)
            
            if e.setting_name != "path":
                # If the missing setting is not the path, we will save the path that was found
                # and then recreate the default configuration
                path = self.samba_manager.get_ps2_share_folder_path()
                
                self.samba_manager.create_default_ps2_share_config()
                
                # Now we can set the path again
                self.samba_manager.set_ps2_share_folder_path(path)
                
                self.log("Configuração padrão criada.")
            
            else:
                # If the missing setting IS the path, we can recreate the entire default configuration
                self.samba_manager.create_default_ps2_share_config()
                self.log("Configuração padrão criada.")
        
        # At this point, we have the global and PS2 share settings checked and created, if necessary.
        # Now let's do the final validations to the PS2 shared folder.
        self.__check_and_create_ps2_share_folder()
        
        # Now we can check if the PS2 share folder is writable and readable
        if not self.samba_manager.check_ps2_share_folder_rw():
            err_msg = "ERRO: A pasta compartilhada do PS2 não possui permissão de leitura e escrita. Vamos corrigir isso."
            
            self.log(err_msg)
            print(Fore.RED + err_msg)
            
            self.samba_manager.add_ps2_share_folder_permissions()
            
            msg = "As permissões foram adicionadas com sucesso."
            self.log(msg)
            print(Fore.GREEN + msg)
        
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
    
    def __get_folder_path_from_file_dialog(self) -> str:
        """Opens a file dialog to choose the folder where to create the PS2 share folder.
        
        Returns:
            str: The path to the PS2 share folder chosen by the user.
        """
        
        folder_path = QFileDialog.getExistingDirectory(
            self.gui, # Parent widget
            "Escolha onde a pasta compartilhada com o PS2 vai ficar", # Title
            os.path.join(os.sep, "home", self.samba_manager.get_user_name()), # Start at the user's home directory
            QFileDialog.Option.ShowDirsOnly | QFileDialog.Option.DontResolveSymlinks # Options
        )
        
        if folder_path == "":
            # User canceled the dialog
            msg = "Operação cancelada pelo usuário."
            
            self.log(msg)
            print(msg)

            return ""
        
        # Add the folder name to the end of the path
        # The folder name is the PS2 share name
        folder_path = os.path.join(folder_path, self.samba_manager.PS2_SHARE_NAME)
        
        return folder_path
    
    def __check_and_create_ps2_share_folder(self):
        """Checks if the PS2 share folder exists and creates it if it doesn't.
        
        It also updates the SambaManager internally with the new path.
        """
        
        while True:
            # Load the PS2 share folder path internally
            self.samba_manager.load_from_conf_ps2_folder_path()
            
            # Verify if the PS2 share folder exists
            if not self.samba_manager.check_ps2_share_folder_exists():
                self.log("ERRO: A pasta compartilhada do PS2 não existe.")
                
                # Launch a dialog to ask the user where to create the PS2 share folder
                dialog = TODialog(
                    self.gui,
                    "Criar pasta compartilhada com o PS2",
                    "A pasta que será compartilhada com o PS2 não existe. Onde você deseja criá-la?",
                    ["Escolher...", "Local Padrão", "Cancelar"]
                )
                response = dialog.exec()
                
                print(f"Retorno do diálogo: {response}")
                folder_path = ""
                
                if response == 1:
                    # User wants to choose the folder
                    # Let's open a file dialog to choose the folder
                    folder_path = self.__get_folder_path_from_file_dialog()           
                    
                    if folder_path == "":
                        # User canceled the dialog, restart the loop
                        # and ask again
                        continue
                    
                    # Create the folder
                    self.samba_manager.create_ps2_share_folder(folder_path)
                    
                    msg = f"A pasta compartilhada com o PS2 foi criada em: {folder_path}"
                    self.log(msg)
                    print(msg)
                    
                elif response == 2:
                    # User chose to create the folder in the default location
                    folder_path = self.samba_manager.create_ps2_share_folder()
                    
                    msg = f"A pasta compartilhada com o PS2 foi criada no local padrão: {folder_path}"
                    self.log(msg)
                
                else:
                    # User canceled the operation
                    self.log("Operação cancelada pelo usuário.")
                    sys.exit(0)
                
                # Now, let's save the new folder path in the configuration file and internally
                try:
                    self.samba_manager.set_ps2_share_folder_path(folder_path)
                
                except SambaServiceFailure as e:
                    err_msg = f"ERRO DE SERVIÇO: {e}"
                    err_description = "A pasta foi criada e o caminho foi salvo no arquivo de configuração, mas houve um erro ao reiniciar o serviço do SAMBA. Portanto, a pasta ainda não está visível na rede."
                    
                    self.log(f"{err_msg}\n{err_description}")
                    print(f"{err_msg}\n{err_description}")
                
                break
        
            # If the folder already exists, there's nothing to do
            return

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
            
        