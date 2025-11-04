# base_model.py - Clase base para manejar operaciones con soft delete
"""
BaseModel: Clase base que implementa soft delete y auditoría automática.
Todas las entidades (productos, categorías, proveedores, etc.) heredan de esta clase.
"""

import sqlite3
from datetime import datetime
from typing import List, Dict, Any, Optional, Union
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BaseModel:
    """
    Clase base que proporciona operaciones CRUD con soft delete y auditoría.
    
    Características:
    - Soft delete: Los registros nunca se eliminan físicamente
    - Auditoría automática: created_at, updated_at, deleted_at
    - Filtros automáticos para excluir registros eliminados
    - Métodos para restaurar registros eliminados
    - Validaciones antes de eliminar
    """
    
    def __init__(self, db_name: str = "inventario.db"):
        self.db_name = db_name
        self.table_name = ""  # Debe ser definido por las clases hijas
        self.primary_key = "id"  # Puede ser redefinido por las clases hijas
        
    def _validate_before_delete(self, record_id: Union[str, int]) -> bool:
        """Método base para validar antes de eliminar un registro"""
        return True
        
    def get_connection(self) -> sqlite3.Connection:
        """Obtener una conexión a la base de datos"""
        return sqlite3.connect(self.db_name)
    
    def execute_query(self, query: str, params: Optional[tuple] = None) -> List[tuple]:
        """
        Ejecutar una consulta SELECT y retornar resultados
        
        Args:
            query (str): Consulta SQL
            params (tuple): Parámetros para la consulta
            
        Returns:
            List[tuple]: Lista de tuplas con los resultados
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            results = cursor.fetchall()
            conn.close()
            return results
            
        except Exception as e:
            logger.error(f"❌ Error ejecutando consulta: {e}")
            return []

    def execute_command(self, command: str, params: Optional[tuple] = None) -> int:
        """
        Ejecutar un comando INSERT, UPDATE o DELETE
        
        Args:
            command (str): Comando SQL
            params (tuple): Parámetros para el comando
            
        Returns:
            int: Número de filas afectadas
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            if params:
                cursor.execute(command, params)
            else:
                cursor.execute(command)
            
            conn.commit()
            rows_affected = cursor.rowcount
            conn.close()
            return rows_affected
            
        except Exception as e:
            logger.error(f"❌ Error ejecutando comando: {e}")
            return 0
    
    def get_active(self, order_by: Optional[str] = None) -> List[tuple]:
        """
        Obtener todos los registros activos (no eliminados)
        
        Args:
            order_by (str): Campo para ordenar los resultados
            
        Returns:
            List[tuple]: Lista de registros activos
        """
        query = f"SELECT * FROM {self.table_name} WHERE deleted_at IS NULL"
        
        if order_by:
            query += f" ORDER BY {order_by}"
            
        return self.execute_query(query)
    
    def get_deleted(self, order_by: Optional[str] = None) -> List[tuple]:
        """
        Obtener todos los registros eliminados (soft deleted)
        
        Args:
            order_by (str): Campo para ordenar los resultados
            
        Returns:
            List[tuple]: Lista de registros eliminados
        """
        query = f"SELECT * FROM {self.table_name} WHERE deleted_at IS NOT NULL"
        
        if order_by:
            query += f" ORDER BY {order_by}"
            
        return self.execute_query(query)
    
    def get_all_including_deleted(self, order_by: Optional[str] = None) -> List[tuple]:
        """
        Obtener todos los registros incluyendo los eliminados
        
        Args:
            order_by (str): Campo para ordenar los resultados
            
        Returns:
            List[tuple]: Lista de todos los registros
        """
        query = f"SELECT * FROM {self.table_name}"
        
        if order_by:
            query += f" ORDER BY {order_by}"
            
        return self.execute_query(query)
    
    def get_by_id(self, record_id: Union[str, int]) -> Optional[tuple]:
        """
        Obtener un registro por su ID (solo si está activo)
        
        Args:
            record_id (Union[str, int]): ID del registro
            
        Returns:
            Optional[tuple]: Registro encontrado o None
        """
        query = f"SELECT * FROM {self.table_name} WHERE {self.primary_key} = ? AND deleted_at IS NULL"
        results = self.execute_query(query, (record_id,))
        
        return results[0] if results else None
    
    def soft_delete(self, record_id: Union[str, int], validate_dependencies: bool = True) -> bool:
        """
        Marcar un registro como eliminado (soft delete)
        
        Args:
            record_id (Union[str, int]): ID del registro a eliminar
            validate_dependencies (bool): Si validar dependencias antes de eliminar
            
        Returns:
            bool: True si se eliminó exitosamente, False en caso contrario
        """
        try:
            # Validar que el registro existe y está activo
            if not self.get_by_id(record_id):
                logger.warning(f"⚠️ Registro {record_id} no encontrado o ya eliminado")
                return False
            
            # Validar dependencias si es necesario
            if validate_dependencies and hasattr(self, '_validate_before_delete'):
                if not self._validate_before_delete(record_id):
                    logger.warning(f"⚠️ No se puede eliminar {record_id}: tiene dependencias activas")
                    return False
            
            # Ejecutar soft delete
            query = f"UPDATE {self.table_name} SET deleted_at = CURRENT_TIMESTAMP WHERE {self.primary_key} = ?"
            rows_affected = self.execute_command(query, (record_id,))
            
            if rows_affected > 0:
                return True
            else:
                logger.error(f"❌ No se pudo eliminar el registro {record_id}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error en soft delete: {e}")
            return False
    
    def restore(self, record_id: Union[str, int]) -> bool:
        """
        Restaurar un registro eliminado
        
        Args:
            record_id (Union[str, int]): ID del registro a restaurar
            
        Returns:
            bool: True si se restauró exitosamente, False en caso contrario
        """
        try:
            query = f"UPDATE {self.table_name} SET deleted_at = NULL WHERE {self.primary_key} = ?"
            rows_affected = self.execute_command(query, (record_id,))
            
            if rows_affected > 0:
                return True
            else:
                logger.warning(f"⚠️ No se encontró el registro {record_id} para restaurar")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error restaurando registro: {e}")
            return False
    
    def search_active(self, field: str, value: str, partial_match: bool = True) -> List[tuple]:
        """
        Buscar registros activos por un campo específico
        
        Args:
            field (str): Campo a buscar
            value (str): Valor a buscar
            partial_match (bool): Si permitir coincidencias parciales
            
        Returns:
            List[tuple]: Lista de registros encontrados
        """
        if partial_match:
            query = f"SELECT * FROM {self.table_name} WHERE {field} LIKE ? AND deleted_at IS NULL"
            params = (f"%{value}%",)
        else:
            query = f"SELECT * FROM {self.table_name} WHERE {field} = ? AND deleted_at IS NULL"
            params = (value,)
            
        return self.execute_query(query, params)
    
    def count_active(self) -> int:
        """
        Contar registros activos
        
        Returns:
            int: Número de registros activos
        """
        query = f"SELECT COUNT(*) FROM {self.table_name} WHERE deleted_at IS NULL"
        result = self.execute_query(query)
        return result[0][0] if result else 0
    
    def count_deleted(self) -> int:
        """
        Contar registros eliminados
        
        Returns:
            int: Número de registros eliminados
        """
        query = f"SELECT COUNT(*) FROM {self.table_name} WHERE deleted_at IS NOT NULL"
        result = self.execute_query(query)
        return result[0][0] if result else 0
    
    def get_audit_info(self, record_id: Union[str, int]) -> Optional[Dict[str, Any]]:
        """
        Obtener información de auditoría de un registro
        
        Args:
            record_id (Union[str, int]): ID del registro
            
        Returns:
            Optional[Dict]: Información de auditoría o None si no existe
        """
        query = f"""
        SELECT created_at, updated_at, deleted_at 
        FROM {self.table_name} 
        WHERE {self.primary_key} = ?
        """
        
        result = self.execute_query(query, (record_id,))
        
        if result:
            created_at, updated_at, deleted_at = result[0]
            return {
                'created_at': created_at,
                'updated_at': updated_at,
                'deleted_at': deleted_at,
                'is_active': deleted_at is None,
                'is_deleted': deleted_at is not None
            }
        
        return None
    
    def bulk_soft_delete(self, record_ids: List[Union[str, int]], validate_dependencies: bool = True) -> Dict[str, List]:
        """
        Eliminar múltiples registros en lote
        
        Args:
            record_ids (List): Lista de IDs a eliminar
            validate_dependencies (bool): Si validar dependencias
            
        Returns:
            Dict: Resultado con éxitos y fallos
        """
        successful = []
        failed = []
        
        for record_id in record_ids:
            if self.soft_delete(record_id, validate_dependencies):
                successful.append(record_id)
            else:
                failed.append(record_id)
        return {
            'successful': successful,
            'failed': failed,
            'total_processed': [len(record_ids)]
        }
    
    def get_recently_created(self, days: int = 7, limit: int = 100) -> List[tuple]:
        """
        Obtener registros creados recientemente
        
        Args:
            days (int): Número de días hacia atrás
            limit (int): Límite de registros
            
        Returns:
            List[tuple]: Lista de registros recientes
        """
        query = f"""
        SELECT * FROM {self.table_name} 
        WHERE deleted_at IS NULL 
        AND created_at >= date('now', '-{days} days')
        ORDER BY created_at DESC 
        LIMIT {limit}
        """
        
        return self.execute_query(query)
    
    def get_recently_updated(self, days: int = 7, limit: int = 100) -> List[tuple]:
        """
        Obtener registros actualizados recientemente
        
        Args:
            days (int): Número de días hacia atrás
            limit (int): Límite de registros
            
        Returns:
            List[tuple]: Lista de registros actualizados
        """
        query = f"""
        SELECT * FROM {self.table_name} 
        WHERE deleted_at IS NULL 
        AND updated_at >= date('now', '-{days} days')
        AND updated_at != created_at
        ORDER BY updated_at DESC 
        LIMIT {limit}
        """
        
        return self.execute_query(query)