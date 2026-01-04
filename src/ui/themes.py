from PyQt6.QtWidgets import QApplication

class ThemeManager:
    @staticmethod
    def apply_theme(mode="dark"):
        app = QApplication.instance()
        if mode == "dark":
            app.setStyle("Fusion")
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
            margin: 0px;
            border-radius: 5px;
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

        /* COLLAPSIBLE BOX HEADER */
        QPushButton#CollapsibleHeader {
            background-color: #2d2d2d;
            border: none; /* Removed Border for simpler look */
            border-radius: 8px; /* Rounder */
            text-align: left;
            padding: 10px 15px;
            font-weight: bold;
            color: #43a047; 
        }
        QPushButton#CollapsibleHeader:hover {
            background-color: #3e3e3e;
        }
        
        /* GROUP BOX */
        QGroupBox {
            border: 1px solid #3e3e3e;
            border-radius: 12px; /* Rounder */
            margin-top: 20px;
            font-weight: bold;
            background-color: #252526;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 0 5px;
            left: 10px;
            color: #66bb6a; 
        }

        /* BUTTONS */
        QPushButton {
            background-color: #333333;
            border: 1px solid #454545;
            border-radius: 8px; /* Rounder */
            padding: 8px 16px;
            color: #ffffff;
        }
        QPushButton:hover {
            background-color: #3e3e3e;
            border-color: #43a047;
        }
        QPushButton:pressed {
            background-color: #1f1f1f;
        }
        QPushButton:disabled {
            background-color: #2b2b2b;
            color: #777;
            border-color: #333;
        }

        /* COMBO BOX - Simpler, Flat */
        QComboBox {
            background-color: #2d2d2d;
            border: none; /* No border by default */
            border-radius: 8px;
            padding: 8px 15px;
            min-height: 25px;
            color: #eee;
        }
        QComboBox:hover {
            background-color: #383838; /* Slight lighten on hover */
        }
        QComboBox::drop-down {
            border: none;
            width: 30px;
        }
        QComboBox::down-arrow {
            image: none;
            border: none; 
            /* Simple CSS Arrow or use image? CSS Arrow is fine */
            width: 0; 
            height: 0; 
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 5px solid #aaa;
            margin-right: 15px;
        }
        /* Fix for editable=True hack */
        QComboBox QLineEdit {
            border: none;
            background: transparent;
            color: #eee;
        }
        QComboBox QAbstractItemView {
            background-color: #252526;
            border: 1px solid #3e3e3e;
            selection-background-color: #43a047;
            selection-color: #ffffff;
            outline: none;
            border-radius: 8px;
            padding: 4px;
        }
        QComboBox QAbstractItemView::item {
            padding: 8px 10px;
            min-height: 25px;
            border-radius: 4px; /* Soft roundness for items */
            margin: 2px; /* Spacing between items */
        }
        QComboBox QAbstractItemView::item:hover {
            background-color: #3e3e3e; /* Distinct hover color */
            color: #ffffff;
        }
        QComboBox QAbstractItemView::item:selected {
            background-color: #43a047; /* Selected item color */
            color: #ffffff;
        }

        /* SLIDERS */
        QSlider {
            min-height: 24px; 
        }
        QSlider::groove:horizontal {
            background: #2b2b2b;
            height: 6px;
            border-radius: 3px;
        }
        QSlider::sub-page:horizontal {
            background: #43a047;
            border-radius: 3px;
        }
        QSlider::handle:horizontal {
            background: #ffffff;
            border: 1px solid #43a047;
            width: 18px; /* Slightly larger thumb */
            height: 18px;
            margin: -6px 0; 
            border-radius: 9px; /* Round */
        }
        QSlider::handle:horizontal:hover {
            background: #e8f5e9;
        }

        /* LABELS & OTHERS */
        QLabel {
            color: #d4d4d4;
            background: transparent;
        }
        QLineEdit {
            background-color: #333;
            border: 1px solid #454545;
            border-radius: 8px;
            padding: 8px;
            color: #fff;
        }
        
        /* HIGHLIGHTS / ACCENTS */
        QLabel#ControlPanelTitle {
            font-size: 18px;
            color: #ffffff;
            font-weight: bold;
            margin-bottom: 15px;
        }

        /* Toolbar Title */
        QLabel#ToolbarTitle {
            font-size: 20px;
            font-weight: bold;
            color: #66bb6a;
            padding: 0 10px;
        }
        
        /* Video Player Area */
        QLabel#VideoDisplay {
            background-color: transparent;
            border: 1px solid #333;
            border-radius: 12px;
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
        
         /* COLLAPSIBLE BOX HEADER */
        QPushButton#CollapsibleHeader {
            background-color: #ffffff;
            border: none;
            border-radius: 8px;
            text-align: left;
            padding: 10px 15px;
            font-weight: bold;
            color: #2e7d32; 
        }
        QPushButton#CollapsibleHeader:hover {
            background-color: #f0f0f0;
        }

        /* GROUP BOX */
        QGroupBox {
            border: 1px solid #d4d4d4;
            border-radius: 12px;
            margin-top: 20px;
            font-weight: bold;
            background-color: #ffffff;
        }
        QGroupBox::title {
            color: #2e7d32;
        }

        /* BUTTONS */
        QPushButton {
            background-color: #ffffff;
            border: 1px solid #c0c0c0;
            border-radius: 8px;
            padding: 8px 16px;
            color: #333;
        }
        QPushButton:hover {
            background-color: #f9f9f9;
            border-color: #43a047;
        }
        QPushButton:pressed {
            background-color: #e6e6e6;
        }

        /* COMBO BOX */
        QComboBox {
            background-color: #ffffff;
            border: none;
            border-radius: 8px;
            padding: 8px 15px;
            min-height: 25px;
            color: #333;
        }
        QComboBox:hover {
            background-color: #e0e0e0;
        }
        QComboBox::drop-down {
            border: none;
            width: 30px;
        }
        QComboBox::down-arrow {
            border: none;
            width: 0; 
            height: 0;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 5px solid #555;
            margin-right: 15px;
        }
        QComboBox QAbstractItemView {
            background-color: #ffffff;
            selection-background-color: #43a047;
            border: 1px solid #d4d4d4;
            outline: none;
            border-radius: 8px;
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
            background: #43a047;
            border-radius: 3px;
        }
        QSlider::handle:horizontal {
            background: #ffffff;
            border: 1px solid #43a047;
            width: 18px;
            height: 18px;
            margin: -6px 0;
            border-radius: 9px;
        }

        /* LABELS */
        QLabel {
            color: #333;
            background: transparent;
        }
        
        QLabel#ControlPanelTitle {
            font-size: 18px;
            color: #111;
            font-weight: bold;
            margin-bottom: 15px;
        }

        /* Toolbar Title */
        QLabel#ToolbarTitle {
            font-size: 20px;
            font-weight: bold;
            color: #2e7d32;
            padding: 0 10px;
        }
        """
