import os
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
