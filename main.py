import sys
import signal
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from src.ui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    
    # Handle Ctrl+C gracefully
    signal.signal(signal.SIGINT, lambda sig, frame: QApplication.quit())
    
    # Required for Python to catch signals while Qt event loop is running
    timer = QTimer()
    timer.start(100) 
    timer.timeout.connect(lambda: None) 

    window = MainWindow()
    window.show()
    
    exit_code = app.exec()
    print("\n🚀 See you later, space cowboy! Thanks for using BlobTrack.")
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
