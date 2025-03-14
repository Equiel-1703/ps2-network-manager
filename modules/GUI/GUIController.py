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
from modules.GUI.GUIColors import GUIColors as Colors
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
    
        # Now, let's load the network interface data, but first, we will load the default blank values
        # in the GUI, so the user can see that there is no interface selected when the GUI is loaded
        self.__load_interface_blank_labels()
        
        # Now we can load the network interface data from the Samba configuration file
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
            status_label.setStyleSheet(f"color: {Colors.LIGHT_GREEN};")
        else:
            status_label.setText("INATIVO")
            status_label.setStyleSheet(f"color: {Colors.SOFT_RED};")

    def __setup_network_interface(self):
        """
        Loads and sets the network interface information from the Samba config file into the GUI and internally in the SambaManager.

        Steps:
        1. Retrieve the interfaces from the Samba configuration file.
        2. Parse the interface settings to get the interface and IP address.
        3. Validate and set the interface and IP address in the SambaManager and GUI.
        4. Log a message if no valid interface and IP address are found.
        """
        
        # Let's check what we have in the SAMBA configuration file
        samba_interfaces = self.samba_manager.get_interfaces_in_samba_conf()
        interface, ip_address = self.__parse_smb_conf_interface_settings(samba_interfaces)
        
        if interface is not None and ip_address is not None:
            self.samba_manager.set_interface_and_ip(interface, ip_address)
            self.__set_interface_and_ip_on_gui(interface, ip_address)
        
        elif interface is not None and ip_address is None:
            # If we have an interface but the IP address wasn't found, we can ask the user
            # if he wants we add it in the interface
            
            # We know the second element in the samba_interfaces list is the IP address
            # because we are using the __parse_smb_conf_interface_settings method
            ip_address = self.samba_manager.get_interfaces_in_samba_conf()[1]
            
            
            msg = f"A interface de rede {interface} foi encontrada, mas o IP configurado {ip_address} não foi encontrado nela. Deseja adicionar esse IP à interface?"
            details = (
                "Se você não quiser adicionar o IP à interface, o PS2 Network Manager vai configurar a interface e o IP do Samba como 'NENHUM'. "
                "Isso é necessário pois o protocolo SMBv1 usado pelo PS2 tem vulnerabilidades de segurança e não sabemos se essa interface possui algum endereço IPv4 disponível. "
                "Portanto, isso é necessário para garantir a segurança do sistema e a confiabilidade do PS2 Network Manager."
            )
            
            message_box = QMessageBox(self.gui)
            message_box.setWindowTitle("Adicionar IP à interface")
            message_box.setText(msg)
            message_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            message_box.setDefaultButton(QMessageBox.StandardButton.Yes)
            message_box.setIcon(QMessageBox.Icon.Question)
            message_box.setDetailedText(details)
            
            reply = message_box.exec()
            
            if reply == QMessageBox.StandardButton.Yes:
                # The user wants to add the IP address to the interface
                self.__add_ip_address_to_interface(interface, ip_address)
                self.__set_interface_and_ip_on_gui(interface, ip_address)
                self.samba_manager.set_interface_and_ip(interface, ip_address)
            else:
                # The user doesn't want to add the IP address to the interface.
                # We can't use the interface without the IP address. This is due to security vulnerabilities of the SMBv1 protocol and
                # also because we don't know if this interface has any available IPv4 address.
                # To guarantee the security of the system and reability of the PS2Manager, we will set the interface and IP address to None
                self.samba_manager.set_interface_and_ip(None, None)
                self.__load_interface_blank_labels()
        else:
            msg = "Por favor, escolha a interface de rede e o endereço IP que deseja usar para o servidor SAMBA."
            self.log(msg)

    def __parse_smb_conf_interface_settings(self, interfaces: list[str]) -> tuple[str, str] | tuple[str, None] | tuple[None, None]:
        """Parses the interfaces list provided from the Samba configuration file and returns the interface and IP address if they are valid.
        Args:
            interfaces (list[str]): The list of interfaces found in the Samba configuration file.
            
        Steps:
        1. If no interfaces are found, log an error and return (None, None).
        2. If more than 2 interfaces are found, log an error and return (None, None).
        3. If only one interface is found, check if it exists and return it with 'None' as the IP address.
        4. If two interfaces are found, check if the first one is a valid interface and the second one is a valid IP address.
        
        Returns:
            tuple[str, str]: The interface and IP address found in the configuration file (interface, ip).
            tuple[str, None]: If the interface was found but the IP address was not found (interface, None).
            tuple[None, None]: If the interface/ip address were invalid or not found.
        """
        
        if len(interfaces) == 0:
            # No interfaces found in the configuration file
            err_msg = "ERRO: Nenhuma interface de rede encontrada."
            
            self.log_error(err_msg)
            
            return (None, None)
    
        elif len(interfaces) > 2:
            # More than 2 elements in the interfaces field
            err_msg = f"ERRO: Mais de duas interfaces encontradas: {interfaces}. Somente uma interface de rede e um endereço IP são permitidos."
            
            self.log_error(err_msg)
            
            return (None, None)
        
        elif len(interfaces) == 1:
            # Only one interface was in the SAMBA configuration file
            # Let's check if the interface is available
            interface = interfaces[0]
            
            self.log(f"Interface de rede encontrada: {interface}")
            
            # Check if the interface is available
            if not self.samba_manager.check_if_interface_exists(interface):
                err_msg = f"ERRO: A interface de rede {interface} não existe."
                
                self.log_error(err_msg)
                
                # Interface settings not found
                return (None, None)
            
            # If the interface is available, we can return it
            else:
                msg = f"A interface de rede {interface} foi encontrada. Mas não foi encontrado um endereço IP para ela."
                
                self.log_success(msg)
                
                return (None, None)
        
        # If there are more than one element in the interfaces field, the second one should be an IP
        # address and the first one should be the interface name
        elif len(interfaces) == 2:
            # Let's check these values
            interface, ip_address = interfaces[0], interfaces[1]
            
            # Check if interface is available
            if not self.samba_manager.check_if_interface_exists(interface):
                err_msg = f"ERRO: A interface de rede {interface} não existe."
                
                self.log_error(err_msg)
                
                return (None, None)
            
            # Check if the IP address is valid
            if not self.samba_manager.check_if_ip_is_valid(ip_address):
                err_msg = f"ERRO: O endereço IP {ip_address} não é válido."
                
                self.log_error(err_msg)
                
                return (None, None)
            
            # Check if the IP address is available in the interface
            if not self.samba_manager.check_if_ip_is_bound(ip_address, interface):
                err_msg = f"ERRO: O endereço IP {ip_address} não está disponível na interface {interface}."
                
                self.log_error(err_msg)
                
                return (interface, None)
        
            # OK, everything is fine, let's return the interface and IP address!
            msg = f"A interface de rede {interface} e o endereço IP {ip_address} foram encontrados e validados!"
            
            self.log_success(msg)
            
            return (interface, ip_address)
    
        # This return should never be reached, but just in case
        return (None, None)

    def __add_ip_address_to_interface(self, interface: str, ip_address: str, subnet_mask: str = "255.255.255.0") -> None:
        """Adds a new IP address to the provided interface.
        
        Args:
            interface (str): The network interface to add the IP address to.
            ip_address (str): The new IP address to add.
            subnet_mask (str): The subnet mask for the new IP address. Defaults to 255.255.255.0
        """
        
        def convert_to_cidr(mask):
            return ipaddress.IPv4Network(f"0.0.0.0/{mask}", strict=False).prefixlen
        
        # Add new IP address to the interface
        try:
            command = ["ip", "addr", "add", f"{ip_address}/{convert_to_cidr(subnet_mask)}", "dev", interface]
            subprocess.run(command, check=True)
            
            self.log_success(f"Novo IP {ip_address} adicionado à interface {interface}.")
            
        except subprocess.CalledProcessError as e:
            self.log_error(f"ERRO: {e}\nNão foi possível adicionar o novo IP à interface {interface}.")
        except FileNotFoundError:
            self.log_error("ERRO: O comando 'ip' não foi encontrado. Certifique-se de que o programa 'ip' está instalado.")
        except Exception as e:
            self.log_error(f"ERRO DESCONHECIDO: {e}")

    def __create_new_ip_dialog(self, parent: LASDialog, interface: str, ip_mask_string_formatter: callable) -> None:
        """Dialog to create a new IP address and subnet-mask for the provided interface.
        
        Returns:
            None
        """
        
        create_ip_dialog = IPDialog(parent, interface)
        dialog_ret = create_ip_dialog.exec()
        
        if dialog_ret == 0:
            # User canceled the dialog
            msg = "Operação cancelada pelo usuário."
            self.log(msg)
            return
        
        # Get the new IP address and subnet mask from create_ip_dialog
        ip_address = create_ip_dialog.get_ip()
        subnet_mask = create_ip_dialog.get_mask()
        
        # Add the new IP address to the interface
        self.__add_ip_address_to_interface(interface, ip_address, subnet_mask)

        # Add new IP and Mask to the list
        parent.add_item_to_list(ip_mask_string_formatter(ip_address, subnet_mask))
        
        return

    def __select_ip_address_dialog(self, interface: str) -> str | None:
        """Shows a dialog where the user cam choose an IP from the available IP addresses of the provided interface.
        
        It also allows the user to create a new IP address and subnet mask for the interface.
        
        Args:
            interface (str): The network interface to choose the IP address for.
        
        Returns:
            str: The selected IP address (without mask) or None if the user canceled the dialog.
        """
        
        available_ips = self.samba_manager.get_ipv4_addresses_for_interface(interface)
        ip_mask_string_formatter = lambda ip, mask: f"{ip} / {mask}"
        
        ip_selection_dialog = LASDialog(
            self.gui,
            "Escolher IP",
            f"Escolha o endereço IP que deseja usar para a interface {interface}",
            (ip_mask_string_formatter(ip, mask) for ip, mask in available_ips)
        )
        
        # Set action for the 'Adicionar...' button in the ip_selection_dialog
        ip_selection_dialog.set_add_button_action(lambda: self.__create_new_ip_dialog(ip_selection_dialog, interface, ip_mask_string_formatter))
        return_value = ip_selection_dialog.exec()
        
        if return_value == 0:
            # User canceled the dialog
            msg = "Operação cancelada pelo usuário."
            self.log(msg)
            return None
        
        ip_selected = ip_selection_dialog.get_selected_option()
        
        if ip_selected is not None:
            # If the user selected an IP address, we need to split it to get the IP address only
            ip_selected = ip_selected.split(" / ")[0].strip()
        
        return ip_selected

    def __load_interface_blank_labels(self) -> None:
        """Loads the interface labels with blank values."""
        
        # Get GUI elements of the interface data
        interface_name_label = self.gui.findChild(QLabel, WN.INTERFACE_NAME_LABEL.value)
        interface_ip_label = self.gui.findChild(QLabel, WN.INTERFACE_IP_LABEL.value)
        interface_mask_label = self.gui.findChild(QLabel, WN.INTERFACE_MASK_LABEL.value)
        
        # Set blank values
        interface_name_label.setText("NENHUMA")
        interface_ip_label.setText("X.X.X.X")
        interface_mask_label.setText("X.X.X.X")

    def __set_interface_and_ip_on_gui(self, interface: str, ip: str):
        """Set the provided interface and IP address in the GUI."""
        
        # Get GUI elements of the interface data
        interface_name_label = self.gui.findChild(QLabel, WN.INTERFACE_NAME_LABEL.value)
        interface_ip_label = self.gui.findChild(QLabel, WN.INTERFACE_IP_LABEL.value)
        interface_mask_label = self.gui.findChild(QLabel, WN.INTERFACE_MASK_LABEL.value)
        
        # Set the values in the GUI
        interface_name_label.setText(interface)
        interface_ip_label.setText(ip)
        interface_mask_label.setText(self.samba_manager.get_subnet_mask_for_ip(ip))

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

    def on_change_folder_button_clicked(self) -> None:
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
    
    def on_change_interface_button_clicked(self) -> None:
        """Shows a dialog to the user to select the network interface and another dialog to prompt for the IP address.
        
        Returns:
            None
        """
        
        available_interfaces = self.samba_manager.get_available_network_interfaces()
        available_interfaces.insert(0, "NENHUMA")
        
        self.log(f"Interfaces de rede disponíveis: {available_interfaces}")
        
        # Show dialog to the user choose the network interface he wants to use
        network_interface_selection_dialog = LSDialog(
            self.gui,
            "Escolher interface de rede",
            "Escolha a interface de rede que deseja usar para o servidor SAMBA",
            available_interfaces
        )
        
        dialog_ret = network_interface_selection_dialog.exec()
        selected_interface = network_interface_selection_dialog.get_selected_option()
        
        # Check if the user canceled the dialog
        if dialog_ret == 0 or selected_interface == None:
            msg = "Operação cancelada pelo usuário."
            self.log(msg)
            return
    
        # Check if the user selected the "NENHUMA" option
        if selected_interface == "NENHUMA":
            # Blank values will be set in the GUI
            self.__load_interface_blank_labels()
            
            msg = "Nenhuma interface de rede foi escolhida."
            self.log(msg)
            
            # Erase the interface and IP address in the SambaManager and config file
            self.samba_manager.set_interface_and_ip(None, None)
            
            return
        
        # If one of the available interfaces was selected, we can prompt for the IP address
        selected_ip = self.__select_ip_address_dialog(selected_interface)
        
        # Check if the user canceled the dialog
        if selected_ip == None:
            msg = "Operação cancelada pelo usuário."
            self.log(msg)
            return
        
        # If the user selected an interface and a valid IP address we can set these values
        # in the SambaManager and in the GUI
        self.samba_manager.set_interface_and_ip(selected_interface, selected_ip)
        self.__set_interface_and_ip_on_gui(selected_interface, selected_ip)
        
        self.log_success(f"Interface de rede {selected_interface} e endereço IP {selected_ip} escolhidos com sucesso.")

    def on_start_server_button_clicked(self) -> None:
        """Handles the 'Start Server' button click event."""
        
        # Start the Samba server
        try:
            self.samba_manager.start_server()
            
            msg = "Servidor SAMBA iniciado com sucesso."
            self.log_success(msg)
            
        except SambaServiceFailure as e:
            err_msg = f"ERRO DE SERVIÇO: {e}"
            err_description = "O servidor SAMBA não pôde ser iniciado. Verifique o log para mais detalhes."
            
            self.log_error(f"{err_msg}\n{err_description}")
        
        except ValueError as e:
            err_msg = f"ERRO: {e}"
            
            self.log_error(err_msg)
            
            message_box = QMessageBox(self.gui)
            message_box.setWindowTitle("Erro")
            message_box.setText(err_msg)
            message_box.setIcon(QMessageBox.Icon.Critical)
            message_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            message_box.exec()
        
        except Exception as e:
            err_msg = f"ERRO DESCONHECIDO: {e}"
            
            self.log_error(err_msg)
        
        finally:
            # Update the server status in the GUI
            self.__update_server_status(self.samba_manager.get_server_status())
    
    def on_stop_server_button_clicked(self) -> None:
        """Handles the 'Stop Server' button click event."""
        
        # Stop the Samba server
        try:
            self.samba_manager.stop_server()
            
            msg = "Servidor SAMBA parado com sucesso."
            self.log_success(msg)
        
        except SambaServiceFailure as e:
            err_msg = f"ERRO DE SERVIÇO: {e}"
            err_description = "O servidor SAMBA não pôde ser parado. Verifique o log para mais detalhes."
            
            self.log_error(f"{err_msg}\n{err_description}")
            self.__update_server_status(self.samba_manager.get_server_status())
        
        except Exception as e:
            err_msg = f"ERRO DESCONHECIDO: {e}"
            
            self.log_error(err_msg)
        
        finally:
            # Update the server status in the GUI
            self.__update_server_status(self.samba_manager.get_server_status())