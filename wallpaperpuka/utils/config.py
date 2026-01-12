import json
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
