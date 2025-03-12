from PyQt6.QtWidgets import *
from PyQt6.QtGui import QFontDatabase, QFont
from PyQt6.QtCore import Qt, QRect

# Importing our custom modules
from modules.SambaManager import SambaManager

class PS2NetManagerGUI(QMainWindow):
    # Dark Purple Palette
    __COLORS = {
        "bg": "#1A1326",  # Deep Purple
        "frame_bg": "#33294E",  # Dark Lavender
        "button_bg": "#815AC0",  # Soft Violet
        "text_color": "#EDE7F6",  # Off-White Text
    }

    __WINDOW_DIMENSIONS = (800, 600)

    # Defining fonts
    __LIGHT_FONT = QFont("Quicksand Light", 16)
    __REGULAR_FONT = QFont("Quicksand Regular", 14)
    __BOLD_FONT = QFont("Quicksand Bold", 16, QFont.Weight.Bold)
    __CODE_FONT = QFont("Ubuntu Mono", 12, QFont.Weight.DemiBold)

    def __init__(self):
        super().__init__()

        self.setWindowTitle("PS2 Network Manager")

        # Center window on screen
        window_rec = QRect(0,0, self.__WINDOW_DIMENSIONS[0], self.__WINDOW_DIMENSIONS[1])
        window_rec.moveCenter(QApplication.primaryScreen().geometry().center())

        self.setGeometry(window_rec)
        self.setFixedSize(self.__WINDOW_DIMENSIONS[0], self.__WINDOW_DIMENSIONS[1])

        self.__load_custom_fonts()

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

        # Adding the widgets to the main layout
        main_layout.addWidget(netbios_widget)
        main_layout.addWidget(share_name_widget)
        main_layout.addWidget(shared_folder_widget)
        main_layout.addWidget(self.__create_hline())
        main_layout.addWidget(net_settings_widget)
        main_layout.addWidget(samba_status_widget)
        main_layout.addStretch()

        # Creating the main widget
        main_widget = QWidget()
        main_widget.setLayout(main_layout)
        main_widget.setStyleSheet(f"background-color: {self.__COLORS['bg']};")

        self.setCentralWidget(main_widget)

    def __load_custom_fonts(self):
        QFontDatabase.addApplicationFont("fonts/Quicksand-Light.ttf")
        QFontDatabase.addApplicationFont("fonts/Quicksand-Regular.ttf")
        QFontDatabase.addApplicationFont("fonts/Quicksand-Bold.ttf")
        QFontDatabase.addApplicationFont("fonts/UbuntuMono-Regular.ttf")

    def __create_hline(self):
        line = QFrame(self)
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        line.setStyleSheet(f"background-color: {self.__COLORS['button_bg']};")
        return line

    def __create_netbios_widget(self):
        netbios_layout = QHBoxLayout()
        netbios_layout.setContentsMargins(0, 0, 0, 0)

        label = QLabel("NOME NETBIOS:", self)
        label.setFont(self.__LIGHT_FONT)

        line_field = QLineEdit(self)
        line_field.setPlaceholderText("Nome NetBIOS")
        line_field.setFont(self.__REGULAR_FONT)
        line_field.setStyleSheet(f"background-color: {self.__COLORS['frame_bg']}; color: {self.__COLORS['text_color']};")
        line_field.setFixedHeight(label.sizeHint().height())
        line_field.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        ok_button = QPushButton("OK", self)
        ok_button.setFont(self.__BOLD_FONT)
        ok_button.setStyleSheet(f"background-color: {self.__COLORS['button_bg']}; color: {self.__COLORS['text_color']};")
        ok_button.clicked.connect(lambda: print("OK button clicked"))

        SPACER_WIDTH = 10

        netbios_layout.addWidget(label)
        netbios_layout.addSpacerItem(QSpacerItem(SPACER_WIDTH, 0))
        netbios_layout.addWidget(line_field)
        netbios_layout.addSpacerItem(QSpacerItem(SPACER_WIDTH, 0))
        netbios_layout.addWidget(ok_button)

        widget = QWidget()
        widget.setLayout(netbios_layout)

        return widget

    def __create_share_name_widget(self):
        share_name_layout = QHBoxLayout()
        share_name_layout.setContentsMargins(0, 0, 0, 0)

        label = QLabel("NOME DO COMPARTILHAMENTO:", self)
        label.setFont(self.__LIGHT_FONT)

        share_name_label = QLabel("PS2SMB", self)
        share_name_label.setFont(self.__BOLD_FONT)
        share_name_label.setStyleSheet(f"color: {self.__COLORS['text_color']};")
        
        share_name_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        share_name_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        share_name_layout.addWidget(label)
        share_name_layout.addWidget(share_name_label)

        widget = QWidget()
        widget.setLayout(share_name_layout)

        return widget
    
    def __create_shared_folder_path_widget(self):
        shared_folder_layout = QHBoxLayout()
        shared_folder_layout.setContentsMargins(0, 0, 0, 0)

        label = QLabel("PASTA COMPARTILHADA:", self)
        label.setFont(self.__LIGHT_FONT)

        shared_folder_path = QLabel("/home/user/ps2smb", self)
        shared_folder_path.setFont(self.__BOLD_FONT)
        shared_folder_path.setStyleSheet(f"color: {self.__COLORS['text_color']};")
        shared_folder_path.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        shared_folder_path.setAlignment(Qt.AlignmentFlag.AlignCenter)

        change_folder_button = QPushButton("ALTERAR", self)
        change_folder_button.setFont(self.__BOLD_FONT)
        change_folder_button.setStyleSheet(f"background-color: {self.__COLORS['button_bg']}; color: {self.__COLORS['text_color']};")
        change_folder_button.clicked.connect(lambda: print("Change folder button clicked"))

        shared_folder_layout.addWidget(label)
        shared_folder_layout.addWidget(shared_folder_path)
        shared_folder_layout.addWidget(change_folder_button)


        widget = QWidget()
        widget.setLayout(shared_folder_layout)
        return widget
    
    def __net_settings_widget(self):
        main_net_layout = QVBoxLayout()
        main_net_layout.setContentsMargins(0, 0, 0, 0)
        main_net_layout.setSpacing(15)

        title_label = QLabel("CONFIGURAÇÕES DE REDE", self)
        title_label.setFont(self.__BOLD_FONT)
        title_label.setStyleSheet(f"color: {self.__COLORS['text_color']};")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        main_net_layout.addWidget(title_label)

        net_settings_layout = QHBoxLayout()
        net_settings_layout.setContentsMargins(0, 0, 0, 0)

        SPACER_WIDTH = 4

        net_interface_label = QLabel("INTERFACE:", self)
        net_interface_label.setFont(self.__LIGHT_FONT)

        net_interface_name = QLabel("eth0", self)
        net_interface_name.setFont(self.__BOLD_FONT)
        net_interface_name.setStyleSheet(f"color: {self.__COLORS['text_color']};")

        ip_label = QLabel("IP:", self)
        ip_label.setFont(self.__LIGHT_FONT)

        ip_address_label = QLabel("192.168.5.5", self)
        ip_address_label.setFont(self.__BOLD_FONT)
        ip_address_label.setStyleSheet(f"color: {self.__COLORS['text_color']};")
        
        netmask_label = QLabel("MASK:", self)
        netmask_label.setFont(self.__LIGHT_FONT)
        netmask_label.setStyleSheet(f"color: {self.__COLORS['text_color']};")

        netmask_address_label = QLabel("255.255.255.0", self)
        netmask_address_label.setFont(self.__BOLD_FONT)
        netmask_address_label.setStyleSheet(f"color: {self.__COLORS['text_color']};")

        net_settings_layout.addWidget(net_interface_label)
        net_settings_layout.addSpacerItem(QSpacerItem(SPACER_WIDTH, 0))
        net_settings_layout.addWidget(net_interface_name)
        net_settings_layout.addStretch()
        net_settings_layout.addWidget(ip_label)
        net_settings_layout.addSpacerItem(QSpacerItem(SPACER_WIDTH, 0))
        net_settings_layout.addWidget(ip_address_label)
        net_settings_layout.addStretch()
        net_settings_layout.addWidget(netmask_label)
        net_settings_layout.addSpacerItem(QSpacerItem(SPACER_WIDTH, 0))
        net_settings_layout.addWidget(netmask_address_label)

        main_net_layout.addLayout(net_settings_layout)

        widget = QWidget()
        widget.setLayout(main_net_layout)
        return widget
        
    def __create_messages_container(self):
        msg_container = QPlainTextEdit(self)

        msg_container.setReadOnly(True)
        msg_container.setFont(self.__CODE_FONT)
        msg_container.setStyleSheet(F"background-color: {self.__COLORS['text_color']}; color: #000000;")
        msg_container.setFixedHeight(200)

        msg_container.setPlainText("Mensagens de status aparecerão aqui.")

        return msg_container
    
    def __create_samba_status_widget(self):
        main_status_layout = QVBoxLayout()
        main_status_layout.setContentsMargins(10, 10, 10, 10)
        main_status_layout.setSpacing(15)

        inner_layout_1 = QHBoxLayout()
        inner_layout_1.setContentsMargins(0, 0, 0, 0)

        status_label = QLabel("STATUS DO SERVIDOR:", self)
        status_label.setFont(self.__LIGHT_FONT)
        status_label.setStyleSheet(f"color: {self.__COLORS['text_color']};")

        status = QLabel("INATIVO", self)
        status.setFont(self.__BOLD_FONT)
        status.setStyleSheet(f"color: {self.__COLORS['text_color']};")
        status.setAlignment(Qt.AlignmentFlag.AlignRight)

        inner_layout_1.addWidget(status_label)
        inner_layout_1.addWidget(status)

        inner_layout_2 = QHBoxLayout()
        inner_layout_2.setContentsMargins(0, 0, 0, 0)

        transmition_speed_label = QLabel("VELOCIDADE DE TRANSMISSÃO:", self)
        transmition_speed_label.setFont(self.__LIGHT_FONT)
        transmition_speed_label.setStyleSheet(f"color: {self.__COLORS['text_color']};")

        transmition_speed = QLabel("100 Mbps", self)
        transmition_speed.setFont(self.__BOLD_FONT)
        transmition_speed.setStyleSheet(f"color: {self.__COLORS['text_color']};")
        transmition_speed.setAlignment(Qt.AlignmentFlag.AlignRight)

        inner_layout_2.addWidget(transmition_speed_label)
        inner_layout_2.addWidget(transmition_speed)

        main_status_layout.addLayout(inner_layout_1)
        main_status_layout.addLayout(inner_layout_2)
        main_status_layout.addWidget(self.__create_messages_container())

        widget = QWidget()
        widget.setLayout(main_status_layout)
        widget.setStyleSheet(f"background-color: {self.__COLORS['frame_bg']};")

        return widget


        



