# database_manager.py - Gestor de base de datos para el sistema de gastos
"""
DatabaseManager: Clase responsable de inicializar y gestionar la base de datos del sistema de gastos.
Implementa todas las tablas con soft delete y auditoría automática.
"""

import sqlite3
import logging
from datetime import datetime
from typing import Dict, Any
from . import sqlstatement as sql
from .base_model import BaseModel

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager(BaseModel):
    """
    Gestor principal de la base de datos del sistema de gastos.
    
    Funcionalidades:
    - Inicialización de todas las tablas
    - Creación de triggers para auditoría automática
    - Creación de índices para optimización
    - Creación de vistas para simplificar consultas
    - Verificación de integridad de datos
    """
    
    def __init__(self, db_name: str = "gastos.db"):
        super().__init__(db_name)
        self.db_name = db_name
        self.init_database()
    
    def init_database(self) -> bool:
        """
        Inicializar completamente la base de datos del sistema de gastos
        
        Returns:
            bool: True si se inicializó correctamente, False en caso contrario
        """
        try:
            logger.info("🚀 Inicializando base de datos del sistema de gastos...")
            
            # Crear todas las tablas
            success = (
                self._create_tables() and
                self._create_triggers() and
                self._create_indexes() and
                self._create_views()
            )
            
            if success:
                logger.info("✅ Base de datos inicializada correctamente")
                return True
            else:
                logger.error("❌ Error al inicializar la base de datos")
                return False
            
        except Exception as e:
            logger.error(f"❌ Error en init_database: {e}")
            return False
    
    def _create_tables(self) -> bool:
        """Crear todas las tablas necesarias"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute(sql.CREATE_TABLE_CATEGORIAS)
            cursor.execute(sql.CREATE_TABLE_TRANSACCIONES)
            
            conn.commit()
            conn.close()
            
            logger.info("✅ Tablas creadas correctamente")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error creando tablas: {e}")
            return False
    
    def _create_triggers(self) -> bool:
        """Crear triggers para auditoría automática"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute(sql.CREATE_TRIGGER_UPDATE_CATEGORIAS)
            cursor.execute(sql.CREATE_TRIGGER_UPDATE_TRANSACCIONES)
            
            conn.commit()
            conn.close()
            
            logger.info("✅ Triggers creados correctamente")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error creando triggers: {e}")
            return False
    
    def _create_indexes(self) -> bool:
        """Crear índices para optimización"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute(sql.CREATE_INDEX_TRANSACCIONES_FECHA)
            cursor.execute(sql.CREATE_INDEX_TRANSACCIONES_TIPO)
            cursor.execute(sql.CREATE_INDEX_TRANSACCIONES_CATEGORIA)
            
            conn.commit()
            conn.close()
            
            logger.info("✅ Índices creados correctamente")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error creando índices: {e}")
            return False
    
    def _create_views(self) -> bool:
        """Crear vistas para reportes"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute(sql.CREATE_VIEW_RESUMEN_MENSUAL)
            cursor.execute(sql.CREATE_VIEW_RESUMEN_CATEGORIAS)
            
            conn.commit()
            conn.close()
            
            logger.info("✅ Vistas creadas correctamente")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error creando vistas: {e}")
            return False
    
    def verificar_integridad(self) -> Dict[str, Any]:
        """
        Verificar la integridad de la base de datos
        
        Returns:
            Dict: Resultado de la verificación
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Verificar integridad
            cursor.execute("PRAGMA integrity_check;")
            integrity_result = cursor.fetchone()
            
            # Contar registros
            cursor.execute("SELECT COUNT(*) FROM categorias WHERE deleted_at IS NULL;")
            categorias_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM transacciones WHERE deleted_at IS NULL;")
            transacciones_count = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                "integrity_ok": integrity_result[0] == "ok",
                "categorias_count": categorias_count,
                "transacciones_count": transacciones_count,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error verificando integridad: {e}")
            return {"error": str(e)}