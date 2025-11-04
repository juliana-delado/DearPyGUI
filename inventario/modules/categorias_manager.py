# categorias_manager.py - Gestor de categorías de productos
"""
CategoriasManager: Clase para manejar todas las operaciones CRUD de categorías.
Hereda de BaseModel para implementar soft delete y auditoría automática.
"""

import logging
from typing import List, Dict, Any, Optional, Tuple, Union
from .base_model import BaseModel
from . import sqlstatement as sql

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CategoriasManager(BaseModel):
    """Manager para gestión de categorías de productos"""
    
    def __init__(self, db_name: str = "inventario.db", app_instance=None):
        super().__init__(db_name)
        self.table_name = "categorias"
        self.primary_key = "id"
        self.app = app_instance  # Referencia a la aplicación principal
        
        # Callbacks para notificar cambios a otros módulos
        self.on_categoria_added = None
        self.on_categoria_updated = None
        self.on_categoria_deleted = None
    
    def _configurar_temas_botones(self):
        """Los temas ahora se configuran globalmente en UIManager"""
        # Los temas se configuran una sola vez en UIManager.configurar_temas_globales()
        pass
    
    def set_callbacks(self, on_categoria_added=None, on_categoria_updated=None, on_categoria_deleted=None):
        """Establecer funciones callback para notificar cambios"""
        self.on_categoria_added = on_categoria_added
        self.on_categoria_updated = on_categoria_updated
        self.on_categoria_deleted = on_categoria_deleted
    
    def agregar_categoria(self, nombre: str, descripcion: str = "", color_identificador: str = "#3498db") -> bool:
        """Agregar una nueva categoría"""
        try:
            # Validar datos
            if not self._validar_datos_categoria(nombre, descripcion, color_identificador):
                return False
            
            # Verificar que el nombre no existe
            if self._categoria_existe(nombre):
                logger.warning(f"⚠️ La categoría '{nombre}' ya existe")
                return False
            
            # Insertar nueva categoría
            rows_affected = self.execute_command(
                sql.INSERT_CATEGORIA,
                (nombre.strip(), descripcion.strip(), color_identificador)
            )
            
            if rows_affected > 0:
                if self.on_categoria_added:
                    self.on_categoria_added()
                
                return True
            else:
                logger.error(f"❌ No se pudo agregar la categoría '{nombre}'")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error agregando categoría: {e}")
            return False
    
    def obtener_todas_categorias(self) -> List[Tuple]:
        """Obtener todas las categorías activas"""
        try:
            categorias = self.execute_query(sql.SELECT_ALL_CATEGORIAS_ACTIVAS)
            if categorias:
                logger.debug(f"Primera categoría: {categorias[0]}")
            return categorias
        except Exception as e:
            logger.error(f"❌ Error obteniendo categorías: {e}")
            return []
    
    def obtener_categoria_por_id(self, categoria_id: int) -> Optional[Tuple]:
        """Obtener una categoría específica por su ID"""
        try:
            resultado = self.execute_query(sql.SELECT_CATEGORIA_BY_ID, (categoria_id,))
            if resultado:
                return resultado[0]
            else:
                logger.warning(f"⚠️ Categoría {categoria_id} no encontrada")
                return None
        except Exception as e:
            logger.error(f"❌ Error obteniendo categoría {categoria_id}: {e}")
            return None
    
    def actualizar_categoria(self, categoria_id: int, nombre: str, descripcion: str = "", 
                           color_identificador: str = "#3498db") -> bool:
        """Actualizar una categoría existente"""
        try:
            # Validar que la categoría existe
            categoria_actual = self.obtener_categoria_por_id(categoria_id)
            if not categoria_actual:
                logger.warning(f"⚠️ Categoría {categoria_id} no encontrada")
                return False
            
            # Validar datos
            if not self._validar_datos_categoria(nombre, descripcion, color_identificador):
                return False
            
            # Verificar que el nombre no esté en uso por otra categoría
            if self._categoria_existe(nombre, categoria_id):
                logger.warning(f"⚠️ La categoría '{nombre}' ya existe")
                return False
            
            # Actualizar categoría
            rows_affected = self.execute_command(
                sql.UPDATE_CATEGORIA,
                (nombre.strip(), descripcion.strip(), color_identificador, categoria_id)
            )
            
            if rows_affected > 0:
                logger.info(f"✅ Categoría {categoria_id} actualizada exitosamente")
                
                if self.on_categoria_updated:
                    self.on_categoria_updated()
                
                return True
            else:
                logger.error(f"❌ No se pudo actualizar la categoría {categoria_id}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error actualizando categoría {categoria_id}: {e}")
            return False

    def buscar_categorias(self, termino_busqueda: str) -> List[Tuple]:
        """Buscar categorías por nombre o descripción"""
        try:
            if not termino_busqueda.strip():
                return self.obtener_todas_categorias()
            
            termino = f"%{termino_busqueda.strip()}%"
            resultados = self.execute_query(sql.SELECT_BUSCAR_CATEGORIAS, (termino, termino))
            
            logger.info(f"🔍 Búsqueda '{termino_busqueda}': {len(resultados)} categorías encontradas")
            return resultados
            
        except Exception as e:
            logger.error(f"❌ Error buscando categorías: {e}")
            return []

    def eliminar_categoria(self, categoria_id: int) -> 'Union[bool, str]':
        """Eliminar categoría (soft delete). Devuelve True si elimina, o string con el motivo si no."""
        try:
            categoria = self.obtener_categoria_por_id(categoria_id)
            if not categoria:
                return "Categoría no encontrada"
            
            if not self._validate_before_delete(categoria_id):
                # Verificar si tiene productos asociados
                result = self.execute_query(sql.SELECT_PRODUCTOS_POR_CATEGORIA, (categoria_id,))
                productos_asociados = result[0][0] if result else 0
                if productos_asociados > 0:
                    return f"tiene {productos_asociados} productos asociados"
                return "no se puede eliminar"
            
            rows_affected = self.execute_command(sql.SOFT_DELETE_CATEGORIA, (categoria_id,))
            if rows_affected > 0:
                if self.on_categoria_deleted:
                    self.on_categoria_deleted()
                return True
            else:
                return "No se pudo eliminar la categoría"
        except Exception as e:
            return f"Error eliminando categoría: {e}"

    def _validate_before_delete(self, record_id: Union[str, int]) -> bool:
        """Validar que una categoría puede ser eliminada"""
        try:
            # Verificar si tiene productos asociados
            result = self.execute_query(sql.SELECT_PRODUCTOS_POR_CATEGORIA, (record_id,))
            productos_asociados = result[0][0] if result else 0
            return productos_asociados == 0
        except Exception as e:
            return False

    def _validar_datos_categoria(self, nombre: str, descripcion: str, color_identificador: str) -> bool:
        """Validar los datos de entrada para una categoría"""
        # Validar nombre
        if not nombre or not nombre.strip():
            logger.error("❌ El nombre de la categoría es obligatorio")
            return False
        
        if len(nombre.strip()) > 100:
            logger.error("❌ El nombre no puede exceder 100 caracteres")
            return False
        
        # Validar descripción
        if len(descripcion) > 500:
            logger.error("❌ La descripción no puede exceder 500 caracteres")
            return False
        
        # Validar color
        if not color_identificador or not color_identificador.strip():
            logger.error("❌ El color identificador es obligatorio")
            return False
        
        return True

    def _categoria_existe(self, nombre: str, excluir_id: Optional[int] = None) -> bool:
        """Verificar si una categoría con el mismo nombre ya existe"""
        try:
            if excluir_id:
                query = "SELECT COUNT(*) FROM categorias WHERE nombre = ? AND id != ? AND deleted_at IS NULL"
                params = (nombre.strip(), excluir_id)
            else:
                query = "SELECT COUNT(*) FROM categorias WHERE nombre = ? AND deleted_at IS NULL"
                params = (nombre.strip(),)
            
            resultado = self.execute_query(query, params)
            return resultado[0][0] > 0 if resultado else False
        except Exception:
            return False

    # ================================
    # INTERFAZ DE USUARIO
    # ================================
    
    def crear_interfaz_categorias(self, parent_tab):
        """Crear la interfaz simplificada de categorías con tabla y ventana modal"""
        import dearpygui.dearpygui as dpg
        
        # Configurar temas para botones (solo una vez)
        self._configurar_temas_botones()
        
        # Título y botones principales
        with dpg.group(horizontal=True, parent=parent_tab):
            dpg.add_text("Gestion de Categorias", color=(0, 255, 0))
            dpg.add_spacer(width=50)
            btn_agregar = dpg.add_button(label="Agregar Categoria", callback=lambda: self._abrir_ventana_categoria("agregar"))
            dpg.bind_item_theme(btn_agregar, "theme_boton_verde")
            btn_imprimir = dpg.add_button(label="Imprimir PDF", callback=self._generar_pdf_categorias)
            dpg.bind_item_theme(btn_imprimir, "theme_boton_blanco")
        
        dpg.add_separator(parent=parent_tab)

        # Tabla de categorías (con altura fija para dejar espacio al mensaje)
        with dpg.table(tag="tabla_categorias", header_row=True,
                     borders_innerH=True, borders_outerH=True,
                     borders_innerV=True, borders_outerV=True,
                     parent=parent_tab, height=400) as tabla_categorias:
            dpg.add_table_column(label="ID", width_fixed=True, init_width_or_weight=80)
            dpg.add_table_column(label="Nombre", width_fixed=True, init_width_or_weight=200)
            dpg.add_table_column(label="Descripcion", width_fixed=True, init_width_or_weight=250)
            dpg.add_table_column(label="Color", width_fixed=True, init_width_or_weight=100)
            dpg.add_table_column(label="Acciones", width_fixed=True, init_width_or_weight=160)

        # Campo de mensajes inferior para feedback de usuario (errores, info)
        dpg.add_spacer(height=10, parent=parent_tab)
        dpg.add_text("", tag="categorias_status_msg", color=(255,0,0), parent=parent_tab)

        # Crear la ventana modal para agregar/editar categorías
        self._crear_ventana_categoria()

    def _crear_ventana_categoria(self):
        """Crear ventana modal para agregar/editar categorías"""
        import dearpygui.dearpygui as dpg
        
        with dpg.window(label="Categoria", tag="ventana_categoria", modal=True, show=False,
                       width=400, height=400, pos=(250, 100)) as ventana:
            
            # Título dinámico
            dpg.add_text("Agregar Categoria", tag="titulo_ventana_categoria", color=(0, 255, 0))
            dpg.add_separator()
            
            # Formulario
            with dpg.group() as grupo_formulario:
                with dpg.group(horizontal=True):
                    dpg.add_text("Nombre")
                    dpg.add_input_text(tag="modal_nombre_categoria", width=300)
                with dpg.group(horizontal=True):
                    dpg.add_text("Descripcion")
                    dpg.add_input_text(tag="modal_descripcion_categoria",
                                  multiline=True, height=80, width=300)
                with dpg.group(horizontal=True):
                    dpg.add_text("Color")
                    dpg.add_color_picker(tag="modal_color_categoria", width=200, height=150,
                                   no_alpha=True, picker_mode=dpg.mvColorPicker_wheel, no_inputs=True, no_small_preview=True)
            
            dpg.add_separator()
            
            # Estado y mensaje
            dpg.add_text("", tag="modal_status_categoria", color=(255, 255, 0))
            
            # Botones
            with dpg.group(horizontal=True):
                btn_aceptar = dpg.add_button(label="Aceptar", tag="btn_aceptar_categoria", 
                              callback=self._procesar_categoria_modal)
                dpg.bind_item_theme(btn_aceptar, "theme_boton_verde")
                btn_cancelar = dpg.add_button(label="Cancelar", tag="btn_cancelar_categoria", callback=lambda: dpg.hide_item("ventana_categoria"))
                dpg.bind_item_theme(btn_cancelar, "theme_boton_rojo")

    def _abrir_ventana_categoria(self, modo, categoria_id=None):
        """Abrir ventana para agregar o editar categoría"""
        import dearpygui.dearpygui as dpg
        
        # Configurar según el modo
        if modo == "agregar":
            dpg.set_value("titulo_ventana_categoria", "Agregar Categoria")
            self._limpiar_formulario_modal()
            dpg.set_item_user_data("btn_aceptar_categoria", {"modo": "agregar", "id": None})
            
        elif modo == "editar" and categoria_id:
            dpg.set_value("titulo_ventana_categoria", "Editar Categoria")
            self._cargar_datos_categoria_modal(categoria_id)
            dpg.set_item_user_data("btn_aceptar_categoria", {"modo": "editar", "id": categoria_id})
        
        # Mostrar ventana
        dpg.show_item("ventana_categoria")

    def _procesar_categoria_modal(self, sender=None, app_data=None):
        """Procesar el formulario según el modo (agregar/editar)"""
        import dearpygui.dearpygui as dpg
        
        try:
            # Obtener datos del usuario del botón
            user_data = dpg.get_item_user_data("btn_aceptar_categoria")
            if not user_data:
                dpg.set_value("modal_status_categoria", "✗ Error: No se pudo obtener datos del formulario")
                return
                
            modo = user_data.get("modo")
            categoria_id_original = user_data.get("id")
            
            # Obtener valores del formulario
            nombre = dpg.get_value("modal_nombre_categoria")
            descripcion = dpg.get_value("modal_descripcion_categoria")
            color_rgb = dpg.get_value("modal_color_categoria")
            
            # Convertir color RGB a hex
            color_hex = f"#{int(color_rgb[0]):02x}{int(color_rgb[1]):02x}{int(color_rgb[2]):02x}"
            # color_hex = f"#{int(color_rgb[0]*255):02x}{int(color_rgb[1]*255):02x}{int(color_rgb[2]*255):02x}"
            logger.info(f"Color seleccionado RGB: {color_rgb}  // {color_hex}")
            
            success = False
            mensaje = ""
            
            if modo == "agregar":
                success = self.agregar_categoria(nombre, descripcion, color_hex)
                mensaje = "Categoría agregada exitosamente" if success else "Error al agregar categoría"
                
            elif modo == "editar":
                success = self.actualizar_categoria(categoria_id_original, nombre, descripcion, color_hex)
                mensaje = "Categoría actualizada exitosamente" if success else "Error al actualizar categoría"
            else:
                mensaje = "Modo no válido"
            
            if success:
                dpg.set_value("modal_status_categoria", f"✓ {mensaje}")
                dpg.hide_item("ventana_categoria")
                self.cargar_categorias()  # Recargar tabla
            else:
                dpg.set_value("modal_status_categoria", f"✗ {mensaje}")
                
        except Exception as e:
            dpg.set_value("modal_status_categoria", f"✗ Error: {str(e)}")
            logger.error(f"❌ Error procesando categoría modal: {e}")

    def _limpiar_formulario_modal(self):
        """Limpiar el formulario modal"""
        import dearpygui.dearpygui as dpg
        
        dpg.set_value("modal_nombre_categoria", "")
        dpg.set_value("modal_descripcion_categoria", "")
        dpg.set_value("modal_color_categoria", [0, 0, 0, 1.0])  # Color negro por defecto
        dpg.set_value("modal_status_categoria", "")

    def _cargar_datos_categoria_modal(self, categoria_id):
        """Cargar datos de una categoría en el formulario modal"""
        import dearpygui.dearpygui as dpg

        try:
            categoria = self.obtener_categoria_por_id(categoria_id)
            if not categoria:
                dpg.set_value("modal_status_categoria", "✗ Categoría no encontrada")
                return

            # Cargar datos en el formulario
            dpg.set_value("modal_nombre_categoria", categoria[1])  # nombre
            dpg.set_value("modal_descripcion_categoria", categoria[2] or "")  # descripcion

            # Convertir color hex a RGB y cargar en el picker con delay
            color_hex = categoria[3]
            logger.info(f"Cargando color {color_hex} en el picker {color_hex.startswith('#') and len(color_hex) == 7}")
            dpg.set_value("modal_color_categoria", [0, 0, 0, 1.0])
            if color_hex.startswith("#") and len(color_hex) == 7:
                try:
                    r = round(int(color_hex[1:3], 16) / 255.0 ,2)
                    g = round(int(color_hex[3:5], 16) / 255.0 ,2)
                    b = round(int(color_hex[5:7], 16) / 255.0 ,2)
                    color_rgb = [r, g, b, 1.0]
                    
                    dpg.set_value("modal_color_categoria", color_rgb)
                    dpg.set_value("modal_status_categoria", f"Color: {color_rgb}")
                    # Usar un callback diferido para asegurar que se cargue
                    def set_color():
                        dpg.set_value("modal_color_categoria", color_rgb)
                        # Forzar actualización del color picker
                        dpg.configure_item("modal_color_categoria", default_value=color_rgb)

                    # Ejecutar en el siguiente frame
                    dpg.set_frame_callback(2, set_color)
                    logger.info(f"Cargando despues del set color {color_rgb} en el picker")

                except ValueError:
                    dpg.set_value("modal_color_categoria", [0, 0, 0, 1.0])  # Default
            else:
                dpg.set_value("modal_color_categoria", [0, 0, 0, 1.0])

        except Exception as e:
            logger.error(f"❌ Error cargando datos categoría modal: {e}")
            dpg.set_value("modal_status_categoria", f"✗ Error: {str(e)}")

    def _eliminar_categoria_callback(self, categoria_id):
        """Callback para eliminar categoría desde la tabla con confirmación"""
        import dearpygui.dearpygui as dpg
        try:
            # Obtener datos de la categoría para confirmación
            categoria = self.obtener_categoria_por_id(categoria_id)
            if not categoria:
                logger.error(f"❌ No se encontró categoría con ID: {categoria_id}")
                return

            if dpg.does_item_exist("modal_confirmar_eliminar_categoria"):
                dpg.delete_item("modal_confirmar_eliminar_categoria")

            with dpg.window(
                label="Confirmar Eliminación",
                tag="modal_confirmar_eliminar_categoria",
                modal=True,
                width=400,
                height=200,
                pos=(400, 300)
            ):
                dpg.add_text("¿Está seguro de eliminar la categoría?")
                dpg.add_text(f"Nombre: {categoria[1]}", color=[255, 255, 0])  # categoria[1] es el nombre
                dpg.add_separator()
                dpg.add_text("Esta acción no se puede deshacer.", color=[255, 100, 100])

                with dpg.group(horizontal=True):
                    btn_eliminar = dpg.add_button(
                        label="Eliminar",
                        callback=lambda: self._confirmar_eliminar_categoria(categoria_id),
                        width=100
                    )
                    dpg.bind_item_theme(btn_eliminar, "theme_boton_rojo")
                    btn_cancelar_eliminar = dpg.add_button(
                        label="Cancelar",
                        callback=lambda: dpg.delete_item("modal_confirmar_eliminar_categoria"),
                        width=100
                    )
                    dpg.bind_item_theme(btn_cancelar_eliminar, "theme_boton_gris")

        except Exception as e:
            logger.error(f"❌ Error en callback eliminar categoría: {e}")

    def _confirmar_eliminar_categoria(self, categoria_id):
        """Confirmar y ejecutar la eliminación de la categoría."""
        import dearpygui.dearpygui as dpg
        try:
            resultado = self.eliminar_categoria(categoria_id)
            if resultado is True:
                dpg.delete_item("modal_confirmar_eliminar_categoria")
                dpg.set_value("categorias_status_msg", f"✓ Categoría {categoria_id} eliminada exitosamente")
                dpg.configure_item("categorias_status_msg", color=(0,180,0))
                self.cargar_categorias()  # Recargar tabla
            else:
                # resultado es string con el motivo
                dpg.set_value("categorias_status_msg", f"✗ No se puede eliminar: {resultado}")
                dpg.configure_item("categorias_status_msg", color=(255,0,0))
        except Exception as e:
            dpg.set_value("categorias_status_msg", f"✗ Error: {str(e)}")
            dpg.configure_item("categorias_status_msg", color=(255,0,0))
            logger.error(f"❌ Error eliminando categoría {categoria_id}: {e}")

    def _hex_to_rgba(self, hex_color):
        """Convierte color hexadecimal a tupla RGBA para DearPyGUI"""
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 6:
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4)) + (255,)
        return (0, 0, 0, 255)  # Color por defecto negro

    def cargar_categorias(self):
        """Cargar y mostrar categorías en la tabla con botones de acción"""
        import dearpygui.dearpygui as dpg
        
        try:
            # Verificar si la tabla existe
            if not dpg.does_item_exist("tabla_categorias"):
                return
                
            # Limpiar solo las filas de la tabla (slot 1 = filas, slot 0 = headers)
            try:
                table_children = dpg.get_item_children("tabla_categorias", slot=1)
                if table_children:
                    for child in table_children:
                        try:
                            dpg.delete_item(child)
                        except Exception as e:
                            logger.debug(f"No se pudo eliminar item {child}: {e}")
            except Exception as e:
                logger.debug(f"Error limpiando tabla: {e}")
                
            # Obtener categorías
            categorias = self.obtener_todas_categorias()
            
            if not categorias:
                logger.warning("⚠️ No se encontraron categorías para mostrar")
                return
            
            # Agregar filas con botones
            for i, categoria in enumerate(categorias):
                try:
                    categoria_id = categoria[0]
                    
                    with dpg.table_row(parent="tabla_categorias"):
                        # Datos de la categoría
                        dpg.add_text(str(categoria_id))  # ID
                        dpg.add_text(categoria[1])  # nombre
                        dpg.add_text(categoria[2] or "")  # descripcion
                        
                        # Color (mostrar código hex y colorear la celda)
                        color_hex = categoria[3] or "#3498db"
                        dpg.add_text(color_hex)
                        
                        # Botones de acción en un grupo horizontal
                        with dpg.group(horizontal=True):
                            # Crear botón editar con user_data
                            btn_editar = dpg.add_button(
                                label="Editar",
                                width=65,
                                user_data=categoria_id,
                                callback=lambda s, a: self._abrir_ventana_categoria("editar", dpg.get_item_user_data(s))
                            )
                            dpg.bind_item_theme(btn_editar, "theme_boton_amarillo")
                            
                            # Crear botón eliminar con user_data  
                            btn_eliminar = dpg.add_button(
                                label="Eliminar",
                                width=65,
                                user_data=categoria_id,
                                callback=lambda s, a: self._eliminar_categoria_callback(dpg.get_item_user_data(s))
                            )
                            dpg.bind_item_theme(btn_eliminar, "theme_boton_rojo")
                    
                    # Colorear la celda de color después de crear la fila
                    try:
                        rgba_color = self._hex_to_rgba(color_hex)
                        dpg.highlight_table_cell("tabla_categorias", i, 3, rgba_color)
                    except Exception as color_error:
                        logger.debug(f"No se pudo colorear celda {i},3: {color_error}")
                
                except Exception as e:
                    logger.error(f"❌ Error procesando categoría {i+1}: {e}")
                    continue
                        
        except Exception as e:
            logger.error(f"❌ Error cargando categorías: {e}")
    
    def _generar_pdf_categorias(self, sender=None, app_data=None):
        """Generar PDF con la lista de categorías"""
        try:
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.lib import colors
            from datetime import datetime
            
            # Obtener categorías
            categorias = self.obtener_todas_categorias()
            
            # Crear documento PDF
            fecha = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"categorias_reporte_{fecha}.pdf"
            doc = SimpleDocTemplate(filename, pagesize=A4)
            
            # Estilos
            styles = getSampleStyleSheet()
            elements = []
            
            # Título
            titulo = Paragraph("Reporte de Categorías", styles['Title'])
            elements.append(titulo)
            elements.append(Spacer(1, 12))
            
            # Fecha
            fecha_str = datetime.now().strftime("%d/%m/%Y %H:%M")
            fecha_p = Paragraph(f"Generado: {fecha_str}", styles['Normal'])
            elements.append(fecha_p)
            elements.append(Spacer(1, 12))
            
            # Tabla de categorías
            data = [['ID', 'Nombre', 'Descripción', 'Color']]
            
            for categoria in categorias:
                data.append([
                    str(categoria[0]),  # id
                    categoria[1],  # nombre
                    categoria[2] or "",  # descripcion
                    categoria[3] or ""  # color_identificador
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