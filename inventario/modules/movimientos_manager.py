"""
Gestor de Movimientos de Stock para el sistema de inventario.
Implementa el patrón de ventanas modales consistente con ProductosManager y ProveedoresManager.
"""

import logging
import dearpygui.dearpygui as dpg
from typing import Dict, List, Optional
from datetime import datetime

from .database_manager import DatabaseManager
from .sqlstatement import (
    INSERT_MOVIMIENTO, SELECT_ALL_MOVIMIENTOS_ACTIVOS, 
    SELECT_MOVIMIENTOS_BY_PRODUCTO, SOFT_DELETE_MOVIMIENTO
)

# Configurar el logger
logger = logging.getLogger(__name__)


class MovimientosManager:
    """Gestor de movimientos de stock para la aplicación de inventario."""
    
    def __init__(self, db_name: str = "inventario.db", app_instance=None):
        """
        Inicializar el gestor de movimientos.
        
        Args:
            db_name: Nombre de la base de datos SQLite
            app_instance: Referencia a la aplicación principal
        """
        self.db_manager = DatabaseManager(db_name)
        self.app = app_instance  # Referencia a la aplicación principal
        
        # Callbacks
        self.on_movimiento_added = None
        self.on_movimiento_updated = None
        self.on_movimiento_deleted = None
        self.on_producto_selected = None
        
        logger.info("🔧 MovimientosManager inicializado correctamente")
    
    def _configurar_temas_botones(self):
        """Los temas ahora se configuran globalmente en UIManager"""
        # Los temas se configuran una sola vez en UIManager.configurar_temas_globales()
        pass
    
    def set_callbacks(self, on_movimiento_added=None, on_movimiento_updated=None, 
                     on_movimiento_deleted=None, on_producto_selected=None):
        """
        Configurar los callbacks para eventos del gestor.
        
        Args:
            on_movimiento_added: Callback para cuando se agrega un movimiento
            on_movimiento_updated: Callback para cuando se actualiza un movimiento  
            on_movimiento_deleted: Callback para cuando se elimina un movimiento
            on_producto_selected: Callback para cuando se selecciona un producto
        """
        self.on_movimiento_added = on_movimiento_added
        self.on_movimiento_updated = on_movimiento_updated
        self.on_movimiento_deleted = on_movimiento_deleted
        self.on_producto_selected = on_producto_selected
        
        logger.debug("🔧 Callbacks de MovimientosManager configurados")

    def registrar_entrada(self, codigo_barras: str, cantidad: int, precio_unitario: float = 0.0,
                         motivo: str = "", numero_documento: str = "",
                         usuario: str = "Sistema") -> bool:
        """
        Registrar entrada de mercadería.
        
        Args:
            codigo_barras: Código del producto
            cantidad: Cantidad a ingresar
            precio_unitario: Precio unitario del producto
            motivo: Descripción del motivo
            numero_documento: Número de documento asociado
            usuario: Usuario responsable
            
        Returns:
            bool: True si se registró correctamente, False en caso contrario
        """
        return self._registrar_movimiento("Entrada", codigo_barras, cantidad, 
                                        precio_unitario, motivo, numero_documento, usuario)

    def registrar_salida(self, codigo_barras: str, cantidad: int, precio_unitario: float = 0.0,
                        motivo: str = "", numero_documento: str = "",
                        usuario: str = "Sistema") -> bool:
        """
        Registrar salida de productos.
        
        Args:
            codigo_barras: Código del producto
            cantidad: Cantidad a retirar
            precio_unitario: Precio unitario del producto
            motivo: Descripción del motivo
            numero_documento: Número de documento asociado
            usuario: Usuario responsable
            
        Returns:
            bool: True si se registró correctamente, False en caso contrario
        """
        return self._registrar_movimiento("Salida", codigo_barras, cantidad,
                                        precio_unitario, motivo, numero_documento, usuario)

    def registrar_ajuste(self, codigo_barras: str, nuevo_stock: int, motivo: str = "",
                        usuario: str = "Sistema") -> bool:
        """
        Registrar ajuste de inventario.
        
        Args:
            codigo_barras: Código del producto
            nuevo_stock: Nuevo stock del producto
            motivo: Descripción del motivo del ajuste
            usuario: Usuario responsable
            
        Returns:
            bool: True si se registró correctamente, False en caso contrario
        """
        return self._registrar_movimiento("Ajuste", codigo_barras, nuevo_stock,
                                        0.0, motivo, "", usuario)

    def _registrar_movimiento(self, tipo: str, codigo_barras: str, cantidad: int,
                             precio_unitario: float, motivo: str, numero_documento: str,
                             usuario: str) -> bool:
        """Método interno para registrar cualquier tipo de movimiento"""
        try:
            # Validar datos
            if not self._validar_movimiento(tipo, codigo_barras, cantidad, precio_unitario):
                return False
            
            # Registrar movimiento
            params = (
                codigo_barras, tipo, cantidad, precio_unitario,
                motivo.strip(), usuario.strip(), numero_documento.strip()
            )
            
            result = self.db_manager.execute_query(INSERT_MOVIMIENTO, params)
            
            if result is not None:
                logger.info(f"✅ Movimiento {tipo} registrado: {cantidad} unidades del producto {codigo_barras}")
                
                # Llamar callback si está configurado
                if hasattr(self, 'on_movimiento_added') and self.on_movimiento_added:
                    self.on_movimiento_added()
                
                return True
            else:
                logger.error(f"❌ No se pudo registrar el movimiento {tipo}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error registrando movimiento {tipo}: {e}")
            return False

    def obtener_todos_movimientos(self, limite: int = 1000) -> List[Dict]:
        """Obtener todos los movimientos activos"""
        try:
            query = f"SELECT * FROM v_movimientos_activos LIMIT {limite}"
            results = self.db_manager.execute_query(query)
            
            if not results:
                return []
            
            movimientos = []
            for row in results:
                movimiento = {
                    'id': row[0],
                    'codigo_barras_producto': row[1],
                    'producto_nombre': row[2],
                    'tipo': row[3],
                    'cantidad': row[4],
                    'precio_unitario': row[5],
                    'motivo_descripcion': row[6] or "",
                    'usuario_responsable': row[7] or "Sistema",
                    'numero_documento_factura': row[8] or "",
                    'created_at': row[9],
                    'updated_at': row[10]
                }
                movimientos.append(movimiento)
            
            logger.info(f"📋 Obtenidos {len(movimientos)} movimientos")
            return movimientos
        except Exception as e:
            logger.error(f"❌ Error obteniendo movimientos: {e}")
            return []

    def obtener_movimientos_por_producto(self, codigo_barras: str) -> List[Dict]:
        """Obtener historial de movimientos de un producto específico"""
        try:
            results = self.db_manager.execute_query(SELECT_MOVIMIENTOS_BY_PRODUCTO, (codigo_barras,))
            
            if not results:
                return []
            
            movimientos = []
            for row in results:
                movimiento = {
                    'id': row[0],
                    'codigo_barras': row[1],
                    'tipo': row[2],
                    'cantidad': row[3],
                    'precio_unitario': row[4],
                    'motivo': row[5] or "",
                    'usuario': row[6] or "Sistema",
                    'numero_documento': row[7] or "",
                    'created_at': row[8],
                    'updated_at': row[9]
                }
                movimientos.append(movimiento)
            
            logger.info(f"📋 Obtenidos {len(movimientos)} movimientos para producto {codigo_barras}")
            return movimientos
        except Exception as e:
            logger.error(f"❌ Error obteniendo movimientos del producto {codigo_barras}: {e}")
            return []

    def obtener_stock_actual(self, codigo_barras: str) -> int:
        """Obtener el stock actual de un producto basado en sus movimientos"""
        try:
            # Query que suma entradas y resta salidas/ajustes
            query = """
            SELECT COALESCE(
                SUM(CASE 
                    WHEN tipo = 'Entrada' THEN cantidad 
                    WHEN tipo = 'Salida' THEN -cantidad 
                    WHEN tipo = 'Ajuste' THEN cantidad 
                    ELSE 0 
                END), 0
            ) as stock_actual
            FROM movimientos 
            WHERE codigo_barras_producto = ? AND deleted_at IS NULL
            """
            
            results = self.db_manager.execute_query(query, (codigo_barras,))
            
            if results and results[0][0] is not None:
                stock = results[0][0]
            else:
                stock = 0
            
            logger.debug(f"📊 Stock actual de {codigo_barras}: {stock}")
            return stock
        except Exception as e:
            logger.error(f"❌ Error calculando stock actual de {codigo_barras}: {e}")
            return 0

    def _validar_movimiento(self, tipo: str, codigo_barras: str, cantidad: int,
                           precio_unitario: float) -> bool:
        """Validar los datos de un movimiento antes de registrarlo"""
        if not codigo_barras or not codigo_barras.strip():
            logger.error("❌ El código de barras no puede estar vacío")
            return False
        
        if tipo not in ["Entrada", "Salida", "Ajuste"]:
            logger.error(f"❌ Tipo de movimiento inválido: {tipo}")
            return False
        
        if cantidad <= 0:
            logger.error("❌ La cantidad debe ser mayor a cero")
            return False
        
        if precio_unitario < 0:
            logger.error("❌ El precio unitario no puede ser negativo")
            return False
        
        # Verificar que el producto existe
        query = "SELECT stock_actual FROM productos WHERE codigo_barras = ? AND deleted_at IS NULL"
        results = self.db_manager.execute_query(query, (codigo_barras,))
        
        if not results:
            logger.error(f"❌ El producto {codigo_barras} no existe o está eliminado")
            return False
        
        return True

    # ==========================================
    # MÉTODOS DE INTERFAZ GRÁFICA
    # ==========================================
    
    def mostrar_ventana_movimientos(self):
        """Mostrar la ventana principal de gestión de movimientos."""
        try:
            # Cerrar ventana si ya existe
            if dpg.does_item_exist("ventana_movimientos"):
                dpg.delete_item("ventana_movimientos")
            
            with dpg.window(
                label="Gestión de Movimientos de Stock", 
                tag="ventana_movimientos",
                width=1200, 
                height=700,
                pos=(50, 50)
            ) as ventana_movimientos:
                with dpg.group(horizontal=True):
                    dpg.add_button(
                        label="Registrar Entrada",
                        callback=self._mostrar_modal_entrada,
                        width=150
                    )
                    dpg.add_button(
                        label="Registrar Salida",
                        callback=self._mostrar_modal_salida,
                        width=150
                    )
                    dpg.add_button(
                        label="Ajuste de Stock",
                        callback=self._mostrar_modal_ajuste,
                        width=150
                    )
                    dpg.add_button(
                        label="Actualizar Lista",
                        callback=self.cargar_movimientos,
                        width=150
                    )
                
                # Barra de búsqueda
                with dpg.group(horizontal=True):
                    dpg.add_text("Buscar por producto:")
                    dpg.add_input_text(
                        tag="buscar_movimiento_input",
                        width=300,
                        callback=self._buscar_movimientos_callback
                    )
                    dpg.add_button(
                        label="Buscar",
                        callback=self._buscar_movimientos_callback,
                        width=80
                    )
                    dpg.add_button(
                        label="Mostrar Todos",
                        callback=self.cargar_movimientos,
                        width=100
                    )
                
                dpg.add_separator()
                
                # Mensaje de estado
                dpg.add_text("", tag="movimientos_status_msg")
                
                # Tabla de movimientos
                with dpg.table(
                    tag="tabla_movimientos",
                    header_row=True,
                    borders_innerH=True,
                    borders_outerH=True,
                    borders_innerV=True,
                    borders_outerV=True,
                    scrollY=True,
                    height=400
                ) as tabla_movimientos:
                    dpg.add_table_column(label="ID", width_fixed=True, init_width_or_weight=50)
                    dpg.add_table_column(label="Fecha", width_fixed=True, init_width_or_weight=120)
                    dpg.add_table_column(label="Producto", width_fixed=True, init_width_or_weight=200)
                    dpg.add_table_column(label="Tipo", width_fixed=True, init_width_or_weight=80)
                    dpg.add_table_column(label="Cantidad", width_fixed=True, init_width_or_weight=80)
                    dpg.add_table_column(label="Precio Unit.", width_fixed=True, init_width_or_weight=100)
                    dpg.add_table_column(label="Total", width_fixed=True, init_width_or_weight=100)
                    dpg.add_table_column(label="Motivo", width_fixed=True, init_width_or_weight=150)
                    dpg.add_table_column(label="Usuario", width_fixed=True, init_width_or_weight=100)
                    dpg.add_table_column(label="N° Doc.", width_fixed=True, init_width_or_weight=100)
            
            # Cargar los datos iniciales
            self.cargar_movimientos()
            
        except Exception as e:
            logger.error(f"❌ Error mostrando ventana de movimientos: {e}")

    def cargar_movimientos(self):
        """Cargar y mostrar la lista de movimientos en la tabla."""
        try:
            if not dpg.does_item_exist("tabla_movimientos"):
                return
            
            # Limpiar solo las filas de la tabla (slot 1 = filas, slot 0 = headers/columnas)
            try:
                table_children = dpg.get_item_children("tabla_movimientos", slot=1)
                if table_children:
                    for child in table_children:
                        try:
                            dpg.delete_item(child)
                        except Exception as e:
                            logger.debug(f"No se pudo eliminar item {child}: {e}")
            except Exception as e:
                logger.debug(f"Error limpiando tabla: {e}")
            
            # Obtener movimientos
            movimientos = self.obtener_todos_movimientos()
            
            if not movimientos:
                with dpg.table_row(parent="tabla_movimientos"):
                    dpg.add_text("No hay movimientos registrados")
                    for _ in range(9):  # Llenar las columnas restantes
                        dpg.add_text("")
                return
            
            # Agregar movimientos a la tabla
            for movimiento in movimientos:
                with dpg.table_row(parent="tabla_movimientos"):
                    dpg.add_text(str(movimiento.get('id', '')))
                    
                    # Formatear fecha
                    fecha_str = movimiento.get('created_at', '')
                    fecha_texto = ""
                    if fecha_str:
                        try:
                            if isinstance(fecha_str, str):
                                # Parsear la fecha ISO y formatearla
                                fecha_dt = datetime.fromisoformat(fecha_str.replace('Z', '+00:00'))
                                fecha_texto = fecha_dt.strftime('%d/%m/%Y %H:%M')
                            else:
                                fecha_texto = str(fecha_str)
                        except:
                            fecha_texto = str(fecha_str)
                    
                    dpg.add_text(fecha_texto)
                    dpg.add_text(movimiento.get('producto_nombre', ''))
                    
                    # Color según tipo de movimiento
                    tipo = movimiento.get('tipo', '')
                    if tipo == 'Entrada':
                        dpg.add_text(tipo, color=[0, 255, 0])  # Verde
                    elif tipo == 'Salida':
                        dpg.add_text(tipo, color=[255, 0, 0])  # Rojo
                    elif tipo == 'Ajuste':
                        dpg.add_text(tipo, color=[255, 165, 0])  # Naranja
                    else:
                        dpg.add_text(tipo)
                    
                    cantidad = movimiento.get('cantidad', 0)
                    precio = movimiento.get('precio_unitario', 0.0)
                    total = cantidad * precio
                    
                    dpg.add_text(str(cantidad))
                    dpg.add_text(f"${precio:.2f}")
                    dpg.add_text(f"${total:.2f}")
                    dpg.add_text(movimiento.get('motivo_descripcion', ''))
                    dpg.add_text(movimiento.get('usuario_responsable', ''))
                    dpg.add_text(movimiento.get('numero_documento_factura', ''))
            
            # Actualizar mensaje de estado
            if dpg.does_item_exist("movimientos_status_msg"):
                dpg.set_value("movimientos_status_msg", f"✓ {len(movimientos)} movimientos cargados")
        
        except Exception as e:
            logger.error(f"❌ Error cargando movimientos: {e}")
            if dpg.does_item_exist("movimientos_status_msg"):
                dpg.set_value("movimientos_status_msg", f"✗ Error cargando movimientos: {str(e)}")

    def _mostrar_modal_entrada(self):
        """Mostrar modal para registrar entrada de stock."""
        self._mostrar_modal_movimiento("Entrada", "📦 Registrar Entrada de Stock")

    def _mostrar_modal_salida(self):
        """Mostrar modal para registrar salida de stock."""
        self._mostrar_modal_movimiento("Salida", "📤 Registrar Salida de Stock")

    def _mostrar_modal_ajuste(self):
        """Mostrar modal para ajuste de stock."""
        self._mostrar_modal_movimiento("Ajuste", "⚖️ Ajuste de Stock")

    def _mostrar_modal_movimiento(self, tipo: str, titulo: str):
        """Mostrar modal genérico para registrar movimientos."""
        try:
            tag_modal = f"modal_{tipo.lower()}_movimiento"
            
            if dpg.does_item_exist(tag_modal):
                dpg.delete_item(tag_modal)
            
            with dpg.window(
                label=titulo,
                tag=tag_modal,
                modal=True,
                width=500,
                height=450,
                pos=(400, 150)
            ) as ventana:
                
                dpg.add_text(f"Complete los datos del movimiento de {tipo.lower()}:")
                dpg.add_separator()
                
                # Campos del formulario
                dpg.add_text("Código de Barras del Producto: *")
                dpg.add_input_text(tag=f"{tipo.lower()}_codigo_barras", width=-1)
                
                dpg.add_text("Cantidad: *")
                dpg.add_input_int(tag=f"{tipo.lower()}_cantidad", default_value=1, width=-1, min_value=1)
                
                dpg.add_text("Precio Unitario:")
                dpg.add_input_float(tag=f"{tipo.lower()}_precio", default_value=0.0, format="%.2f", width=-1, min_value=0.0)
                
                dpg.add_text("Motivo:")
                motivos_default = {
                    "Entrada": "Compra", 
                    "Salida": "Venta", 
                    "Ajuste": "Ajuste de inventario"
                }
                dpg.add_input_text(
                    tag=f"{tipo.lower()}_motivo",
                    default_value=motivos_default.get(tipo, ""),
                    width=-1
                )
                
                dpg.add_text("Número de Documento:")
                dpg.add_input_text(tag=f"{tipo.lower()}_documento", width=-1)
                
                dpg.add_text("Usuario Responsable:")
                dpg.add_input_text(tag=f"{tipo.lower()}_usuario", default_value="Sistema", width=-1)
                
                dpg.add_separator()
                dpg.add_text("* Campos obligatorios", color=[255, 255, 0])
                
                # Botones
                with dpg.group(horizontal=True):
                    btn_registrar = dpg.add_button(
                        label=f"Registrar {tipo}",
                        callback=lambda: self._guardar_movimiento(tipo),
                        width=150
                    )
                    dpg.bind_item_theme(btn_registrar, "theme_boton_verde")
                    btn_cancelar = dpg.add_button(
                        label="Cancelar",
                        callback=lambda: dpg.delete_item(tag_modal),
                        width=100
                    )
                    dpg.bind_item_theme(btn_cancelar, "theme_boton_rojo")
        
        except Exception as e:
            logger.error(f"❌ Error mostrando modal de {tipo}: {e}")

    def _guardar_movimiento(self, tipo: str):
        """Guardar un nuevo movimiento desde el modal."""
        try:
            # Obtener valores del formulario
            codigo = dpg.get_value(f"{tipo.lower()}_codigo_barras") or ""
            cantidad = dpg.get_value(f"{tipo.lower()}_cantidad") or 0
            precio = dpg.get_value(f"{tipo.lower()}_precio") or 0.0
            motivo = dpg.get_value(f"{tipo.lower()}_motivo") or ""
            documento = dpg.get_value(f"{tipo.lower()}_documento") or ""
            usuario = dpg.get_value(f"{tipo.lower()}_usuario") or "Sistema"
            
            # Registrar el movimiento según el tipo
            exito = False
            if tipo == "Entrada":
                exito = self.registrar_entrada(codigo, cantidad, precio, motivo, documento, usuario)
            elif tipo == "Salida":
                exito = self.registrar_salida(codigo, cantidad, precio, motivo, documento, usuario)
            elif tipo == "Ajuste":
                exito = self.registrar_ajuste(codigo, cantidad, motivo, usuario)
            
            if exito:
                dpg.delete_item(f"modal_{tipo.lower()}_movimiento")
                self.cargar_movimientos()
                if dpg.does_item_exist("movimientos_status_msg"):
                    dpg.set_value("movimientos_status_msg", f"✓ {tipo} registrado correctamente")
            else:
                if dpg.does_item_exist("movimientos_status_msg"):
                    dpg.set_value("movimientos_status_msg", f"✗ Error al registrar {tipo.lower()}")
        
        except Exception as e:
            logger.error(f"❌ Error guardando {tipo}: {e}")
            if dpg.does_item_exist("movimientos_status_msg"):
                dpg.set_value("movimientos_status_msg", f"✗ Error: {str(e)}")

    def _buscar_movimientos_callback(self):
        """Callback para buscar movimientos por producto."""
        try:
            termino = dpg.get_value("buscar_movimiento_input") or ""
            
            if not termino.strip():
                self.cargar_movimientos()
                return
            
            # Buscar movimientos del producto específico
            movimientos = self.obtener_movimientos_por_producto(termino.strip())
            self._mostrar_movimientos_filtrados(movimientos, f"Movimientos del producto: {termino}")
        
        except Exception as e:
            logger.error(f"❌ Error buscando movimientos: {e}")
            if dpg.does_item_exist("movimientos_status_msg"):
                dpg.set_value("movimientos_status_msg", f"✗ Error en búsqueda: {str(e)}")

    def _mostrar_movimientos_filtrados(self, movimientos: List[Dict], mensaje: str = ""):
        """Mostrar movimientos filtrados en la tabla."""
        try:
            if not dpg.does_item_exist("tabla_movimientos"):
                return
            
            # Limpiar tabla
            dpg.delete_item("tabla_movimientos", children_only=True)
            
            # Recrear columnas
            dpg.add_table_column(label="ID", width_fixed=True, init_width_or_weight=50, parent="tabla_movimientos")
            dpg.add_table_column(label="Fecha", width_fixed=True, init_width_or_weight=120, parent="tabla_movimientos")
            dpg.add_table_column(label="Código Barras", width_fixed=True, init_width_or_weight=150, parent="tabla_movimientos")
            dpg.add_table_column(label="Tipo", width_fixed=True, init_width_or_weight=80, parent="tabla_movimientos")
            dpg.add_table_column(label="Cantidad", width_fixed=True, init_width_or_weight=80, parent="tabla_movimientos")
            dpg.add_table_column(label="Precio Unit.", width_fixed=True, init_width_or_weight=100, parent="tabla_movimientos")
            dpg.add_table_column(label="Total", width_fixed=True, init_width_or_weight=100, parent="tabla_movimientos")
            dpg.add_table_column(label="Motivo", width_fixed=True, init_width_or_weight=150, parent="tabla_movimientos")
            dpg.add_table_column(label="Usuario", width_fixed=True, init_width_or_weight=100, parent="tabla_movimientos")
            dpg.add_table_column(label="N° Doc.", width_fixed=True, init_width_or_weight=100, parent="tabla_movimientos")
            
            if not movimientos:
                with dpg.table_row(parent="tabla_movimientos"):
                    dpg.add_text("No se encontraron movimientos")
                    for _ in range(9):
                        dpg.add_text("")
                
                if dpg.does_item_exist("movimientos_status_msg"):
                    dpg.set_value("movimientos_status_msg", "ℹ️ No se encontraron movimientos")
                return
            
            # Agregar movimientos
            for movimiento in movimientos:
                with dpg.table_row(parent="tabla_movimientos"):
                    dpg.add_text(str(movimiento.get('id', '')))
                    
                    # Formatear fecha
                    fecha_str = movimiento.get('created_at', '')
                    fecha_texto = ""
                    if fecha_str:
                        try:
                            fecha_dt = datetime.fromisoformat(fecha_str.replace('Z', '+00:00'))
                            fecha_texto = fecha_dt.strftime('%d/%m/%Y %H:%M')
                        except:
                            fecha_texto = str(fecha_str)
                    
                    dpg.add_text(fecha_texto)
                    dpg.add_text(movimiento.get('codigo_barras', ''))
                    
                    # Color según tipo
                    tipo = movimiento.get('tipo', '')
                    if tipo == 'Entrada':
                        dpg.add_text(tipo, color=[0, 255, 0])
                    elif tipo == 'Salida':
                        dpg.add_text(tipo, color=[255, 0, 0])
                    elif tipo == 'Ajuste':
                        dpg.add_text(tipo, color=[255, 165, 0])
                    else:
                        dpg.add_text(tipo)
                    
                    cantidad = movimiento.get('cantidad', 0)
                    precio = movimiento.get('precio_unitario', 0.0)
                    total = cantidad * precio
                    
                    dpg.add_text(str(cantidad))
                    dpg.add_text(f"${precio:.2f}")
                    dpg.add_text(f"${total:.2f}")
                    dpg.add_text(movimiento.get('motivo', ''))
                    dpg.add_text(movimiento.get('usuario', ''))
                    dpg.add_text(movimiento.get('numero_documento', ''))
            
            # Actualizar mensaje
            if dpg.does_item_exist("movimientos_status_msg"):
                status_msg = mensaje if mensaje else f"✓ {len(movimientos)} movimientos encontrados"
                dpg.set_value("movimientos_status_msg", status_msg)
        
        except Exception as e:
            logger.error(f"❌ Error mostrando movimientos filtrados: {e}")

    def crear_interfaz_movimientos(self, parent_tab):
        """Crear la interfaz simplificada de movimientos con tabla y botones modales - Compatibilidad con UI Manager"""
        try:
            # Configurar temas para botones (solo una vez)
            self._configurar_temas_botones()
            
            # Título y botones principales
            with dpg.group(horizontal=True, parent=parent_tab):
                dpg.add_text("Gestión de Movimientos", color=(0, 255, 255))
                dpg.add_spacer(width=50)
                btn_nueva_entrada = dpg.add_button(label="Nueva Entrada", callback=self._mostrar_modal_entrada)
                dpg.bind_item_theme(btn_nueva_entrada, "theme_boton_verde")
                btn_nueva_salida = dpg.add_button(label="Nueva Salida", callback=self._mostrar_modal_salida)
                dpg.bind_item_theme(btn_nueva_salida, "theme_boton_rojo")
                btn_ajuste = dpg.add_button(label="Ajuste Stock", callback=self._mostrar_modal_ajuste)
                dpg.bind_item_theme(btn_ajuste, "theme_boton_amarillo")
            
            dpg.add_separator(parent=parent_tab)

            # Barra de búsqueda compacta
            with dpg.group(horizontal=True, parent=parent_tab):
                dpg.add_text("Buscar:")
                dpg.add_input_text(
                    tag="buscar_movimiento_tab",
                    width=200,
                    callback=self._buscar_movimientos_tab_callback,
                    parent=parent_tab
                )
                dpg.add_button(
                    label="Buscar",
                    callback=self._buscar_movimientos_tab_callback,
                    parent=parent_tab
                )

            # Tabla de movimientos (con altura fija para dejar espacio al mensaje)
            with dpg.table(tag="table_movimientos_tab", header_row=True,
                         borders_innerH=True, borders_outerH=True,
                         borders_innerV=True, borders_outerV=True,
                         parent=parent_tab, height=350):
                dpg.add_table_column(label="ID", width_fixed=True, init_width_or_weight=50)
                dpg.add_table_column(label="Fecha", width_fixed=True, init_width_or_weight=120)
                dpg.add_table_column(label="Producto", width_fixed=True, init_width_or_weight=180)
                dpg.add_table_column(label="Tipo", width_fixed=True, init_width_or_weight=80)
                dpg.add_table_column(label="Cantidad", width_fixed=True, init_width_or_weight=80)
                dpg.add_table_column(label="Precio", width_fixed=True, init_width_or_weight=100)
                dpg.add_table_column(label="Motivo", width_fixed=True, init_width_or_weight=150)

            # Campo de mensajes inferior para feedback de usuario
            dpg.add_spacer(height=10, parent=parent_tab)
            dpg.add_text("", tag="movimientos_tab_status_msg", color=(255,0,0), parent=parent_tab)

            # Cargar datos iniciales
            self.cargar_movimientos_tab()
            
        except Exception as e:
            logger.error(f"❌ Error creando interfaz de movimientos: {e}")

    def cargar_movimientos_tab(self):
        """Cargar movimientos en la tabla del tab principal"""
        try:
            if not dpg.does_item_exist("table_movimientos_tab"):
                return
            
            # Limpiar solo las filas de la tabla (slot 1 = filas, slot 0 = headers/columnas)
            try:
                table_children = dpg.get_item_children("table_movimientos_tab", slot=1)
                if table_children:
                    for child in table_children:
                        try:
                            dpg.delete_item(child)
                        except Exception as e:
                            logger.debug(f"No se pudo eliminar item {child}: {e}")
            except Exception as e:
                logger.debug(f"Error limpiando tabla: {e}")
            
            # Obtener últimos movimientos (limitado para el tab)
            movimientos = self.obtener_todos_movimientos(50)  # Solo últimos 50
            movimientos = self.obtener_todos_movimientos(50)  # Solo últimos 50
            
            if not movimientos:
                with dpg.table_row(parent="table_movimientos_tab"):
                    dpg.add_text("No hay movimientos registrados")
                    for _ in range(6):  # Llenar las columnas restantes
                        dpg.add_text("")
                return
            
            # Agregar movimientos a la tabla
            for movimiento in movimientos:
                with dpg.table_row(parent="table_movimientos_tab"):
                    dpg.add_text(str(movimiento.get('id', '')))
                    
                    # Formatear fecha
                    fecha_str = movimiento.get('created_at', '')
                    fecha_texto = ""
                    if fecha_str:
                        try:
                            if isinstance(fecha_str, str):
                                fecha_dt = datetime.fromisoformat(fecha_str.replace('Z', '+00:00'))
                                fecha_texto = fecha_dt.strftime('%d/%m %H:%M')  # Formato compacto
                            else:
                                fecha_texto = str(fecha_str)[:10]  # Solo primeros 10 caracteres
                        except:
                            fecha_texto = str(fecha_str)[:10]
                    
                    dpg.add_text(fecha_texto)
                    
                    # Nombre del producto (truncar si es muy largo)
                    nombre_producto = movimiento.get('producto_nombre', '')
                    if len(nombre_producto) > 20:
                        nombre_producto = nombre_producto[:17] + "..."
                    dpg.add_text(nombre_producto)
                    
                    # Color según tipo de movimiento
                    tipo = movimiento.get('tipo', '')
                    if tipo == 'Entrada':
                        dpg.add_text(tipo, color=[0, 255, 0])  # Verde
                    elif tipo == 'Salida':
                        dpg.add_text(tipo, color=[255, 0, 0])  # Rojo
                    elif tipo == 'Ajuste':
                        dpg.add_text(tipo, color=[255, 165, 0])  # Naranja
                    else:
                        dpg.add_text(tipo)
                    
                    cantidad = movimiento.get('cantidad', 0)
                    precio = movimiento.get('precio_unitario', 0.0)
                    
                    dpg.add_text(str(cantidad))
                    dpg.add_text(f"${precio:.2f}")
                    
                    # Motivo truncado
                    motivo = movimiento.get('motivo_descripcion', '')
                    if len(motivo) > 15:
                        motivo = motivo[:12] + "..."
                    dpg.add_text(motivo)
            
            # Actualizar mensaje de estado
            if dpg.does_item_exist("movimientos_tab_status_msg"):
                dpg.set_value("movimientos_tab_status_msg", f"✓ Últimos {len(movimientos)} movimientos")
        
        except Exception as e:
            logger.error(f"❌ Error cargando movimientos en tab: {e}")
            if dpg.does_item_exist("movimientos_tab_status_msg"):
                dpg.set_value("movimientos_tab_status_msg", f"✗ Error: {str(e)}")

    def _buscar_movimientos_tab_callback(self):
        """Callback para buscar movimientos desde el tab principal"""
        try:
            termino = dpg.get_value("buscar_movimiento_tab") or ""
            
            if not termino.strip():
                self.cargar_movimientos_tab()
                return
            
            # Buscar movimientos del producto específico
            movimientos = self.obtener_movimientos_por_producto(termino.strip())
            self._mostrar_movimientos_tab_filtrados(movimientos, f"Producto: {termino}")
        
        except Exception as e:
            logger.error(f"❌ Error buscando movimientos en tab: {e}")
            if dpg.does_item_exist("movimientos_tab_status_msg"):
                dpg.set_value("movimientos_tab_status_msg", f"✗ Error en búsqueda: {str(e)}")

    def _mostrar_movimientos_tab_filtrados(self, movimientos: List[Dict], mensaje: str = ""):
        """Mostrar movimientos filtrados en la tabla del tab"""
        try:
            if not dpg.does_item_exist("table_movimientos_tab"):
                return
            
            # Limpiar tabla
            dpg.delete_item("table_movimientos_tab", children_only=True)
            
            # Recrear columnas
            dpg.add_table_column(label="ID", width_fixed=True, init_width_or_weight=50, parent="table_movimientos_tab")
            dpg.add_table_column(label="Fecha", width_fixed=True, init_width_or_weight=120, parent="table_movimientos_tab")
            dpg.add_table_column(label="Código", width_fixed=True, init_width_or_weight=120, parent="table_movimientos_tab")
            dpg.add_table_column(label="Tipo", width_fixed=True, init_width_or_weight=80, parent="table_movimientos_tab")
            dpg.add_table_column(label="Cantidad", width_fixed=True, init_width_or_weight=80, parent="table_movimientos_tab")
            dpg.add_table_column(label="Precio", width_fixed=True, init_width_or_weight=100, parent="table_movimientos_tab")
            dpg.add_table_column(label="Motivo", width_fixed=True, init_width_or_weight=150, parent="table_movimientos_tab")
            
            if not movimientos:
                with dpg.table_row(parent="table_movimientos_tab"):
                    dpg.add_text("No se encontraron movimientos")
                    for _ in range(6):
                        dpg.add_text("")
                
                if dpg.does_item_exist("movimientos_tab_status_msg"):
                    dpg.set_value("movimientos_tab_status_msg", "ℹ️ No se encontraron movimientos")
                return
            
            # Agregar movimientos (limitado para el tab)
            for movimiento in movimientos[:20]:  # Solo primeros 20
                with dpg.table_row(parent="table_movimientos_tab"):
                    dpg.add_text(str(movimiento.get('id', '')))
                    
                    # Formatear fecha
                    fecha_str = movimiento.get('created_at', '')
                    fecha_texto = ""
                    if fecha_str:
                        try:
                            fecha_dt = datetime.fromisoformat(fecha_str.replace('Z', '+00:00'))
                            fecha_texto = fecha_dt.strftime('%d/%m %H:%M')
                        except:
                            fecha_texto = str(fecha_str)[:10]
                    
                    dpg.add_text(fecha_texto)
                    dpg.add_text(movimiento.get('codigo_barras', ''))
                    
                    # Color según tipo
                    tipo = movimiento.get('tipo', '')
                    if tipo == 'Entrada':
                        dpg.add_text(tipo, color=[0, 255, 0])
                    elif tipo == 'Salida':
                        dpg.add_text(tipo, color=[255, 0, 0])
                    elif tipo == 'Ajuste':
                        dpg.add_text(tipo, color=[255, 165, 0])
                    else:
                        dpg.add_text(tipo)
                    
                    cantidad = movimiento.get('cantidad', 0)
                    precio = movimiento.get('precio_unitario', 0.0)
                    
                    dpg.add_text(str(cantidad))
                    dpg.add_text(f"${precio:.2f}")
                    dpg.add_text(movimiento.get('motivo', ''))
            
            # Actualizar mensaje
            if dpg.does_item_exist("movimientos_tab_status_msg"):
                status_msg = mensaje if mensaje else f"✓ {len(movimientos)} movimientos encontrados"
                if len(movimientos) > 20:
                    status_msg += f" (mostrando primeros 20)"
                dpg.set_value("movimientos_tab_status_msg", status_msg)
        
        except Exception as e:
            logger.error(f"❌ Error mostrando movimientos filtrados en tab: {e}")