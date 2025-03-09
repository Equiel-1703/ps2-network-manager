# Código que gerencia o servidor e a conexão com o cliente
# Autores: Henrique Rodrigues, Daniel Lisboa & Gabriel Pink

import os
import sys
import re
import socket
from colorama import Fore, init

SAMBA_CONF_PATH = "/etc/samba/smb.conf"
DEBUG = False

# Verifica se o script está sendo executado como root
def check_root():
    if os.geteuid() != 0:
        print(Fore.RED + "Este script precisa ser executado como root.")
        sys.exit(1)

# Lê o arquivo de configuração do SAMBA e retorna os dados (ignorando comentários e linhas em branco)
def read_samba_conf():
    conf_file = open(SAMBA_CONF_PATH, "r")
    original_conf_data = conf_file.readlines()
    conf_file.close()

    # Vamos remover os comentários e as linhas em branco dos nossos dados
    conf_data = []
    for line in original_conf_data:
        if line[0] != "#" and line[0] != ";" and line != "\n":
            conf_data.append(line)

    return conf_data

# Extrai o conteúdo de uma tag de configuração do SAMBA
def extract_tag_content(tag, conf_data):
    tag_data = re.search(rf"\[{tag}\]\s*(?P<tag_data>.*?)(?=\[|$)", conf_data, flags=re.DOTALL)

    if tag_data is not None:
        return tag_data.group("tag_data")
    else:
        return None

# Verifica se as configurações globais do SAMBA estão corretas para o PS2
def check_global_samba_conf():
    conf_data = read_samba_conf()

    if DEBUG:
        print()
        print(Fore.CYAN + f"Dados lidos de {SAMBA_CONF_PATH}:")
        for line in conf_data:
            print(line, end='')
        print()

    conf_data = "".join(conf_data)
    global_config_data = extract_tag_content("global", conf_data)

    if global_config_data is None:
        print(Fore.RED + "Erro: Seção [global] não encontrada no arquivo de configuração do SAMBA.")
        print(Fore.RED + f"Por favor, verifique se o arquivo de configuração do SAMBA {SAMBA_CONF_PATH} está correto e tente novamente.")
        sys.exit(1)

    if DEBUG:
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

# Cria um novo arquivo de configuração do SAMBA mantendo uma cópia do original
def backup_and_update_samba_conf():
    # Criar uma cópia de backup do arquivo de configuração original (se ela não existir)
    os.system(f"cp --update=none {SAMBA_CONF_PATH} {SAMBA_CONF_PATH}.bak")

    # Lendo o arquivo de configuração do SAMBA
    conf_data = read_samba_conf()
    conf_data = "".join(conf_data)

    # Obtendo a seção [global]
    global_config_data = extract_tag_content("global", conf_data)

    # Verificando se já temos o nome netbios (se tiver, vamos manter o mesmo)
    netbios_name = re.search(r"\s*netbios name = (.*)", global_config_data)

    if netbios_name is not None:
        global_config_data = re.sub(r"\s*netbios name = (.*)", "", global_config_data)
        netbios_name = netbios_name.group(1)

    # Removendo configurações que vamos adicionar e que talvez já estejam lá (para garantir tenham os valores corretos)
    global_config_data = re.sub(r"\bserver min protocol = .*|\bclient min protocol = .*", "", global_config_data).strip()
    print(Fore.GREEN + "Configurações antigas removidas.")

    if DEBUG:
        print()
        print(Fore.CYAN + "Arquivo sem as configurações antigas:")
        print(global_config_data)
        print()

    global_config_data = global_config_data.split("\n")

    for i in range(len(global_config_data)):
        global_config_data[i] = global_config_data[i].strip()    
    
    # Adicionando as novas configurações
    if netbios_name is not None:
        global_config_data.insert(0, "netbios name = " + netbios_name)
    else:
        global_config_data.insert(0, "netbios name = SAMBA") # Se não tiver o nome netbios, vamos adicionar um nome padrão
    global_config_data.insert(1, "server min protocol = NT1")
    global_config_data.insert(2, "client min protocol = NT1")

    global_config_data = "\n   ".join(global_config_data)
    global_config_data = f"[global]\n   {global_config_data.strip()}\n"

    # Removendo as configurações globais antigas
    conf_data = re.sub(r"\[global\]\s*(.*?)(?=\[|$)", "", conf_data, flags=re.DOTALL)

    # Adicionando as novas configurações globais
    conf_data = global_config_data + conf_data

    # Escrevendo as novas configurações no arquivo de configuração
    conf_file = open(SAMBA_CONF_PATH, "w")
    conf_file.write(conf_data)
    conf_file.close()

    print(Fore.GREEN + "Configurações globais do compartilhamento SAMBA atualizadas com sucesso!")

    if DEBUG:
        print()
        print(Fore.CYAN + "Novo arquivo de configuração do SAMBA:")
        print(conf_data.strip())
        print()

if __name__ == "__main__":
    # Inicializar o colorama
    init(autoreset=True)

    # Este script precisa ser executado como root!
    check_root()

    #ler argumentos
    if len(sys.argv) > 1 and sys.argv[1] == "-d":
        DEBUG = True
        print(Fore.YELLOW + "Modo debug ativado.")

    if check_global_samba_conf() == False:
        print()
        print(Fore.YELLOW + "Parece que algumas configurações globais do compartilhamento SAMBA não estão corretas para se comunicar com o PS2.")
        print(Fore.YELLOW + "Iremos consertar isso para você.")
        print()

        backup_and_update_samba_conf()
    else:
        print(Fore.GREEN + "Configurações globais do compartilhamento SAMBA estão corretas.")
    

    exit(0)

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
