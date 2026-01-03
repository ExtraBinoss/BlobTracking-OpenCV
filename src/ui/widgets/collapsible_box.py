from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, 
                             QScrollArea, QSizePolicy)
from PyQt6.QtCore import Qt, QPropertyAnimation, QParallelAnimationGroup, QAbstractAnimation, QEasingCurve

class CollapsibleBox(QWidget):
    def __init__(self, title="", parent=None):
        super().__init__(parent)
        self.toggle_btn = QPushButton(title)
        self.toggle_btn.setObjectName("CollapsibleHeader")
        self.toggle_btn.setCheckable(True)
        self.toggle_btn.setChecked(False) # Collapsed by default
        self.toggle_btn.toggled.connect(self.on_toggle)
        
        # Arrow icon logic could be added here (e.g., using setIcon or styled text)
        self.update_arrow()
        self.toggle_btn.toggled.connect(self.update_arrow)

        self.content_area = QWidget()
        self.content_area.setMaximumHeight(0)
        self.content_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        self.content_layout = QVBoxLayout(self.content_area)
        self.content_layout.setContentsMargins(0, 10, 0, 10)
        
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.addWidget(self.toggle_btn)
        self.main_layout.addWidget(self.content_area)
        
        self.anim = QPropertyAnimation(self.content_area, b"maximumHeight")
        self.anim.setDuration(300)
        self.anim.setStartValue(0)
        self.anim.setEndValue(0) # Will be updated
        self.anim.setEasingCurve(QEasingCurve.Type.InOutQuad)

    def on_toggle(self, checked):
        # Calculate height
        # self.content_area.adjustSize() 
        # But content layout might need time to calc? 
        # Let's rely on sizeHint
        content_height = self.content_layout.sizeHint().height()
        
        self.anim.setStartValue(self.content_area.height())
        self.anim.setEndValue(content_height if checked else 0)
        self.anim.start()

    def update_arrow(self):
        arrow = "▼" if self.toggle_btn.isChecked() else "▶"
        title = self.toggle_btn.text().replace("▼ ", "").replace("▶ ", "")
        self.toggle_btn.setText(f"{arrow} {title}")

    def set_content_layout(self, layout):
        # Move items from existing layout if any? Or just expect user to add to this layout
        # For this usage, we expose addWidget helper or access to content_layout
        pass

    def add_widget(self, widget):
        self.content_layout.addWidget(widget)

    def expand(self):
        self.toggle_btn.setChecked(True)

    def collapse(self):
        self.toggle_btn.setChecked(False)
