from PyQt6.QtWidgets import QComboBox
from PyQt6.QtCore import Qt, QEvent

class ClickableComboBox(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setEditable(True)
        self.popup_was_visible = False
        if self.lineEdit():
            self.lineEdit().setReadOnly(True)
            self.lineEdit().setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.lineEdit().installEventFilter(self)

    def eventFilter(self, obj, event):
        if self.lineEdit() and obj == self.lineEdit():
            if event.type() == QEvent.Type.MouseButtonPress:
                self.popup_was_visible = self.view().isVisible()
                return True # Consume press
            elif event.type() == QEvent.Type.MouseButtonRelease:
                if self.popup_was_visible:
                    self.hidePopup()
                else:
                    self.showPopup()
                return True
        return super().eventFilter(obj, event)
