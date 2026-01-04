from PyQt6.QtWidgets import QApplication

class ThemeManager:
    @staticmethod
    def apply_theme():
        """Apply the single dark theme to the application."""
        app = QApplication.instance()
        app.setStyle("Fusion")
        app.setStyleSheet(ThemeManager.get_stylesheet())

    @staticmethod
    def get_stylesheet():
        return """
        /* GLOBAL */
        QWidget {
            background-color: #121212; /* Deep Dark Background */
            color: #e0e0e0;
            font-family: "Segoe UI", "Roboto", sans-serif;
            font-size: 14px;
        }

        /* SCROLL BAR */
        QScrollBar:vertical {
            border: none;
            background: #1e1e1e;
            width: 8px;
            margin: 0px;
            border-radius: 4px;
        }
        QScrollBar::handle:vertical {
            background: #444;
            min-height: 20px;
            border-radius: 4px;
        }
        QScrollBar::handle:vertical:hover {
            background: #666;
        }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0px;
        }
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
            background: none;
        }
        
        QScrollBar:horizontal {
            border: none;
            background: #1e1e1e;
            height: 8px;
            margin: 0px;
            border-radius: 4px;
        }
        QScrollBar::handle:horizontal {
            background: #444;
            min-width: 20px;
            border-radius: 4px;
        }
        QScrollBar::handle:horizontal:hover {
            background: #666;
        }
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
            width: 0px;
        }
        QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
            background: none;
        }

        /* GROUP BOX */
        QGroupBox {
            border: 1px solid #333;
            border-radius: 8px;
            margin-top: 1.5em; /* Space for title */
            background-color: #1e1e1e; /* Slightly lighter card */
            padding-top: 10px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 0 5px;
            left: 10px;
            color: #81c784; /* Soft Green */
            font-weight: bold;
            background-color: #121212; /* Matches global bg to look floating */
        }

        /* BUTTONS */
        QPushButton {
            background-color: #2c2c2c;
            border: 1px solid #3d3d3d;
            border-radius: 6px;
            padding: 6px 12px;
            color: #eee;
        }
        QPushButton:hover {
            background-color: #383838;
            border-color: #81c784;
        }
        QPushButton:pressed {
            background-color: #1f1f1f;
        }
        QPushButton:disabled {
            background-color: #222;
            color: #555;
            border-color: #2a2a2a;
        }
        
        QPushButton#PrimaryButton {
            background-color: #2e7d32;
            color: white;
            font-weight: bold;
            border: 1px solid #1b5e20;
        }
        QPushButton#PrimaryButton:hover {
            background-color: #388e3c;
            border-color: #4caf50;
        }
        QPushButton#PrimaryButton:disabled {
            background-color: #222;
            color: #555;
            border-color: #2a2a2a;
        }

        /* COMBO BOX */
        QComboBox {
            background-color: #2c2c2c;
            border: 1px solid #3d3d3d;
            border-radius: 6px;
            padding: 6px 12px;
            color: #eee;
        }
        QComboBox:hover {
            background-color: #353535;
            border-color: #555;
        }
        QComboBox::drop-down {
            border: none;
            width: 24px;
        }
        QComboBox::down-arrow {
            width: 0; 
            height: 0; 
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 5px solid #aaa;
            margin-right: 10px;
        }
        QComboBox QAbstractItemView {
            background-color: #2c2c2c;
            border: 1px solid #3d3d3d;
            selection-background-color: #2e7d32;
            selection-color: #ffffff;
            outline: none;
            border-radius: 6px;
            padding: 4px;
        }

        /* CHECKBOX */
        QCheckBox {
            spacing: 8px;
            color: #ccc;
        }
        QCheckBox::indicator {
            width: 16px;
            height: 16px;
            border: 1px solid #555;
            border-radius: 4px;
            background: #2c2c2c;
        }
        QCheckBox::indicator:hover {
            border-color: #81c784;
            background: #353535;
        }
        QCheckBox::indicator:checked {
            background-color: #2e7d32; /* Green Fill */
            border-color: #2e7d32;
            /* Note: Fusion style might not draw checkmark if we override indicator. 
               We use a distinct solid green square to indicate active. */
        }
        QCheckBox::indicator:unchecked:hover {
            background: #333;
        }

        /* SLIDERS */
        QSlider::groove:horizontal {
            background: #333;
            height: 4px;
            border-radius: 2px;
        }
        QSlider::sub-page:horizontal {
            background: #66bb6a;
            border-radius: 2px;
        }
        QSlider::handle:horizontal {
            background: #eee;
            border: none;
            width: 14px;
            height: 14px;
            margin: -5px 0; 
            border-radius: 7px;
        }
        QSlider::handle:horizontal:hover {
            background: #fff;
            transform: scale(1.1);
        }

        /* LABELS & INPUTS */
        QLabel {
            color: #ccc;
            background: transparent;
        }
        QLineEdit {
            background-color: #2c2c2c;
            border: 1px solid #3d3d3d;
            border-radius: 6px;
            padding: 6px;
            color: #fff;
        }
        QLineEdit:focus {
            border-color: #66bb6a;
        }
        
        /* SPECIFIC WIDGETS */
        QLabel#ControlPanelTitle {
            font-size: 16px;
            color: #fff;
            font-weight: bold;
            margin-bottom: 10px;
        }

        QLabel#ToolbarTitle {
            font-size: 18px;
            font-weight: bold;
            color: #81c784;
            padding: 0 10px;
        }
        
        QLabel#VideoDisplay {
            background-color: #000;
            border: 1px solid #333;
            border-radius: 8px;
        }
        
        QLabel#PlaceholderLabel {
            color: #666;
            font-size: 18px;
            font-weight: 500;
            letter-spacing: 0.5px;
        }
        
        QPushButton#ModeToggle {
            background-color: transparent;
            border: 1px solid #66bb6a;
            color: #aaa;
        }
        QPushButton#ModeToggle:checked {
            background-color: #2e7d32;
            color: #fff;
            font-weight: bold;
            border-color: #2e7d32;
        }
        
        /* TABS (If QTabWidget is used) */
        QTabWidget::pane {
            border: 1px solid #333;
            background: #1e1e1e;
            border-radius: 8px;
        }
        QTabBar::tab {
            background: #121212;
            color: #888;
            padding: 8px 16px;
            border-top-left-radius: 6px;
            border-top-right-radius: 6px;
            margin-right: 2px;
        }
        QTabBar::tab:selected {
            background: #1e1e1e;
            color: #81c784;
            font-weight: bold;
            border-bottom: none;
        }
        QTabBar::tab:hover {
            background: #222;
            color: #bbb;
        }
        """
