import json
import os
from PyQt6.QtWidgets import QLabel, QWidget, QToolTip
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QCursor, QFont

class TooltipManager:
    _instance = None
    _data = {}

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = TooltipManager()
        return cls._instance

    def __init__(self):
        if TooltipManager._instance is not None:
            raise Exception("This class is a singleton!")
        self.load_data()

    def load_data(self):
        try:
            path = os.path.join("src", "assets", "tooltips.json")
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    TooltipManager._data = json.load(f)
            else:
                print(f"Warning: Tooltips file not found at {path}")
        except Exception as e:
            print(f"Error loading tooltips: {e}")

    def get_tooltip(self, category, key):
        """Returns (title, desc) tuple or None."""
        if category in TooltipManager._data:
            if key in TooltipManager._data[category]:
                item = TooltipManager._data[category][key]
                return item.get("title", ""), item.get("desc", "")
        return None, None

class InfoTooltip(QLabel):
    def __init__(self, category, key, parent=None):
        super().__init__(" [I] ", parent)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.tooltip_text = ""
        
        # Style
        self.setStyleSheet("""
            QLabel {
                color: #29b6f6;
                font-weight: bold;
                background: transparent;
                border: none;
                padding: 0px;
            }
            QLabel:hover {
                color: #81d4fa;
            }
        """)
        
        # Load Text
        title, desc = TooltipManager.get_instance().get_tooltip(category, key)
        if title and desc:
            # HTML formatted tooltip
            self.tooltip_text = f"<b>{title}</b><br><br>{desc}"
        else:
            self.setVisible(False) # Hide if key not found

    def enterEvent(self, event):
        if self.tooltip_text:
            QToolTip.showText(QCursor.pos(), self.tooltip_text, self)
        super().enterEvent(event)

    def leaveEvent(self, event):
        QToolTip.hideText()
        super().leaveEvent(event)
