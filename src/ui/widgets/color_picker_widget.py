"""
Modern Color Picker Widget
Based on Tom F.'s design, simplified for inline use.
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QFrame)
from PyQt6.QtCore import Qt, pyqtSignal, QPoint
from PyQt6.QtGui import QColor, QPainter, QLinearGradient, QBrush, QPen, QMouseEvent
import colorsys


class HueBar(QWidget):
    """Vertical hue selection bar."""
    hueChanged = pyqtSignal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(20, 150)
        self._hue = 0
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw hue gradient
        for y in range(self.height()):
            hue = int(360 * y / self.height())
            color = QColor.fromHsv(hue, 255, 255)
            painter.setPen(QPen(color))
            painter.drawLine(0, y, self.width(), y)
        
        # Draw selector
        selector_y = int(self._hue * self.height() / 360)
        painter.setPen(QPen(Qt.GlobalColor.white, 2))
        painter.drawRect(0, selector_y - 2, self.width() - 1, 4)
    
    def mousePressEvent(self, event: QMouseEvent):
        self._updateHue(event.position().y())
    
    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self._updateHue(event.position().y())
    
    def _updateHue(self, y):
        y = max(0, min(y, self.height() - 1))
        self._hue = int(360 * y / self.height())
        self.update()
        self.hueChanged.emit(self._hue)
    
    def setHue(self, hue):
        self._hue = hue
        self.update()


class SaturationValueBox(QWidget):
    """Saturation/Value selection box."""
    svChanged = pyqtSignal(int, int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(150, 150)
        self._hue = 0
        self._sat = 255
        self._val = 255
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw color gradient
        base_color = QColor.fromHsv(self._hue, 255, 255)
        
        # White to color gradient (horizontal)
        for x in range(self.width()):
            for y in range(self.height()):
                sat = int(255 * x / self.width())
                val = int(255 * (self.height() - y) / self.height())
                color = QColor.fromHsv(self._hue, sat, val)
                painter.setPen(QPen(color))
                painter.drawPoint(x, y)
        
        # Draw selector
        sel_x = int(self._sat * self.width() / 255)
        sel_y = int((255 - self._val) * self.height() / 255)
        painter.setPen(QPen(Qt.GlobalColor.white, 2))
        painter.drawEllipse(sel_x - 5, sel_y - 5, 10, 10)
        painter.setPen(QPen(Qt.GlobalColor.black, 1))
        painter.drawEllipse(sel_x - 4, sel_y - 4, 8, 8)
    
    def mousePressEvent(self, event: QMouseEvent):
        self._updateSV(event.position())
    
    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self._updateSV(event.position())
    
    def _updateSV(self, pos):
        x = max(0, min(pos.x(), self.width() - 1))
        y = max(0, min(pos.y(), self.height() - 1))
        self._sat = int(255 * x / self.width())
        self._val = int(255 * (self.height() - y) / self.height())
        self.update()
        self.svChanged.emit(self._sat, self._val)
    
    def setHue(self, hue):
        self._hue = hue
        self.update()
    
    def setSV(self, sat, val):
        self._sat = sat
        self._val = val
        self.update()


class ColorPickerWidget(QWidget):
    """Modern inline color picker with HSV gradient."""
    colorChanged = pyqtSignal(QColor)
    
    def __init__(self, initial_color=None, parent=None):
        super().__init__(parent)
        self._color = initial_color or QColor(255, 255, 255)
        self.init_ui()
        self._setColorInternal(self._color)
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # Picker row
        picker_row = QHBoxLayout()
        picker_row.setSpacing(8)
        
        # SV Box
        self.sv_box = SaturationValueBox()
        self.sv_box.svChanged.connect(self._onSVChanged)
        picker_row.addWidget(self.sv_box)
        
        # Hue Bar
        self.hue_bar = HueBar()
        self.hue_bar.hueChanged.connect(self._onHueChanged)
        picker_row.addWidget(self.hue_bar)
        
        layout.addLayout(picker_row)
        
        # Color Preview & Hex Input
        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(8)
        
        # Preview
        self.preview = QFrame()
        self.preview.setFixedSize(40, 30)
        self.preview.setStyleSheet("background-color: #ffffff; border: 1px solid #555; border-radius: 4px;")
        bottom_row.addWidget(self.preview)
        
        # Hex Input
        self.hex_input = QLineEdit()
        self.hex_input.setPlaceholderText("#FFFFFF")
        self.hex_input.setMaxLength(7)
        self.hex_input.textEdited.connect(self._onHexEdited)
        bottom_row.addWidget(self.hex_input, 1)
        
        layout.addLayout(bottom_row)
    
    def _onHueChanged(self, hue):
        self.sv_box.setHue(hue)
        self._updateColor()
    
    def _onSVChanged(self, sat, val):
        self._updateColor()
    
    def _updateColor(self):
        hue = self.hue_bar._hue
        sat = self.sv_box._sat
        val = self.sv_box._val
        self._color = QColor.fromHsv(hue, sat, val)
        self._updatePreview()
        self.colorChanged.emit(self._color)
    
    def _updatePreview(self):
        self.preview.setStyleSheet(
            f"background-color: {self._color.name()}; border: 1px solid #555; border-radius: 4px;"
        )
        self.hex_input.setText(self._color.name().upper())
    
    def _onHexEdited(self, text):
        if not text.startswith('#'):
            text = '#' + text
        if len(text) == 7:
            color = QColor(text)
            if color.isValid():
                self._setColorInternal(color)
                self.colorChanged.emit(self._color)
    
    def _setColorInternal(self, color):
        self._color = color
        h, s, v, _ = color.getHsv()
        self.hue_bar.setHue(h)
        self.sv_box.setHue(h)
        self.sv_box.setSV(s, v)
        self._updatePreview()
    
    def getColor(self):
        return self._color
    
    def setColor(self, color):
        self._setColorInternal(color)
        self.colorChanged.emit(self._color)
    
    def getRGB(self):
        return (self._color.red(), self._color.green(), self._color.blue())


class CompactColorButton(QPushButton):
    """A button that shows a color and opens a picker popup."""
    colorChanged = pyqtSignal(QColor)
    
    def __init__(self, initial_color=None, parent=None):
        super().__init__(parent)
        self._color = initial_color or QColor(255, 255, 255)
        self._updateStyle()
        self.clicked.connect(self._showPicker)
        self.setMinimumHeight(30)
    
    def _updateStyle(self):
        # Button background IS the picked color
        text_color = '#000' if self._color.lightness() > 128 else '#fff'
        self.setStyleSheet(
            f"QPushButton {{ "
            f"background-color: {self._color.name()}; "
            f"color: {text_color}; "
            "border: 1px solid #555; border-radius: 4px; padding: 8px 12px; "
            "}"
            f"QPushButton:hover {{ background-color: {self._color.lighter(110).name()}; }}"
        )
        self.setText(self._color.name().upper())
    
    def _showPicker(self):
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QDialogButtonBox
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Pick Color")
        layout = QVBoxLayout(dialog)
        
        picker = ColorPickerWidget(self._color)
        layout.addWidget(picker)
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._color = picker.getColor()
            self._updateStyle()
            self.colorChanged.emit(self._color)
    
    def getColor(self):
        return self._color
    
    def setColor(self, color):
        self._color = color
        self._updateStyle()
    
    def getRGB(self):
        return (self._color.red(), self._color.green(), self._color.blue())
