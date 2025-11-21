# transacciones_manager.py - Manager para la gestión de transacciones
"""
TransaccionesManager: Clase para manejar todas las operaciones relacionadas con ingresos y egresos.
"""

import dearpygui.dearpygui as dpg
from .database_manager import DatabaseManager
from .categorias_manager import CategoriasManager
from . import sqlstatement as sql
import logging
from datetime import datetime, date
from typing import List, Optional

logger = logging.getLogger(__name__)

class TransaccionesManager(DatabaseManager):
    """Clase para manejar todas las operaciones relacionadas con transacciones"""
    
    def __init__(self, db_name="gastos.db"):
        super().__init__(db_name)
        self.table_name = "transacciones"
        self.categorias_manager = CategoriasManager(db_name)
    
    # ================================
    # OPERACIONES CRUD - TRANSACCIONES
    # ================================
    
    def agregar_transaccion(self, tipo: str, monto: float, categoria_id: Optional[int], 
                          descripcion: str = "", fecha: Optional[str] = None) -> bool:
        """
        Agregar una nueva transacción
        
        Args:
            tipo (str): 'ingreso' o 'egreso'
            monto (float): Monto de la transacción
            categoria_id (int): ID de la categoría (opcional)
            descripcion (str): Descripción opcional
            fecha (str): Fecha en formato YYYY-MM-DD (opcional, usa hoy por defecto)
            
        Returns:
            bool: True si se agregó correctamente
        """
        try:
            if tipo not in ['ingreso', 'egreso']:
                logger.warning("⚠️ Tipo de transacción inválido")
                return False
            
            if monto <= 0:
                logger.warning("⚠️ El monto debe ser mayor a cero")
                return False
            
            if not fecha:
                fecha = date.today().isoformat()
            
            # Validar que la categoría existe si se proporciona
            if categoria_id and not self.categorias_manager.obtener_categoria_por_id(categoria_id):
                logger.warning(f"⚠️ Categoría {categoria_id} no encontrada")
                return False
            
            rows_affected = self.execute_command(
                sql.INSERT_TRANSACCION, 
                (tipo, monto, categoria_id, descripcion.strip(), fecha)
            )
            
            if rows_affected > 0:
                logger.info(f"✅ Transacción {tipo} de ${monto} agregada correctamente")
                return True
            else:
                logger.error("❌ No se pudo agregar la transacción")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error agregando transacción: {e}")
            return False
    
    def actualizar_transaccion(self, transaccion_id: int, tipo: str, monto: float, 
                             categoria_id: Optional[int], descripcion: str = "", fecha: Optional[str] = None) -> bool:
        """
        Actualizar una transacción existente
        
        Args:
            transaccion_id (int): ID de la transacción
            tipo (str): 'ingreso' o 'egreso'
            monto (float): Monto de la transacción
            categoria_id (int): ID de la categoría (opcional)
            descripcion (str): Descripción
            fecha (str): Fecha en formato YYYY-MM-DD
            
        Returns:
            bool: True si se actualizó correctamente
        """
        try:
            if tipo not in ['ingreso', 'egreso']:
                logger.warning("⚠️ Tipo de transacción inválido")
                return False
            
            if monto <= 0:
                logger.warning("⚠️ El monto debe ser mayor a cero")
                return False
            
            if not fecha:
                fecha = date.today().isoformat()
            
            # Validar que la categoría existe si se proporciona
            if categoria_id and not self.categorias_manager.obtener_categoria_por_id(categoria_id):
                logger.warning(f"⚠️ Categoría {categoria_id} no encontrada")
                return False
            
            rows_affected = self.execute_command(
                sql.UPDATE_TRANSACCION, 
                (tipo, monto, categoria_id, descripcion.strip(), fecha, transaccion_id)
            )
            
            if rows_affected > 0:
                logger.info(f"✅ Transacción {transaccion_id} actualizada correctamente")
                return True
            else:
                logger.warning(f"⚠️ No se encontró la transacción {transaccion_id}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error actualizando transacción: {e}")
            return False
    
    def obtener_transacciones(self) -> List[tuple]:
        """
        Obtener todas las transacciones activas
        
        Returns:
            List[tuple]: Lista de transacciones
        """
        return self.execute_query(sql.SELECT_TRANSACCIONES_ACTIVAS)
    
    def obtener_transaccion_por_id(self, transaccion_id: int):
        """
        Obtener una transacción por su ID
        
        Args:
            transaccion_id (int): ID de la transacción
            
        Returns:
            tuple: Datos de la transacción o None
        """
        results = self.execute_query(sql.SELECT_TRANSACCION_BY_ID, (transaccion_id,))
        return results[0] if results else None
    
    def filtrar_transacciones(self, tipo: Optional[str] = None, categoria: Optional[str] = None,
                            fecha_desde: Optional[str] = None, fecha_hasta: Optional[str] = None) -> List[tuple]:
        """
        Filtrar transacciones por criterios
        
        Args:
            tipo (str): 'ingreso' o 'egreso' (opcional)
            categoria (str): Nombre de la categoría (opcional)
            fecha_desde (str): Fecha desde en YYYY-MM-DD (opcional)
            fecha_hasta (str): Fecha hasta en YYYY-MM-DD (opcional)
            
        Returns:
            List[tuple]: Lista de transacciones filtradas
        """
        params = (tipo, tipo, categoria, categoria, fecha_desde, fecha_desde, fecha_hasta, fecha_hasta)
        return self.execute_query(sql.SELECT_TRANSACCIONES_BY_FILTRO, params)
    def soft_delete(self, trans_id: int) -> bool:
        try:
            sql = "UPDATE transacciones SET eliminado = 1 WHERE id = ?"
            rows = self.execute_command(sql, (trans_id,))
            if rows and rows > 0:
                logger.info(f"Transacción id={trans_id} marcada como eliminada.")
                return True
            else:
                logger.error(f"No se pudo eliminar la transacción id={trans_id}.")
                return False
        except Exception as e:
            logger.error(f"Error al eliminar (soft) transacción id={trans_id}: {e}", exc_info=True)
            return False

    # ================================
    # REPORTES Y ESTADÍSTICAS
    # ================================
    
    def obtener_totales_por_tipo(self) -> List[tuple]:
        """
        Obtener totales agrupados por tipo
        
        Returns:
            List[tuple]: Lista con (tipo, total)
        """
        return self.execute_query(sql.SELECT_TOTALES_POR_TIPO)
    
    def obtener_totales_por_categoria(self) -> List[tuple]:
        """
        Obtener totales agrupados por categoría y tipo
        
        Returns:
            List[tuple]: Lista con (categoria, tipo, total)
        """
        return self.execute_query(sql.SELECT_TOTALES_POR_CATEGORIA)
    
    def obtener_totales_por_mes(self) -> List[tuple]:
        """
        Obtener totales agrupados por mes y tipo
        
        Returns:
            List[tuple]: Lista con (mes, tipo, total)
        """
        return self.execute_query(sql.SELECT_TOTALES_POR_MES)
    
    def obtener_balance_actual(self) -> float:
        """
        Obtener el balance actual (ingresos - egresos)
        
        Returns:
            float: Balance actual
        """
        result = self.execute_query(sql.SELECT_BALANCE_ACTUAL)
        return result[0][0] if result else 0.0 
    def obtener_resumen_balance(self):
        """
        Retorna dict: {'total_ingresos': X, 'total_egresos': Y, 'balance': X - Y}
        """
        try:
            sql_ing = "SELECT IFNULL(SUM(monto), 0) FROM transacciones WHERE tipo = 'ingreso' AND eliminado = 0"
            sql_eg = "SELECT IFNULL(SUM(monto), 0) FROM transacciones WHERE tipo = 'egreso' AND eliminado = 0"
            ingresos = self.execute_query(sql_ing, ())
            egresos = self.execute_query(sql_eg, ())
            total_ing = float(ingresos[0][0]) if ingresos and ingresos[0][0] is not None else 0.0
            total_eg = float(egresos[0][0]) if egresos and egresos[0][0] is not None else 0.0
            balance = total_ing - total_eg
            return {"total_ingresos": total_ing, "total_egresos": total_eg, "balance": balance}
        except Exception as e:
            logger.error(f"Error al calcular resumen balance: {e}", exc_info=True)
            return {"total_ingresos": 0.0, "total_egresos": 0.0, "balance": 0.0}

    
    def obtener_datos_para_grafico_categorias(self, tipo: Optional[str] = None) -> List[tuple]:
        """
        Obtener datos para gráfico de categorías
        
        Args:
            tipo (str): Filtrar por tipo ('ingreso' o 'egreso') o None para ambos
            
        Returns:
            List[tuple]: Lista con (categoria, total)
        """
        if tipo:
            query = """
            SELECT c.nombre as categoria, SUM(t.monto) as total
            FROM transacciones t
            JOIN categorias c ON t.categoria_id = c.id
            WHERE t.deleted_at IS NULL AND c.deleted_at IS NULL AND t.tipo = ?
            GROUP BY c.nombre
            ORDER BY total DESC
            """
            return self.execute_query(query, (tipo,))
        else:
            # Sin filtro, agrupar solo por categoría (sumando todos los tipos)
            query = """
            SELECT c.nombre as categoria, SUM(t.monto) as total
            FROM transacciones t
            JOIN categorias c ON t.categoria_id = c.id
            WHERE t.deleted_at IS NULL AND c.deleted_at IS NULL
            GROUP BY c.nombre
            ORDER BY total DESC
            """
            return self.execute_query(query)
    
    def obtener_datos_para_grafico_mensual(self, tipo: Optional[str] = None) -> List[tuple]:
        """
        Obtener datos para gráfico mensual
        
        Args:
            tipo (str): Filtrar por tipo ('ingreso' o 'egreso') o None para ambos
            
        Returns:
            List[tuple]: Lista con (mes, total)
        """
        if tipo:
            query = """
            SELECT strftime('%Y-%m', fecha) as mes, SUM(monto) as total
            FROM transacciones
            WHERE deleted_at IS NULL AND tipo = ?
            GROUP BY strftime('%Y-%m', fecha)
            ORDER BY mes
            """
            return self.execute_query(query, (tipo,))
        else:
            return self.obtener_totales_por_mes()