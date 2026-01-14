# pylint: disable=no-member,no-name-in-module
"""
Reproductor de video que se coloca detrás del escritorio de Windows
"""
import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtCore import QTimer, Qt, QRect
from PyQt5.QtGui import QImage, QPainter, QPixmap
import ctypes
from ctypes import wintypes


class DesktopVideoPlayer(QWidget):
    """Ventana que reproduce video detrás del escritorio"""
    
    def __init__(self):
        super().__init__()
        self.video_capture = None
        self.current_frame = None
        self.is_playing = False
        self.video_path = None
        
        # Timer para actualizar frames
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.fps = 24  # Reducir FPS para menor consumo
        
        # Cache de frames para optimización
        self.frame_skip = 1  # Saltar frames si es necesario
        
        self.init_window()
        
    def init_window(self):
        """Inicializar ventana detrás del escritorio"""
        # Obtener tamaño de la pantalla
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(screen)
        
        # Sin marco ni barra de título
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnBottomHint |
            Qt.Tool
        )
        
        # Fondo negro
        self.setStyleSheet("background-color: black;")
        
        # Hacer que la ventana esté detrás del escritorio
        self.send_to_desktop_background()
        
    def send_to_desktop_background(self):
        """Enviar ventana detrás del escritorio usando WinAPI"""
        try:
            # Obtener handle de la ventana
            hwnd = int(self.winId())
            
            # Encontrar el "Progman" (Program Manager)
            progman = ctypes.windll.user32.FindWindowW("Progman", None)
            
            # Enviar mensaje para crear WorkerW
            result = ctypes.c_int()
            ctypes.windll.user32.SendMessageTimeoutW(
                progman,
                0x052C,  # WM_SPAWN_WORKER
                0,
                0,
                0x0000,
                1000,
                ctypes.byref(result)
            )
            
            # Encontrar WorkerW que está detrás del escritorio
            workerw = None
            
            def enum_windows_callback(hwnd_enum, lparam):
                nonlocal workerw
                shelldll = ctypes.windll.user32.FindWindowExW(
                    hwnd_enum, 0, "SHELLDLL_DefView", None
                )
                if shelldll:
                    workerw = ctypes.windll.user32.FindWindowExW(
                        0, hwnd_enum, "WorkerW", None
                    )
                return True
            
            WNDENUMPROC = ctypes.WINFUNCTYPE(
                wintypes.BOOL,
                wintypes.HWND,
                wintypes.LPARAM
            )
            
            ctypes.windll.user32.EnumWindows(
                WNDENUMPROC(enum_windows_callback),
                0
            )
            
            # Establecer nuestra ventana como hijo de WorkerW
            if workerw:
                ctypes.windll.user32.SetParent(hwnd, workerw)
            else:
                ctypes.windll.user32.SetParent(hwnd, progman)
                
        except Exception as e:
            print(f"Error al colocar ventana en escritorio: {e}")
    
    def load_video(self, video_path):
        """Cargar video"""
        self.video_path = video_path
        
        if self.video_capture:
            self.video_capture.release()
        
        self.video_capture = cv2.VideoCapture(video_path)
        
        if not self.video_capture.isOpened():
            print(f"Error al abrir video: {video_path}")
            return False
        
        # Obtener FPS del video y limitarlo
        fps = self.video_capture.get(cv2.CAP_PROP_FPS)
        if fps > 0:
            self.fps = min(int(fps), 30)  # Máximo 30 FPS
        
        # Configurar para menor calidad pero mejor rendimiento
        self.video_capture.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        
        print(f"Video cargado: {video_path} ({self.fps} FPS)")
        return True
    
    def play(self):
        """Iniciar reproducción"""
        if self.video_capture and not self.is_playing:
            self.is_playing = True
            self.timer.start(1000 // self.fps)
            self.show()
            print("Reproducción iniciada")
    
    def pause(self):
        """Pausar reproducción"""
        if self.is_playing:
            self.is_playing = False
            self.timer.stop()
            print("Reproducción pausada")
    
    def stop(self):
        """Detener reproducción"""
        self.is_playing = False
        self.timer.stop()
        self.hide()
        
        if self.video_capture:
            self.video_capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
        
        print("Reproducción detenida")
    
    def update_frame(self):
        """Actualizar frame del video"""
        if not self.video_capture:
            return
        
        ret, frame = self.video_capture.read()
        
        if not ret:
            # Reiniciar video (loop)
            self.video_capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = self.video_capture.read()
            
            if not ret:
                return
        
        # Convertir frame a QImage
        self.current_frame = self.cv_to_qimage(frame)
        self.update()
    
    def cv_to_qimage(self, cv_frame):
        """Convertir frame de OpenCV a QImage"""
        # Obtener tamaño de pantalla
        height, width = self.height(), self.width()
        
        # Redimensionar con interpolación rápida
        frame_resized = cv2.resize(
            cv_frame, 
            (width, height),
            interpolation=cv2.INTER_LINEAR  # Más rápido que INTER_CUBIC
        )
        
        # Convertir BGR a RGB
        rgb_frame = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
        
        h, w, ch = rgb_frame.shape
        bytes_per_line = ch * w
        
        # Copiar datos para evitar problemas de memoria
        q_image = QImage(
            rgb_frame.copy(),
            w,
            h,
            bytes_per_line,
            QImage.Format_RGB888
        )
        
        return q_image
    
    def paintEvent(self, event):
        """Dibujar frame en la ventana"""
        if self.current_frame:
            painter = QPainter(self)
            painter.drawImage(0, 0, self.current_frame)
    
    def closeEvent(self, event):
        """Limpiar recursos al cerrar"""
        self.stop()
        if self.video_capture:
            self.video_capture.release()
        event.accept()


# Test standalone
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    player = DesktopVideoPlayer()
    
    # Cargar un video de prueba
    import os
    if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
        player.load_video(sys.argv[1])
        player.play()
    else:
        print("Uso: python desktop_video_player.py ruta_al_video.mp4")
    
    sys.exit(app.exec_())