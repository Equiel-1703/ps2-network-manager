# Código que gerencia o servidor e a conexão com o cliente
# Autores: Henrique Rodrigues, Daniel Lisboa & Gabriel Pink

import os
import socket

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
