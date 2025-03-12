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

        # Adding the widgets to the main layout
        main_layout.addWidget(netbios_widget)
        main_layout.addWidget(share_name_widget)
        main_layout.addWidget(shared_folder_widget)

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

    def __create_netbios_widget(self):
        netbios_layout = QHBoxLayout()

        label = QLabel("NOME NETBIOS:", self)
        label.setFont(self.__LIGHT_FONT)

        line_field = QLineEdit(self)
        line_field.setPlaceholderText("Nome NetBIOS")
        line_field.setFont(self.__REGULAR_FONT)
        line_field.setStyleSheet(f"background-color: {self.__COLORS['frame_bg']}; color: {self.__COLORS['text_color']};")
        line_field.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        ok_button = QPushButton("OK", self)
        ok_button.setFont(self.__BOLD_FONT)
        ok_button.setStyleSheet(f"background-color: {self.__COLORS['button_bg']}; color: {self.__COLORS['text_color']};")
        ok_button.clicked.connect(lambda: print("OK button clicked"))

        LINE_FIELD_H_SPACE = 10

        netbios_layout.addWidget(label)
        netbios_layout.addSpacerItem(QSpacerItem(LINE_FIELD_H_SPACE, 0))
        netbios_layout.addWidget(line_field)
        netbios_layout.addSpacerItem(QSpacerItem(LINE_FIELD_H_SPACE, 0))
        netbios_layout.addWidget(ok_button)

        netbios_layout.setContentsMargins(0, 0, 0, 0)

        widget = QWidget()
        widget.setLayout(netbios_layout)

        return widget

    def __create_share_name_widget(self):
        share_name_layout = QHBoxLayout()

        label = QLabel("NOME DO COMPARTILHAMENTO:", self)
        label.setFont(self.__LIGHT_FONT)

        share_name_label = QLabel("PS2SMB", self)
        share_name_label.setFont(self.__BOLD_FONT)
        share_name_label.setStyleSheet(f"color: {self.__COLORS['text_color']};")
        
        share_name_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        share_name_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        share_name_layout.addWidget(label)
        share_name_layout.addWidget(share_name_label)

        share_name_layout.setContentsMargins(0, 0, 0, 0)

        widget = QWidget()
        widget.setLayout(share_name_layout)

        return widget
    
    def __create_shared_folder_path_widget(self):
        shared_folder_layout = QHBoxLayout()

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

        shared_folder_layout.setContentsMargins(0, 0, 0, 0)

        widget = QWidget()
        widget.setLayout(shared_folder_layout)
        return widget
    
    def __ip_settings_widget(self):
        pass