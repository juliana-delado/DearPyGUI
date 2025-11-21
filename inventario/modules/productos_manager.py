# productos_manager.py - Gestor de productos del inventario
"""
ProductosManager: Clase para manejar todas las operaciones CRUD de productos.
Incluye validación de códigos de barras, manejo de imágenes y alertas de stock.
"""

import logging
import re
import os
from typing import List, Dict, Any, Optional, Tuple, Union
from datetime import date
from .base_model import BaseModel
from . import sqlstatement as sql

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProductosManager(BaseModel):
    """Manager para gestión de productos con funcionalidades empresariales"""
    
    def __init__(self, db_name: str = "inventario.db", app_instance=None):
        super().__init__(db_name)
        self.table_name = "productos"
        self.primary_key = "codigo_barras"
        self.app = app_instance  # Referencia a la aplicación principal
        
        # Callbacks para notificar cambios
        self.on_producto_added = None
        self.on_producto_updated = None
        self.on_producto_deleted = None
        self.on_stock_alert = None
    
    def _configurar_temas_botones(self):
        """Los temas ahora se configuran globalmente en UIManager"""
        # Los temas se configuran una sola vez en UIManager.configurar_temas_globales()
        pass
        
    
    def set_callbacks(self, on_producto_added=None, on_producto_updated=None, 
                     on_producto_deleted=None, on_stock_alert=None):
        """Establecer funciones callback"""
        self.on_producto_added = on_producto_added
        self.on_producto_updated = on_producto_updated
        self.on_producto_deleted = on_producto_deleted
        self.on_stock_alert = on_stock_alert
    
    def agregar_producto(self, codigo_barras: str, nombre: str, descripcion: str = "",
                        categoria_id: Optional[int] = None, proveedor_id: Optional[int] = None,
                        stock_actual: int = 0, stock_minimo: int = 0,
                        precio_compra: float = 0.0, precio_venta: float = 0.0,
                        imagen_producto: str = "") -> bool:
        """Agregar un nuevo producto al inventario"""
        try:
            # Validar datos de entrada
            if not self._validar_datos_producto(codigo_barras, nombre, descripcion,
                                              stock_actual, stock_minimo, precio_compra, precio_venta):
                return False
            
            # Verificar que el código de barras no existe
            if self.obtener_producto_por_codigo(codigo_barras):
                logger.warning(f"⚠️ El producto con código '{codigo_barras}' ya existe")
                return False
            
            # Insertar nuevo producto
            rows_affected = self.execute_command(
                sql.INSERT_PRODUCTO,
                (codigo_barras, nombre.strip(), descripcion.strip(), categoria_id, proveedor_id,
                 stock_actual, stock_minimo, precio_compra, precio_venta, 
                 date.today().isoformat(), imagen_producto.strip())
            )
            
            if rows_affected > 0:
                # Verificar alerta de stock
                self._verificar_alerta_stock(codigo_barras, stock_actual, stock_minimo)
                
                if self.on_producto_added:
                    self.on_producto_added()
                
                return True
            else:
                logger.error(f"❌ No se pudo agregar el producto '{nombre}'")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error agregando producto: {e}")
            return False
    
    def obtener_todos_productos(self) -> List[Tuple]:
        """Obtener todos los productos activos con información completa"""
        try:
            productos = self.execute_query(sql.SELECT_ALL_PRODUCTOS_ACTIVOS)
            return productos
        except Exception as e:
            logger.error(f"❌ Error obteniendo productos: {e}")
            return []
    
    def obtener_producto_por_codigo(self, codigo_barras: str) -> Optional[Tuple]:
        """Obtener un producto específico por su código de barras"""
        try:
            resultado = self.execute_query(sql.SELECT_PRODUCTO_BY_CODIGO, (codigo_barras,))
            if resultado:
                return resultado[0]
            else:
                logger.warning(f"⚠️ Producto {codigo_barras} no encontrado")
                return None
        except Exception as e:
            logger.error(f"❌ Error obteniendo producto {codigo_barras}: {e}")
            return None
    
    def actualizar_producto(self, codigo_barras: str, nombre: str, descripcion: str = "",
                          categoria_id: Optional[int] = None, proveedor_id: Optional[int] = None,
                          stock_minimo: int = 0, precio_compra: float = 0.0, 
                          precio_venta: float = 0.0, imagen_producto: str = "") -> bool:
        """Actualizar un producto existente"""
        try:
            # Validar que el producto existe
            producto_actual = self.obtener_producto_por_codigo(codigo_barras)
            if not producto_actual:
                logger.warning(f"⚠️ Producto {codigo_barras} no encontrado")
                return False
            
            # Validar datos
            if not self._validar_datos_producto(codigo_barras, nombre, descripcion,
                                              producto_actual[5], stock_minimo, precio_compra, precio_venta):
                return False
            
            # Actualizar producto
            rows_affected = self.execute_command(
                sql.UPDATE_PRODUCTO,
                (nombre.strip(), descripcion.strip(), categoria_id, proveedor_id,
                 stock_minimo, precio_compra, precio_venta, imagen_producto.strip(), codigo_barras)
            )
            
            if rows_affected > 0:
                
                # Verificar alerta de stock con nuevo stock mínimo
                self._verificar_alerta_stock(codigo_barras, producto_actual[5], stock_minimo)
                
                if self.on_producto_updated:
                    self.on_producto_updated()
                
                return True
            else:
                logger.error(f"❌ No se pudo actualizar el producto {codigo_barras}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error actualizando producto {codigo_barras}: {e}")
            return False
    
    def obtener_productos_stock_bajo(self) -> List[Tuple]:
        """Obtener productos con stock por debajo del mínimo"""
        try:
            productos = self.execute_query(sql.SELECT_PRODUCTOS_STOCK_BAJO)
            return productos
        except Exception as e:
            logger.error(f"❌ Error obteniendo productos con stock bajo: {e}")
            return []
    
    def buscar_productos(self, termino_busqueda: str) -> List[Tuple]:
        """Buscar productos por código, nombre o descripción"""
        try:
            if not termino_busqueda.strip():
                return self.obtener_todos_productos()
            
            # Buscar en vista de productos activos
            termino = f"%{termino_busqueda.strip()}%"
            resultados = self.execute_query(sql.SELECT_BUSCAR_PRODUCTOS, (termino, termino, termino))
            
            return resultados
            
        except Exception as e:
            logger.error(f"❌ Error buscando productos: {e}")
            return []
    
    def eliminar_producto(self, codigo_barras: str) -> 'Union[bool, str]':
        """Eliminar producto (soft delete). Devuelve True si elimina, o string con el motivo si no."""
        try:
            producto = self.obtener_producto_por_codigo(codigo_barras)
            if not producto:
                return "Producto no encontrado"
            if not self._validate_before_delete(codigo_barras):
                # Revisar si hay stock o movimientos
                prod = self.obtener_producto_por_codigo(codigo_barras)
                if prod and prod[5] > 0:
                    return f"tiene stock actual de {prod[5]} unidades"
                # Si no es stock, es por movimientos recientes
                return "tiene movimientos recientes en los últimos 30 días"
            rows_affected = self.execute_command(sql.DELETE_PRODUCTO_SOFT, (codigo_barras,))
            if rows_affected > 0:
                if self.on_producto_deleted:
                    self.on_producto_deleted()
                return True
            else:
                return "No se pudo eliminar el producto"
        except Exception as e:
            return f"Error eliminando producto: {e}"
    
    def generar_codigo_barras(self) -> str:
        """Generar un código de barras personalizable"""
        import random
        from datetime import datetime
        
        # Generar código usando timestamp + número aleatorio para unicidad
        timestamp = datetime.now().strftime("%y%m%d")  # YYMMDD
        numero_aleatorio = random.randint(1000, 9999)   # 4 dígitos
        
        codigo_completo = f"PRD-{timestamp}-{numero_aleatorio}"
        
        # Verificar que no exista ya en la base de datos
        contador = 1
        codigo_original = codigo_completo
        while self.obtener_producto_por_codigo(codigo_completo):
            codigo_completo = f"{codigo_original}-{contador:02d}"
            contador += 1
        
        return codigo_completo
    
    def _validar_datos_producto(self, codigo_barras: str, nombre: str, descripcion: str,
                               stock_actual: int, stock_minimo: int, precio_compra: float,
                               precio_venta: float) -> bool:
        """Validar los datos de entrada para un producto"""
        
        # Validar código de barras
        if not codigo_barras or not codigo_barras.strip():
            logger.error("❌ El código de barras es obligatorio")
            return False
        
        if not self._validar_codigo_barras(codigo_barras):
            return False
        
        # Validar nombre
        if not nombre or not nombre.strip():
            logger.error("❌ El nombre del producto es obligatorio")
            return False
        
        if len(nombre.strip()) > 200:
            logger.error("❌ El nombre no puede exceder 200 caracteres")
            return False
        
        # Validar stock
        if stock_actual < 0:
            logger.error("❌ El stock actual no puede ser negativo")
            return False
        
        if stock_minimo < 0:
            logger.error("❌ El stock mínimo no puede ser negativo")
            return False
        
        # Validar precios
        if precio_compra < 0:
            logger.error("❌ El precio de compra no puede ser negativo")
            return False
        
        if precio_venta < 0:
            logger.error("❌ El precio de venta no puede ser negativo")
            return False
        
        # Validar descripción
        if len(descripcion) > 500:
            logger.error("❌ La descripción no puede exceder 500 caracteres")
            return False
        
        return True
    
    def _validar_codigo_barras(self, codigo_barras: str) -> bool:
        """Validar formato de código de barras - Formato libre"""
        # Validar que no esté vacío
        codigo_limpio = codigo_barras.strip()
        
        if not codigo_limpio:
            logger.error("❌ El código de barras no puede estar vacío")
            return False
        
        # Validar longitud mínima y máxima (flexible)
        if len(codigo_limpio) < 3:
            logger.error(f"❌ Código de barras demasiado corto (mínimo 3 caracteres): '{codigo_barras}'")
            return False
            
        if len(codigo_limpio) > 50:
            logger.error(f"❌ Código de barras demasiado largo (máximo 50 caracteres): '{codigo_barras}'")
            return False
        
        # Permitir caracteres alfanuméricos, guiones y puntos
        import re
        if not re.match(r'^[a-zA-Z0-9\-\.\_]+$', codigo_limpio):
            logger.error(f"❌ Código de barras contiene caracteres no válidos: '{codigo_barras}'")
            return False
        
        return True
    
    def _verificar_alerta_stock(self, codigo_barras: str, stock_actual: int, stock_minimo: int):
        """Verificar si un producto necesita alerta de stock bajo"""
        if stock_actual <= stock_minimo and stock_minimo > 0:
            logger.warning(f"⚠️ ALERTA DE STOCK: Producto {codigo_barras} tiene stock bajo ({stock_actual} <= {stock_minimo})")
            
            if self.on_stock_alert:
                self.on_stock_alert(codigo_barras, stock_actual, stock_minimo)
    
    def _validate_before_delete(self, record_id: Union[str, int]) -> bool:
        """Validar que un producto puede ser eliminado"""
        import dearpygui.dearpygui as dpg
        
        try:
            # Verificar si tiene movimientos recientes (últimos 30 días)
            result = self.execute_query(sql.SELECT_MOVIMIENTOS_RECIENTES_PRODUCTO, (record_id,))
            movimientos_recientes = result[0][0] if result else 0
            if movimientos_recientes > 0:
                return False
            # Verificar si tiene stock actual
            producto = self.obtener_producto_por_codigo(str(record_id))
            if producto and producto[5] > 0:  # stock_actual > 0
                return False
            return True
        except Exception as e:
            return False

    # ================================
    # INTERFAZ DE USUARIO
    # ================================
    
    def crear_interfaz_productos(self, parent_tab):
        """Crear la interfaz simplificada de productos con tabla y ventana modal"""
        import dearpygui.dearpygui as dpg
        
        # Configurar temas para botones (solo una vez)
        self._configurar_temas_botones()
        
        # Título y botones principales
        with dpg.group(horizontal=True, parent=parent_tab):
            dpg.add_text("Gestion de Productos", color=(0, 255, 0))
            dpg.add_spacer(width=50)
            btn_agregar = dpg.add_button(label="Agregar Producto", callback=lambda: self._abrir_ventana_producto("agregar"))
            if self.app and hasattr(self.app, 'ui_manager'):
                self.app.ui_manager.aplicar_temas_elementos(btn_agregar, "boton_verde")
            else:
                dpg.bind_item_theme(btn_agregar, "theme_boton_verde")
            btn_imprimir = dpg.add_button(label="Imprimir PDF", callback=self._generar_pdf_productos)
            if self.app and hasattr(self.app, 'ui_manager'):
                self.app.ui_manager.aplicar_temas_elementos(btn_imprimir, "boton_blanco")
            else:
                dpg.bind_item_theme(btn_imprimir, "theme_boton_blanco")
            btn_stock_bajo = dpg.add_button(label="Reporte Stock Bajo", callback=self._generar_reporte_stock_bajo)
            if self.app and hasattr(self.app, 'ui_manager'):
                self.app.ui_manager.aplicar_temas_elementos(btn_stock_bajo, "boton_blanco")
            else:
                dpg.bind_item_theme(btn_stock_bajo, "theme_boton_blanco")
        
        dpg.add_separator(parent=parent_tab)

        # Tabla de productos (con altura fija para dejar espacio al mensaje)
        with dpg.table(tag="tabla_productos", header_row=True,
                     borders_innerH=True, borders_outerH=True,
                     borders_innerV=True, borders_outerV=True,
                     parent=parent_tab, height=400) as tabla_productos:
            dpg.add_table_column(label="Codigo", width_fixed=True, init_width_or_weight=120)
            dpg.add_table_column(label="Nombre", width_fixed=True, init_width_or_weight=200)
            dpg.add_table_column(label="Categoria", width_fixed=True, init_width_or_weight=150)
            dpg.add_table_column(label="Stock", width_fixed=True, init_width_or_weight=80)
            dpg.add_table_column(label="Precio", width_fixed=True, init_width_or_weight=100)
            dpg.add_table_column(label="Acciones", width_fixed=True, init_width_or_weight=140)
            
            # Aplicar tema gris oscuro a la tabla
            if self.app and hasattr(self.app, 'ui_manager'):
                self.app.ui_manager.aplicar_temas_elementos(tabla_productos, "tabla")

        # Campo de mensajes inferiores para feedback de usuario (errores, info)
        dpg.add_spacer(height=10, parent=parent_tab)
        dpg.add_text("", tag="productos_status_msg", color=(255,0,0), parent=parent_tab)

        # Crear la ventana modal para agregar/editar productos
        self._crear_ventana_producto()
    
    def _crear_ventana_producto(self):
        """Crear ventana modal para agregar/editar productos"""
        import dearpygui.dearpygui as dpg
        
        with dpg.window(label="Producto", tag="ventana_producto", modal=True, show=False,
                       width=500, height=600, pos=(200, 100)) as ventana:
            
            # Título dinámico
            dpg.add_text("Agregar Producto", tag="titulo_ventana_producto", color=(0, 255, 0))
            dpg.add_separator()
            
            # Formulario
            with dpg.group() as grupo_formulario:
                with dpg.group(horizontal=True):
                    dpg.add_text("Codigo Barras")
                    dpg.add_input_text(tag="modal_codigo_producto", width=300)
                with dpg.group(horizontal=True):
                    dpg.add_text("Nombre")
                    dpg.add_input_text(tag="modal_nombre_producto", width=300)
                with dpg.group(horizontal=True):
                    dpg.add_text("Descripcion")
                    dpg.add_input_text(tag="modal_descripcion_producto", 
                                      multiline=True, height=80, width=300)

                # Combos
                
                dpg.add_combo(label="Categoria", tag="modal_combo_categoria", width=300)
                dpg.add_combo(label="Proveedor", tag="modal_combo_proveedor", width=300)
                
                # Campos numéricos
                dpg.add_input_float(label="Precio Compra", tag="modal_precio_compra_producto", width=300, format="%.2f")
                dpg.add_input_float(label="Precio Venta", tag="modal_precio_venta_producto", width=300, format="%.2f")
                dpg.add_input_int(label="Stock Inicial", tag="modal_stock_producto", width=300)
                dpg.add_input_int(label="Stock Minimo", tag="modal_stock_minimo", width=300)
                dpg.add_input_text(label="Ubicacion", tag="modal_ubicacion_producto", width=300)
                dpg.add_input_text(label="Imagen (URL/Ruta)", tag="modal_imagen_producto", width=300)
            
            dpg.add_separator()
            
            # Estado y mensaje
            dpg.add_text("", tag="modal_status_producto", color=(255, 255, 0))
            
            # Botones centrados usando tabla de 3 columnas
            with dpg.table(header_row=False, borders_innerH=False, borders_outerH=False,
                          borders_innerV=False, borders_outerV=False, height=800):
                # Columna izquierda (espacio), central (botones), derecha (espacio)
                # Ancho window: 500px - márgenes ≈ 460px disponible
                dpg.add_table_column(width_fixed=True, init_width_or_weight=130)  # ~28% izquierda
                dpg.add_table_column(width_fixed=True, init_width_or_weight=200)  # ~44% centro para botones
                dpg.add_table_column(width_fixed=True, init_width_or_weight=130)  # ~28% derecha
                
                with dpg.table_row():
                    dpg.add_text("")  # Celda izquierda vacía
                    # Celda central con botones
                    with dpg.group(horizontal=True):
                        btn_aceptar = dpg.add_button(label="Aceptar", tag="btn_aceptar_producto", 
                                      callback=self._procesar_producto_modal)
                        dpg.bind_item_theme(btn_aceptar, "theme_boton_verde")
                        dpg.add_spacer(width=10)  # Espacio entre botones
                        btn_cancelar = dpg.add_button(label="Cancelar", tag="btn_cancelar_producto", callback=lambda: dpg.hide_item("ventana_producto"))
                        dpg.bind_item_theme(btn_cancelar, "theme_boton_rojo")
                    dpg.add_text("")  # Celda derecha vacía
    
    def _abrir_ventana_producto(self, modo, producto_codigo=None):
        """Abrir ventana para agregar o editar producto"""
        import dearpygui.dearpygui as dpg
        
        # Configurar según el modo
        if modo == "agregar":
            dpg.set_value("titulo_ventana_producto", "Agregar Producto")
            self._limpiar_formulario_modal()
            dpg.set_item_user_data("btn_aceptar_producto", {"modo": "agregar", "codigo": None})
            
        elif modo == "editar" and producto_codigo:
            dpg.set_value("titulo_ventana_producto", "Editar Producto")
            # Cargar datos ANTES de actualizar combos para evitar que se sobrescriban
            self._cargar_datos_producto_modal(producto_codigo)
            dpg.set_item_user_data("btn_aceptar_producto", {"modo": "editar", "codigo": producto_codigo})
        
        # Actualizar combos DESPUÉS de cargar datos (para modo agregar) o DESPUÉS de cargar datos (para modo editar)
        self._actualizar_combos_modal()
        
        # Mostrar ventana
        dpg.show_item("ventana_producto")
    
    def _procesar_producto_modal(self, sender=None, app_data=None):
        """Procesar el formulario según el modo (agregar/editar)"""
        import dearpygui.dearpygui as dpg
        
        try:
            # Obtener datos del usuario del botón
            user_data = dpg.get_item_user_data("btn_aceptar_producto")
            if not user_data:
                dpg.set_value("modal_status_producto", "✗ Error: No se pudo obtener datos del formulario")
                return
                
            modo = user_data.get("modo")
            codigo_original = user_data.get("codigo")
            
            # Obtener valores del formulario
            codigo = dpg.get_value("modal_codigo_producto")
            nombre = dpg.get_value("modal_nombre_producto")
            descripcion = dpg.get_value("modal_descripcion_producto")
            categoria = dpg.get_value("modal_combo_categoria")
            proveedor = dpg.get_value("modal_combo_proveedor")
            precio_compra = dpg.get_value("modal_precio_compra_producto") or 0.0
            precio_venta = dpg.get_value("modal_precio_venta_producto") or 0.0
            stock = dpg.get_value("modal_stock_producto") or 0
            stock_min = dpg.get_value("modal_stock_minimo") or 0
            ubicacion = dpg.get_value("modal_ubicacion_producto") or ""
            imagen = dpg.get_value("modal_imagen_producto") or ""
            
            # Obtener IDs de categoria y proveedor
            categoria_id = self._obtener_id_categoria(categoria)
            proveedor_id = self._obtener_id_proveedor(proveedor)
            
            success = False
            mensaje = ""
            
            if modo == "agregar":
                success = self.agregar_producto(
                    codigo_barras=codigo,
                    nombre=nombre,
                    descripcion=descripcion,
                    categoria_id=categoria_id,
                    proveedor_id=proveedor_id,
                    stock_actual=stock,
                    stock_minimo=stock_min,
                    precio_compra=precio_compra,
                    precio_venta=precio_venta,
                    imagen_producto=imagen
                )
                mensaje = "Producto agregado exitosamente" if success else "Error al agregar producto"
                
            elif modo == "editar":
                success = self._actualizar_producto_datos(
                    codigo_original, codigo, nombre, descripcion,
                    categoria_id, proveedor_id, stock, stock_min, precio_compra, precio_venta, ubicacion, imagen
                )
                mensaje = "Producto actualizado exitosamente" if success else "Error al actualizar producto"
            else:
                mensaje = "Modo no válido"
            
            if success:
                dpg.set_value("modal_status_producto", f"✓ {mensaje}")
                dpg.hide_item("ventana_producto")
                self.cargar_productos()  # Recargar tabla
            else:
                dpg.set_value("modal_status_producto", f"✗ {mensaje}")
                
        except Exception as e:
            dpg.set_value("modal_status_producto", f"✗ Error: {str(e)}")
            logger.error(f"❌ Error procesando producto modal: {e}")
    
    def _generar_pdf_productos(self, sender=None, app_data=None):
        """Generar PDF con la lista de productos"""
        try:
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.lib import colors
            from datetime import datetime
            
            # Obtener productos
            productos = self.obtener_todos_productos()
            
            # Crear documento PDF
            fecha = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"productos_reporte_{fecha}.pdf"
            doc = SimpleDocTemplate(filename, pagesize=A4)
            
            # Estilos
            styles = getSampleStyleSheet()
            elements = []
            
            # Título
            titulo = Paragraph("Reporte de Productos", styles['Title'])
            elements.append(titulo)
            elements.append(Spacer(1, 12))
            
            # Fecha
            fecha_str = datetime.now().strftime("%d/%m/%Y %H:%M")
            fecha_p = Paragraph(f"Generado: {fecha_str}", styles['Normal'])
            elements.append(fecha_p)
            elements.append(Spacer(1, 12))
            
            # Tabla de productos
            data = [['Código', 'Nombre', 'Categoría', 'Stock', 'Precio']]
            
            for producto in productos:
                data.append([
                    producto[0],  # codigo
                    producto[1],  # nombre
                    producto[3] or "Sin categoría",  # categoria
                    str(producto[6]),  # stock
                    f"${producto[9]:.2f}" if producto[9] else "$0.00"  # precio
                ])
            
            # Crear tabla
            tabla = Table(data)
            tabla.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elements.append(tabla)
            
            # Construir PDF
            doc.build(elements)
            
            print(f"✓ PDF generado: {filename}")
            
        except ImportError:
            print("❌ reportlab no está instalado. Instale con: pip install reportlab")
        except Exception as e:
            print(f"❌ Error generando PDF: {e}")
            logger.error(f"❌ Error generando PDF: {e}")
    
    def _generar_reporte_stock_bajo(self, sender=None, app_data=None):
        """Generar reporte PDF de productos con stock bajo"""
        try:
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.lib import colors
            from datetime import datetime
            
            # Obtener productos con stock bajo
            productos = self.obtener_productos_stock_bajo()
            
            if not productos:
                print("✓ No hay productos con stock bajo")
                return
            
            # Crear documento PDF
            fecha = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"stock_bajo_reporte_{fecha}.pdf"
            doc = SimpleDocTemplate(filename, pagesize=A4)
            
            # Estilos
            styles = getSampleStyleSheet()
            elements = []
            
            # Título
            titulo = Paragraph("Reporte de Stock Bajo", styles['Title'])
            elements.append(titulo)
            elements.append(Spacer(1, 12))
            
            # Fecha y resumen
            fecha_str = datetime.now().strftime("%d/%m/%Y %H:%M")
            fecha_p = Paragraph(f"Generado: {fecha_str}", styles['Normal'])
            elements.append(fecha_p)
            elements.append(Spacer(1, 6))
            
            resumen_p = Paragraph(f"Total de productos con stock bajo: {len(productos)}", styles['Normal'])
            elements.append(resumen_p)
            elements.append(Spacer(1, 12))
            
            # Tabla de productos con stock bajo
            data = [['Código', 'Nombre', 'Stock Actual', 'Stock Mínimo', 'Estado']]
            
            for producto in productos:
                stock_actual = producto[6]  # índice 6 para stock_actual
                stock_minimo = producto[7]  # índice 7 para stock_minimo
                estado = "CRÍTICO" if stock_actual == 0 else "BAJO"
                
                data.append([
                    producto[0],  # codigo
                    producto[1],  # nombre
                    str(stock_actual),  # stock_actual
                    str(stock_minimo),  # stock_minimo
                    estado  # estado
                ])
            
            # Crear tabla
            tabla = Table(data)
            tabla.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.red),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightcoral),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elements.append(tabla)
            
            # Construir PDF
            doc.build(elements)
            
            print(f"✓ PDF generado: {filename}")
            
        except ImportError:
            print("❌ reportlab no está instalado. Instale con: pip install reportlab")
        except Exception as e:
            print(f"❌ Error generando PDF de stock bajo: {e}")
            logger.error(f"❌ Error generando PDF de stock bajo: {e}")
    
    def _actualizar_combos_modal(self):
        """Actualizar los combos de la ventana modal"""
        import dearpygui.dearpygui as dpg
        
        try:
            # Actualizar categorías (preservar valor actual)
            categorias = self.execute_query(sql.SELECT_CATEGORIAS_NOMBRES)
            items_categorias = ["Sin categoria"] + [cat[0] for cat in categorias]
            if dpg.does_item_exist("modal_combo_categoria"):
                valor_actual_categoria = dpg.get_value("modal_combo_categoria")
                dpg.configure_item("modal_combo_categoria", items=items_categorias)
                # Solo restaurar el valor si existe en las nuevas opciones
                if valor_actual_categoria in items_categorias:
                    dpg.set_value("modal_combo_categoria", valor_actual_categoria)
                else:
                    dpg.set_value("modal_combo_categoria", "Sin categoria")
            
            # Actualizar proveedores (preservar valor actual)
            proveedores = self.execute_query(sql.SELECT_PROVEEDORES_NOMBRES)
            items_proveedores = ["Sin proveedor"] + [prov[0] for prov in proveedores]
            if dpg.does_item_exist("modal_combo_proveedor"):
                valor_actual_proveedor = dpg.get_value("modal_combo_proveedor")
                dpg.configure_item("modal_combo_proveedor", items=items_proveedores)
                # Solo restaurar el valor si existe en las nuevas opciones
                if valor_actual_proveedor in items_proveedores:
                    dpg.set_value("modal_combo_proveedor", valor_actual_proveedor)
                else:
                    dpg.set_value("modal_combo_proveedor", "Sin proveedor")
                
        except Exception as e:
            logger.error(f"❌ Error actualizando combos modal: {e}")
    
    def _limpiar_formulario_modal(self):
        """Limpiar el formulario modal"""
        import dearpygui.dearpygui as dpg
        
        dpg.set_value("modal_codigo_producto", "")
        dpg.set_value("modal_nombre_producto", "")
        dpg.set_value("modal_descripcion_producto", "")
        dpg.set_value("modal_combo_categoria", "Sin categoria")
        dpg.set_value("modal_combo_proveedor", "Sin proveedor")
        dpg.set_value("modal_precio_compra_producto", 0.0)
        dpg.set_value("modal_precio_venta_producto", 0.0)
        dpg.set_value("modal_stock_producto", 0)
        dpg.set_value("modal_stock_minimo", 0)
        dpg.set_value("modal_ubicacion_producto", "")
        dpg.set_value("modal_imagen_producto", "")
        dpg.set_value("modal_status_producto", "")
    
    def _cargar_datos_producto_modal(self, codigo_barras):
        """Cargar datos de un producto en el formulario modal"""
        import dearpygui.dearpygui as dpg

        try:
            # Obtener producto usando la query específica que devuelve datos básicos (no la vista)
            resultado = self.execute_query(sql.SELECT_PRODUCTO_BY_CODIGO, (codigo_barras,))
            if not resultado:
                dpg.set_value("modal_status_producto", "✗ Producto no encontrado")
                return
            
            producto = resultado[0]

            # Cargar datos en el formulario usando los índices correctos de la tabla productos
            dpg.set_value("modal_codigo_producto", producto[0])  # codigo_barras
            dpg.set_value("modal_nombre_producto", producto[1])  # nombre  
            dpg.set_value("modal_descripcion_producto", producto[2] or "")  # descripcion

            # Stock
            dpg.set_value("modal_stock_producto", producto[5])  # stock_actual
            dpg.set_value("modal_stock_minimo", producto[6])  # stock_minimo

            # Manejar precios de forma segura
            try:
                precio_compra = float(producto[7]) if producto[7] is not None else 0.0
                dpg.set_value("modal_precio_compra_producto", precio_compra)
            except (ValueError, TypeError):
                dpg.set_value("modal_precio_compra_producto", 0.0)

            try:
                precio_venta = float(producto[8]) if producto[8] is not None else 0.0
                dpg.set_value("modal_precio_venta_producto", precio_venta)
            except (ValueError, TypeError):
                dpg.set_value("modal_precio_venta_producto", 0.0)

            # Imagen y ubicación
            dpg.set_value("modal_imagen_producto", producto[10] or "")  # imagen_producto
            dpg.set_value("modal_ubicacion_producto", "")  # ubicacion no está en la tabla

            # Para categoría y proveedor, necesitamos obtener los nombres por ID
            categoria_nombre = "Sin categoria"
            if producto[3]:  # categoria_id
                try:
                    cat_result = self.execute_query("SELECT nombre FROM categorias WHERE id = ? AND deleted_at IS NULL", (producto[3],))
                    if cat_result:
                        categoria_nombre = cat_result[0][0]
                except Exception:
                    pass
            
            proveedor_nombre = "Sin proveedor"  
            if producto[4]:  # proveedor_id
                try:
                    prov_result = self.execute_query("SELECT nombre_razon_social FROM proveedores WHERE id = ? AND deleted_at IS NULL", (producto[4],))
                    if prov_result:
                        proveedor_nombre = prov_result[0][0]
                except Exception:
                    pass

            # Establecer valores de combo
            dpg.set_value("modal_combo_categoria", categoria_nombre)
            dpg.set_value("modal_combo_proveedor", proveedor_nombre)

        except Exception as e:
            logger.error(f"❌ Error cargando datos producto modal: {e}")
            dpg.set_value("modal_status_producto", f"✗ Error: {str(e)}")
    
    def _obtener_id_categoria(self, nombre_categoria):
        """Obtener ID de categoría por nombre"""
        if not nombre_categoria or nombre_categoria == "Sin categoria":
            return None
        
        try:
            categorias = self.execute_query(sql.SELECT_CATEGORIA_ID_BY_NOMBRE, (nombre_categoria,))
            return categorias[0][0] if categorias else None
        except Exception:
            return None
    
    def _obtener_id_proveedor(self, nombre_proveedor):
        """Obtener ID de proveedor por nombre"""
        if not nombre_proveedor or nombre_proveedor == "Sin proveedor":
            return None
        
        try:
            proveedores = self.execute_query(sql.SELECT_PROVEEDOR_ID_BY_NOMBRE, (nombre_proveedor,))
            return proveedores[0][0] if proveedores else None
        except Exception:
            return None
    
    def _actualizar_producto_datos(self, codigo_original, nuevo_codigo, nombre, descripcion, 
                                  categoria_id, proveedor_id, stock_actual, stock_min, precio_compra, precio_venta, ubicacion, imagen):
        """Actualizar datos de un producto existente"""
        try:
            # Parámetros incluyendo stock_actual
            params = (nuevo_codigo, nombre, descripcion, categoria_id, proveedor_id, 
                     stock_actual, stock_min, precio_compra, precio_venta, imagen, codigo_original)
            
            # Usar execute_command para operaciones UPDATE
            rows_affected = self.execute_command(sql.UPDATE_PRODUCTO_COMPLETO, params)
            
            if rows_affected > 0:
                # Llamar callback si existe
                if self.on_producto_updated:
                    self.on_producto_updated(codigo_original, nuevo_codigo)
                
                return True
            else:
                logger.warning(f"⚠️ No se actualizó ninguna fila para el producto {codigo_original}")
                return False
            
        except Exception as e:
            logger.error(f"❌ Error actualizando producto {codigo_original}: {e}")
            return False
    
    def _eliminar_producto_callback(self, codigo_barras):
        """Callback para eliminar producto desde la tabla con confirmación"""
        import dearpygui.dearpygui as dpg
        try:
            # Obtener datos del producto para confirmación
            producto = self.obtener_producto_por_codigo(codigo_barras)
            if not producto:
                logger.error(f"❌ No se encontró producto con código: {codigo_barras}")
                return

            if dpg.does_item_exist("modal_confirmar_eliminar_producto"):
                dpg.delete_item("modal_confirmar_eliminar_producto")

            with dpg.window(
                label="Confirmar Eliminación",
                tag="modal_confirmar_eliminar_producto",
                modal=True,
                width=400,
                height=200,
                pos=(400, 300)
            ):
                dpg.add_text("¿Está seguro de eliminar el producto?")
                dpg.add_text(f"Nombre: {producto[1]}", color=[255, 255, 0])  # producto[1] es el nombre
                dpg.add_text(f"Código: {codigo_barras}", color=[200, 200, 200])
                dpg.add_separator()
                dpg.add_text("Esta acción no se puede deshacer.", color=[255, 100, 100])

                with dpg.group(horizontal=True):
                    btn_eliminar = dpg.add_button(
                        label="Eliminar",
                        callback=lambda: self._confirmar_eliminar_producto(codigo_barras),
                        width=100
                    )
                    dpg.bind_item_theme(btn_eliminar, "theme_boton_rojo")
                    btn_cancelar_eliminar = dpg.add_button(
                        label="Cancelar",
                        callback=lambda: dpg.delete_item("modal_confirmar_eliminar_producto"),
                        width=100
                    )
                    dpg.bind_item_theme(btn_cancelar_eliminar, "theme_boton_gris")

        except Exception as e:
            logger.error(f"❌ Error en callback eliminar producto: {e}")

    def _confirmar_eliminar_producto(self, codigo_barras):
        """Confirmar y ejecutar la eliminación del producto."""
        import dearpygui.dearpygui as dpg
        try:
            resultado = self.eliminar_producto(codigo_barras)
            if resultado is True:
                dpg.delete_item("modal_confirmar_eliminar_producto")
                dpg.set_value("productos_status_msg", f"✓ Producto {codigo_barras} eliminado exitosamente")
                dpg.configure_item("productos_status_msg", color=(0,180,0))
                self.cargar_productos()  # Recargar tabla
            else:
                # resultado es string con el motivo
                dpg.set_value("productos_status_msg", f"✗ No se puede eliminar: {resultado}")
                dpg.configure_item("productos_status_msg", color=(255,0,0))
        except Exception as e:
            dpg.set_value("productos_status_msg", f"✗ Error: {str(e)}")
            dpg.configure_item("productos_status_msg", color=(255,0,0))
            logger.error(f"❌ Error eliminando producto {codigo_barras}: {e}")
    
    def _agregar_producto_callback(self, sender=None, app_data=None):
        """Callback para agregar producto desde la interfaz"""
        import dearpygui.dearpygui as dpg
        
        try:
            # Obtener valores de la interfaz
            codigo = dpg.get_value("input_codigo_producto")
            nombre = dpg.get_value("input_nombre_producto")
            descripcion = dpg.get_value("input_descripcion_producto")
            categoria = dpg.get_value("combo_categoria_producto")
            proveedor = dpg.get_value("combo_proveedor_producto")
            precio = float(dpg.get_value("input_precio_producto") or 0)
            stock = dpg.get_value("input_stock_producto") or 0
            stock_min = dpg.get_value("input_stock_minimo_producto") or 0
            ubicacion = dpg.get_value("input_ubicacion_producto")
            
            # Obtener IDs de categoria y proveedor
            # Obtener IDs usando las funciones auxiliares
            categoria_id = self._obtener_id_categoria(categoria)
            proveedor_id = self._obtener_id_proveedor(proveedor)
            
            # Agregar producto
            success = self.agregar_producto(
                codigo_barras=codigo,
                nombre=nombre,
                descripcion=descripcion,
                categoria_id=categoria_id,
                proveedor_id=proveedor_id,
                stock_actual=stock,
                stock_minimo=stock_min,
                precio_venta=precio
            )
            
            if success:
                dpg.set_value("status_productos", "✓ Producto agregado exitosamente")
                # Limpiar formulario
                self._limpiar_formulario_productos()
                # Recargar tabla
                self.cargar_productos()
            else:
                dpg.set_value("status_productos", "✗ Error al agregar producto")
                
        except Exception as e:
            dpg.set_value("status_productos", f"✗ Error: {str(e)}")
            logger.error(f"❌ Error en callback agregar producto: {e}")
    
    def _limpiar_formulario_productos(self):
        """Limpiar el formulario de productos"""
        import dearpygui.dearpygui as dpg
        
        dpg.set_value("input_codigo_producto", "")
        dpg.set_value("input_nombre_producto", "")
        dpg.set_value("input_descripcion_producto", "")
        dpg.set_value("input_precio_producto", "")
        dpg.set_value("input_stock_producto", 0)
        dpg.set_value("input_stock_minimo_producto", 0)
        dpg.set_value("input_ubicacion_producto", "")
    
    def _actualizar_combos_productos(self):
        """Actualizar los combos de categorías y proveedores"""
        import dearpygui.dearpygui as dpg
        
        try:
            # Actualizar categorías
            try:
                categorias = self.execute_query(sql.SELECT_CATEGORIAS_NOMBRES)
                if categorias is None:
                    categorias = []
                items_categorias = ["Sin categoria"] + [cat[0] for cat in categorias if cat and len(cat) > 0]
            except Exception as e:
                logger.warning(f"⚠️ Error obteniendo categorías: {e}")
                items_categorias = ["Sin categoria"]
                
            if dpg.does_item_exist("combo_categoria_producto"):
                try:
                    dpg.configure_item("combo_categoria_producto", items=items_categorias)
                except Exception as e:
                    logger.warning(f"⚠️ Error configurando combo categorías: {e}")
            
            # Actualizar proveedores
            try:
                proveedores = self.execute_query(sql.SELECT_PROVEEDORES_NOMBRES)
                if proveedores is None:
                    proveedores = []
                items_proveedores = ["Sin proveedor"] + [prov[0] for prov in proveedores if prov and len(prov) > 0]
            except Exception as e:
                logger.warning(f"⚠️ Error obteniendo proveedores: {e}")
                items_proveedores = ["Sin proveedor"]
                
            if dpg.does_item_exist("combo_proveedor_producto"):
                try:
                    dpg.configure_item("combo_proveedor_producto", items=items_proveedores)
                except Exception as e:
                    logger.warning(f"⚠️ Error configurando combo proveedores: {e}")
                
        except Exception as e:
            logger.error(f"❌ Error actualizando combos productos: {e}")
    
    def cargar_productos(self):
        """Cargar y mostrar productos en la tabla con botones de acción"""
        import dearpygui.dearpygui as dpg
        
        try:
            # Verificar si la tabla existe
            if not dpg.does_item_exist("tabla_productos"):
                logger.warning("⚠️ La tabla 'tabla_productos' no existe")
                return
                
            # Limpiar solo las filas de la tabla
            table_children = dpg.get_item_children("tabla_productos", slot=1)
            if table_children:
                for child in table_children:
                    try:
                        dpg.delete_item(child)
                    except:
                        pass  # Ignorar errores al eliminar
                
            # Obtener productos
            productos = self.obtener_todos_productos()
            
            # Agregar filas con botones
            for i, producto in enumerate(productos):
                codigo_barras = producto[0]
                
                with dpg.table_row(parent="tabla_productos"):
                    # Datos del producto
                    dpg.add_text(codigo_barras)
                    dpg.add_text(producto[1])  # nombre
                    dpg.add_text(producto[3] if producto[3] else "Sin categoria")
                    dpg.add_text(str(producto[6]))  # stock_actual
                    
                    # Manejar precio de forma segura
                    try:
                        precio = float(producto[9]) if producto[9] is not None else 0.0
                        dpg.add_text(f"${precio:.2f}")
                    except (ValueError, TypeError):
                        dpg.add_text("$0.00")  # Fallback si no se puede convertir
                    
                    # Botones de acción
                    with dpg.group(horizontal=True):
                        # Botón Editar
                        btn_editar = dpg.add_button(
                            label="Editar",
                            callback=lambda s, a, u: self._abrir_ventana_producto("editar", u),
                            user_data=codigo_barras,
                            width=60
                        )
                        dpg.bind_item_theme(btn_editar, "theme_boton_amarillo")
                        
                        # Botón Eliminar
                        btn_eliminar = dpg.add_button(
                            label="Eliminar",
                            callback=lambda s, a, u: self._eliminar_producto_callback(u),
                            user_data=codigo_barras,
                            width=60
                        )
                        dpg.bind_item_theme(btn_eliminar, "theme_boton_rojo")
                        
        except Exception as e:
            logger.error(f"❌ Error cargando productos: {e}")