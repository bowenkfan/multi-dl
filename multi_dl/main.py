import sys

from PyQt6.QtWidgets import QApplication

from multi_dl.gui import MultiDLWindow

def main():
    # Initialize app
    app = QApplication(sys.argv)
    
    # Create and show GUI window
    window = MultiDLWindow()
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()