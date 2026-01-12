import os

print("🌊 Creando estructura de WallpaperPUKA...\n")

# Crear carpetas
os.makedirs('wallpaperpuka', exist_ok=True)
os.makedirs('wallpaperpuka/gui', exist_ok=True)
os.makedirs('wallpaperpuka/core', exist_ok=True)
os.makedirs('wallpaperpuka/utils', exist_ok=True)
os.makedirs('wallpaperpuka/resources', exist_ok=True)
os.makedirs('tests', exist_ok=True)
print("✓ Carpetas creadas")

# setup.py
with open('setup.py', 'w', encoding='utf-8') as f:
    f.write('''from setuptools import setup, find_packages

setup(
    name="wallpaperpuka",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "PyQt5>=5.15.0",
        "opencv-python>=4.5.0",
        "Pillow>=8.0.0",
        "pywin32>=300",
    ],
    entry_points={
        "console_scripts": [
            "wallpaperpuka=wallpaperpuka.main:main",
        ],
        "gui_scripts": [
            "wallpaperpuka-gui=wallpaperpuka.main:main",
        ],
    },
)
''')
print("✓ setup.py creado")

# requirements.txt
with open('requirements.txt', 'w') as f:
    f.write('''PyQt5>=5.15.0
opencv-python>=4.5.0
Pillow>=8.0.0
pywin32>=300
''')
print("✓ requirements.txt creado")

# wallpaperpuka/__init__.py
with open('wallpaperpuka/__init__.py', 'w') as f:
    f.write('__version__ = "0.1.0"\n')
print("✓ wallpaperpuka/__init__.py creado")

# wallpaperpuka/main.py
with open('wallpaperpuka/main.py', 'w', encoding='utf-8') as f:
    f.write('''import sys
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
''')
print("✓ wallpaperpuka/main.py creado")

# wallpaperpuka/gui/__init__.py
with open('wallpaperpuka/gui/__init__.py', 'w') as f:
    f.write('')
print("✓ wallpaperpuka/gui/__init__.py creado")

# wallpaperpuka/gui/main_window.py
with open('wallpaperpuka/gui/main_window.py', 'w', encoding='utf-8') as f:
    f.write('''from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                                QPushButton, QLabel, QFileDialog, QSlider, QSystemTrayIcon,
                                QMenu, QAction)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon
from wallpaperpuka.core.video_player import VideoPlayer
from wallpaperpuka.core.wallpaper_manager import WallpaperManager
import os

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.video_player = VideoPlayer()
        self.wallpaper_manager = WallpaperManager()
        self.current_file = None
        
        self.init_ui()
        self.create_tray_icon()
        
    def init_ui(self):
        """Inicializar interfaz de usuario"""
        self.setWindowTitle("🌊 WallpaperPUKA")
        self.setGeometry(100, 100, 500, 400)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        # Título
        title = QLabel("WallpaperPUKA")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin: 20px;")
        layout.addWidget(title)
        
        # Label de archivo actual
        self.file_label = QLabel("No hay archivo seleccionado")
        self.file_label.setAlignment(Qt.AlignCenter)
        self.file_label.setStyleSheet("color: gray; margin: 10px;")
        layout.addWidget(self.file_label)
        
        # Botón seleccionar archivo
        btn_select = QPushButton("📁 Seleccionar Video/GIF")
        btn_select.clicked.connect(self.select_file)
        btn_select.setStyleSheet("padding: 10px; font-size: 14px;")
        layout.addWidget(btn_select)
        
        # Controles de reproducción
        controls_layout = QHBoxLayout()
        
        self.btn_play = QPushButton("▶️ Reproducir")
        self.btn_play.clicked.connect(self.play)
        self.btn_play.setEnabled(False)
        
        self.btn_pause = QPushButton("⏸️ Pausar")
        self.btn_pause.clicked.connect(self.pause)
        self.btn_pause.setEnabled(False)
        
        self.btn_stop = QPushButton("⏹️ Detener")
        self.btn_stop.clicked.connect(self.stop)
        self.btn_stop.setEnabled(False)
        
        controls_layout.addWidget(self.btn_play)
        controls_layout.addWidget(self.btn_pause)
        controls_layout.addWidget(self.btn_stop)
        
        layout.addLayout(controls_layout)
        
        # Control de volumen
        volume_layout = QHBoxLayout()
        volume_label = QLabel("🔊 Volumen:")
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)
        self.volume_slider.valueChanged.connect(self.change_volume)
        
        volume_layout.addWidget(volume_label)
        volume_layout.addWidget(self.volume_slider)
        layout.addLayout(volume_layout)
        
        # Botón establecer como fondo
        btn_set_wallpaper = QPushButton("🖥️ Establecer como Fondo de Pantalla")
        btn_set_wallpaper.clicked.connect(self.set_as_wallpaper)
        btn_set_wallpaper.setStyleSheet("padding: 15px; font-size: 14px; background-color: #4CAF50; color: white; font-weight: bold;")
        btn_set_wallpaper.setEnabled(False)
        self.btn_set_wallpaper = btn_set_wallpaper
        layout.addWidget(btn_set_wallpaper)
        
        # Espaciador
        layout.addStretch()
        
        # Label de estado
        self.status_label = QLabel("Listo")
        self.status_label.setStyleSheet("color: green; padding: 10px;")
        layout.addWidget(self.status_label)
        
    def create_tray_icon(self):
        """Crear icono en system tray"""
        self.tray_icon = QSystemTrayIcon(self)
        
        # Menú del tray
        tray_menu = QMenu()
        
        show_action = QAction("Mostrar", self)
        show_action.triggered.connect(self.show)
        tray_menu.addAction(show_action)
        
        play_action = QAction("▶️ Reproducir", self)
        play_action.triggered.connect(self.play)
        tray_menu.addAction(play_action)
        
        pause_action = QAction("⏸️ Pausar", self)
        pause_action.triggered.connect(self.pause)
        tray_menu.addAction(pause_action)
        
        tray_menu.addSeparator()
        
        quit_action = QAction("Salir", self)
        quit_action.triggered.connect(self.quit_app)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        
    def select_file(self):
        """Seleccionar archivo de video/GIF"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar Video o GIF",
            "",
            "Videos (*.mp4 *.avi *.mov *.mkv);;GIFs (*.gif);;Todos los archivos (*.*)"
        )
        
        if file_path:
            self.current_file = file_path
            filename = os.path.basename(file_path)
            self.file_label.setText(f"📹 {filename}")
            self.file_label.setStyleSheet("color: black; font-weight: bold; margin: 10px;")
            
            # Habilitar botones
            self.btn_play.setEnabled(True)
            self.btn_set_wallpaper.setEnabled(True)
            
            self.status_label.setText(f"Archivo cargado: {filename}")
            self.status_label.setStyleSheet("color: blue; padding: 10px;")
    
    def play(self):
        """Reproducir video"""
        if self.current_file:
            self.video_player.play(self.current_file)
            self.btn_pause.setEnabled(True)
            self.btn_stop.setEnabled(True)
            self.status_label.setText("▶️ Reproduciendo...")
            self.status_label.setStyleSheet("color: green; padding: 10px;")
    
    def pause(self):
        """Pausar video"""
        self.video_player.pause()
        self.status_label.setText("⏸️ Pausado")
        self.status_label.setStyleSheet("color: orange; padding: 10px;")
    
    def stop(self):
        """Detener video"""
        self.video_player.stop()
        self.btn_pause.setEnabled(False)
        self.btn_stop.setEnabled(False)
        self.status_label.setText("⏹️ Detenido")
        self.status_label.setStyleSheet("color: red; padding: 10px;")
    
    def change_volume(self, value):
        """Cambiar volumen"""
        self.video_player.set_volume(value)
    
    def set_as_wallpaper(self):
        """Establecer como fondo de pantalla"""
        if self.current_file:
            success = self.wallpaper_manager.set_wallpaper(self.current_file)
            if success:
                self.status_label.setText("✅ Fondo de pantalla establecido")
                self.status_label.setStyleSheet("color: green; padding: 10px;")
            else:
                self.status_label.setText("❌ Error al establecer fondo")
                self.status_label.setStyleSheet("color: red; padding: 10px;")
    
    def closeEvent(self, event):
        """Minimizar a tray en lugar de cerrar"""
        event.ignore()
        self.hide()
        self.tray_icon.showMessage(
            "WallpaperPUKA",
            "La aplicación sigue ejecutándose en segundo plano",
            QSystemTrayIcon.Information,
            2000
        )
    
    def quit_app(self):
        """Cerrar aplicación completamente"""
        self.video_player.stop()
        self.tray_icon.hide()
        QApplication.quit()
''')
print("✓ wallpaperpuka/gui/main_window.py creado")

# wallpaperpuka/core/__init__.py
with open('wallpaperpuka/core/__init__.py', 'w') as f:
    f.write('')
print("✓ wallpaperpuka/core/__init__.py creado")

# wallpaperpuka/core/video_player.py
with open('wallpaperpuka/core/video_player.py', 'w', encoding='utf-8') as f:
    f.write('''import cv2
from PyQt5.QtCore import QThread, pyqtSignal

class VideoPlayer:
    """Reproductor de videos optimizado"""
    
    def __init__(self):
        self.cap = None
        self.is_playing = False
        self.is_paused = False
        self.volume = 50
        self.current_file = None
        
    def play(self, file_path):
        """Iniciar reproducción de video"""
        self.current_file = file_path
        self.cap = cv2.VideoCapture(file_path)
        self.is_playing = True
        self.is_paused = False
        print(f"Reproduciendo: {file_path}")
        
    def pause(self):
        """Pausar reproducción"""
        self.is_paused = not self.is_paused
        print("Pausado" if self.is_paused else "Reanudado")
        
    def stop(self):
        """Detener reproducción"""
        self.is_playing = False
        self.is_paused = False
        if self.cap:
            self.cap.release()
            self.cap = None
        print("Detenido")
        
    def set_volume(self, volume):
        """Establecer volumen (0-100)"""
        self.volume = volume
        print(f"Volumen: {volume}%")
        
    def get_frame(self):
        """Obtener frame actual del video"""
        if self.cap and self.is_playing and not self.is_paused:
            ret, frame = self.cap.read()
            if ret:
                return frame
            else:
                # Loop del video
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret, frame = self.cap.read()
                return frame if ret else None
        return None
''')
print("✓ wallpaperpuka/core/video_player.py creado")

# wallpaperpuka/core/wallpaper_manager.py
with open('wallpaperpuka/core/wallpaper_manager.py', 'w', encoding='utf-8') as f:
    f.write('''import os
import ctypes
from ctypes import wintypes

class WallpaperManager:
    """Gestor de fondos de pantalla de Windows"""
    
    def __init__(self):
        self.SPI_SETDESKWALLPAPER = 0x0014
        self.SPIF_UPDATEINIFILE = 0x01
        self.SPIF_SENDCHANGE = 0x02
        
    def set_wallpaper(self, image_path):
        """
        Establecer imagen como fondo de pantalla
        Para videos, se toma un frame y se establece como fondo
        """
        try:
            # Convertir a ruta absoluta
            abs_path = os.path.abspath(image_path)
            
            # Establecer fondo usando API de Windows
            ctypes.windll.user32.SystemParametersInfoW(
                self.SPI_SETDESKWALLPAPER,
                0,
                abs_path,
                self.SPIF_UPDATEINIFILE | self.SPIF_SENDCHANGE
            )
            
            print(f"Fondo establecido: {abs_path}")
            return True
            
        except Exception as e:
            print(f"Error al establecer fondo: {e}")
            return False
    
    def set_video_as_wallpaper(self, video_path):
        """
        Establecer video como fondo (versión avanzada)
        Por ahora establece un frame del video
        """
        # TODO: Implementar reproducción continua en el fondo
        # Esto requiere crear una ventana detrás del escritorio
        print(f"Estableciendo video como fondo: {video_path}")
        return self.set_wallpaper(video_path)
''')
print("✓ wallpaperpuka/core/wallpaper_manager.py creado")

# wallpaperpuka/utils/__init__.py
with open('wallpaperpuka/utils/__init__.py', 'w') as f:
    f.write('')
print("✓ wallpaperpuka/utils/__init__.py creado")

# wallpaperpuka/utils/config.py
with open('wallpaperpuka/utils/config.py', 'w', encoding='utf-8') as f:
    f.write('''import json
import os
from pathlib import Path

class Config:
    """Gestor de configuración de la aplicación"""
    
    def __init__(self):
        self.config_dir = Path.home() / '.wallpaperpuka'
        self.config_file = self.config_dir / 'config.json'
        self.config_dir.mkdir(exist_ok=True)
        self.settings = self.load()
    
    def load(self):
        """Cargar configuración"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return json.load(f)
        return self.default_settings()
    
    def save(self):
        """Guardar configuración"""
        with open(self.config_file, 'w') as f:
            json.dump(self.settings, f, indent=2)
    
    def default_settings(self):
        """Configuración por defecto"""
        return {
            'volume': 50,
            'autostart': False,
            'loop': True,
            'recent_files': []
        }
    
    def get(self, key, default=None):
        """Obtener valor de configuración"""
        return self.settings.get(key, default)
    
    def set(self, key, value):
        """Establecer valor de configuración"""
        self.settings[key] = value
        self.save()
''')
print("✓ wallpaperpuka/utils/config.py creado")

# tests/__init__.py
with open('tests/__init__.py', 'w') as f:
    f.write('')
print("✓ tests/__init__.py creado")

# .gitignore adicional para el proyecto
with open('.gitignore', 'a') as f:
    f.write('''
# WallpaperPUKA específico
*.mp4
*.avi
*.mov
*.gif
build/
dist/
*.spec
''')
print("✓ .gitignore actualizado")

print("\n✨ ¡Estructura creada exitosamente!")
print("\n📋 Siguientes pasos:")
print("1. pip install -e .")
print("2. python -m wallpaperpuka.main")
print("\n🌊 ¡WallpaperPUKA listo para desarrollar!")