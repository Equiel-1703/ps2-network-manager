import os
import re
import sys
from colorama import Fore

from modules.Exceptions import *

class SambaManager:
    SAMBA_CONF_PATH = "/etc/samba/smb.conf"
    DEFAULT_NETBIOS_NAME = "SAMBA"

    __netbios_name = ""

    def __init__(self, debug=False):
        self.debug = debug

        # Check if samba config file exists
        if not os.path.exists(self.SAMBA_CONF_PATH):
            raise SambaConfNotFound(self.SAMBA_CONF_PATH)

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

    def __extract_tag_content(self, tag: str, conf_data: str) -> (str | None):
        """Extracts the content of a tag from a configuration file.

        Args:
            tag (str): The tag to search for.
            conf_data (str): The configuration file data as a unique string.
        
        Returns:
            str: The content of the tag.
            None: If the tag is not found.
        """

        tag_data = re.search(rf"\[{tag}\]\s*(?P<tag_data>.*?)(?=\[|$)", conf_data, flags=re.DOTALL)

        if tag_data is not None:
            return tag_data.group("tag_data")
        else:
            return None
    
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
    
    def start_server(self) -> None:
        """Starts the SAMBA and NerBIOS service."""
        os.system("sudo systemctl start smbd nmbd")
        print(Fore.GREEN + "Servidor SAMBA e NetBIOS iniciado com sucesso!")
    
    def stop_server(self) -> None:
        """Stops the SAMBA and NetBIOS service."""
        os.system("sudo systemctl stop smbd nmbd")
        print(Fore.GREEN + "Servidor SAMBA e NetBIOS parado com sucesso!")
    
    def restart_server(self) -> None:
        """Restarts the SAMBA and NetBIOS service."""
        os.system("sudo systemctl restart smbd nmbd")
        print(Fore.GREEN + "Servidor SAMBA e NetBIOS reiniciado com sucesso!")
    
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

        # Restart server to changes take effect
        self.restart_server()

        print(Fore.GREEN + f"Nome NetBIOS alterado para '{netbios_name}' com sucesso!")