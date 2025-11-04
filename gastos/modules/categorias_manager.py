# categorias_manager.py - Manager para la gestión de categorías
"""
CategoriasManager: Clase para manejar todas las operaciones relacionadas con categorías de gastos/ingresos.
"""

import dearpygui.dearpygui as dpg
from .database_manager import DatabaseManager
from . import sqlstatement as sql
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class CategoriasManager(DatabaseManager):
    """Clase para manejar todas las operaciones relacionadas con categorías"""
    
    def __init__(self, db_name="gastos.db"):
        super().__init__(db_name)
        self.table_name = "categorias"
    
    # ================================
    # OPERACIONES CRUD - CATEGORIAS
    # ================================
    
    def agregar_categoria(self, nombre: str, descripcion: str = "") -> bool:
        """
        Agregar una nueva categoría
        
        Args:
            nombre (str): Nombre de la categoría
            descripcion (str): Descripción opcional
            
        Returns:
            bool: True si se agregó correctamente
        """
        try:
            if not nombre.strip():
                logger.warning("⚠️ El nombre de la categoría no puede estar vacío")
                return False
            
            rows_affected = self.execute_command(sql.INSERT_CATEGORIA, (nombre.strip(), descripcion.strip()))
            
            if rows_affected > 0:
                logger.info(f"✅ Categoría '{nombre}' agregada correctamente")
                return True
            else:
                logger.error("❌ No se pudo agregar la categoría")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error agregando categoría: {e}")
            return False
    
    def actualizar_categoria(self, categoria_id: int, nombre: str, descripcion: str = "") -> bool:
        """
        Actualizar una categoría existente
        
        Args:
            categoria_id (int): ID de la categoría
            nombre (str): Nuevo nombre
            descripcion (str): Nueva descripción
            
        Returns:
            bool: True si se actualizó correctamente
        """
        try:
            if not nombre.strip():
                logger.warning("⚠️ El nombre de la categoría no puede estar vacío")
                return False
            
            rows_affected = self.execute_command(sql.UPDATE_CATEGORIA, (nombre.strip(), descripcion.strip(), categoria_id))
            
            if rows_affected > 0:
                logger.info(f"✅ Categoría {categoria_id} actualizada correctamente")
                return True
            else:
                logger.warning(f"⚠️ No se encontró la categoría {categoria_id}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error actualizando categoría: {e}")
            return False
    
    def obtener_categorias(self) -> list:
        """
        Obtener todas las categorías activas
        
        Returns:
            list: Lista de tuplas con las categorías
        """
        return self.execute_query(sql.SELECT_CATEGORIAS_ACTIVAS)
    
    def obtener_categoria_por_id(self, categoria_id: int):
        """
        Obtener una categoría por su ID
        
        Args:
            categoria_id (int): ID de la categoría
            
        Returns:
            tuple: Datos de la categoría o None
        """
        results = self.execute_query(sql.SELECT_CATEGORIA_BY_ID, (categoria_id,))
        return results[0] if results else None
    
    def buscar_categorias(self, termino: str) -> list:
        """
        Buscar categorías por nombre
        
        Args:
            termino (str): Término de búsqueda
            
        Returns:
            list: Lista de categorías que coinciden
        """
        return self.search_active("nombre", termino)
    
    def obtener_nombres_categorias(self) -> list:
        """
        Obtener lista de nombres de categorías para combos
        
        Returns:
            list: Lista de nombres de categorías
        """
        categorias = self.obtener_categorias()
        return [cat[1] for cat in categorias]  # nombre está en la posición 1
    
    def validar_categoria_unica(self, nombre: str, exclude_id: Optional[int] = None) -> bool:
        """
        Validar que el nombre de la categoría sea único
        
        Args:
            nombre (str): Nombre a validar
            exclude_id (int): ID a excluir de la validación (para updates)
            
        Returns:
            bool: True si es único
        """
        query = "SELECT COUNT(*) FROM categorias WHERE nombre = ? AND deleted_at IS NULL"
        params = (nombre.strip(),)
        
        if exclude_id:
            query += " AND id != ?"
            params = (nombre.strip(), exclude_id)
        
        result = self.execute_query(query, params)
        return result[0][0] == 0 if result else True