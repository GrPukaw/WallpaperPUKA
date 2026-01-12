import sys
from PyQt5.QtWidgets import QApplication
from wallpaperpuka.gui.main_window import MainWindow

def main():
    """Entry point de la aplicación"""
    app = QApplication(sys.argv)
    app.setApplicationName("WallpaperPUKA")
    app.setOrganizationName("PUKA")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
