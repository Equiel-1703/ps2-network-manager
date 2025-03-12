# Código que gerencia o servidor e a conexão com o cliente
# Autores: Henrique Rodrigues, Daniel Lisboa & Gabriel Pink

import os
import sys
import socket
import colorama
from PyQt6.QtWidgets import QApplication
from colorama import Fore

# Importing our custom modules
from modules.SambaManager import SambaManager
from modules.Exceptions import *
from modules.GUI.GUI import PS2NetManagerGUI

def check_root():
    """Checks if the script is running as root. If not, it exits the script with an error message."""

    if os.geteuid() != 0:
        print(Fore.RED + "Este script precisa ser executado como root.")
        sys.exit(1)

def check_os_support():
    """Checks if the script is running on a supported OS. If not, print an error message and exit the script."""

    if not sys.platform.startswith("linux"):
        print(Fore.RED + "Desculpe, mas este script só pode ser executado em sistemas operacionais Linux.")
        sys.exit(1)

def process_args():
    """Processes the command line arguments and returns the debug flag."""
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "-d" or sys.argv[1] == "--debug":
            print(Fore.YELLOW + "Modo debug ativado.")
            return True
        else:
            if not (sys.argv[1] == "-h" or sys.argv[1] == "--help"):
                print(Fore.RED + "Erro: Argumento inválido.")
                print(Fore.RED + "Use -h ou --help para obter ajuda.")
                sys.exit(1)
            else:
                # Print help message
                print(f"USO: {Fore.LIGHTYELLOW_EX}python3 {Fore.WHITE}'PS2 Network Manager.py' {Fore.LIGHTBLUE_EX}[OPÇÕES]\n")
                print(f"OPÇÕES:")
                print(f"  {Fore.LIGHTBLUE_EX}-d, --debug{Fore.RESET}  Ativa o modo de depuração.")
                print(f"  {Fore.LIGHTBLUE_EX}-h, --help{Fore.RESET}   Mostra esta mensagem de ajuda.")
            
            sys.exit(0)

    return False


if __name__ == "__main__":
    # Initializing colorama
    colorama.init(autoreset=True)

    # Check if the script is running on a supported OS
    check_os_support()

    # Check if the script is running as root
    check_root()
    
    # Process command line arguments and return the debug flag
    debug_flag = process_args()

    try:
        # Create a SambaManager instance
        samba_manager = SambaManager(debug_flag)

        if samba_manager.check_global_samba_conf() == False:
            print()
            print(Fore.YELLOW + "Parece que algumas configurações globais do compartilhamento SAMBA não estão corretas para se comunicar com o PS2.")
            print(Fore.YELLOW + "Iremos consertar isso para você.")
            print()

            samba_manager.backup_and_fix_global_conf()
        else:
            print(Fore.GREEN + "Configurações globais do compartilhamento SAMBA estão corretas.")
    
    except BaseManagerException as e:
        print(Fore.RED + "PS2 Network Manager encontrou um erro:\n")
        print(e)
        sys.exit(1)
    
    except Exception as e:
        print(Fore.RED + "Um erro inesperado ocorreu:\n")
        print(e)
        sys.exit(1)

    # Setup the PyQt6 application
    app = QApplication([])

    # Create the main window
    window = PS2NetManagerGUI()
    window.show()
    
    # Execute the application
    app_return = app.exec()

    del window
    
    if QApplication.instance() is not None:
        # Exit the script with the return code from the application
        sys.exit(app_return)

# -----------------------------------------------------------------------------

# # Restart Samba
# os.system("sudo systemctl restart smbd")

SHELL_SCRIPT = "start_server.sh"

print("Python: PS2 Network Manager iniciado")

try:
    while True:
        response = int(input("Insira a opção que deseja: \n1-Ligar o SAMBA e a conexão ao PS2\n2-Parar o SAMBA e encerrar a conexão\n3-Reiniciar o SAMBA\n4-Mostrar status (IP, nome NetBios)\n5-Mostrar conexões ativas\n\nInsira -1 para encerrar o programa\n"))
        if response == 1:
            os.system("sudo systemctl start smbd")
            os.system("sudo systemctl start nmbd")
            print("Python: Samba iniciado.")
        elif response == 2:
            os.system("sudo systemctl stop smbd")
            os.system("sudo systemctl stop nmbd")
            print("Python: Samba finalizado.")
        elif response == 3:
            os.system("sudo systemctl restart smbd")
            os.system("sudo systemctl restart nmbd")
            print("Python: Samba reiniciado.")
        elif response == 4:
            # Obtém o nome do host
            hostname = socket.gethostname()

            # Obtém o nome NetBIOS
            netbios_name = os.popen("nmblookup -A " + hostname).read().split()[0]

            # Obtém o IP do servidor
            server_ip = os.popen("hostname -I").read().split()[0]

            print("Nome do host: " + hostname)
            print("Nome NetBIOS: " + netbios_name)
            print("IP do servidor: " + server_ip)
        elif response == 5:
            os.system("sudo smbstatus")
            os.system("sudo nmdbtatus")
        elif response > 5:
            print("Opção inválida")
        elif response < 0:
            print("Encerrando programa")
            break 

        print("\n")

except KeyboardInterrupt:
    print("Encerrando programa")
    exit(0)

except Exception:
    print("Alguma coisa deu pau")
    print("Encerrando programa")
    exit(1)
