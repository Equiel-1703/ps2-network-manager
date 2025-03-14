from PyQt6.QtGui import QFontDatabase, QFont

class GUIFonts:
    LIGHT_FONT = QFont("Quicksand Light", 16, QFont.Weight.Light)
    REGULAR_FONT = QFont("Quicksand Regular", 14, QFont.Weight.Normal)
    BOLD_FONT = QFont("Quicksand Bold", 16, QFont.Weight.Bold)
    CODE_FONT = QFont("Ubuntu Mono", 12, QFont.Weight.Normal)

    @staticmethod
    def load_fonts():
        QFontDatabase.addApplicationFont(":/fonts/Quicksand-Light.ttf")
        QFontDatabase.addApplicationFont(":/fonts/Quicksand-Regular.ttf")
        QFontDatabase.addApplicationFont(":/fonts/Quicksand-Bold.ttf")
        QFontDatabase.addApplicationFont(":/fonts/UbuntuMono-R.ttf")