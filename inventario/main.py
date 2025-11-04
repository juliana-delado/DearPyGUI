# main.py - Sistema de Gestión de Inventario Empresarial (Refactorizado)
"""
Sistema completo de gestión de inventario con DearPyGUI.
Versión refactorizada con separación de responsabilidades:
- main.py: Solo inicialización y configuración
- ui_manager.py: Gestión de interfaz
- *_manager.py: Lógica de negocio y interfaces específicas
"""

import dearpygui.dearpygui as dpg
import sys
import os
import logging
from datetime import datetime

# Importar módulos de gestión
from modules.database_manager import DatabaseManager
from modules.categorias_manager import CategoriasManager
from modules.proveedores_manager import ProveedoresManager  
from modules.productos_manager import ProductosManager
from modules.movimientos_manager import MovimientosManager
from modules.ui_manager import UIManager

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InventarioApp:
    """Aplicación principal del sistema de inventario empresarial"""
    
    def __init__(self):
        self.db_name = "inventario.db"
        
        try:
            # Inicializar managers con manejo de errores
            logger.info("🚀 Inicializando sistema de inventario...")
            
            self.db_manager = DatabaseManager(self.db_name)
            logger.info("✅ Base de datos inicializada")
            
            self.categorias_manager = CategoriasManager(self.db_name, self)
            logger.info("✅ Manager de categorías inicializado")
            
            self.proveedores_manager = ProveedoresManager(self.db_name, self)
            logger.info("✅ Manager de proveedores inicializado")
            
            self.productos_manager = ProductosManager(self.db_name, self)
            logger.info("✅ Manager de productos inicializado")
            
            self.movimientos_manager = MovimientosManager(self.db_name, self)
            logger.info("✅ Manager de movimientos inicializado")
            
            # Inicializar UI Manager
            self.ui_manager = UIManager(self)
            logger.info("✅ UI Manager inicializado")
            
            # Configurar callbacks entre módulos
            self._configure_callbacks()
            logger.info("✅ Callbacks configurados")
            
        except Exception as e:
            logger.error(f"❌ Error durante la inicialización: {e}")
            raise
    
    def _configure_callbacks(self):
        """Configurar callbacks entre módulos para mantener sincronización"""
        
        # Callbacks de categorías
        self.categorias_manager.set_callbacks(
            on_categoria_added=self.actualizar_combos_categorias,
            on_categoria_updated=self.actualizar_combos_categorias,
            on_categoria_deleted=self.actualizar_combos_categorias
        )
        
        # Callbacks de proveedores
        self.proveedores_manager.set_callbacks(
            on_proveedore_added=self.actualizar_combos_proveedores,
            on_proveedore_updated=self.actualizar_combos_proveedores,
            on_proveedore_deleted=self.actualizar_combos_proveedores
        )
        
        # Callbacks de productos
        self.productos_manager.set_callbacks(
            on_producto_added=self.actualizar_dashboard,
            on_producto_updated=self.actualizar_dashboard,
            on_producto_deleted=self.actualizar_dashboard,
            on_stock_alert=self.mostrar_alerta_stock
        )
        
        # Callbacks de movimientos
        self.movimientos_manager.set_callbacks(
            on_movimiento_added=self.actualizar_movimientos_callback,
            on_movimiento_updated=self.actualizar_dashboard,
            on_movimiento_deleted=self.actualizar_dashboard
        )
    
    # ================================
    # MÉTODOS DE ACTUALIZACIÓN
    # ================================
    
    def actualizar_dashboard(self, sender=None, app_data=None):
        """Actualizar métricas del dashboard"""
        try:
            # Actualizar métricas
            total_productos = len(self.productos_manager.obtener_todos_productos())
            total_categorias = len(self.categorias_manager.obtener_todas_categorias())
            total_proveedores = len(self.proveedores_manager.obtener_todos_proveedores())
            
            # Actualizar en la interfaz
            if dpg.does_item_exist("metric_productos_value"):
                dpg.set_value("metric_productos_value", str(total_productos))
            if dpg.does_item_exist("metric_categorias_value"):
                dpg.set_value("metric_categorias_value", str(total_categorias))
            if dpg.does_item_exist("metric_proveedores_value"):
                dpg.set_value("metric_proveedores_value", str(total_proveedores))
            
            # Actualizar productos con stock bajo
            self.actualizar_tabla_stock_bajo()
            
            # Actualizar movimientos recientes
            self.actualizar_tabla_movimientos_recientes()
            
        except Exception as e:
            print(f"Error actualizando dashboard: {e}")
    
    def actualizar_tabla_stock_bajo(self):
        """Actualizar tabla de productos con stock bajo"""
        try:
            if not dpg.does_item_exist("table_stock_bajo"):
                return
                
            # Limpiar tabla
            dpg.delete_item("table_stock_bajo", children_only=True)
            
            # Recrear columnas
            dpg.add_table_column(label="Codigo", parent="table_stock_bajo")
            dpg.add_table_column(label="Nombre", parent="table_stock_bajo")
            dpg.add_table_column(label="Stock Actual", parent="table_stock_bajo")
            dpg.add_table_column(label="Stock Minimo", parent="table_stock_bajo")
            
            # Obtener productos con stock bajo
            productos = self.productos_manager.obtener_productos_stock_bajo()
            
            # Agregar filas
            for producto in productos[:10]:  # Solo los primeros 10
                with dpg.table_row(parent="table_stock_bajo"):
                    dpg.add_text(producto[0])  # codigo
                    dpg.add_text(producto[1])  # nombre
                    dpg.add_text(str(producto[2]))  # stock_actual
                    dpg.add_text(str(producto[3]))  # stock_minimo
                    
        except Exception as e:
            print(f"Error actualizando tabla stock bajo: {e}")
    
    def actualizar_tabla_movimientos_recientes(self):
        """Actualizar tabla de movimientos recientes"""
        try:
            if not dpg.does_item_exist("table_movimientos_recientes"):
                return
                
            # Limpiar tabla
            dpg.delete_item("table_movimientos_recientes", children_only=True)
            
            # Recrear columnas
            dpg.add_table_column(label="Fecha", parent="table_movimientos_recientes")
            dpg.add_table_column(label="Producto", parent="table_movimientos_recientes")
            dpg.add_table_column(label="Tipo", parent="table_movimientos_recientes")
            dpg.add_table_column(label="Cantidad", parent="table_movimientos_recientes")
            
            # Obtener movimientos recientes (simulado por ahora)
            # TODO: Implementar método real en MovimientosManager
            movimientos = []
            
            # Agregar filas
            for movimiento in movimientos[:10]:  # Solo los primeros 10
                with dpg.table_row(parent="table_movimientos_recientes"):
                    dpg.add_text(movimiento[0])  # fecha
                    dpg.add_text(movimiento[1])  # producto
                    dpg.add_text(movimiento[2])  # tipo
                    dpg.add_text(str(movimiento[3]))  # cantidad
                    
        except Exception as e:
            print(f"Error actualizando tabla movimientos recientes: {e}")
    
    def actualizar_combos_categorias(self):
        """Actualizar combos de categorías en productos"""
        try:
            self.productos_manager._actualizar_combos_productos()
        except Exception as e:
            print(f"Error actualizando combos categorías: {e}")
    
    def actualizar_combos_proveedores(self):
        """Actualizar combos de proveedores en productos"""
        try:
            self.productos_manager._actualizar_combos_productos()
        except Exception as e:
            print(f"Error actualizando combos proveedores: {e}")
    
    def mostrar_alerta_stock(self, codigo_barras: str, stock_actual: int, stock_minimo: int):
        """Mostrar alerta de stock bajo"""
        mensaje = f"⚠️ Stock bajo: Producto {codigo_barras} tiene {stock_actual} unidades (mínimo: {stock_minimo})"
        logger.warning(mensaje)
        
        # TODO: Agregar notificación visual si es necesario
        print(mensaje)
    
    def actualizar_movimientos_callback(self):
        """Callback para actualizar los movimientos cuando se agrega uno nuevo"""
        try:
            if hasattr(self, 'movimientos_manager'):
                self.movimientos_manager.cargar_movimientos_tab()
            self.actualizar_dashboard()
        except Exception as e:
            logger.error(f"❌ Error actualizando movimientos: {e}")
    
    # ================================
    # MÉTODOS DE REPORTES
    # ================================
    
    def exportar_excel(self, sender=None, app_data=None):
        """Exportar datos a Excel"""
        try:
            import pandas as pd
            from datetime import datetime
            
            # Obtener datos
            productos = self.productos_manager.obtener_todos_productos()
            
            # Crear DataFrame
            df = pd.DataFrame(productos, columns=[
                'Codigo', 'Nombre', 'Descripcion', 'Categoria', 'Proveedor',
                'Stock Actual', 'Stock Minimo', 'Precio Compra', 'Precio Venta'
            ])
            
            # Generar archivo
            fecha = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"inventario_export_{fecha}.xlsx"
            df.to_excel(filename, index=False)
            
            print(f"✓ Datos exportados a {filename}")
            
        except ImportError:
            print("❌ pandas no está instalado. Instale con: pip install pandas openpyxl")
        except Exception as e:
            print(f"❌ Error exportando a Excel: {e}")
    
    def reporte_stock_bajo(self, sender=None, app_data=None):
        """Generar reporte de stock bajo"""
        try:
            productos = self.productos_manager.obtener_productos_stock_bajo()
            
            if not productos:
                print("✓ No hay productos con stock bajo")
                return
            
            print("📊 REPORTE DE STOCK BAJO:")
            print("-" * 60)
            for producto in productos:
                print(f"{producto[0]}: {producto[1]} - Stock: {producto[2]}/{producto[3]}")
            print("-" * 60)
            
        except Exception as e:
            print(f"❌ Error generando reporte: {e}")
    
    def _verificar_datos_basicos(self):
        """Verificar y crear categorías y proveedores básicos si no existen"""
        try:
            logger.info("🔍 Verificando datos básicos...")
            
            # Verificar si existen categorías
            categorias = self.categorias_manager.obtener_todas_categorias()
            if not categorias:
                logger.info("📂 Creando categoría básica...")
                self.categorias_manager.agregar_categoria(
                    "General", 
                    "Categoría general para productos sin clasificación específica", 
                    "#3498db"
                )
            
            # Verificar si existen proveedores
            proveedores = self.proveedores_manager.obtener_todos_proveedores()
            if not proveedores:
                logger.info("🏢 Creando proveedor básico...")
                # Usar el método correcto del base model para insertar proveedor
                try:
                    query = """INSERT INTO proveedores 
                              (nombre_razon_social, cuit_rut, direccion, telefono, email) 
                              VALUES (?, ?, ?, ?, ?)"""
                    self.db_manager.execute_command(query, 
                        ("Proveedor General", "00-00000000-0", "Sin dirección", 
                         "Sin teléfono", "sin@email.com"))
                    logger.info("✅ Proveedor básico creado")
                except Exception as e:
                    logger.warning(f"⚠️ Error creando proveedor básico: {e}")
            
            logger.info("✅ Verificación de datos básicos completada")
            
        except Exception as e:
            logger.error(f"❌ Error verificando datos básicos: {e}")
    
    # ================================
    # EJECUCIÓN PRINCIPAL
    # ================================
    
    def ejecutar(self):
        """Ejecutar la aplicación"""
        # Crear interfaz usando el UI Manager
        self.ui_manager.crear_interfaz_completa()
        
        # Configurar DearPyGUI
        dpg.setup_dearpygui()
        
        # Mostrar la aplicación primero
        dpg.show_viewport()
        
        # Verificar y crear datos básicos si es necesario
        self._verificar_datos_basicos()
        
        # Cargar datos iniciales usando los managers DESPUÉS de mostrar la interfaz
        try:
            self.productos_manager._actualizar_combos_productos()
            self.productos_manager.cargar_productos()
            self.categorias_manager.cargar_categorias()
            self.proveedores_manager.cargar_proveedores()
            self.movimientos_manager.cargar_movimientos_tab()
            
            # Actualizar dashboard
            self.actualizar_dashboard()
        except Exception as e:
            logger.error(f"⚠️ Error cargando datos iniciales: {e}")
            # Continuar con la aplicación aunque fallen los datos iniciales
        dpg.start_dearpygui()
        
        # Limpiar recursos al cerrar
        dpg.destroy_context()

def main():
    """Función principal"""
    try:
        app = InventarioApp()
        app.ejecutar()
    except Exception as e:
        print(f"❌ Error iniciando aplicación: {e}")
        if dpg.is_dearpygui_running():
            dpg.destroy_context()

if __name__ == "__main__":
    main()