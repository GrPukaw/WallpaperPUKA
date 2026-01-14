# pylint: disable=no-member
import os
import cv2
import tempfile
from pathlib import Path
import ctypes


class WallpaperManager:
    """Gestor de fondos de pantalla de Windows"""
    
    def __init__(self):
        self.SPI_SETDESKWALLPAPER = 0x0014
        self.SPIF_UPDATEINIFILE = 0x01
        self.SPIF_SENDCHANGE = 0x02
        self.original_wallpaper = self.get_current_wallpaper()
        self.temp_dir = Path(tempfile.gettempdir()) / 'wallpaperpuka'
        self.temp_dir.mkdir(exist_ok=True)
        
    def get_current_wallpaper(self):
        """Obtener fondo de pantalla actual"""
        try:
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Control Panel\Desktop",
                0,
                winreg.KEY_READ
            )
            wallpaper_path = winreg.QueryValueEx(key, "Wallpaper")
            winreg.CloseKey(key)
            return wallpaper_path[0]
        except Exception:
            return None
    
    def extract_frame_from_video(self, video_path):
        """Extraer un frame del video para usar como imagen"""
        try:
            cap = cv2.VideoCapture(video_path)  # pylint: disable=no-member
            
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            cap.set(cv2.CAP_PROP_POS_FRAMES, total_frames // 4)
            
            ret, frame = cap.read()
            cap.release()
            
            if ret:
                video_name = Path(video_path).stem
                temp_image = self.temp_dir / f"{video_name}_frame.jpg"
                cv2.imwrite(str(temp_image), frame)
                print(f"Frame extraido: {temp_image}")
                return str(temp_image)
            
            return None
        except Exception as e:
            print(f"Error al extraer frame: {e}")
            return None
        
    def set_wallpaper(self, file_path):
        """Establecer imagen o video como fondo de pantalla"""
        try:
            if not os.path.exists(file_path):
                print(f"Error: Archivo no existe: {file_path}")
                return False
            
            ext = Path(file_path).suffix.lower()
            
            # Si es video, extraer un frame primero
            video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.webm']
            if ext in video_extensions:
                print("Detectado video, extrayendo frame...")
                image_path = self.extract_frame_from_video(file_path)
                if not image_path:
                    print("No se pudo extraer frame del video")
                    return False
                file_path = image_path
            
            # Verificar que sea imagen válida
            valid_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
            if Path(file_path).suffix.lower() not in valid_extensions:
                print(f"Formato no soportado para fondo: {Path(file_path).suffix}")
                return False
            
            # Convertir a ruta absoluta
            abs_path = os.path.abspath(file_path)
            
            # Establecer fondo usando API de Windows
            result = ctypes.windll.user32.SystemParametersInfoW(
                self.SPI_SETDESKWALLPAPER,
                0,
                abs_path,
                self.SPIF_UPDATEINIFILE | self.SPIF_SENDCHANGE
            )
            
            if result:
                print(f"Fondo establecido: {abs_path}")
                return True
            else:
                print("Error al establecer fondo")
                return False
            
        except Exception as e:
            print(f"Error al establecer fondo: {e}")
            return False
    
    def restore_wallpaper(self):
        """Restaurar fondo de pantalla original"""
        if self.original_wallpaper:
            return self.set_wallpaper(self.original_wallpaper)
        return False