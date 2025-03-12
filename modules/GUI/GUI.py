from enum import Enum
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt, QRect

# Importing our custom modules
from modules.GUI.GUIColors import GUIColors as Colors
from modules.GUI.GUIFonts import GUIFonts as Fonts
from modules.GUI.GUICustomWidgets import GUICustomWidgets as Widgets
from modules.SambaManager import SambaManager

class WindowDimensions(Enum):
    WIDTH = 800
    HEIGHT = 650

class MainLayoutSettings(Enum):
    MARGIN = 10
    SPACING = 15
    
class PS2NetManagerGUI(QMainWindow):
    def __init__(self, samba_manager: SambaManager):
        super().__init__()

        self.__samba_manager = samba_manager

        # Window title
        self.setWindowTitle("PS2 Network Manager")

        # Center window on screen
        window_rec = QRect(
            0,
            0,
            WindowDimensions.WIDTH.value,
            WindowDimensions.HEIGHT.value
        )
        window_rec.moveCenter(QApplication.primaryScreen().geometry().center())

        self.setGeometry(window_rec)
        self.setFixedSize(window_rec.size())

        # Loading custom fonts
        Fonts.load_fonts()

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(
            MainLayoutSettings.MARGIN.value,
            MainLayoutSettings.MARGIN.value,
            MainLayoutSettings.MARGIN.value,
            MainLayoutSettings.MARGIN.value
        )
        main_layout.setSpacing(MainLayoutSettings.SPACING.value)

        # Creating widgets for the GUI sections
        netbios_widget = self.__create_netbios_widget()
        share_name_widget = self.__create_share_name_widget()
        shared_folder_widget = self.__create_shared_folder_path_widget()
        net_settings_widget = self.__net_settings_widget()
        samba_status_widget = self.__create_samba_status_widget()
        main_buttons_widget = self.__create_main_buttons_widget()

        # Adding the widgets to the main layout
        main_layout.addWidget(netbios_widget)
        main_layout.addWidget(share_name_widget)
        main_layout.addWidget(shared_folder_widget)
        main_layout.addWidget(Widgets.create_hline(self))
        main_layout.addWidget(net_settings_widget)
        main_layout.addWidget(samba_status_widget)
        main_layout.addStretch()
        main_layout.addWidget(main_buttons_widget)

        # Creating main widget
        main_widget = QWidget()
        main_widget.setLayout(main_layout)
        main_widget.setStyleSheet(f"background-color: {Colors.DEEP_PURPLE};")

        self.setCentralWidget(main_widget)

    def __wrap_layout(self, layout: QLayout) -> QWidget:
        """Helper method to wrap a layout in a QWidget."""

        widget = QWidget()
        widget.setLayout(layout)
        return widget

    def __create_netbios_widget(self) -> QWidget:
        netbios_layout = QHBoxLayout()
        netbios_layout.setContentsMargins(0, 0, 0, 0)

        label = Widgets.create_label(self, "NOME NETBIOS:")

        line_field = Widgets.create_line_edit(self, placeholder="Digite o nome do servidor...")
        line_field.setFixedHeight(label.sizeHint().height()) # Same height as the label
        line_field.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        line_field.setText(self.__samba_manager.get_netbios_name())

        ok_button = Widgets.create_button(self, "OK")
        ok_button.clicked.connect(lambda: print("OK button clicked"))

        SPACER_WIDTH = 10

        netbios_layout.addWidget(label)
        netbios_layout.addSpacerItem(QSpacerItem(SPACER_WIDTH, 0))
        netbios_layout.addWidget(line_field)
        netbios_layout.addSpacerItem(QSpacerItem(SPACER_WIDTH, 0))
        netbios_layout.addWidget(ok_button)

        return self.__wrap_layout(netbios_layout)

    def __create_share_name_widget(self) -> QWidget:
        share_name_layout = QHBoxLayout()
        share_name_layout.setContentsMargins(0, 0, 0, 0)

        label = Widgets.create_label(self, "NOME DO COMPARTILHAMENTO:")

        share_name_label = Widgets.create_label(self, "PS2SMB", font=Fonts.BOLD_FONT)
        share_name_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        share_name_layout.addWidget(label)
        share_name_layout.addWidget(share_name_label)

        return self.__wrap_layout(share_name_layout)
    
    def __create_shared_folder_path_widget(self) -> QWidget:
        shared_folder_layout = QHBoxLayout()
        shared_folder_layout.setContentsMargins(0, 0, 0, 0)

        shared_folder_label = Widgets.create_label(self, "PASTA COMPARTILHADA:")

        shared_folder_path = Widgets.create_label(self, "/home/user/ps2smb", font=Fonts.BOLD_FONT)
        shared_folder_path.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        shared_folder_path.setAlignment(Qt.AlignmentFlag.AlignCenter)

        change_folder_button = Widgets.create_button(self, "ALTERAR")
        change_folder_button.clicked.connect(lambda: print("Change folder button clicked"))

        shared_folder_layout.addWidget(shared_folder_label)
        shared_folder_layout.addWidget(shared_folder_path)
        shared_folder_layout.addWidget(change_folder_button)

        return self.__wrap_layout(shared_folder_layout)
    
    def __net_settings_widget(self) -> QWidget:
        main_net_layout = QVBoxLayout()
        main_net_layout.setContentsMargins(0, 0, 0, 0)

        H_SPACE = 4
        V_SPACE = 20

        # Section title
        title_label = Widgets.create_label(self, "CONFIGURAÇÕES DE REDE", font=Fonts.BOLD_FONT)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Section body
        net_settings_layout = QHBoxLayout()
        net_settings_layout.setContentsMargins(0, 0, 0, 0)

        net_interface_label = Widgets.create_label(self, "INTERFACE:")
        net_interface_name = Widgets.create_label(self, "eth0", font=Fonts.BOLD_FONT)

        ip_label = Widgets.create_label(self, "IP:")
        ip_address_label = Widgets.create_label(self, "192.168.5.5", font=Fonts.BOLD_FONT)

        netmask_label = Widgets.create_label(self, "MASK:")
        netmask_address_label = Widgets.create_label(self, "255.255.255.0", font=Fonts.BOLD_FONT)

        net_settings_layout.addWidget(net_interface_label)
        net_settings_layout.addSpacerItem(QSpacerItem(H_SPACE, 0))
        net_settings_layout.addWidget(net_interface_name)
        net_settings_layout.addStretch()
        net_settings_layout.addWidget(ip_label)
        net_settings_layout.addSpacerItem(QSpacerItem(H_SPACE, 0))
        net_settings_layout.addWidget(ip_address_label)
        net_settings_layout.addStretch()
        net_settings_layout.addWidget(netmask_label)
        net_settings_layout.addSpacerItem(QSpacerItem(H_SPACE, 0))
        net_settings_layout.addWidget(netmask_address_label)

        # Adding the title and the settings layout to the main layout
        main_net_layout.addWidget(title_label)
        main_net_layout.addSpacing(V_SPACE)
        main_net_layout.addLayout(net_settings_layout)

        return self.__wrap_layout(main_net_layout)
        
    def __create_log_messages_container(self) -> QPlainTextEdit:
        msg_container = QPlainTextEdit(self)

        CONTAINER_HEIGHT = 200

        msg_container.setReadOnly(True)
        msg_container.setFont(Fonts.CODE_FONT)
        msg_container.setStyleSheet(F"background-color: {Colors.OFF_WHITE}; color: {Colors.OFF_BLACK};")
        msg_container.setFixedHeight(CONTAINER_HEIGHT)

        msg_container.setPlainText("Mensagens de status aparecerão aqui.")

        return msg_container
    
    def __create_samba_status_widget(self) -> QWidget:
        main_samba_status_layout = QVBoxLayout()
        main_samba_status_layout.setContentsMargins(10, 10, 10, 10)
        main_samba_status_layout.setSpacing(15)

        # Status line
        status_layout = QHBoxLayout()
        status_layout.setContentsMargins(0, 0, 0, 0)

        status_label = Widgets.create_label(self, "STATUS DO SERVIDOR:")

        status_value_label = Widgets.create_label(self, "INATIVO", font=Fonts.BOLD_FONT)
        status_value_label.setAlignment(Qt.AlignmentFlag.AlignRight)

        status_layout.addWidget(status_label)
        status_layout.addWidget(status_value_label)

        # Transmission speed line
        transmition_speed_layout = QHBoxLayout()
        transmition_speed_layout.setContentsMargins(0, 0, 0, 0)

        transmition_speed_label = Widgets.create_label(self, "VELOCIDADE DE TRANSMISSÃO:")

        transmission_speed_value_label = Widgets.create_label(self, "0 KB/s", font=Fonts.BOLD_FONT)
        transmission_speed_value_label.setAlignment(Qt.AlignmentFlag.AlignRight)

        transmition_speed_layout.addWidget(transmition_speed_label)
        transmition_speed_layout.addWidget(transmission_speed_value_label)

        # Log messages container
        log_msg_container = self.__create_log_messages_container()

        # Adding the widgets to the main layout
        main_samba_status_layout.addLayout(status_layout)
        main_samba_status_layout.addLayout(transmition_speed_layout)
        main_samba_status_layout.addWidget(log_msg_container)

        samba_status_widget = self.__wrap_layout(main_samba_status_layout)
        samba_status_widget.setStyleSheet(f"background-color: {Colors.DARK_LAVENDER}; border-radius: 10px;")
        return samba_status_widget
    
    def __create_main_buttons_widget(self):
        buttons_layout = QHBoxLayout()
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_layout.setSpacing(10)

        change_interface_button = Widgets.create_button(self, "ALTERAR INTERFACE DE REDE")
        change_interface_button.clicked.connect(lambda: print("Change interface button clicked"))

        start_button = Widgets.create_button(self, "INICIAR", bg_color=Colors.LIGHT_GREEN)
        start_button.clicked.connect(lambda: print("Start button clicked"))

        stop_button = Widgets.create_button(self, "PARAR", bg_color=Colors.SOFT_RED)
        stop_button.clicked.connect(lambda: print("Stop button clicked"))

        buttons_layout.addWidget(change_interface_button)
        buttons_layout.addStretch()
        buttons_layout.addWidget(start_button)
        buttons_layout.addWidget(stop_button)

        return self.__wrap_layout(buttons_layout)
