"""
Manejador de archivos .mlw (MyLiveWallpapers)
"""
# pylint: disable=no-member
import os
import shutil
import zipfile
import tempfile
from pathlib import Path


class MLWHandler:
    """Manejador de archivos .mlw"""
    
    def __init__(self):
        self.temp_dir = Path(tempfile.gettempdir()) / 'wallpaperpuka_mlw'
        self.temp_dir.mkdir(exist_ok=True)
    
    def extract_video(self, mlw_path):
        """Extraer video de archivo .mlw"""
        mlw_path = Path(mlw_path)
        
        # Método 1: Intentar como ZIP
        video_path = self._extract_from_zip(mlw_path)
        if video_path:
            print(f"Video extraido (ZIP): {video_path}")
            return video_path
        
        # Método 2: Es un video renombrado
        video_path = self._try_as_video(mlw_path)
        if video_path:
            print(f"Video detectado (renombrado): {video_path}")
            return video_path
        
        # Método 3: Buscar video embebido
        video_path = self._extract_embedded_video(mlw_path)
        if video_path:
            print(f"Video extraido (embebido): {video_path}")
            return video_path
        
        print(f"No se pudo extraer video de: {mlw_path}")
        return None
    
    def _extract_from_zip(self, mlw_path):
        """Intentar extraer como archivo ZIP"""
        try:
            with zipfile.ZipFile(mlw_path, 'r') as zip_ref:
                video_extensions = ['.mp4', '.avi', '.mov', '.webm', '.mkv']
                
                for file_info in zip_ref.filelist:
                    file_ext = Path(file_info.filename).suffix.lower()
                    if file_ext in video_extensions:
                        extract_path = self.temp_dir / file_info.filename
                        zip_ref.extract(file_info.filename, self.temp_dir)
                        return str(extract_path)
                
                zip_ref.extractall(self.temp_dir)
                for root, dirs, files in os.walk(self.temp_dir):
                    for filename in files:
                        file_path = Path(root) / filename
                        if file_path.suffix.lower() in video_extensions:
                            return str(file_path)
        except Exception as e:
            print(f"Error ZIP: {e}")
        
        return None
    
    def _try_as_video(self, mlw_path):
        """Intentar usar directamente como video"""
        try:
            import cv2
            
            temp_video = self.temp_dir / f"{mlw_path.stem}.mp4"
            shutil.copy2(mlw_path, temp_video)
            
            cap = cv2.VideoCapture(str(temp_video))
            if cap.isOpened():
                cap.release()
                return str(temp_video)
            
            temp_video = self.temp_dir / f"{mlw_path.stem}.webm"
            shutil.copy2(mlw_path, temp_video)
            cap = cv2.VideoCapture(str(temp_video))
            if cap.isOpened():
                cap.release()
                return str(temp_video)
        except Exception as e:
            print(f"Error video directo: {e}")
        
        return None
    
    def _extract_embedded_video(self, mlw_path):
        """Buscar video embebido en el archivo"""
        try:
            with open(mlw_path, 'rb') as f:
                data = f.read()
            
            mp4_start = data.find(b'ftyp')
            if mp4_start > 0:
                mp4_start -= 4
                output_path = self.temp_dir / f"{mlw_path.stem}_extracted.mp4"
                with open(output_path, 'wb') as out:
                    out.write(data[mp4_start:])
                return str(output_path)
            
            webm_signature = b'\x1A\x45\xDF\xA3'
            webm_start = data.find(webm_signature)
            if webm_start >= 0:
                output_path = self.temp_dir / f"{mlw_path.stem}_extracted.webm"
                with open(output_path, 'wb') as out:
                    out.write(data[webm_start:])
                return str(output_path)
        
        except Exception as e:
            print(f"Error video embebido: {e}")
        
        return None
    
    def cleanup(self):
        """Limpiar archivos temporales"""
        try:
            if self.temp_dir.exists():
                shutil.rmtree(self.temp_dir)
            print("Archivos temporales limpiados")
        except Exception as e:
            print(f"Error al limpiar: {e}")
    
    @staticmethod
    def is_mlw_file(file_path):
        """Verificar si es un archivo .mlw"""
        return Path(file_path).suffix.lower() == '.mlw'


def load_mlw(mlw_path):
    """Cargar archivo .mlw y obtener ruta del video"""
    handler = MLWHandler()
    return handler.extract_video(mlw_path)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        mlw_file = sys.argv[1]
        print(f"Procesando: {mlw_file}")
        
        handler = MLWHandler()
        video = handler.extract_video(mlw_file)
        
        if video:
            print(f"Video extraido: {video}")
        else:
            print("No se pudo extraer el video")
    else:
        print("Uso: python mlw_handler.py archivo.mlw")