from PyQt6.QtWidgets import QComboBox
from PyQt6.QtCore import Qt, QEvent

class ClickableComboBox(QComboBox):
    """Custom combo box with better click handling."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setEditable(True)
        if self.lineEdit():
            self.lineEdit().setReadOnly(True)
            self.lineEdit().setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.lineEdit().installEventFilter(self)

    def eventFilter(self, obj, event):
        if self.lineEdit() and obj == self.lineEdit():
            if event.type() == QEvent.Type.MouseButtonRelease:
                # Toggle popup on click
                if self.view().isVisible():
                    self.hidePopup()
                else:
                    self.showPopup()
                return True
        return super().eventFilter(obj, event)
    
    def showPopup(self):
        """Override to ensure proper popup display."""
        super().showPopup()
    
    def hidePopup(self):
        """Override to ensure proper popup hide."""
        super().hidePopup()

    def wheelEvent(self, event):
        # Disable scrolling
        event.ignore()
