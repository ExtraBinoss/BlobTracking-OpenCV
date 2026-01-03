from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPalette, QColor

class ThemeManager:
    @staticmethod
    def apply_theme(mode="dark"):
        app = QApplication.instance()
        if mode == "dark":
            app.setStyle("Fusion") # Fusion is a good base for cross-platform QSS
            app.setStyleSheet(ThemeManager.get_dark_qss())
        else:
            app.setStyle("Fusion")
            app.setStyleSheet(ThemeManager.get_light_qss())

    @staticmethod
    def get_dark_qss():
        return """
        /* GLOBAL */
        QWidget {
            background-color: #1e1e1e;
            color: #e0e0e0;
            font-family: "Segoe UI", "Roboto", sans-serif;
            font-size: 14px;
        }

        /* SCROLL BAR */
        QScrollBar:vertical {
            border: none;
            background: #2b2b2b;
            width: 10px;
            margin: 0px 0px 0px 0px;
        }
        QScrollBar::handle:vertical {
            background: #555;
            min-height: 20px;
            border-radius: 5px;
        }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            border: none;
            background: none;
        }
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
            background: none;
        }

        /* GROUP BOX */
        QGroupBox {
            border: 1px solid #3e3e3e;
            border-radius: 8px;
            margin-top: 20px;
            font-weight: bold;
            background-color: #252526;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 0 5px;
            left: 10px;
            color: #4facfe; 
        }

        /* BUTTONS */
        QPushButton {
            background-color: #333333;
            border: 1px solid #454545;
            border-radius: 6px;
            padding: 6px 12px;
            color: #ffffff;
        }
        QPushButton:hover {
            background-color: #3e3e3e;
            border-color: #0078d4;
        }
        QPushButton:pressed {
            background-color: #1f1f1f;
        }
        QPushButton:disabled {
            background-color: #2b2b2b;
            color: #777;
            border-color: #333;
        }

        /* COMBO BOX - Modern Web Style */
        QComboBox {
            background-color: #2d2d2d;
            border: 1px solid #3e3e3e;
            border-radius: 4px;
            padding: 5px 10px;
            min-height: 25px;
        }
        QComboBox:hover {
            border-color: #0078d4;
        }
        QComboBox::drop-down {
            border: none;
            width: 30px;
        }
        QComboBox::down-arrow {
            image: none;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 5px solid #e0e0e0;
            margin-right: 10px;
        }
        QComboBox QAbstractItemView {
            background-color: #2d2d2d;
            border: 1px solid #3e3e3e;
            selection-background-color: #0078d4;
            outline: none;
        }
        QComboBox QAbstractItemView::item {
            padding: 8px 10px;
            min-height: 25px;
        }
        QComboBox QAbstractItemView::item:hover {
            background-color: #3e3e3e;
        }

        /* SLIDERS */
        QSlider {
            min-height: 24px; /* Ensure space for handle */
        }
        QSlider::groove:horizontal {
            background: #2b2b2b;
            height: 6px;
            border-radius: 3px;
        }
        QSlider::sub-page:horizontal {
            background: #0078d4;
            border-radius: 3px;
        }
        QSlider::handle:horizontal {
            background: #ffffff;
            border: 1px solid #0078d4;
            width: 16px;
            height: 16px;
            margin: -5px 0; /* Center vertically */
            border-radius: 8px;
        }
        QSlider::handle:horizontal:hover {
            background: #f0f0f0;
        }

        /* LABELS & OTHERS */
        QLabel {
            color: #d4d4d4;
        }
        QLineEdit {
            background-color: #333;
            border: 1px solid #454545;
            border-radius: 4px;
            padding: 4px;
            color: #fff;
        }
        
        /* HIGHLIGHTS / ACCENTS */
        /* Make the title label in control panel pop */
        QLabel#ControlPanelTitle {
            font-size: 18px;
            color: #ffffff;
            font-weight: bold;
            margin-bottom: 10px;
        }
        
        /* Video Player Area */
        QLabel#VideoDisplay {
            background-color: #000000;
            border: 1px solid #333;
            border-radius: 4px;
        }
        """

    @staticmethod
    def get_light_qss():
        return """
        /* GLOBAL */
        QWidget {
            background-color: #f3f3f3;
            color: #333333;
            font-family: "Segoe UI", "Roboto", sans-serif;
            font-size: 14px;
        }

        /* GROUP BOX */
        QGroupBox {
            border: 1px solid #d4d4d4;
            border-radius: 8px;
            margin-top: 20px;
            font-weight: bold;
            background-color: #ffffff;
        }
        QGroupBox::title {
            color: #0078d4;
        }

        /* BUTTONS */
        QPushButton {
            background-color: #ffffff;
            border: 1px solid #c0c0c0;
            border-radius: 6px;
            padding: 6px 12px;
            color: #333;
        }
        QPushButton:hover {
            background-color: #f9f9f9;
            border-color: #0078d4;
        }
        QPushButton:pressed {
            background-color: #e6e6e6;
        }

        /* COMBO BOX */
        QComboBox {
            background-color: #ffffff;
            border: 1px solid #d4d4d4;
            border-radius: 4px;
            padding: 5px 10px;
            min-height: 25px;
        }
        QComboBox:hover {
            border-color: #0078d4;
        }
        QComboBox::drop-down {
            border: none;
            width: 30px;
        }
        QComboBox::down-arrow {
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 5px solid #555;
            margin-right: 10px;
        }
        QComboBox QAbstractItemView {
            background-color: #ffffff;
            selection-background-color: #0078d4;
            border: 1px solid #d4d4d4;
            outline: none;
        }

        /* SLIDERS */
        QSlider {
            min-height: 24px;
        }
        QSlider::groove:horizontal {
            background: #d4d4d4;
            height: 6px;
            border-radius: 3px;
        }
        QSlider::sub-page:horizontal {
            background: #0078d4;
            border-radius: 3px;
        }
        QSlider::handle:horizontal {
            background: #ffffff;
            border: 1px solid #0078d4;
            width: 16px;
            height: 16px;
            margin: -5px 0;
            border-radius: 8px;
        }

        /* LABELS */
        QLabel {
            color: #333;
        }
        
        QLabel#ControlPanelTitle {
            font-size: 18px;
            color: #111;
            font-weight: bold;
            margin-bottom: 10px;
        }
        """
