from colorama import Fore

class BaseManagerException(Exception):
    def __init__(self, error_message, description=""):
        self.error_message = error_message
        self.description = description
        super().__init__(f"{Fore.RED}ERRO: {error_message}\n{description}")

class SambaConfNotFound(BaseManagerException):
    def __init__(self, samba_conf_path):
        self.error_message = "Arquivo de configuração do SAMBA não encontrado."
        self.description = f"Por favor, verifique se o arquivo de configuração do SAMBA em '{samba_conf_path}' existe e tente novamente."
        super().__init__(self.error_message, self.description)

class SambaServiceFailure(BaseManagerException):
    def __init__(self, return_value):
        self.error_message = "Houve uma falha no serviço do samba e/ou NetBIOS (smbd/nmbd)."
        self.description = f"Código de retorno {return_value}."
        super().__init__(self.error_message, self.description)

class GlobalSettingsNotFound(BaseManagerException):
    def __init__(self):
        self.error_message = "Seção [global] não encontrada no arquivo de configuração do SAMBA."
        self.description = f"Por favor, verifique se o arquivo de configuração do SAMBA está correto e tente novamente."
        super().__init__(self.error_message, self.description)

class SettingNotFound(BaseManagerException):
    def __init__(self, setting_name):
        self.error_message = f"Configuração '{setting_name}' não encontrada no arquivo de configuração do SAMBA."
        self.description = f"Por favor, verifique se o arquivo de configuração do SAMBA está correto e tente novamente."
        super().__init__(self.error_message, self.description)