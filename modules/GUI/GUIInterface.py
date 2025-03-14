from typing import Protocol
from PyQt6.QtWidgets import QWidget

class GUIInterface(Protocol):
    """Interface for the GUI controller to interact with simulating the main GUI of the program.
    
    This interface is used to decouple the GUI controller from the actual GUI implementation. Not to mention that this avoids circular imports.
    """
    
    def findChild(self, type, name: str) -> QWidget:
        """Should return a child widget given its type and name."""
        pass
    
    def closeEvent(self, event) -> None:
        """Should handle the close event of the GUI."""
        pass