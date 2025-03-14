import os
import re
import sys
import pwd
import grp
import psutil
import socket
from colorama import Fore

from modules.Exceptions import *

class SambaManager:
    SAMBA_CONF_PATH = "/etc/samba/smb.conf"
    DEFAULT_NETBIOS_NAME = "SAMBA"
    PS2_SHARE_NAME = "PS2SMB"

    __netbios_name = ""
    __user_name = ""
    __shared_ps2_folder_path = ""
    
    __server_active = False
    
    __server_ip = None
    __server_interface = None

    def __init__(self, debug=False):
        self.debug = debug

        # Check if samba config file exists
        if not os.path.exists(self.SAMBA_CONF_PATH):
            raise SambaConfNotFound(self.SAMBA_CONF_PATH)
        
        # Get user name
        try:
            self.__user_name = os.getlogin()
        except OSError:
            print(Fore.RED + "ERRO: Não foi possível obter o nome de usuário do sistema.")
            sys.exit(1)
        except Exception as e:
            print(Fore.RED + f"ERRO DESCONHECIDO: {e}")
            sys.exit(1)
            
        if self.debug:
            print(Fore.LIGHTGREEN_EX + f"Nome de usuário do sistema: {self.__user_name}")
        
        self.stop_server()

    # --- UTILITY METHODS ---
    
    def __read_samba_conf(self) -> list:
        """Reads the SAMBA configuration file and returns its contents as a list of strings, removing comments and blank lines.

        Returns:
            list: The SAMBA configuration file contents as a list of strings.
        """
        conf_file = open(self.SAMBA_CONF_PATH, "r")
        original_conf_data = conf_file.readlines()
        conf_file.close()

        conf_data = []
        # Reoving comments and blank lines
        for line in original_conf_data:
            if line[0] != "#" and line[0] != ";" and line != "\n":
                conf_data.append(line)

        return conf_data

    def __check_if_tag_exists(self, tag: str, conf_data: str) -> bool:
        """Checks if a tag exists in a configuration file.

        Args:
            tag (str): The tag to search for.
            conf_data (str): The configuration file data as a unique string.
        
        Returns:
            bool: True if the tag exists, False otherwise.
        """
        tag_data = re.search(rf"\[{tag.strip()}\]\s*", conf_data)

        if tag_data is not None:
            return True
        else:
            return False

    def __check_if_setting_exists(self, tag: str, setting: str, conf_data: str) -> bool:
        """Checks if a setting exists in a tag in a configuration file.

        Args:
            tag (str): The tag to search for.
            setting (str): The setting to search for in the tag.
            conf_data (str): The configuration file data as a unique string.
        
        Returns:
            bool: True if the setting exists, False otherwise.
        """
        
        tag_data = self.__extract_tag_content(tag, conf_data)
        setting_data = re.search(rf"\s*{setting} = .*", tag_data)

        if setting_data is not None:
            return True
        else:
            return False

    def __create_tag(self, tag: str, conf_data: str) -> str:
        """Creates an empty tag in a configuration file.

        Args:
            tag (str): The tag to create.
            conf_data (str): The configuration file data as a unique string.
        
        Returns:
            str: The new configuration file data with the created tag at the end.
        """
        
        # Adding the tag header to the new content
        tag_header = f"\n\n[{tag}]\n"

        # Removing trailing spaces only at the end of the file
        conf_data = conf_data.rstrip() + tag_header

        return conf_data

    def __extract_tag_content(self, tag: str, conf_data: str) -> str:
        """Extracts the content of a tag from a configuration file.

        Args:
            tag (str): The tag to search for.
            conf_data (str): The configuration file data as a unique string.
        
        Returns:
            str: The content of the tag.
        
        Raises:
            TagNotFound: If the tag is not found in the configuration file.
        """

        tag_data = re.search(rf"\[{tag}\]\s*(?P<tag_data>.*?)(?=\[|$)", conf_data, flags=re.DOTALL)

        if tag_data is not None:
            return tag_data.group("tag_data").strip()
        else:
            raise TagNotFound(tag)
    
    def __update_tag_content(self, tag: str, new_content: list, conf_data: str) -> str:
        """Updates the content of a tag in a configuration file.

        Args:
            tag (str): The tag to search for.
            new_content (list): The new content of the tag (only the content, not the tag itself) as list of strings.
            conf_data (str): The configuration file to update as a unique string.

        Returns:
            str: The new configuration file data with the updated tag content.
        """

        # Adding the tag header to the new content
        new_content.insert(0, f"[{tag}]")
        
        # Strip new content for consistency indentation
        for i in range(len(new_content)):
            new_content[i] = new_content[i].strip()
        
        # Removing empty lines
        new_content = [line for line in new_content if line != ""]

        # Joining the new content and adding 3 spaces before each line
        indentation = "\n   "
        new_content = indentation.join(new_content)
        new_content += "\n"
        
        # Escaping backslashes
        new_content = new_content.replace("\\", "\\\\")

        # Updating the tag content
        conf_data = re.sub(rf"\[{tag}\]\s*(.*?)(?=\[|$)", new_content, conf_data, flags=re.DOTALL)

        return conf_data
    
    def __update_setting_in_tag(self, tag: str, setting: str, new_value: str, conf_data: str) -> str:
        """Updates a setting in a tag in a configuration file.
        
        If the setting doesn't exist, it will be added at the end of the tag.

        Args:
            tag (str): The tag to search for.
            setting (str): The setting to update.
            new_value (str): The new value of the setting.
            conf_data (str): The configuration file to update as a unique string.

        Returns:
            str: The new configuration file data with the updated setting.
        """
        # Extract tag content
        tag_data = self.__extract_tag_content(tag, conf_data)

        # Escape backslashes in new value for setting
        new_value = new_value.replace("\\", "\\\\")

        if not self.__check_if_setting_exists(tag, setting, conf_data):
            # If the setting doesn't exist, we add it to the end of the tag
            tag_data += f"\n   {setting} = {new_value}"
        else:
            # If the setting exists, we update it
            tag_data = re.sub(rf"{setting} = .*", f"{setting} = {new_value}", tag_data)

        # Update tag content in configuration data
        conf_data = self.__update_tag_content(tag, tag_data.split("\n"), conf_data)

        return conf_data

    def __remove_setting_from_tag(self, tag: str, setting: str, conf_data: str) -> str:
        """Removes a setting from a tag in a configuration file.
        
        If the setting doesn't exist, this method does nothing.

        Args:
            tag (str): The tag to search for.
            setting (str): The setting to remove.
            conf_data (str): The configuration file to update as a unique string.

        Returns:
            str: The new configuration file data with the setting removed.
        """
        # Extract tag content
        tag_data = self.__extract_tag_content(tag, conf_data)

        # Remove the setting from the tag content
        tag_data = re.sub(rf"\s*{setting} = .*", "", tag_data)

        # Update tag content in configuration data
        conf_data = self.__update_tag_content(tag, tag_data.split("\n"), conf_data)

        return conf_data

    def __extract_setting_from_tag(self, tag: str, setting: str, conf_data: str) -> str:
        """Extracts a setting from a tag in a configuration file.

        Args:
            tag (str): The tag to search for.
            setting (str): The setting to extract.
            conf_data (str): The configuration file to search in as a unique string.

        Returns:
            str: The value of the setting.

        Raises:
            SettingNotFound: If the setting is not found in the tag.
        """
        # Extract tag content
        tag_data = self.__extract_tag_content(tag, conf_data)

        # Extract setting value
        setting_value = re.search(rf"\s*{setting} = (.*)", tag_data)

        if setting_value is not None:
            return setting_value.group(1).strip()
        else:
            raise SettingNotFound(setting)

    def __validate_netbios_name(self, netbios_name: str) -> None:
        """Validates a NetBIOS name.

        Args:
            netbios_name (str): The NetBIOS name to validate.

        Raises:
            ValueError: If the NetBIOS name is empty, has more than 15 characters or contains invalid characters.
        """
        if netbios_name == "":
            raise ValueError("O nome NetBIOS não pode ser vazio.")
        elif len(netbios_name) > 15:
            raise ValueError("O nome NetBIOS não pode ter mais de 15 caracteres.")
        elif not re.match(r"[a-zA-Z0-9][a-zA-Z0-9\-\.]*[a-zA-Z0-9]", netbios_name):
            raise ValueError("O nome NetBIOS só pode conter letras, números, hífens e pontos. Não deve ter espaços nem caracteres especiais. Deve começar e terminar com letras ou números e não pode ultrapassar 15 caracteres.")

    def get_user_name(self) -> str:
        """Returns the user name of the system.

        Returns:
            str: The user name of the system.
        """
        return self.__user_name

    def get_user_info(self) -> dict:
        """Returns the user id and group id of the system user.
        
        Returns:
            dict: A dictionary with the user id and group id of the system user.
        """
        user_info = pwd.getpwnam(self.__user_name)
        
        return {
            "user_id": user_info.pw_uid,
            "group_id": user_info.pw_gid
        }

    # --- GLOBAL SAMBA METHODS ---

    def check_global_samba_conf(self) -> bool:
        """Checks if the global SAMBA configuration is correct for communicating with the PS2.

        Returns:
            bool: True if the global SAMBA configuration is correct, False otherwise.

        Raises:
            GlobalSettingsNotFound: If the [global] section is not found in the SAMBA configuration.
        """
        conf_data = self.__read_samba_conf()

        if self.debug:
            print()
            print(Fore.CYAN + "Verificando a seção [global] do arquivo de configuração do SAMBA...")
            print(Fore.CYAN + f"Dados lidos de {self.SAMBA_CONF_PATH}:")
            for line in conf_data:
                print(line, end='')
            print()

        conf_data = "".join(conf_data)
        global_config_data = self.__extract_tag_content("global", conf_data)

        if global_config_data is None:
            raise GlobalSettingsNotFound()

        if self.debug:
            print(Fore.CYAN + "Dados da seção [global]:")
            print(global_config_data)
        
        # Validando a seção [global]
        global_valid = True

        global_regexes = [r"\s*netbios name = .*", r"\s*server min protocol = NT1", r"\s*client min protocol = NT1"]

        for regex in global_regexes:
            if not re.search(regex, global_config_data):
                global_valid = False
                print(Fore.RED + f"Erro: {regex} não encontrado no arquivo de configuração.")

        return global_valid    

    def backup_and_fix_global_conf(self) -> None:
        """Backups the original SAMBA configuration file (if it isn't already) and updates the global SAMBA configuration to communicate with the PS2."""

        # Creating a backup of the original SAMBA configuration file (if it doesn't already exist)
        os.system(f"cp --update=none {self.SAMBA_CONF_PATH} {self.SAMBA_CONF_PATH}.bak")

        # Reading the SAMBA configuration file
        conf_data = self.__read_samba_conf()

        # Extracting the [global] section content
        global_config_data = self.__extract_tag_content("global", "".join(conf_data))

        # Check for netbios name
        netbios_name = re.search(r"\s*netbios name = (.*)", global_config_data)

        if netbios_name is not None:
            # If we find the netbios name, we remove the line with it to add it later
            global_config_data = re.sub(r"\s*netbios name = (.*)", "", global_config_data)
            # Save the netbios name already set
            netbios_name = netbios_name.group(1)
        else:
            # If we don't find the netbios name, we'll add a default name
            netbios_name = self.DEFAULT_NETBIOS_NAME

        # Removing settings that may already exist but we need to ensure they are correct
        global_config_data = re.sub(r"\bserver min protocol = .*|\bclient min protocol = .*", "", global_config_data).strip()
        print(Fore.GREEN + "Configurações antigas removidas.")

        if self.debug:
            print()
            print(Fore.CYAN + "Arquivo sem as configurações antigas:")
            print(global_config_data)
            print()

        # Splitting the global configuration data into lines
        global_config_data = global_config_data.split("\n")

        for i in range(len(global_config_data)):
            # Removing leading and trailing whitespaces
            global_config_data[i] = global_config_data[i].strip()
        
        # Adding the new settings
        global_config_data.insert(0, "netbios name = " + netbios_name)
        global_config_data.insert(1, "server min protocol = NT1")
        global_config_data.insert(2, "client min protocol = NT1")

        # Removing the old [global] section from the original configuration file
        conf_data = self.__update_tag_content("global", global_config_data, "".join(conf_data))

        # Writing the new configuration file
        conf_file = open(self.SAMBA_CONF_PATH, "w")
        conf_file.write(conf_data)
        conf_file.close()

        print(Fore.GREEN + "Configurações globais do compartilhamento SAMBA atualizadas com sucesso!")

        if self.debug:
            print()
            print(Fore.CYAN + "Novo arquivo de configuração do SAMBA:")
            print(conf_data.strip())
            print()
    
    def get_netbios_name(self) -> str:
        """Returns the NetBIOS name of the SAMBA server.

        Returns:
            str: The NetBIOS name of the SAMBA server.
        """
        if self.__netbios_name == "":
            conf_data = self.__read_samba_conf()
            self.__netbios_name = self.__extract_setting_from_tag("global", "netbios name", "".join(conf_data))
        
        return self.__netbios_name
    
    def set_netbios_name(self, netbios_name: str) -> None:
        """Sets the NetBIOS name of the SAMBA server.

        Args:
            netbios_name (str): The new NetBIOS name of the SAMBA server.

        Raises:
            ValueError: If the NetBIOS name is the same, empty, has more than 15 characters or contains invalid characters.
            SambeServiceFailure: If the service restart command returns a non-zero value.
        """

        self.__validate_netbios_name(netbios_name)
        
        if self.__netbios_name == netbios_name:
            raise ValueError("O nome NetBIOS informado é o mesmo que já está configurado.")

        conf_data = self.__read_samba_conf()
        conf_data = self.__update_setting_in_tag("global", "netbios name", netbios_name, "".join(conf_data))

        conf_file = open(self.SAMBA_CONF_PATH, "w")
        conf_file.write(conf_data)
        conf_file.close()

        self.__netbios_name = netbios_name
        
        if self.debug:
            print(Fore.GREEN + f"Nome NetBIOS alterado para '{netbios_name}' com sucesso!")
        
        # Restart server (if active) to changes take effect
        if self.__server_active:
            self.restart_server()
    
    # --- PS2 SHARE METHODS ---
    
    def __get_ps2_default_folder_path(self) -> str:
        """Returns the default path for the PS2 share folder.
        The user_name is used to create the default shared folder path, wich is /home/#user_name/PS2SMB.
        
        Returns:
            str: The default path for the PS2 share folder.
        """
        
        # Creating default folder path: /home/<user_name>/PS2SMB
        ps2_default_folder_location = os.path.join(os.sep, "home", self.__user_name, self.PS2_SHARE_NAME)
        
        return ps2_default_folder_location
    
    def __get_ps2_force_user(self) -> str:
        """Returns the user name of the system to be used as the force user for the PS2 share configuration.
        The user name is used to create the default shared folder path, wich is /home/#user_name/PS2SMB.
        
        Returns:
            str: The user name of the system.
        """
        
        # Getting the user name
        ps2_force_user = self.__user_name
        
        return ps2_force_user
    
    def __get_default_ps2_share_settings(self) -> list:
        """Returns the default settings for the PS2 share configuration.
        The user_name is used to create the default shared folder path, wich is /home/#user_name/PS2SMB.
        
        Returns:
            list: The default settings for the PS2 share configuration.
        """
        
        ps2_default_settings = [
            "comment = Pasta compartilhada com o PS2",
            "guest ok = yes",
            "read only = no",
            "browseable = yes",
            "create mask = 0777",
            "directory mask = 0777"
        ]
        
        # Creating default folder path: /home/<user_name>/PS2SMB
        default_shared_folder = self.__get_ps2_default_folder_path()
        
        # Add path to the default settings
        ps2_default_settings.insert(1, f"path = {default_shared_folder}")
        # Add force user to the default settings
        ps2_default_settings.append(f"force user = {self.__get_ps2_force_user()}")
        
        return ps2_default_settings
    
    def __get_default_ps2_share_settings_regex(self) -> list:
        """Uses the default settings for the PS2 share configuration to create regexes and validate the configuration.
        These regexes are used to check if the configuration is correct in the SAMBA configuration file.

        Returns:
            list: The default settings for the PS2 share configuration as regexes. Comments and path settings are ignored.
        """
        
        default_settings = self.__get_default_ps2_share_settings()
        
        # Creating regex for the default settings
        
        ps2_default_settings_regex = []
        for setting in default_settings:
            # Ignoring the path and comment settings
            if setting.startswith("path = ") or setting.startswith("comment = "):
                continue
            
            # Creating regex for the setting
            setting_regex = "\\s*" + setting.strip()
            
            ps2_default_settings_regex.append(setting_regex)
        
        return ps2_default_settings_regex
    
    def check_ps2_share_settings(self) -> None:
        """Checks if the PS2 share configurations are correct in the SAMBA configuration file for communicating with the PS2.
        If any configuration is incorrect, an exception is raised.
        
        Regarding the path, THIS METHOD ONLY CHECKS IF THE PATH IS SET. IT DOESN'T CHECK IF IT IS CORRECT OR EXISTS.
        
        If the configuration is correct, it prints a success message.
        
        Raises:
            TagNotFound: If the [PS2SMB] section is not found in the SAMBA configuration file.
            SettingNotFound: If any of the settings are not found in the [PS2SMB] section.
        """
        
        conf_data = self.__read_samba_conf()
        conf_data = "".join(conf_data)
        
        if self.debug:
            print()
            print(Fore.CYAN + "Verificando a seção [PS2SMB] do arquivo de configuração do SAMBA...")
            print(Fore.CYAN + f"Dados lidos de {self.SAMBA_CONF_PATH}:")
            print(conf_data)
            print()
        
        # If the share config [PS2SMB] is not found, this line will raise an exception and stop the execution
        share_config_data = self.__extract_tag_content(self.PS2_SHARE_NAME, conf_data)
        
        if self.debug:
            print(Fore.CYAN + f"Dados lidos da seção [{self.PS2_SHARE_NAME}]:")
            print(share_config_data)
        
        # If the config was found, we'll first check for the path
        folder_path_regex = r"\s*path = (.*)"
        
        folder_path = re.search(folder_path_regex, share_config_data)
        if folder_path == None:
            # If the path is not found, we raise this exception
            raise SettingNotFound("path")
        
        # If the path was found we'll check for the other settings using generated regexes
        other_settings_regexes = self.__get_default_ps2_share_settings_regex()
        
        for regex in other_settings_regexes:
            if not re.search(regex, share_config_data):
                raise SettingNotFound(regex.split("=")[0].strip().replace("\\s*", ""))
        
        # If everything is ok, this will be printed
        print(Fore.GREEN + "Configuração de compartilhamento do PS2 está correta.")
    
    def create_default_ps2_share_config(self) -> None:
        """Add the PS2 share configuration with the default settings in the SAMBA configuration file.
        If the configuration already exists, it will be replaced with the default settings.
        If the configuration doesn't exist, it will be created with the default values.
        """
        
        # Reading the SAMBA configuration file
        conf_data = self.__read_samba_conf()
        conf_data = "".join(conf_data)

        if not self.__check_if_tag_exists(self.PS2_SHARE_NAME, conf_data):
            # If the tag doesn't exist, we create it
            conf_data = self.__create_tag(self.PS2_SHARE_NAME, conf_data)
            print(Fore.GREEN + f"Tag [{self.PS2_SHARE_NAME}] criada com sucesso!")
        
        # Getting the default settings for the PS2 share configuration
        default_settings = self.__get_default_ps2_share_settings()
        
        # Replacing the old settings with the default settings
        conf_data = self.__update_tag_content(self.PS2_SHARE_NAME, default_settings, conf_data)
        
        # Writing the new configuration file
        conf_file = open(self.SAMBA_CONF_PATH, "w")
        conf_file.write(conf_data)
        conf_file.close()

        print(Fore.GREEN + f"Configuração de compartilhamento do PS2 criada com sucesso em {self.SAMBA_CONF_PATH}!")
        
        if self.debug:
            print()
            print(Fore.CYAN + "Dados da configuração de compartilhamento do PS2:")
            for line in default_settings:
                print(line)
            print()
    
    def check_ps2_share_folder_exists(self) -> bool:
        """Checks if the PS2 share folder exists.
        
        Returns:
            bool: True if the PS2 share folder exists, False otherwise.
        """
        
        path = self.get_ps2_share_folder_path()
        
        if os.path.exists(path):
            print(Fore.GREEN + f"A pasta compartilhada do PS2 '{path}' existe.")
            return True
        else:
            print(Fore.RED + f"A pasta compartilhada do PS2 '{path}' não existe.")
            return False
    
    def check_ps2_share_folder_permissions(self) -> bool:
        """Checks if the PS2 share folder is readable and writable.
        
        The internal path variable is used to check the permissions.

        Returns:
            bool: True if the PS2 share folder is readable and writable, False otherwise.
        """
        
        path = self.get_ps2_share_folder_path()
        
        if os.access(path, os.W_OK | os.R_OK):
            print(Fore.GREEN + f"A pasta compartilhada do PS2 '{path}' possui permissão de leitura e escrita.")
            return True
        else:
            print(Fore.RED + f"A pasta compartilhada do PS2 '{path}' não possui permissão de leitura e escrita.")
            return False
    
    def create_ps2_share_folder(self, path: str = "") -> str:
        """Creates the PS2 share folder in the specified path.
        If the path is empty, it will create the folder in the default location: /home/#user_name/PS2SMB.
        
        Args:
            path (str): The path to create the PS2 share folder. If empty, it will use the default location.
        
        Returns:
            str: The path of the created PS2 share folder.
        
        Raises:
            OSError: If there was an error creating the folder.
        """
        
        if path == "":
            path = self.__get_ps2_default_folder_path()
        
        try:
            os.makedirs(path, exist_ok=True)
            
            user_info = self.get_user_info()
            os.chown(path, user_info["user_id"], user_info["group_id"])
            
            os.chmod(path, 0o777)
            
            print(Fore.GREEN + f"Pasta compartilhada do PS2 criada com sucesso em '{path}'!")
        
        except OSError as e:
            print(Fore.RED + f"Erro ao criar a pasta compartilhada do PS2: {e}")
            raise e
        
        except Exception as e:
            print(Fore.RED + f"Erro desconhecido: {e}")
            raise e
        
        return path
    
    def add_ps2_share_folder_permissions(self) -> None:
        """Adds read and write permissions to the PS2 share folder for all users. 
        
        The permissions are set to 0777 (read, write, execute for owner, group and others).
        
        The internal path variable is used to set the permissions.
        """
        
        user_info = self.get_user_info()
        os.chown(self.__shared_ps2_folder_path, user_info["user_id"], user_info["group_id"])
        
        os.chmod(self.__shared_ps2_folder_path, 0o777)
        
        print(Fore.GREEN + f"Permissões de leitura e escrita adicionadas à pasta compartilhada do PS2 '{self.__shared_ps2_folder_path}'!")
    
    def load_from_conf_ps2_folder_path(self) -> None:
        """Loads the PS2 share folder path from the SAMBA configuration file into the internal variable.
        
        The path is extracted from the [PS2SMB] section of the configuration file.
        If the path is not found, it will be set to an empty string.
        """
        
        conf_data = self.__read_samba_conf()
        conf_data = "".join(conf_data)
        
        try:
            self.__shared_ps2_folder_path = self.__extract_setting_from_tag(self.PS2_SHARE_NAME, "path", conf_data)
        
        except SettingNotFound:
            self.__shared_ps2_folder_path = ""
    
    def get_ps2_share_folder_path(self) -> str:
        """Returns the path of the PS2 share folder from the internal variable. If it is not set, it will be loaded from the SAMBA configuration file.
        
        Returns:
            str: The path of the PS2 share folder.
        """
        
        if self.__shared_ps2_folder_path == "":
            self.load_from_conf_ps2_folder_path()
        
        return self.__shared_ps2_folder_path

    def set_ps2_share_folder_path(self, path: str) -> None:
        """Sets the path of the PS2 share folder in the SAMBA configuration file and in the internal variable.

        Args:
            path (str): The new path of the PS2 share folder.

        Raises:
            ValueError: If the path is empty or doesn't exist.
            SambaServiceFailure: If the service restart command returns a non-zero value.
        """
        
        if path == "":
            raise ValueError("O caminho da pasta compartilhada não pode ser vazio.")
        elif not os.path.exists(path):
            raise ValueError("O caminho da pasta compartilhada não existe.")
        
        conf_data = self.__read_samba_conf()
        conf_data = self.__update_setting_in_tag(self.PS2_SHARE_NAME, "path", path, "".join(conf_data))

        conf_file = open(self.SAMBA_CONF_PATH, "w")
        conf_file.write(conf_data)
        conf_file.close()

        self.__shared_ps2_folder_path = path
        
        print(Fore.GREEN + f"Caminho da pasta compartilhada alterado para '{path}' com sucesso!")
        
        # Restart server (if active) to changes take effect
        if self.__server_active:
            self.restart_server()
    
    # --- NETWORK INTERFACE METHODS ---
    
    def get_available_network_interfaces(self) -> list:
        """Returns a list of network interfaces available on the system.

        Returns:
            list: A list of network interfaces available on the system.
        """
        
        interfaces = psutil.net_if_addrs()
        interface_list = []
        
        for interface in interfaces:
            if interface == "lo":
                continue
            
            interface_list.append(interface)
        
        return interface_list
    
    def get_ipv4_addresses_for_interface(self, interface: str) -> list:
        """Returns a list of IPv4 addresses along with their masks for a given network interface.

        Args:
            interface (str): The name of the network interface.

        Returns:
            list: A list of tuples in the format (ip, mask) for the given network interface.
            If the interface is not found, an empty list is returned.
        """
        
        interfaces = psutil.net_if_addrs()
        ipv4_addresses = []
        
        if interface in interfaces:
            for addr in interfaces[interface]:
                if addr.family == socket.AF_INET:  # AF_INET (IPv4)
                    ipv4_addresses.append((addr.address, addr.netmask))
        
        return ipv4_addresses
    
    def get_subnet_mask_for_ip(self, ip: str) -> str:
        """Returns the subnet mask for a given IPv4 address.

        Args:
            ip (str): The IPv4 address.

        Returns:
            str: The subnet mask for the given IPv4 address or None if the address is not found.
        """
        
        interfaces = psutil.net_if_addrs()
        
        for interface in interfaces:
            for addr in interfaces[interface]:
                if addr.family == socket.AF_INET and addr.address == ip:
                    return addr.netmask
        
        return None
    
    def check_if_ip_is_valid(self, ip: str) -> bool:
        """Checks if the provided IPv4 address is valid.

        Args:
            ip (str): The IP address to check.

        Returns:
            bool: True if the IP address is valid, False otherwise.
        """
        
        try:
            socket.inet_pton(socket.AF_INET, ip)
            
            return True
        except socket.error:
            return False
    
    def check_if_ip_is_bound(self, ip: str, interface: str) -> bool:
        """Checks if the provided IPv4 address is bound to the specified network interface.

        Args:
            ip (str): The IP address to check.
            interface (str): The name of the network interface.

        Returns:
            bool: True if the IP address is bound to the specified network interface, False otherwise.
        """
        
        ipv4_addresses = self.get_ipv4_addresses_for_interface(interface)
        
        for addr in ipv4_addresses:
            if addr[0] == ip:
                return True
        
        return False
    
    def check_if_interface_exists(self, interface: str) -> bool:
        """Checks if a network interface exists on the system.

        Args:
            interface (str): The name of the network interface.

        Returns:
            bool: True if the network interface exists, False otherwise.
        """
        
        interfaces = psutil.net_if_addrs()
        
        if interface in interfaces:
            return True
        else:
            return False
    
    def __erase_interface_and_ip(self) -> None:
        """Erases the network interface and IP address from the SAMBA configuration file and internal variables."""
        
        conf_data = self.__read_samba_conf()
        conf_data = "".join(conf_data)
        
        # Removing the interface and IP address from the [global] section
        conf_data = self.__remove_setting_from_tag("global", "interfaces", conf_data)
        conf_data = self.__remove_setting_from_tag("global", "bind interfaces only", conf_data)
        
        # Writing the new configuration file
        conf_file = open(self.SAMBA_CONF_PATH, "w")
        conf_file.write(conf_data)
        conf_file.close()
        
        # Erasing the internal variables
        self.__server_interface = None
        self.__server_ip = None
        
        if self.debug:
            print(Fore.GREEN + "Interface e IP apagados do arquivo de configuração do SAMBA.")
    
    def set_interface_and_ip(self, interface: str | None, ip: str | None) -> None:
        """Sets the network interface and IP address in the SAMBA configuration file and internally.

        Args:
            interface (str): The name of the network interface.
            ip (str): The IP address to set for the interface.
            
            If one of the parameters is None, the interface and IP address will be
            erased from the SAMBA configuration file and the internal variables.
        """
        
        if interface is None or ip is None:
            self.__erase_interface_and_ip()
            return
        
        conf_data = self.__read_samba_conf()
        conf_data = "".join(conf_data)
        
        # Adding the interface and IP address to the [global] section
        conf_data = self.__update_setting_in_tag("global", "interfaces", f"{interface} {ip}", conf_data)
        # Adding binding to the interface
        conf_data = self.__update_setting_in_tag("global", "bind interfaces only", "yes", conf_data)
        
        # Writing the new configuration file
        conf_file = open(self.SAMBA_CONF_PATH, "w")
        conf_file.write(conf_data)
        conf_file.close()
        
        # Saving the interface and IP address in the internal variables
        self.__server_interface = interface
        self.__server_ip = ip
        
        if self.debug:
            print(Fore.GREEN + f"Interface {interface} e IP {ip} foram carregados no arquivo de configuração do SAMBA.")
        
        # Restart server (if active) to changes take effect
        if self.__server_active:
            self.restart_server()
    
    def get_interfaces_in_samba_conf(self) -> list[str]:
        """Returns the network interfaces set in the SAMBA configuration file.

        Returns:
            list: A list of network interfaces set in the SAMBA configuration file.

            If there are no interfaces set, an empty list is returned.
        """
        conf_data = self.__read_samba_conf()
        conf_data = "".join(conf_data)
        
        try:
            interface = self.__extract_setting_from_tag("global", "interfaces", conf_data)
            
            interface = interface.split(" ")
            
            # Removing empty strings from the list
            interface = [i for i in interface if i != ""]
            
        except SettingNotFound:
            return []
        
        return interface
    
    def get_current_interface(self) -> str | None:
        """Returns the current network interface set for the SAMBA server.
        
        Returns:
            str: The current network interface set for the SAMBA server or None if not set.
        """
        
        return self.__server_interface
    
    # --- SAMBA SERVICE METHODS ---
    
    def start_server(self) -> int:
        """Starts the SAMBA and NetBIOS service.

        Returns:
            int: The return code of the service start command.
            
        Raises:
            SambaServiceFailure: If the service start command returns a non-zero value.
            ValueError: If the server IP or interface is not set.
        """
        
        if self.__server_interface is None:
            raise ValueError("A interface do servidor não foi definida. Defina a interface do servidor antes de iniciar o servidor!")

        if self.__server_ip is None:
            raise ValueError("O IP do servidor não foi definido. Defina o IP do servidor antes de iniciar o servidor!")
        
        ret = os.system("systemctl start smbd nmbd")
        
        if ret != 0:
            raise SambaServiceFailure(ret)
        else:
            print(Fore.GREEN + "Servidor SAMBA e NetBIOS iniciado com sucesso!")
            self.__server_active = True
            return ret
    
    def stop_server(self) -> int:
        """Stops the SAMBA and NetBIOS service.

        Returns:
            int: The return code of the service stop

        Raises:
            SambaServiceFailure: If the service stop command returns a non-zero value.
        """
        
        ret = os.system("systemctl stop smbd nmbd")
        
        if ret != 0:
            raise SambaServiceFailure(ret)
        else:
            print(Fore.GREEN + "Servidor SAMBA e NetBIOS parados com sucesso!")
            self.__server_active = False
            return ret
    
    def restart_server(self) -> int:
        """Restarts the SAMBA and NetBIOS service.
        
        Returns:
            int: The return code of the service restart command.
            
        Raises:
            SambaServiceFailure: If the service restart command returns a non-zero value.
            ValueError: If the server IP or interface is not set.
        """
        
        if self.__server_ip is None:
            raise ValueError("O IP do servidor não foi definido. Defina o IP do servidor antes de reiniciar o servidor!")

        if self.__server_interface is None:
            raise ValueError("A interface do servidor não foi definida. Defina a interface do servidor antes de reiniciar o servidor!")
        
        ret = os.system("systemctl restart smbd nmbd")
        
        if ret != 0:
            raise SambaServiceFailure(ret)
        else:
            print(Fore.GREEN + "Servidor SAMBA e NetBIOS reiniciados com sucesso!")
            self.__server_active = True
            return ret

    def get_server_status(self) -> bool:
        """Returns the status of the SAMBA and NetBIOS service.

        Returns:
            bool: True if the server is active, False otherwise.
        """
        
        return self.__server_active