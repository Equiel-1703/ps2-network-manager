from colorama import Fore

class BaseManagerException(Exception):
    def __init__(self, error_message, description=""):
        self.error_message = error_message
        self.description = description
        super().__init__(f"{Fore.RED}Error: {error_message}\n\n{description}")

class GlobalSettingsNotFound(BaseManagerException):
    def __init__(self):
        self.error_message = "Seção [global] não encontrada no arquivo de configuração do SAMBA."
        self.description = f"Por favor, verifique se o arquivo de configuração do SAMBA {self.SAMBA_CONF_PATH} está correto e tente novamente."
        super().__init__(self.error_message, self.description)