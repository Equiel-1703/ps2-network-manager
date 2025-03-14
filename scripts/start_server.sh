#!/bin/bash

# Configurações do samba
CONFIG_FILE="/etc/samba/smb.conf"
NOME_DO_COMPARTILHAMENTO="PS2SMB"
PATH_DA_PASTA="/home/$SUDO_USER/$NOME_DO_COMPARTILHAMENTO"
PYTHON_SCRIPT="server_manager.py"

# Códigos de cores
RED='\033[0;31m'     # Vermelho
GREEN='\033[0;32m'   # Verde
YELLOW='\033[1;33m'  # Amarelo
NC='\033[0m'        # Sem cor

# Cria a pasta compartilhada com o nome "PS2SMB"
create_shared_folder()
{
    echo "Criando pasta compartilhada em $PATH_DA_PASTA"
    sudo -c mkdir -p $PATH_DA_PASTA

    # Torna a pasta compartilhada acessível para todos os usuários
    sudo chmod 777 $PATH_DA_PASTA
}

# Verifica se o samba está instalado
check_samba()
{
    if dpkg -s samba &>/dev/null; then
        echo -e "${GREEN}O samba está instalado corretamente.${NC}"
    else
        echo -e "${RED}Parece que você não tem o samba instalado. Por favor, instale o samba e tente novamente.${NC}"
        exit
    fi
}

# Confere se o compartilhamento PS2SMB está público, para permitir o acesso ao PS2
check_smb_server_exists()
{
    retorno=1
    read_next_line=false

    regex_1="guest ok.*"
    regex_2=".*yes"

    while IFS= read -r line; do
        if [[ $read_next_line == true ]]; then
            if [[ $line =~ $regex_1 ]]; then
                if [[ $line =~ $regex_2 ]]; then
                    echo -e "${GREEN}O compartilhamento existe e o acesso público está habilitado. OK!${NC}"
                    retorno=2
                    break
                else
                    echo -e "${RED}O compartilhamento existe, mas o acesso público não está habilitado. Por favor, edite as configurações no seu arquivo smb.conf para habilitar o acesso público (guest ok = yes) no compartilhamento $NOME_DO_COMPARTILHAMENTO.${NC}"
                    retorno=0
                    break
                fi
            fi
        fi

        if [[ "$line" == "[$NOME_DO_COMPARTILHAMENTO]" ]]; then
            read_next_line=true

            echo -e "${GREEN}O compartilhamento $NOME_DO_COMPARTILHAMENTO foi encontrado no arquivo de configuração do samba.${NC}"

            continue
        fi
    done < "$CONFIG_FILE"

    return $retorno
}

# Cria o arquivo de configuração do samba
create_smb_config()
{
    sudo bash -c "cat <<EOL >> $CONFIG_FILE

[$NOME_DO_COMPARTILHAMENTO]
  path = $PATH_DA_PASTA
  guest ok = yes
  read only = no
  writeable = yes
  browsable = yes
  create mask = 0777
  directory mask = 0777
EOL"
}

# Verifica se o script está usando o comando sudo (usuário root)
# if [[ "$EUID" -ne 0 ]]; then
#     echo -e "${RED}Por favor, execute o script como root.${NC}"
#     exit
# fi

# Verifica se o samba está instalado
check_samba

# Verifica se a pasta de compartilhamento existe
if [[ -d $PATH_DA_PASTA ]]; then
    echo -e "${YELLOW}A pasta de compartilhamento $PATH_DA_PASTA já existe.${NC}"
else
    create_shared_folder
fi

# Verifica se o compartilhamento PS2SMB está configurado corretamente
check_smb_server_exists
ret=$?

if [[ $ret -eq 0 ]]; then
    exit 1
elif [[ $ret -eq 1 ]]; then
    echo -e "${YELLOW}O compartilhamento $NOME_DO_COMPARTILHAMENTO não foi encontrado no arquivo de configuração do samba. Criando o compartilhamento $NOME_DO_COMPARTILHAMENTO...${NC}"
    create_smb_config
    echo -e "${GREEN}Compartilhamento $NOME_DO_COMPARTILHAMENTO adicionado ao arquivo de configuração do samba $CONFIG_FILE ${NC}"
fi

echo -e "${GREEN}Configurações do servidor SAMBA concluídas! O gerenciador em Python ${PYTHON_SCRIPT} já pode ser iniciado.${NC}"