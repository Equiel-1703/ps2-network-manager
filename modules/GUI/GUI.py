from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt, QRect

# Importing our custom modules
from modules.GUI.GUIColors import GUIColors as Colors
from modules.GUI.GUIFonts import GUIFonts as Fonts
from modules.GUI.GUIFactory import GUIFactory
from modules.SambaManager import SambaManager

class PS2NetManagerGUI(QMainWindow):
    # (Width, Height)
    __WINDOW_DIMENSIONS = (800, 650)

    def __init__(self):
        super().__init__()

        self.setWindowTitle("PS2 Network Manager")

        # Center window on screen
        window_rec = QRect(0,0, self.__WINDOW_DIMENSIONS[0], self.__WINDOW_DIMENSIONS[1])
        window_rec.moveCenter(QApplication.primaryScreen().geometry().center())

        self.setGeometry(window_rec)
        self.setFixedSize(self.__WINDOW_DIMENSIONS[0], self.__WINDOW_DIMENSIONS[1])

        # Loading custom fonts
        Fonts.load_fonts()

        # Layouts
        ML_MARGIN = 10
        ML_SPACING = 15

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(ML_MARGIN, ML_MARGIN, ML_MARGIN, ML_MARGIN)
        main_layout.setSpacing(ML_SPACING)

        # Creating layouts for the sections of the GUI
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
        main_layout.addWidget(GUIFactory.create_hline(self, Colors.LIGHT_GOLD))
        main_layout.addWidget(net_settings_widget)
        main_layout.addWidget(samba_status_widget)
        main_layout.addStretch()
        main_layout.addWidget(main_buttons_widget)

        # Creating the main widget
        main_widget = QWidget()
        main_widget.setLayout(main_layout)
        main_widget.setStyleSheet(f"background-color: {Colors.DEEP_PURPLE};")

        self.setCentralWidget(main_widget)

    def __wrap_layout(self, layout: QLayout) -> QWidget:
        widget = QWidget()
        widget.setLayout(layout)
        return widget

    def __create_netbios_widget(self) -> QWidget:
        netbios_layout = QHBoxLayout()
        netbios_layout.setContentsMargins(0, 0, 0, 0)

        label = GUIFactory.create_label(self, "NOME NETBIOS:", Fonts.LIGHT_FONT, Colors.OFF_WHITE)

        line_field = QLineEdit(self)
        line_field.setPlaceholderText("Nome NetBIOS")
        line_field.setFont(Fonts.REGULAR_FONT)
        line_field.setStyleSheet(f"background-color: {Colors.DARK_LAVENDER}; color: {Colors.OFF_WHITE};")
        line_field.setFixedHeight(label.sizeHint().height()) # Same height as the label
        line_field.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        ok_button = GUIFactory.create_button(self, "OK", Fonts.BOLD_FONT, Colors.DEEP_MARINE, Colors.OFF_WHITE)
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

        label = GUIFactory.create_label(self, "NOME DO COMPARTILHAMENTO:", Fonts.LIGHT_FONT, Colors.OFF_WHITE)

        share_name_label = GUIFactory.create_label(self, "PS2SMB", Fonts.BOLD_FONT, Colors.OFF_WHITE)        
        share_name_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        share_name_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        share_name_layout.addWidget(label)
        share_name_layout.addWidget(share_name_label)

        return self.__wrap_layout(share_name_layout)
    
    def __create_shared_folder_path_widget(self) -> QWidget:
        shared_folder_layout = QHBoxLayout()
        shared_folder_layout.setContentsMargins(0, 0, 0, 0)

        shared_folder_label = GUIFactory.create_label(self, "PASTA COMPARTILHADA:", Fonts.LIGHT_FONT, Colors.OFF_WHITE)

        shared_folder_path = GUIFactory.create_label(self, "/home/user/ps2smb", Fonts.BOLD_FONT, Colors.OFF_WHITE)
        shared_folder_path.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        shared_folder_path.setAlignment(Qt.AlignmentFlag.AlignCenter)

        change_folder_button = GUIFactory.create_button(self, "ALTERAR", Fonts.BOLD_FONT, Colors.DEEP_MARINE, Colors.OFF_WHITE)
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
        title_label = GUIFactory.create_label(self, "CONFIGURAÇÕES DE REDE", Fonts.BOLD_FONT, Colors.OFF_WHITE)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Section body
        net_settings_layout = QHBoxLayout()
        net_settings_layout.setContentsMargins(0, 0, 0, 0)

        net_interface_label = GUIFactory.create_label(self, "INTERFACE:", Fonts.LIGHT_FONT, Colors.OFF_WHITE)
        net_interface_name = GUIFactory.create_label(self, "eth0", Fonts.BOLD_FONT, Colors.OFF_WHITE)

        ip_label = GUIFactory.create_label(self, "IP:", Fonts.LIGHT_FONT, Colors.OFF_WHITE)
        ip_address_label = GUIFactory.create_label(self, "192.168.5.5", Fonts.BOLD_FONT, Colors.OFF_WHITE)

        netmask_label = GUIFactory.create_label(self, "MASK:", Fonts.LIGHT_FONT, Colors.OFF_WHITE)
        netmask_address_label = GUIFactory.create_label(self, "255.255.255.0", Fonts.BOLD_FONT, Colors.OFF_WHITE)

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

        status_label = GUIFactory.create_label(self, "STATUS DO SERVIDOR:", Fonts.LIGHT_FONT, Colors.OFF_WHITE)

        status_value_label = GUIFactory.create_label(self, "INATIVO", Fonts.BOLD_FONT, Colors.OFF_WHITE)
        status_value_label.setAlignment(Qt.AlignmentFlag.AlignRight)

        status_layout.addWidget(status_label)
        status_layout.addWidget(status_value_label)

        # Transmission speed line
        transmition_speed_layout = QHBoxLayout()
        transmition_speed_layout.setContentsMargins(0, 0, 0, 0)

        transmition_speed_label = GUIFactory.create_label(self, "VELOCIDADE DE TRANSMISSÃO:", Fonts.LIGHT_FONT, Colors.OFF_WHITE)

        transmission_speed_value_label = GUIFactory.create_label(self, "0 KB/s", Fonts.BOLD_FONT, Colors.OFF_WHITE)
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
        samba_status_widget.setStyleSheet(f"background-color: {Colors.DARK_LAVENDER};")
        return samba_status_widget
    
    def __create_main_buttons_widget(self):
        buttons_layout = QHBoxLayout()
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_layout.setSpacing(10)

        change_interface_button = GUIFactory.create_button(
            self,
            "ALTERAR INTERFACE",
            Fonts.BOLD_FONT,
            Colors.DEEP_MARINE,
            Colors.OFF_WHITE
        )
        change_interface_button.clicked.connect(lambda: print("Change interface button clicked"))

        start_button = GUIFactory.create_button(
            self,
            "INICIAR",
            Fonts.BOLD_FONT,
            Colors.DEEP_MARINE,
            Colors.OFF_WHITE
        )
        start_button.clicked.connect(lambda: print("Start button clicked"))

        stop_button = GUIFactory.create_button(
            self,
            "PARAR",
            Fonts.BOLD_FONT,
            Colors.DEEP_MARINE,
            Colors.OFF_WHITE
        )
        stop_button.clicked.connect(lambda: print("Stop button clicked"))

        buttons_layout.addWidget(change_interface_button)
        buttons_layout.addStretch()
        buttons_layout.addWidget(start_button)
        buttons_layout.addWidget(stop_button)

        return self.__wrap_layout(buttons_layout)


        



