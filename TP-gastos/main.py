# main.py - Sistema de Control de Gastos y Presupuesto Personal
"""
Sistema completo de gestión de gastos personales con DearPyGUI.
Control de ingresos y egresos, filtrado por categorías y fechas, gráficos.
"""

import dearpygui.dearpygui as dpg
import sys
import os
import logging
from datetime import datetime

# Importar módulos de gestión
from modules.database_manager import DatabaseManager
from modules.categorias_manager import CategoriasManager
from modules.transacciones_manager import TransaccionesManager
from modules.ui_manager import UIManager

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GastosApp:
    """Aplicación principal del sistema de control de gastos"""
    
    def __init__(self):
        self.db_name = "gastos.db"
        
        try:
            logger.info("🚀 Inicializando sistema de control de gastos...")
            
            # Inicializar managers
            self.db_manager = DatabaseManager(self.db_name)
            logger.info("✅ Base de datos inicializada")
            
            self.categorias_manager = CategoriasManager(self.db_name)
            logger.info("✅ Manager de categorías inicializado")
            
            self.transacciones_manager = TransaccionesManager(self.db_name)
            logger.info("✅ Manager de transacciones inicializado")
            
            self.ui_manager = UIManager(self)
            logger.info("✅ Manager de interfaz inicializado")
            
            # Crear interfaz
            self.ui_manager.crear_interfaz_completa()
            logger.info("✅ Interfaz creada")
            
        except Exception as e:
            logger.error(f"❌ Error inicializando la aplicación: {e}")
            raise
    
    def cargar_datos_iniciales(self):
        """Cargar datos iniciales en las tablas - llamar después de show_viewport()"""
        logger.info("📊 Cargando datos iniciales en las tablas...")
        try:
            self.ui_manager.cargar_datos_iniciales()
            logger.info("✅ Datos iniciales cargados exitosamente")
        except Exception as e:
            logger.error(f"❌ Error cargando datos iniciales: {e}")
    
    def run(self):
        """Ejecutar la aplicación"""
        try:
            # Cargar datos DESPUÉS de show_viewport() pero ANTES de start_dearpygui()
            self.cargar_datos_iniciales()
            dpg.start_dearpygui()
        except KeyboardInterrupt:
            logger.info("Aplicación interrumpida por el usuario")
        finally:
            dpg.destroy_context()

def main():
    """Función principal"""
    try:
        app = GastosApp()
        app.run()
    except Exception as e:
        logger.error(f"Error fatal: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()