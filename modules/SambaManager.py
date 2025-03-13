import os
import re
import sys
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
        tag_data = re.search(rf"\[{tag.strip()}\]\s*(?=\[|$)", conf_data)

        if tag_data is not None:
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

    def __extract_tag_content(self, tag: str, conf_data: str) -> (str | None):
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
            return tag_data.group("tag_data")
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

        # Joining the new content and adding 3 spaces before each line
        new_content = "\n   ".join(new_content)
        
        # Escaping backslashes
        new_content = new_content.replace("\\", "\\\\")

        # Updating the tag content
        conf_data = re.sub(rf"\[{tag}\]\s*(.*?)(?=\[|$)", new_content, conf_data, flags=re.DOTALL)

        return conf_data
    
    def __update_setting_in_tag(self, tag: str, setting: str, new_value: str, conf_data: str) -> str:
        """Updates a setting in a tag in a configuration file.

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

        # Update setting
        tag_data = re.sub(rf"{setting} = .*", f"{setting} = {new_value}", tag_data)

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
        
        print(Fore.GREEN + f"Nome NetBIOS alterado para '{netbios_name}' com sucesso!")
        
        # Restart server to changes take effect
        self.restart_server()
    
    # --- PS2 SHARE METHODS ---
    
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
        default_shared_folder = os.path.join(os.sep, "home", self.__user_name, self.PS2_SHARE_NAME)
        
        # Add path to the default settings
        ps2_default_settings.insert(1, f"path = {default_shared_folder}")
        
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
        """Checks if the PS2 share configuration is correct in the SAMBA configuration file for communicating with the PS2.
        If the configuration is not correct, it raises an exception. THIS METHOD ONLY CHECKS IF THE PATH IS SET, IT DOESN'T CHECK IF IT IS CORRECT OR EXISTS.
        
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
        
        # If the tag exists, we replace it with the default settings
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
    
    def check_ps2_share_folder_rw(self) -> bool:
        """Checks if the PS2 share folder is readable and writable.

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
    
    def get_ps2_share_folder_path(self) -> str:
        """Returns the path of the PS2 share folder.

        Returns:
            str: The path of the PS2 share folder.
        """
        
        if self.__shared_ps2_folder_path == "":
            conf_data = self.__read_samba_conf()
            conf_data = "".join(conf_data)
            self.__shared_ps2_folder_path = self.__extract_setting_from_tag(self.PS2_SHARE_NAME, "path", conf_data)
        
        return self.__shared_ps2_folder_path

    def set_ps2_share_folder_path(self, path: str) -> None:
        """Sets the path of the PS2 share folder.

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
        
        # Restart server to changes take effect
        self.restart_server()
    
    # --- SAMBA SERVICE METHODS ---
    
    def start_server(self) -> int:
        """Starts the SAMBA and NetBIOS service.

        Returns:
            int: The return code of the service start command.
            
        Raises:
            SambaServiceFailure: If the service start command returns a non-zero value.
        """
        
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
        """
        
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