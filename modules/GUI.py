import sys
from PyQt6.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout
from PyQt6.QtGui import QFontDatabase, QFont
from PyQt6.QtCore import Qt

class PS2NetManager(QWidget):
    # Dark Purple Palette
    _COLORS = {
        "bg": "#1A1326",  # Deep Purple
        "frame_bg": "#33294E",  # Dark Lavender
        "button_bg": "#815AC0",  # Soft Violet
        "text_color": "#EDE7F6",  # Off-White Text
    }

    def __init__(self):
        super().__init__()

        self.setWindowTitle("PS2 Network Manager")
        self.setGeometry(100, 100, 600, 600)

        # Carrega fontes personalizadas
        self._load_custom_fonts()

        menu_font = QFont("Quicksand Light", 16)

        # Create label with custom font
        label = QLabel("Hello, PyQt with Custom Font!", self)
        label.setFont(menu_font)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(label)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        self.setLayout(layout)

    def _load_custom_fonts(self):
        QFontDatabase.addApplicationFont("fonts/Quicksand-Light.ttf")
        QFontDatabase.addApplicationFont("fonts/Quicksand-Regular.ttf")
        QFontDatabase.addApplicationFont("fonts/Quicksand-Bold.ttf")

if __name__ == "__main__":
    # Executa a aplicação
    app = QApplication([])
    window = PS2NetManager()
    window.show()
    sys.exit(app.exec())