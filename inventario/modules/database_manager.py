# database_manager.py - Gestor de base de datos para el sistema de inventario
"""
DatabaseManager: Clase responsable de inicializar y gestionar la base de datos del inventario.
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
    Gestor principal de la base de datos del inventario.
    
    Funcionalidades:
    - Inicialización de todas las tablas
    - Creación de triggers para auditoría automática
    - Creación de índices para optimización
    - Creación de vistas para simplificar consultas
    - Verificación de integridad de datos
    """
    
    def __init__(self, db_name: str = "inventario.db"):
        super().__init__(db_name)
        self.db_name = db_name
        self.init_database()
    
    def init_database(self) -> bool:
        """
        Inicializar completamente la base de datos del inventario
        
        Returns:
            bool: True si se inicializó correctamente, False en caso contrario
        """
        try:
            # Crear todas las tablas
            success = (
                self._create_tables() and
                self._create_triggers() and
                self._create_indexes() and
                self._create_views()
            )
            
            if success:
                self._log_database_info()
                return True
            else:
                logger.error("❌ Error durante la inicialización de la base de datos")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error crítico inicializando base de datos: {e}")
            return False
    
    def _create_tables(self) -> bool:
        """
        Crear todas las tablas del sistema
        
        Returns:
            bool: True si se crearon exitosamente, False en caso contrario
        """
        try:
            tables = [
                ("categorias", sql.CREATE_TABLE_CATEGORIAS),
                ("proveedores", sql.CREATE_TABLE_PROVEEDORES),
                ("productos", sql.CREATE_TABLE_PRODUCTOS),
                ("movimientos_stock", sql.CREATE_TABLE_MOVIMIENTOS_STOCK)
            ]
            
            for table_name, create_statement in tables:
                self.execute_command(create_statement)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error creando tablas: {e}")
            return False
    
    def _create_triggers(self) -> bool:
        """
        Crear todos los triggers para auditoría automática y lógica de negocio
        
        Returns:
            bool: True si se crearon exitosamente, False en caso contrario
        """
        try:
            
            triggers = [
                ("categorias_updated_at", sql.CREATE_TRIGGER_CATEGORIAS_UPDATED_AT),
                ("proveedores_updated_at", sql.CREATE_TRIGGER_PROVEEDORES_UPDATED_AT),
                ("productos_updated_at", sql.CREATE_TRIGGER_PRODUCTOS_UPDATED_AT),
                ("movimientos_updated_at", sql.CREATE_TRIGGER_MOVIMIENTOS_UPDATED_AT),
                ("actualizar_stock", sql.CREATE_TRIGGER_ACTUALIZAR_STOCK)
            ]
            
            for trigger_name, create_statement in triggers:
                self.execute_command(create_statement)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error creando triggers: {e}")
            return False
    
    def _create_indexes(self) -> bool:
        """
        Crear índices para optimizar consultas
        
        Returns:
            bool: True si se crearon exitosamente, False en caso contrario
        """
        try:
            indexes = [
                ("productos_deleted_at", sql.CREATE_INDEX_PRODUCTOS_DELETED_AT),
                ("categorias_deleted_at", sql.CREATE_INDEX_CATEGORIAS_DELETED_AT),
                ("proveedores_deleted_at", sql.CREATE_INDEX_PROVEEDORES_DELETED_AT),
                ("movimientos_deleted_at", sql.CREATE_INDEX_MOVIMIENTOS_DELETED_AT),
                ("productos_categoria", sql.CREATE_INDEX_PRODUCTOS_CATEGORIA),
                ("productos_proveedor", sql.CREATE_INDEX_PRODUCTOS_PROVEEDOR),
                ("movimientos_producto", sql.CREATE_INDEX_MOVIMIENTOS_PRODUCTO)
            ]
            
            for index_name, create_statement in indexes:
                self.execute_command(create_statement)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error creando índices: {e}")
            return False
    
    def _create_views(self) -> bool:
        """
        Crear vistas para simplificar consultas complejas
        
        Returns:
            bool: True si se crearon exitosamente, False en caso contrario
        """
        try:
            views = [
                ("v_productos_activos", sql.CREATE_VIEW_PRODUCTOS_ACTIVOS),
                ("v_movimientos_activos", sql.CREATE_VIEW_MOVIMIENTOS_ACTIVOS)
            ]
            
            for view_name, create_statement in views:
                self.execute_command(create_statement)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error creando vistas: {e}")
            return False
    
    def _log_database_info(self) -> None:
        """Mostrar información sobre el estado de la base de datos"""
        try:
            info = self.verificar_datos()
            
            logger.info("📊 Estado actual de la base de datos:")
            logger.info(f"  📦 Productos: {info['productos']} activos")
            logger.info(f"  🏷️ Categorías: {info['categorias']} activas")
            logger.info(f"  🏭 Proveedores: {info['proveedores']} activos") 
            logger.info(f"  📋 Movimientos: {info['movimientos']} registrados")
            logger.info(f"  ⚠️ Alertas de stock: {info['alertas_stock']} productos")
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo info de la base de datos: {e}")
    
    def verificar_datos(self) -> Dict[str, Any]:
        """
        Verificar el estado actual de los datos en la base de datos
        
        Returns:
            Dict[str, Any]: Diccionario con conteos de cada entidad y valores totales
        """
        try:
            # Contar registros activos
            count_productos = self.execute_query("SELECT COUNT(*) FROM productos WHERE deleted_at IS NULL")[0][0]
            count_categorias = self.execute_query("SELECT COUNT(*) FROM categorias WHERE deleted_at IS NULL")[0][0]
            count_proveedores = self.execute_query("SELECT COUNT(*) FROM proveedores WHERE deleted_at IS NULL")[0][0]
            count_movimientos = self.execute_query("SELECT COUNT(*) FROM movimientos_stock WHERE deleted_at IS NULL")[0][0]
            
            # Contar alertas de stock
            alertas_result = self.execute_query(sql.SELECT_ALERTAS_STOCK_CRITICO)
            count_alertas = alertas_result[0][0] if alertas_result else 0
            
            # Calcular valor total del inventario
            valor_result = self.execute_query(sql.SELECT_VALOR_TOTAL_INVENTARIO)
            valor_total = valor_result[0][0] if valor_result and valor_result[0][0] else 0.0
            
            info = {
                'productos': count_productos,
                'categorias': count_categorias,
                'proveedores': count_proveedores,
                'movimientos': count_movimientos,
                'alertas_stock': count_alertas,
                'valor_total': float(valor_total)
            }
            
            return info
            
        except Exception as e:
            logger.error(f"❌ Error verificando datos: {e}")
            return {
                'productos': 0,
                'categorias': 0,
                'proveedores': 0,
                'movimientos': 0,
                'alertas_stock': 0,
                'valor_total': 0.0
            }
    
    def get_dashboard_metrics(self) -> Dict[str, Any]:
        """
        Obtener métricas para el dashboard principal
        
        Returns:
            Dict[str, Any]: Métricas del sistema
        """
        try:
            base_info = self.verificar_datos()
            
            # Productos más vendidos últimos 30 días
            productos_vendidos = self.execute_query(sql.SELECT_PRODUCTOS_MAS_VENDIDOS)
            
            # Movimientos por fecha últimos 30 días
            movimientos_fecha = self.execute_query(sql.SELECT_MOVIMIENTOS_POR_FECHA)
            metrics = {
                **base_info,
                'productos_mas_vendidos': productos_vendidos[:5],  # Top 5
                'movimientos_recientes': movimientos_fecha[:10],  # Últimos 10 días
                'timestamp': datetime.now().isoformat()
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo métricas del dashboard: {e}")
            return {}
    
    def backup_database(self, backup_path: str) -> bool:
        """
        Crear una copia de seguridad de la base de datos
        
        Args:
            backup_path (str): Ruta donde guardar el backup
            
        Returns:
            bool: True si el backup fue exitoso, False en caso contrario
        """
        try:
            import shutil
            shutil.copy2(self.db_name, backup_path)
            return True
            
        except Exception as e:
            logger.error(f"❌ Error creando backup: {e}")
            return False
    
    def restore_database(self, backup_path: str) -> bool:
        """
        Restaurar la base de datos desde un backup
        
        Args:
            backup_path (str): Ruta del archivo de backup
            
        Returns:
            bool: True si la restauración fue exitosa, False en caso contrario
        """
        try:
            import shutil
            import os
            
            if not os.path.exists(backup_path):
                logger.error(f"❌ Archivo de backup no encontrado: {backup_path}")
                return False
            
            shutil.copy2(backup_path, self.db_name)
            
            # Verificar integridad después de la restauración
            self._log_database_info()
            return True
            
        except Exception as e:
            logger.error(f"❌ Error restaurando backup: {e}")
            return False
    
    def optimize_database(self) -> bool:
        """
        Optimizar la base de datos (VACUUM y ANALYZE)
        
        Returns:
            bool: True si la optimización fue exitosa, False en caso contrario
        """
        try:
            # VACUUM para reorganizar y compactar la base de datos
            self.execute_command("VACUUM;")
            
            # ANALYZE para actualizar estadísticas de consulta
            self.execute_command("ANALYZE;")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error durante la optimización: {e}")
            return False
    
    def check_integrity(self) -> bool:
        """
        Verificar la integridad de la base de datos
        
        Returns:
            bool: True si la base de datos está íntegra, False en caso contrario
        """
        try:
            # Verificar integridad con PRAGMA integrity_check
            result = self.execute_query("PRAGMA integrity_check;")
            
            if result and result[0][0] == "ok":
                return True
            else:
                logger.error("❌ Problemas de integridad detectados")
                for issue in result:
                    logger.error(f"  ❌ {issue[0]}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error verificando integridad: {e}")
            return False