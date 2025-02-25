#!/bin/bash

CONFIG_FILE="/etc/samba/smb.conf"
NOME_DO_COMPARTILHAMENTO="PS2SMB"
PATH_DA_PASTA="/home/$SUDO_USER/$NOME_DO_COMPARTILHAMENTO"

# Cria a pasta compartilhada com o nome "PS2SMB"
create_shared_folder()
{
    echo "Criando pasta compartilhada em $PATH_DA_PASTA"
    mkdir -p $PATH_DA_PASTA

    # Torna a pasta compartilhada acessível para todos os usuários
    chmod 777 $PATH_DA_PASTA
}

# Verifica se o samba está instalado
check_samba()
{
    if dpkg -s samba &>/dev/null; then
        echo 'O samba está instalado corretamente.'
    else
        echo 'Parece que você não tem o samba instalado. Por favor, instale o samba e tente novamente.'
        exit
    fi
}

# Confere se o compartilhamento PS2SMB está público, para permitir o acesso ao PS2
check_smb_server_exists()
{
    read_next_line=false

    regex_1="guest ok.*"
    regex_2=".*yes"

    cat $CONFIG_FILE | while IFS= read -r line; do
        if [[ $read_next_line == true ]]; then
            if [[ $line =~ $regex_1 ]]; then
                if [[ $line =~ $regex_2 ]]; then
                    echo "O compartilhamento existe e o acesso público está habilitado. OK!"
                    return 1
                else
                    echo "O compartilhamento existe, mas o acesso público não está habilitado. Por favor, edite as configurações no seu arquivo smb.conf para habilitar o acesso público (guest ok = yes) no compartilhamento $NOME_DO_COMPARTILHAMENTO."
                    return -1
                fi
            fi
        fi

        if [[ "$line" == "[$NOME_DO_COMPARTILHAMENTO]" ]]; then
            read_next_line=true

            echo "O compartilhamento $NOME_DO_COMPARTILHAMENTO foi encontrado no arquivo de configuração do samba."

            continue
        fi
    done

    return 0
}

# Cria o arquivo de configuração do samba
create_smb_config()
{
    echo "" >> $CONFIG_FILE
    echo "[$NOME_DO_COMPARTILHAMENTO]" >> $CONFIG_FILE
    echo "  path = $PATH_DA_PASTA" >> $CONFIG_FILE
    echo "  guest ok = yes" >> $CONFIG_FILE
    echo "  read only = no" >> $CONFIG_FILE
    echo "  writeable = yes" >> $CONFIG_FILE
    echo "  browsable = yes" >> $CONFIG_FILE
    echo "  create mask = 0777" >> $CONFIG_FILE
    echo "  directory mask = 0777" >> $CONFIG_FILE
}

# Verifica se o script está usando o comando sudo (usuário root)
if [[ "$EUID" -ne 0 ]]; then
    echo "Por favor, execute o script como root."
    exit
fi

# Verifica se o samba está instalado
check_samba

# Verifica se a pasta de compartilhamento existe
if [[ -d $PATH_DA_PASTA ]]; then
    echo "A pasta de compartilhamento $PATH_DA_PASTA já existe."
else
    create_shared_folder
fi

# Verifica se o compartilhamento PS2SMB está configurado corretamente
check_smb_server_exists
ret=$?

if [[ $ret -eq -1 ]]; then
    exit 1
elif [[ $ret -eq 0 ]]; then
    echo "O compartilhamento $NOME_DO_COMPARTILHAMENTO não foi encontrado no arquivo de configuração do samba. Criando o compartilhamento $NOME_DO_COMPARTILHAMENTO.."
    create_smb_config
    echo "Compartilhamento $NOME_DO_COMPARTILHAMENTO adicionado ao arquivo de configuração do samba $CONFIG_FILE"
fi