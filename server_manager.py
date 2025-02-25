# Código que gerencia o servidor e a conexão com o cliente
# Autores: Henrique Rodrigues, Daniel Lisboa & Gabriel Pink

import os
import subprocess
import sys

SHELL_SCRIPT = "start_server.sh"

def get_process_name(id):
    return subprocess.check_output(["ps", "-p", str(id), "-o", "comm="]).decode().strip()

parent_pid = os.getppid()
parent_name = get_process_name(parent_pid)

if not parent_name.endswith(SHELL_SCRIPT):
    print(f"Para iniciar o PS2 Network Manager, execute o script '{SHELL_SCRIPT}' como root.")
    sys.exit(1)

print("PS2 Network Manager iniciado (Python).")

