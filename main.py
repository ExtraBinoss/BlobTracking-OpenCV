import sys
import signal
import ctypes
import platform
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from src.ui.main_window import MainWindow

def main():
    # Set App User Model ID for Windows (Icon Fix)
    if platform.system() == 'Windows':
        myappid = 'com.blobtrack.processor.v1' # arbitrary string
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    app = QApplication(sys.argv)
    
    # Set Desktop File Name for Linux
    if platform.system() == 'Linux':
        app.setDesktopFileName('blobtrack-cv')
    
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
