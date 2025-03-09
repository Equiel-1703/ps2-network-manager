from smb.SMBConnection import SMBConnection

server_ip = "172.24.69.65"  # Replace with your SMB server's IP
server_name = "server"  # Replace with your SMB server's name

conn = SMBConnection(
    "",  # Username
    "",  # Password
    "teste",  # Client name
    server_name,  # Server name
    use_ntlm_v2=True,
    is_direct_tcp=True
)

if conn.connect(server_ip, port=445):
    print(f"Connected to {server_name} ({server_ip})")
    
    shares = conn.listShares()
    print("Available shares:")
    for share in shares:
        print(f" - {share.name}")

    conn.close()
else:
    print(f"Failed to connect to {server_name}.")
