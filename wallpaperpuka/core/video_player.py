import cv2
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
