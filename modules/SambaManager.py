import os
import re
import sys
from colorama import Fore

from modules.Exceptions import GlobalSettingsNotFound

class SambaManager:
    SAMBA_CONF_PATH = "/etc/samba/smb.conf"
    DEFAULT_NETBIOS_NAME = "SAMBA"

    def __init__(self, debug=False):
        self.debug = debug

    def __read_samba_conf(self):
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

    def __extract_tag_content(self, tag, conf_data):
        """Extracts the content of a tag from a configuration file.

        Args:
            tag (str): The tag to search for.
            conf_data (str): The configuration file data as a unique string.
        
        Returns:
            str: The content of the tag. If the tag is not found, it returns None.
        """

        tag_data = re.search(rf"\[{tag}\]\s*(?P<tag_data>.*?)(?=\[|$)", conf_data, flags=re.DOTALL)

        if tag_data is not None:
            return tag_data.group("tag_data")
        else:
            return None
    
    def __update_tag_content(self, tag, new_content, conf_data):
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
        # Joining the new content and adding 3 spaces before each line
        new_content = "\n   ".join(new_content)
        # Escaping backslashes
        new_content = new_content.replace("\\", "\\\\")

        # Updating the tag content
        conf_data = re.sub(rf"\[{tag}\]\s*(.*?)(?=\[|$)", new_content, conf_data, flags=re.DOTALL)

        return conf_data

    def check_global_samba_conf(self):
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

    def backup_and_fix_global_conf(self):
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