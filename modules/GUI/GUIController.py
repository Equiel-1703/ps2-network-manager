import sys
import os
import subprocess
import ipaddress
from colorama import Fore
from PyQt6.QtWidgets import *

from modules.SambaManager import SambaManager
from modules.GUI.GUIInterface import GUIInterface
from modules.GUI.WidgetsNames import WidgetsNames as WN
from modules.GUI.ThreeOptionsDialog import ThreeOptionsDialog as TODialog
from modules.GUI.ListSelectDialog import ListSelectDialog as LSDialog
from modules.GUI.ListAddSelectDialog import ListAddSelectDialog as LASDialog
from modules.GUI.CreateNewIPDialog import CreateNewIPDialog as IPDialog
from modules.Exceptions import *

class PS2NetManagerGUIController:
    """This class handles the logic for events in the 'PS2 Network Manager' GUI."""
    
    def __init__(self, samba_manager: SambaManager, gui: GUIInterface, log_display_widget: QPlainTextEdit):
        """Initializes the GUI controller with a SambaManager instance."""
        
        self.samba_manager = samba_manager
        self.log_display_widget = log_display_widget
        self.gui = gui
        
    def setup_samba_settings(self):
        """
        Loads and sets the proper SAMBA share settings relevant to the PS2 sharing into the GUI.

        Steps:
        1. Stops the SAMBA service.
        2. Loads the NetBIOS name and sets it in the GUI.
        3. Checks and creates the PS2 share settings in smb.conf if necessary.
        4. Validates the PS2 shared folder and sets permissions if needed.
        5. Loads the network interface data.
        6. Loads the remaining settings into the GUI, including PS2 share name and folder path.
        7. Updates the server status in the GUI.
        """
        
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
            
            self.log_error(err_msg)
            
            self.samba_manager.create_default_ps2_share_config()
            self.log_success("Configuração padrão criada.")
        
        except SettingNotFound as e:
            err_msg = f"ERRO: {e.error_message}\nPara garantir o funcionamento, todas as configurações do compartilhamento do PS2 serão recriadas."
            
            self.log_error(err_msg)
            
            if e.setting_name != "path":
                # If the missing setting is not the path, we will save the path that was found
                # and then recreate the default configuration
                path = self.samba_manager.get_ps2_share_folder_path()
                
                self.samba_manager.create_default_ps2_share_config()
                
                # Now we can set the path again
                self.samba_manager.set_ps2_share_folder_path(path)
                
                self.log_success("Configuração padrão criada.")
            
            else:
                # If the missing setting IS the path, we can recreate the entire default configuration
                self.samba_manager.create_default_ps2_share_config()
                self.log_success("Configuração padrão criada.")
        
        # At this point, we have the global and PS2 share settings checked and created, if necessary.
        # Now let's do the final validations to the PS2 shared folder.
        self.__setup_ps2_share_folder()
        
        # Now we can check if the PS2 share folder is writable and readable
        if not self.samba_manager.check_ps2_share_folder_permissions():
            err_msg = "ERRO: A pasta compartilhada do PS2 não possui permissão de leitura e escrita. Vamos corrigir isso."
            
            self.log_error(err_msg)
            
            self.samba_manager.add_ps2_share_folder_permissions()
            
            msg = "As permissões foram adicionadas com sucesso."
            
            self.log_success(msg)
        
        # At this point, we have the global and the PS2 share settings checked and created if necessary
        # Now, let's load the network interface data
        self.__setup_network_interface()

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

            return ""
        
        # Add the folder name to the end of the path
        # The folder name is the PS2 share name
        folder_path = os.path.join(folder_path, self.samba_manager.PS2_SHARE_NAME)
        
        return folder_path
    
    def __setup_ps2_share_folder(self):
        """Checks if the PS2 share folder exists and creates it if it doesn't.
        
        It also updates the SambaManager internally with the new path.
        """
        
        while True:
            # Load the PS2 share folder path internally
            self.samba_manager.load_from_conf_ps2_folder_path()
            
            # Verify if the PS2 share folder exists
            if not self.samba_manager.check_ps2_share_folder_exists():
                self.log_error("ERRO: A pasta compartilhada do PS2 não existe.")
                
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
                    self.log_success(msg)
                    
                elif response == 2:
                    # User chose to create the folder in the default location
                    folder_path = self.samba_manager.create_ps2_share_folder()
                    
                    msg = f"A pasta compartilhada com o PS2 foi criada no local padrão: {folder_path}"
                    self.log_success(msg)
                
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
                    
                    self.log_error(f"{err_msg}\n{err_description}")
                
                break
            else:
                # If the folder already exists, there's nothing to do
                return

    def __update_server_status(self, status: bool) -> None:
        """Updates the server status label in the GUI."""

        status_label = self.gui.findChild(QLabel, WN.SERVER_STATUS_LABEL.value)
        if status:
            status_label.setText("ATIVO")
        else:
            status_label.setText("INATIVO")

    def __setup_network_interface(self):
        """Loads and sets the network interface information into the GUI and internally in the SambaManager."""
        
        # Load blank labels first
        self.__load_interface_blank_labels()
        
        # Let's check what we have in the SAMBA configuration file
        interfaces = self.samba_manager.get_interfaces_in_samba_conf()
        
        # Check amount of interfaces found
        
        if len(interfaces) == 1:
            # Only one interface found, let's use it
            interface = interfaces[0]
            
            self.log(f"Interface de rede encontrada: {interface}")
            
            # If the interface is not available, we need to ask the user to choose another one
            if not self.samba_manager.check_if_interface_exists(interface):
                err_msg = f"ERRO: A interface de rede {interface} não existe."
                
                self.log_error(err_msg)
                
                # Show dialog to the user choose an interface
                self.__configure_network_interface_and_ip()
                return
            
            # If the interface is available, we ask the user to choose an IP address
            else:
                msg = f"A interface de rede {interface} foi encontrada."
                
                self.log_success(msg)
                
                # TODO: Show dialog to the user choose an available IP for the interface
        
        # If there are more than one element in the interfaces field, the second one should be an IP
        # address and the first one should be the interface name
        elif len(interfaces) == 2:
            interface = interfaces[0]
            ip_address = interfaces[1]
            
            # Check if interface is available
            if not self.samba_manager.check_if_interface_exists(interface):
                err_msg = f"ERRO: A interface de rede {interface} não existe."
                
                self.log_error(err_msg)
                
                # TODO: Show dialog to the user choose an interface
                return
            
            # Check if the IP address is valid
            if not self.samba_manager.check_if_ip_is_valid(ip_address):
                err_msg = f"ERRO: O endereço IP {ip_address} não é válido."
                
                self.log_error(err_msg)
                
                # TODO: Show dialog to the user choose an interface (the IP is invalid, so it's better to ask the user
                # for a new interface)
                return
            
            # Check if the IP address is available in the interface
            if not self.samba_manager.check_if_ip_is_bound(ip_address, interface):
                err_msg = f"ERRO: O endereço IP {ip_address} não está disponível na interface {interface}."
                
                self.log_error(err_msg)
                
                # TODO: Show dialog to the user choose an interface (probably the IP is not available anymore, so 
                # it's better to ask the user to choose a new interface)
                return
            
            # If nothing went wrong, we can set the interface and IP address
            msg = f"A interface de rede {interface} foi encontrada e o endereço IP {ip_address} está disponível."
            self.log_success(msg)
            
            try:
                self.samba_manager.set_interface_in_samba_conf(interface, ip_address)
            
            except SambaServiceFailure as e:
                err_msg = f"ERRO DE SERVIÇO: {e.error_message}\nA interface foi alterada no arquivo de configuração, mas houve um erro ao reiniciar o serviço do SAMBA. Portanto, a nova interface ainda não está visível na rede."
                
                self.log_error(err_msg)
        
        # If there are more than two elements or none, we ask for the user to choose
        # the interface
        else:
            if len(interfaces) > 2:
                err_msg = f"ERRO: Mais de duas interfaces encontradas: {interfaces}."
            else:
                err_msg = "ERRO: Nenhuma interface de rede encontrada."
            
            self.log_error(err_msg)
            
            # Show dialog to the user choose an interface
            self.__configure_network_interface_and_ip()
            return    

    def __configure_network_interface_and_ip(self):
        """Shows a dialog to the user to select the network interface and then asks for the IP address."""
        
        # Get GUI elements of the interface data
        interface_name_label = self.gui.findChild(QLabel, WN.INTERFACE_NAME_LABEL.value)
        interface_ip_label = self.gui.findChild(QLabel, WN.INTERFACE_IP_LABEL.value)
        interface_mask_label = self.gui.findChild(QLabel, WN.INTERFACE_MASK_LABEL.value)
        
        available_interfaces = self.samba_manager.get_available_network_interfaces()
        available_interfaces.insert(0, "NENHUMA")
        
        self.log(f"Interfaces de rede disponíveis: {available_interfaces}")
        
        # Show dialog to the user to choose the network interface
        dialog = LSDialog(
            self.gui,
            "Escolher interface de rede",
            "Escolha a interface de rede que deseja usar para o servidor SAMBA",
            available_interfaces
        )
        
        dialog_ret = dialog.exec()
        selected_interface = dialog.get_selected_option()
        
        if dialog_ret == 0 or selected_interface == None:
            # User canceled the dialog
            msg = "Operação cancelada pelo usuário."
            self.log(msg)
            return
    
        if selected_interface == "NENHUMA":
            # Blank values will be set in the GUI
            self.__load_interface_blank_labels()
            
            msg = "Nenhuma interface de rede foi escolhida."
            self.log(msg)
            
            return
        
        # Now let's choose the ip for this interface
        selected_ip = self.__choose_ip_address(selected_interface)
        
        if selected_ip == None:
            return
        
        selected_mask = selected_ip.split(" / ")[1]
        selected_ip = selected_ip.split(" / ")[0]
        
        # Now let's set the interface and IP address in the SambaManager
        try:
            self.samba_manager.set_interface_in_samba_conf(selected_interface, selected_ip)
            
        except SambaServiceFailure as e:
            err_msg = f"ERRO DE SERVIÇO: {e.error_message}\nA interface foi alterada no arquivo de configuração, mas houve um erro ao reiniciar o serviço do SAMBA. Portanto, a nova interface ainda não está visível na rede."
            
            self.log_error(err_msg)
        
        finally:
            # Now let's set the interface and IP address in the GUI
            interface_name_label.setText(selected_interface)
            interface_ip_label.setText(selected_ip)
            interface_mask_label.setText(selected_mask)
        
    def __choose_ip_address(self, interface: str) -> str:
        """Shows a dialog to the user to select the available IP addresses for the provided interface.
        
        Args:
            interface (str): The network interface to choose the IP address for.
        
        Returns:
            str: The selected IP address or None if the user canceled the dialog.
        """
        
        available_ips = self.samba_manager.get_ipv4_addresses_for_interface(interface)
        available_ips = [f"{ip} / {mask}" for ip, mask in available_ips]
        
        dialog = LASDialog(
            self.gui,
            "Escolher IP",
            f"Escolha o endereço IP que deseja usar para a interface {interface}",
            available_ips
        )
        
        dialog.set_add_button_action(lambda: self.__create_new_ip_address(dialog, interface))
        return_value = dialog.exec()
        
        if return_value == 0:
            # User canceled the dialog
            msg = "Operação cancelada pelo usuário."
            self.log(msg)
            return None
        
        return dialog.get_selected_option()
    
    def __create_new_ip_address(self, parent: LASDialog, interface: str):
        """Dialog to create a new IP address and subnet-mask for the provided interface."""
        
        dialog = IPDialog(parent, interface)
        
        dialog_ret = dialog.exec()
        
        if dialog_ret == 0:
            # User canceled the dialog
            msg = "Operação cancelada pelo usuário."
            self.log(msg)
            return
        
        # Get the new IP address and subnet mask
        ip_address = dialog.get_ip()
        subnet_mask = dialog.get_mask()
        
        convert_to_cidr = lambda mask: ipaddress.IPv4Network(f"0.0.0.0/{mask}", strict=False).prefixlen
        
        # Add new IP address to the interface
        try:
            command = ["ip", "addr", "add", f"{ip_address}/{convert_to_cidr(subnet_mask)}", "dev", interface]
            subprocess.run(command, check=True)
            
            # Add new IP and Mask to the list
            parent.add_item_to_list(f"{ip_address} / {subnet_mask}")
            
            self.log_success(f"Novo IP {ip_address} adicionado à interface {interface}.")
            
        except subprocess.CalledProcessError as e:
            self.log_error(f"ERRO: {e}\nNão foi possível adicionar o novo IP à interface {interface}.")
            return

    def __load_interface_blank_labels(self):
        """Loads the interface labels with blank values."""
        
        # Get GUI elements of the interface data
        interface_name_label = self.gui.findChild(QLabel, WN.INTERFACE_NAME_LABEL.value)
        interface_ip_label = self.gui.findChild(QLabel, WN.INTERFACE_IP_LABEL.value)
        interface_mask_label = self.gui.findChild(QLabel, WN.INTERFACE_MASK_LABEL.value)
        
        # Set blank values
        interface_name_label.setText("NENHUMA")
        interface_ip_label.setText("X.X.X.X")
        interface_mask_label.setText("X.X.X.X")

    def log(self, text: str):
        """Logs a message to the log display widget and the terminal."""
        
        self.log_display_widget.appendPlainText(f"\n{text}")
        print(text)
    
    def log_success(self, text: str):
        """Logs a success message to the log display widget and the terminal."""
        
        self.log_display_widget.appendHtml(f"\n<p style='color: green;'>{text}</p>")
        print(Fore.GREEN + text)
    
    def log_error(self, text: str):
        """Logs an error message to the log display widget and the terminal."""
        
        self.log_display_widget.appendHtml(f"\n<p style='color: red;'>{text}</p>")
        print(Fore.RED + text)

    def on_netbios_ok_clicked(self):
        """Handles the 'OK' button click event for the NetBIOS name dialog."""
        
        line_edit = self.gui.findChild(QLineEdit, WN.NETBIOS_LINE_EDIT.value)
        netbios_name = line_edit.text().strip()
        
        try:
            self.samba_manager.set_netbios_name(netbios_name)
        
        except ValueError as e:
            self.log_error(f"ERRO: {e}")
            
            # Put old NetBIOS name back
            line_edit.setText(self.samba_manager.get_netbios_name())
            
        except SambaServiceFailure as e:
            self.log_error(f"ERRO DE SERVIÇO: {e}")
            
            self.log("O nome foi alterado no arquivo de configuração, mas houve um erro ao reiniciar o serviço do SAMBA. Portanto, o novo nome ainda não está visível na rede.")        
        except Exception as e:
            self.log_error(f"ERRO DESCONHECIDO: {e}")
            
            sys.exit(1)

    def on_change_folder_button_clicked(self):
        """Handles the 'Change Folder' button click event."""
        
        # Launch a dialog to ask the user where to create the PS2 share folder
        dialog = TODialog(
            self.gui,
            "Criar pasta compartilhada com o PS2",
            "Onde você deseja criar a pasta compartilhada com o PS2?",
            ["Escolher...", "Local Padrão", "Cancelar"]
        )
        response = dialog.exec()
        
        folder_path = ""
        if response == 1:
            # User wants to choose the folder
            # Let's open a file dialog to choose the folder
            folder_path = self.__get_folder_path_from_file_dialog()           
            
            if folder_path == "":
                # User canceled the dialog, restart the loop
                return
            
            # Create the folder
            self.samba_manager.create_ps2_share_folder(folder_path)
            
            msg = f"A pasta compartilhada com o PS2 foi criada em: {folder_path}"
            self.log_success(msg)
            
        elif response == 2:
            # User chose to create the folder in the default location
            folder_path = self.samba_manager.create_ps2_share_folder()
            
            msg = f"A pasta compartilhada com o PS2 foi criada no local padrão: {folder_path}"
            self.log_success(msg)
            
        else:
            # User canceled the operation
            self.log("Operação cancelada pelo usuário.")
            return
        
        # Now, let's save the new folder path in the configuration file and internally
        try:
            
            self.samba_manager.set_ps2_share_folder_path(folder_path)
        
        except SambaServiceFailure as e:
            err_msg = f"ERRO DE SERVIÇO: {e}"
            err_description = "A pasta foi criada e o caminho foi salvo no arquivo de configuração, mas houve um erro ao reiniciar o serviço do SAMBA. Portanto, a pasta ainda não está visível na rede."
            
            self.log_error(f"{err_msg}\n{err_description}")
        
        finally:
            # Update the label in the GUI
            share_folder_path_label = self.gui.findChild(QLabel, WN.SHARE_FOLDER_PATH.value)
            share_folder_path_label.setText(folder_path)