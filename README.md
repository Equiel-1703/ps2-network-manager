# PS2 Network Manager

PS2 Network Manager is a tool designed to manage and configure a Samba server for sharing files with a PlayStation 2 console via [OPL](https://www.ps2homebrew.org/Open-PS2-Loader/). It provides a graphical user interface (GUI) to simplify the setup and management of network shares, IPs, and other Samba settings.

This project is a collaborative effort by Henrique Rodrigues, Daniel Lisboa, and Gabriel Pink, and is intended for educational purposes. It is not affiliated with or endorsed by any official PlayStation or Sony products.

![screenshot](https://github.com/user-attachments/assets/92490267-4213-4888-bad4-e263f1c424b6)

## Features

- **NetBIOS Name Configuration**: Easily set and change the NetBIOS name of your Samba server.
- **PS2 Share Configuration**: Automatically create and manage the PS2 share folder with the correct access permissions.
- **Samba Configuration**: Automatically configure the Samba configuration file (`smb.conf`) to include the necessary settings for communicating with the PS2.
- **Network Interface Management**: Select and configure the network interface and IP address for the Samba server.
- **Server Control**: Start, stop, and monitor the Samba server status.
- **Network Speed Monitoring**: Real-time monitoring of upload and download speeds on the selected network interface.

## Installation

### Prerequisites

- Linux operating system
- Python 3.6 or higher
- Samba installed on your system

### Installation Steps

1. Clone the repository:
    ```sh
    git clone https://github.com/Equiel-1703/ps2-network-manager.git
    cd ps2-network-manager
    ```

2. Make sure you are in a Python 3 virtual environment. If you don't have one, create it and activate it:
    ```sh
    python3 -m venv myenv
    source myenv/bin/activate
    ```

3. Install all the required Python packages in your virtual environment:
    ```sh
    pip install -r requirements.txt
    ```

4. Ensure you have the necessary permissions to run the script:
    ```sh
    sudo chmod +x "PS2 Network Manager.py"
    ```

5. Done! You can now run the script.

## Usage

1. Ensure you are in sudo mode or have root privileges. The script needs these permisions to manipulate the Samba configuration file in `/etc/samba/smb.conf`:
    ```sh
    sudo su
    ```

2. Ensure you are in a Python 3 virtual environment. If you don't have one, create it:
    ```sh
    python3 -m venv myenv
    source myenv/bin/activate
    ```

3. Run the script:
    ```sh
    python3 "PS2 Network Manager.py"
    ```

4. Enjoy!

## Debug Mode

To run the script in debug mode, use the `-d` or `--debug` flag:
```sh
python3 "PS2 Network Manager.py" --debug
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Authors

- [Henrique Rodrigues](https://github.com/Equiel-1703)
- [Daniel Lisboa](https://github.com/danlisb)
- [Gabriel Pink](https://github.com/GabrielRosaO)

## Acknowledgements

Special thanks to [PS2 Homebrew](https://www.ps2homebrew.org/) for their amazing work on the Open PS2 Loader.
