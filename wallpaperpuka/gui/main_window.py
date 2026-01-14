# pylint: disable=no-name-in-module
import os
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFileDialog, QSlider, 
    QSystemTrayIcon, QMenu, QAction, QApplication
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon
from wallpaperpuka.core.video_player import VideoPlayer
from wallpaperpuka.core.wallpaper_manager import WallpaperManager
from wallpaperpuka.core.desktop_video_player import DesktopVideoPlayer


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.video_player = VideoPlayer()
        self.wallpaper_manager = WallpaperManager()
        self.desktop_player = DesktopVideoPlayer()  # Reproductor de escritorio
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
        btn_select = QPushButton("📁 Seleccionar Video/GIF/MLW")
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
        btn_set_wallpaper.setStyleSheet(
            "padding: 15px; font-size: 14px; background-color: #4CAF50; "
            "color: white; font-weight: bold;"
        )
        btn_set_wallpaper.setEnabled(False)
        self.btn_set_wallpaper = btn_set_wallpaper
        layout.addWidget(btn_set_wallpaper)
        
        # Botón detener fondo animado
        btn_stop_wallpaper = QPushButton("⏹️ Detener Fondo Animado")
        btn_stop_wallpaper.clicked.connect(self.stop_animated_wallpaper)
        btn_stop_wallpaper.setStyleSheet(
            "padding: 10px; font-size: 12px; background-color: #f44336; "
            "color: white;"
        )
        layout.addWidget(btn_stop_wallpaper)
        
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
        """Seleccionar archivo de video/GIF/MLW"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar Video, GIF o MLW",
            "",
            "Todos los soportados (*.mp4 *.avi *.mov *.mkv *.gif *.mlw);;"
            "Videos (*.mp4 *.avi *.mov *.mkv);;"
            "GIFs (*.gif);;"
            "MLW Files (*.mlw);;"
            "Todos los archivos (*.*)"
        )
        
        if file_path:
            # Si es archivo .mlw, extraer el video primero
            if file_path.lower().endswith('.mlw'):
                from wallpaperpuka.utils.mlw_handler import MLWHandler
                self.status_label.setText("🔄 Procesando archivo .mlw...")
                self.status_label.setStyleSheet("color: orange; padding: 10px;")
                
                handler = MLWHandler()
                extracted_video = handler.extract_video(file_path)
                
                if extracted_video:
                    file_path = extracted_video
                    self.status_label.setText("✅ Archivo .mlw procesado")
                    self.status_label.setStyleSheet("color: green; padding: 10px;")
                else:
                    self.status_label.setText("❌ Error al procesar .mlw")
                    self.status_label.setStyleSheet("color: red; padding: 10px;")
                    return
            
            self.current_file = file_path
            filename = os.path.basename(file_path)
            self.file_label.setText(f"📹 {filename}")
            self.file_label.setStyleSheet(
                "color: black; font-weight: bold; margin: 10px;"
            )
            
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
            from pathlib import Path
            ext = Path(self.current_file).suffix.lower()
            video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.webm']
            
            # Si es video, usar reproductor de escritorio
            if ext in video_extensions:
                success = self.desktop_player.load_video(self.current_file)
                if success:
                    self.desktop_player.play()
                    self.status_label.setText("✅ Video animado establecido como fondo")
                    self.status_label.setStyleSheet("color: green; padding: 10px;")
                else:
                    self.status_label.setText("❌ Error al cargar video")
                    self.status_label.setStyleSheet("color: red; padding: 10px;")
            else:
                # Si es imagen, usar método tradicional
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
        # NO detener el reproductor de escritorio al minimizar
        self.tray_icon.showMessage(
            "WallpaperPUKA",
            "La aplicación sigue ejecutándose en segundo plano",
            QSystemTrayIcon.Information,
            2000
        )
    
    def stop_animated_wallpaper(self):
        """Detener fondo animado"""
        self.desktop_player.stop()
        self.status_label.setText("⏹️ Fondo animado detenido")
        self.status_label.setStyleSheet("color: orange; padding: 10px;")
    
    def quit_app(self):
        """Cerrar aplicación completamente"""
        self.video_player.stop()
        self.desktop_player.stop()  # Detener reproductor de escritorio
        self.tray_icon.hide()
        QApplication.quit()