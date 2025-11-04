"""
Gestor de Proveedores para el sistema de inventario.
"""

import logging
import dearpygui.dearpygui as dpg
from typing import Dict, List, Optional
from .sqlstatement import (
    INSERT_PROVEEDOR, UPDATE_PROVEEDOR, DELETE_PROVEEDOR,
    SELECT_ALL_PROVEEDORES_ACTIVOS, SELECT_PROVEEDOR_BY_ID,
    BUSCAR_PROVEEDORES, SELECT_PROVEEDOR_BY_NAME
)

# Configurar el logger
logger = logging.getLogger(__name__)


class ProveedoresManager:
    """Gestor de proveedores para la aplicación de inventario."""
    
    def __init__(self, db_name: str = "inventario.db", app_instance=None):
        """
        Inicializar el gestor de proveedores.
        
        Args:
            db_name: Nombre del archivo de base de datos
            app_instance: Referencia a la aplicación principal
        """
        from .database_manager import DatabaseManager
        self.db_manager = DatabaseManager(db_name)
        self.app = app_instance  # Referencia a la aplicación principal
        
        # Inicializar callbacks
        self.on_proveedore_added = None
        self.on_proveedore_updated = None
        self.on_proveedore_deleted = None
        self.on_stock_alert = None
    
    def _configurar_temas_botones(self):
        """Los temas ahora se configuran globalmente en UIManager"""
        # Los temas se configuran una sola vez en UIManager.configurar_temas_globales()
        pass
        
        logger.info("✅ ProveedoresManager inicializado correctamente")
        
    def set_callbacks(self, on_proveedore_added=None, on_proveedore_updated=None, on_proveedore_deleted=None, on_stock_alert=None):
        """
        Configurar callbacks para eventos de proveedores.
        
        Args:
            on_proveedore_added: Callback cuando se agrega un proveedor
            on_proveedore_updated: Callback cuando se actualiza un proveedor
            on_proveedore_deleted: Callback cuando se elimina un proveedor
            on_stock_alert: Callback para alertas de stock (no usado en proveedores)
        """
        self.on_proveedore_added = on_proveedore_added
        self.on_proveedore_updated = on_proveedore_updated
        self.on_proveedore_deleted = on_proveedore_deleted
        self.on_stock_alert = on_stock_alert
        
    def agregar_proveedor(self, nombre_razon_social: str, cuit_rut: str = "", 
                         direccion: str = "", telefono: str = "", email: str = "", 
                         contacto_responsable: str = "") -> bool:
        """
        Agregar un nuevo proveedor a la base de datos.
        
        Args:
            nombre_razon_social: Nombre o razón social del proveedor
            cuit_rut: CUIT o RUT del proveedor
            direccion: Dirección del proveedor
            telefono: Teléfono del proveedor
            email: Email del proveedor
            contacto_responsable: Persona de contacto
            
        Returns:
            bool: True si se agregó correctamente, False en caso contrario
        """
        try:
            # Validar datos obligatorios
            if not nombre_razon_social or not nombre_razon_social.strip():
                logger.error("❌ El nombre o razón social es obligatorio")
                return False
            
            # Verificar si ya existe un proveedor con el mismo nombre
            proveedor_existente = self.db_manager.execute_query(
                SELECT_PROVEEDOR_BY_NAME, (nombre_razon_social.strip(),)
            )
            
            if proveedor_existente:
                logger.error(f"❌ Ya existe un proveedor con el nombre: {nombre_razon_social}")
                return False
            
            # Insertar el nuevo proveedor
            params = (
                nombre_razon_social.strip(),
                cuit_rut.strip() if cuit_rut else "",
                direccion.strip() if direccion else "",
                telefono.strip() if telefono else "",
                email.strip() if email else "",
                contacto_responsable.strip() if contacto_responsable else ""
            )
            
            result = self.db_manager.execute_query(INSERT_PROVEEDOR, params)
            
            if result is not None:
                logger.info(f"✅ Proveedor agregado correctamente: {nombre_razon_social}")
                # Llamar callback si está configurado
                if hasattr(self, 'on_proveedore_added') and self.on_proveedore_added:
                    self.on_proveedore_added()
                return True
            else:
                logger.error("❌ Error al insertar el proveedor en la base de datos")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error agregando proveedor: {e}")
            return False
    
    def obtener_proveedor_por_id(self, proveedor_id: int) -> Optional[Dict]:
        """
        Obtener un proveedor por su ID.
        
        Args:
            proveedor_id: ID del proveedor
            
        Returns:
            Dict con los datos del proveedor o None si no existe
        """
        try:
            result = self.db_manager.execute_query(SELECT_PROVEEDOR_BY_ID, (proveedor_id,))
            
            if result and len(result) > 0:
                proveedor = result[0]
                return {
                    'id': proveedor[0],
                    'nombre_razon_social': proveedor[1],
                    'cuit_rut': proveedor[2] or "",
                    'direccion': proveedor[3] or "",
                    'telefono': proveedor[4] or "",
                    'email': proveedor[5] or "",
                    'contacto_responsable': proveedor[6] or "",
                    'created_at': proveedor[7],
                    'updated_at': proveedor[8]
                }
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo proveedor por ID {proveedor_id}: {e}")
            return None
    
    def obtener_todos_los_proveedores(self) -> List[Dict]:
        """
        Obtener todos los proveedores activos.
        
        Returns:
            Lista de diccionarios con los datos de los proveedores
        """
        try:
            results = self.db_manager.execute_query(SELECT_ALL_PROVEEDORES_ACTIVOS)
            
            if not results:
                return []
            
            proveedores = []
            for row in results:
                proveedor = {
                    'id': row[0],
                    'nombre_razon_social': row[1],
                    'cuit_rut': row[2] or "",
                    'direccion': row[3] or "",
                    'telefono': row[4] or "",
                    'email': row[5] or "",
                    'contacto_responsable': row[6] or "",
                    'created_at': row[7],
                    'updated_at': row[8]
                }
                proveedores.append(proveedor)
            
            return proveedores
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo todos los proveedores: {e}")
            return []
    
    def actualizar_proveedor(self, proveedor_id: int, nombre_razon_social: str, 
                           cuit_rut: str = "", direccion: str = "", telefono: str = "", 
                           email: str = "", contacto_responsable: str = "") -> bool:
        """
        Actualizar un proveedor existente.
        
        Args:
            proveedor_id: ID del proveedor a actualizar
            nombre_razon_social: Nuevo nombre o razón social
            cuit_rut: Nuevo CUIT o RUT
            direccion: Nueva dirección
            telefono: Nuevo teléfono
            email: Nuevo email
            contacto_responsable: Nueva persona de contacto
            
        Returns:
            bool: True si se actualizó correctamente, False en caso contrario
        """
        try:
            # Validar datos obligatorios
            if not nombre_razon_social or not nombre_razon_social.strip():
                logger.error("❌ El nombre o razón social es obligatorio")
                return False
            
            # Verificar que el proveedor existe
            proveedor_actual = self.obtener_proveedor_por_id(proveedor_id)
            if not proveedor_actual:
                logger.error(f"❌ No existe proveedor con ID: {proveedor_id}")
                return False
            
            # Verificar si ya existe otro proveedor con el mismo nombre
            proveedores_con_nombre = self.db_manager.execute_query(
                SELECT_PROVEEDOR_BY_NAME, (nombre_razon_social.strip(),)
            )
            
            if (proveedores_con_nombre and 
                len(proveedores_con_nombre) > 0 and 
                proveedores_con_nombre[0][0] != proveedor_id):
                logger.error(f"❌ Ya existe otro proveedor con el nombre: {nombre_razon_social}")
                return False
            
            # Actualizar el proveedor
            params = (
                nombre_razon_social.strip(),
                cuit_rut.strip() if cuit_rut else "",
                direccion.strip() if direccion else "",
                telefono.strip() if telefono else "",
                email.strip() if email else "",
                contacto_responsable.strip() if contacto_responsable else "",
                proveedor_id
            )
            
            result = self.db_manager.execute_query(UPDATE_PROVEEDOR, params)
            
            if result is not None:
                logger.info(f"✅ Proveedor actualizado correctamente: {nombre_razon_social}")
                # Llamar callback si está configurado
                if hasattr(self, 'on_proveedore_updated') and self.on_proveedore_updated:
                    self.on_proveedore_updated()
                return True
            else:
                logger.error("❌ Error al actualizar el proveedor en la base de datos")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error actualizando proveedor: {e}")
            return False
    
    def eliminar_proveedor(self, proveedor_id: int) -> bool:
        """
        Eliminar un proveedor (eliminación lógica).
        
        Args:
            proveedor_id: ID del proveedor a eliminar
            
        Returns:
            bool: True si se eliminó correctamente, False en caso contrario
        """
        try:
            # Verificar que el proveedor existe
            proveedor = self.obtener_proveedor_por_id(proveedor_id)
            if not proveedor:
                logger.error(f"❌ No existe proveedor con ID: {proveedor_id}")
                return False
            
            # Eliminar el proveedor (eliminación lógica)
            result = self.db_manager.execute_query(DELETE_PROVEEDOR, (proveedor_id,))
            
            if result is not None:
                logger.info(f"✅ Proveedor eliminado correctamente: {proveedor['nombre_razon_social']}")
                # Llamar callback si está configurado
                if hasattr(self, 'on_proveedore_deleted') and self.on_proveedore_deleted:
                    self.on_proveedore_deleted()
                return True
            else:
                logger.error("❌ Error al eliminar el proveedor de la base de datos")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error eliminando proveedor: {e}")
            return False
    
    def buscar_proveedores(self, termino_busqueda: str) -> List[Dict]:
        """
        Buscar proveedores por término de búsqueda.
        
        Args:
            termino_busqueda: Término a buscar
            
        Returns:
            Lista de diccionarios con los proveedores encontrados
        """
        try:
            if not termino_busqueda or not termino_busqueda.strip():
                return self.obtener_todos_los_proveedores()
            
            termino = f"%{termino_busqueda.strip()}%"
            results = self.db_manager.execute_query(BUSCAR_PROVEEDORES, (termino, termino, termino))
            
            if not results:
                return []
            
            proveedores = []
            for row in results:
                proveedor = {
                    'id': row[0],
                    'nombre_razon_social': row[1],
                    'cuit_rut': row[2] or "",
                    'direccion': row[3] or "",
                    'telefono': row[4] or "",
                    'email': row[5] or "",
                    'contacto_responsable': row[6] or "",
                    'created_at': row[7],
                    'updated_at': row[8]
                }
                proveedores.append(proveedor)
            
            return proveedores
            
        except Exception as e:
            logger.error(f"❌ Error buscando proveedores: {e}")
            return []
    
    # ==========================================
    # MÉTODOS DE INTERFAZ GRÁFICA
    # ==========================================
    
    def mostrar_ventana_proveedores(self):
        """Mostrar la ventana principal de gestión de proveedores."""
        try:
            # Cerrar ventana si ya existe
            if dpg.does_item_exist("ventana_proveedores"):
                dpg.delete_item("ventana_proveedores")
            
            with dpg.window(
                label="Gestión de Proveedores", 
                tag="ventana_proveedores",
                width=1000, 
                height=700,
                pos=(50, 50)
            ) as ventana_proveedores:
                with dpg.group(horizontal=True):
                    dpg.add_button(
                        label="Agregar Proveedor",
                        callback=self._mostrar_modal_agregar_proveedor,
                        width=150
                    )
                    dpg.add_button(
                        label="Actualizar Lista",
                        callback=self._actualizar_lista_proveedores,
                        width=150
                    )
                
                # Barra de búsqueda
                with dpg.group(horizontal=True):
                    dpg.add_text("Buscar:")
                    dpg.add_input_text(
                        tag="buscar_proveedor_input",
                        width=300,
                        callback=self._buscar_proveedores_callback
                    )
                    dpg.add_button(
                        label="Buscar",
                        callback=self._buscar_proveedores_callback,
                        width=80
                    )
                
                dpg.add_separator()
                
                # Mensaje de estado
                dpg.add_text("", tag="proveedores_status_msg")
                
                # Tabla de proveedores
                with dpg.table(
                    tag="tabla_proveedores",
                    header_row=True,
                    borders_innerH=True,
                    borders_outerH=True,
                    borders_innerV=True,
                    borders_outerV=True,
                    scrollY=True,
                    height=400
                ) as tabla_proveedores:
                    dpg.add_table_column(label="ID", width_fixed=True, init_width_or_weight=50)
                    dpg.add_table_column(label="Nombre/Razón Social", width_fixed=True, init_width_or_weight=200)
                    dpg.add_table_column(label="CUIT/RUT", width_fixed=True, init_width_or_weight=120)
                    dpg.add_table_column(label="Teléfono", width_fixed=True, init_width_or_weight=120)
                    dpg.add_table_column(label="Email", width_fixed=True, init_width_or_weight=150)
                    dpg.add_table_column(label="Contacto", width_fixed=True, init_width_or_weight=120)
                    dpg.add_table_column(label="Acciones", width_fixed=True, init_width_or_weight=140)
            
            # Cargar los datos iniciales
            self.cargar_proveedores()
            
        except Exception as e:
            logger.error(f"❌ Error mostrando ventana de proveedores: {e}")
    
    def _mostrar_modal_agregar_proveedor(self):
        """Mostrar modal para agregar un nuevo proveedor."""
        try:
            if dpg.does_item_exist("modal_agregar_proveedor"):
                dpg.delete_item("modal_agregar_proveedor")
            
            with dpg.window(
                label="Agregar Proveedor",
                tag="modal_agregar_proveedor",
                modal=True,
                width=500,
                height=400,
                pos=(300, 150)):
                
                dpg.add_text("Complete los datos del proveedor:")
                dpg.add_separator()
                
                # Campos del formulario
                dpg.add_text("Nombre/Razón Social: *")
                dpg.add_input_text(tag="nuevo_proveedor_nombre", width=-1)
                
                dpg.add_text("CUIT/RUT:")
                dpg.add_input_text(tag="nuevo_proveedor_cuit", width=-1)
                
                dpg.add_text("Dirección:")
                dpg.add_input_text(tag="nuevo_proveedor_direccion", width=-1)
                
                dpg.add_text("Teléfono:")
                dpg.add_input_text(tag="nuevo_proveedor_telefono", width=-1)
                
                dpg.add_text("Email:")
                dpg.add_input_text(tag="nuevo_proveedor_email", width=-1)
                
                dpg.add_text("Contacto Responsable:")
                dpg.add_input_text(tag="nuevo_proveedor_contacto", width=-1)
                
                dpg.add_separator()
                dpg.add_text("* Campos obligatorios", color=[255, 255, 0])
                
                # Botones
                with dpg.group(horizontal=True):
                    btn_guardar = dpg.add_button(
                        label="Guardar",
                        callback=self._guardar_nuevo_proveedor,
                        width=100
                    )
                    dpg.bind_item_theme(btn_guardar, "theme_boton_verde")
                    btn_cancelar = dpg.add_button(
                        label="Cancelar",
                        callback=lambda: dpg.delete_item("modal_agregar_proveedor"),
                        width=100
                    )
                    dpg.bind_item_theme(btn_cancelar, "theme_boton_rojo")
        
        except Exception as e:
            logger.error(f"❌ Error mostrando modal agregar proveedor: {e}")
    
    def _guardar_nuevo_proveedor(self):
        """Guardar un nuevo proveedor desde el modal."""
        try:
            # Obtener valores del formulario
            nombre = dpg.get_value("nuevo_proveedor_nombre") or ""
            cuit = dpg.get_value("nuevo_proveedor_cuit") or ""
            direccion = dpg.get_value("nuevo_proveedor_direccion") or ""
            telefono = dpg.get_value("nuevo_proveedor_telefono") or ""
            email = dpg.get_value("nuevo_proveedor_email") or ""
            contacto = dpg.get_value("nuevo_proveedor_contacto") or ""
            
            # Agregar el proveedor
            if self.agregar_proveedor(nombre, cuit, direccion, telefono, email, contacto):
                dpg.delete_item("modal_agregar_proveedor")
                self.cargar_proveedores()
                if dpg.does_item_exist("proveedores_status_msg"):
                    dpg.set_value("proveedores_status_msg", "✓ Proveedor agregado correctamente")
            else:
                if dpg.does_item_exist("proveedores_status_msg"):
                    dpg.set_value("proveedores_status_msg", "✗ Error al agregar proveedor")
        
        except Exception as e:
            logger.error(f"❌ Error guardando nuevo proveedor: {e}")
            if dpg.does_item_exist("proveedores_status_msg"):
                dpg.set_value("proveedores_status_msg", f"✗ Error: {str(e)}")
    
    def _callback_editar_proveedor(self, sender, app_data):
        """Callback para el botón editar proveedor."""
        proveedor_id = dpg.get_item_user_data(sender)
        
        if proveedor_id is None:
            logger.error("❌ Error: No se pudo obtener el ID del proveedor desde user_data")
            return
            
        self._mostrar_modal_editar_proveedor(proveedor_id)

    def _mostrar_modal_editar_proveedor(self, proveedor_id: int):
        """Mostrar modal para editar un proveedor existente."""
        try:
            # Obtener datos del proveedor
            proveedor = self.obtener_proveedor_por_id(proveedor_id)
            if not proveedor:
                logger.error(f"❌ No se encontró proveedor con ID: {proveedor_id}")
                return
            
            if dpg.does_item_exist("modal_editar_proveedor"):
                dpg.delete_item("modal_editar_proveedor")
            
            with dpg.window(
                label=f"Editar Proveedor - {proveedor['nombre_razon_social']}",
                tag="modal_editar_proveedor",
                modal=True,
                width=500,
                height=400,
                pos=(300, 150)):
                dpg.add_text("Modifique los datos del proveedor:")
                dpg.add_separator()
                
                # Campos del formulario con valores actuales
                dpg.add_text("Nombre/Razón Social: *")
                dpg.add_input_text(
                    tag="editar_proveedor_nombre",
                    default_value=proveedor['nombre_razon_social'],
                    width=-1
                )
                
                dpg.add_text("CUIT/RUT:")
                dpg.add_input_text(
                    tag="editar_proveedor_cuit",
                    default_value=proveedor['cuit_rut'],
                    width=-1
                )
                
                dpg.add_text("Dirección:")
                dpg.add_input_text(
                    tag="editar_proveedor_direccion",
                    default_value=proveedor['direccion'],
                    width=-1
                )
                
                dpg.add_text("Teléfono:")
                dpg.add_input_text(
                    tag="editar_proveedor_telefono",
                    default_value=proveedor['telefono'],
                    width=-1
                )
                
                dpg.add_text("Email:")
                dpg.add_input_text(
                    tag="editar_proveedor_email",
                    default_value=proveedor['email'],
                    width=-1
                )
                
                dpg.add_text("Contacto Responsable:")
                dpg.add_input_text(
                    tag="editar_proveedor_contacto",
                    default_value=proveedor['contacto_responsable'],
                    width=-1
                )
                
                dpg.add_separator()
                dpg.add_text("* Campos obligatorios", color=[255, 255, 0])
                
                # Botones
                with dpg.group(horizontal=True):
                    btn_actualizar = dpg.add_button(
                        label="Actualizar",
                        callback=lambda: self._actualizar_proveedor_modal(proveedor_id),
                        width=100
                    )
                    dpg.bind_item_theme(btn_actualizar, "theme_boton_verde")
                    btn_cancelar_editar = dpg.add_button(
                        label="Cancelar",
                        callback=lambda: dpg.delete_item("modal_editar_proveedor"),
                        width=100
                    )
                    dpg.bind_item_theme(btn_cancelar_editar, "theme_boton_rojo")
        
        except Exception as e:
            logger.error(f"❌ Error mostrando modal editar proveedor: {e}")
    
    def _actualizar_proveedor_modal(self, proveedor_id: int):
        """Actualizar un proveedor desde el modal de edición."""
        try:
            # Obtener valores del formulario
            nombre = dpg.get_value("editar_proveedor_nombre") or ""
            cuit = dpg.get_value("editar_proveedor_cuit") or ""
            direccion = dpg.get_value("editar_proveedor_direccion") or ""
            telefono = dpg.get_value("editar_proveedor_telefono") or ""
            email = dpg.get_value("editar_proveedor_email") or ""
            contacto = dpg.get_value("editar_proveedor_contacto") or ""
            
            # Actualizar el proveedor
            if self.actualizar_proveedor(proveedor_id, nombre, cuit, direccion, telefono, email, contacto):
                dpg.delete_item("modal_editar_proveedor")
                self.cargar_proveedores()
                if dpg.does_item_exist("proveedores_status_msg"):
                    dpg.set_value("proveedores_status_msg", "✓ Proveedor actualizado correctamente")
            else:
                if dpg.does_item_exist("proveedores_status_msg"):
                    dpg.set_value("proveedores_status_msg", "✗ Error al actualizar proveedor")
        
        except Exception as e:
            logger.error(f"❌ Error actualizando proveedor: {e}")
            if dpg.does_item_exist("proveedores_status_msg"):
                dpg.set_value("proveedores_status_msg", f"✗ Error: {str(e)}")
    
    def _callback_eliminar_proveedor(self, sender, app_data):
        """Callback para el botón eliminar proveedor."""
        proveedor_id = dpg.get_item_user_data(sender)
        
        if proveedor_id is None:
            logger.error("❌ Error: No se pudo obtener el ID del proveedor desde user_data")
            return
            
        self._eliminar_proveedor_callback(proveedor_id)

    def _eliminar_proveedor_callback(self, proveedor_id: int):
        """Callback para eliminar un proveedor con confirmación."""
        try:
            # Obtener datos del proveedor para confirmación
            proveedor = self.obtener_proveedor_por_id(proveedor_id)
            if not proveedor:
                logger.error(f"❌ No se encontró proveedor con ID: {proveedor_id}")
                return
            
            if dpg.does_item_exist("modal_confirmar_eliminar_proveedor"):
                dpg.delete_item("modal_confirmar_eliminar_proveedor")
            
            with dpg.window(
                label="Confirmar Eliminación",
                tag="modal_confirmar_eliminar_proveedor",
                modal=True,
                width=400,
                height=200,
                pos=(400, 300)
            ):
                dpg.add_text(f"¿Está seguro de eliminar el proveedor?")
                dpg.add_text(f"Nombre: {proveedor['nombre_razon_social']}", color=[255, 255, 0])
                dpg.add_separator()
                dpg.add_text("Esta acción no se puede deshacer.", color=[255, 100, 100])
                
                with dpg.group(horizontal=True):
                    btn_eliminar = dpg.add_button(
                        label="Eliminar",
                        callback=lambda: self._confirmar_eliminar_proveedor(proveedor_id),
                        width=100
                    )
                    dpg.bind_item_theme(btn_eliminar, "theme_boton_rojo")
                    btn_cancelar_eliminar = dpg.add_button(
                        label="Cancelar",
                        callback=lambda: dpg.delete_item("modal_confirmar_eliminar_proveedor"),
                        width=100
                    )
                    dpg.bind_item_theme(btn_cancelar_eliminar, "theme_boton_gris")
        
        except Exception as e:
            logger.error(f"❌ Error en callback eliminar proveedor: {e}")
    
    def _confirmar_eliminar_proveedor(self, proveedor_id: int):
        """Confirmar y ejecutar la eliminación del proveedor."""
        try:
            if self.eliminar_proveedor(proveedor_id):
                dpg.delete_item("modal_confirmar_eliminar_proveedor")
                self.cargar_proveedores()
                if dpg.does_item_exist("proveedores_status_msg"):
                    dpg.set_value("proveedores_status_msg", "✓ Proveedor eliminado correctamente")
            else:
                if dpg.does_item_exist("proveedores_status_msg"):
                    dpg.set_value("proveedores_status_msg", "✗ Error al eliminar proveedor")
        
        except Exception as e:
            logger.error(f"❌ Error confirmando eliminación: {e}")
            if dpg.does_item_exist("proveedores_status_msg"):
                dpg.set_value("proveedores_status_msg", f"✗ Error: {str(e)}")
    
    def _actualizar_lista_proveedores(self):
        """Actualizar la lista de proveedores."""
        self.cargar_proveedores()
        if dpg.does_item_exist("proveedores_status_msg"):
            dpg.set_value("proveedores_status_msg", "✓ Lista actualizada")
    
    def _buscar_proveedores_callback(self):
        """Callback para buscar proveedores."""
        try:
            termino = dpg.get_value("buscar_proveedor_input") or ""
            self._cargar_proveedores_filtrados(termino)
        
        except Exception as e:
            logger.error(f"❌ Error en búsqueda: {e}")
            if dpg.does_item_exist("proveedores_status_msg"):
                dpg.set_value("proveedores_status_msg", f"✗ Error en búsqueda: {str(e)}")
    
    def _cargar_proveedores_filtrados(self, termino_busqueda: str = ""):
        """Cargar proveedores filtrados por término de búsqueda."""
        try:
            # Limpiar tabla actual
            if dpg.does_item_exist("tabla_proveedores"):
                # Eliminar todas las filas existentes
                children = dpg.get_item_children("tabla_proveedores", slot=1)
                if children:
                    for child in children:
                        dpg.delete_item(child)
            
            # Obtener proveedores filtrados
            if termino_busqueda and termino_busqueda.strip():
                proveedores = self.buscar_proveedores(termino_busqueda)
            else:
                proveedores = self.obtener_todos_los_proveedores()
            
            # Agregar filas a la tabla
            if dpg.does_item_exist("tabla_proveedores"):
                for proveedor in proveedores:
                    proveedor_id = proveedor['id']
                    
                    with dpg.table_row(parent="tabla_proveedores"):
                        dpg.add_text(str(proveedor['id']))
                        dpg.add_text(proveedor['nombre_razon_social'])
                        dpg.add_text(proveedor['cuit_rut'])
                        dpg.add_text(proveedor['telefono'])
                        dpg.add_text(proveedor['email'])
                        dpg.add_text(proveedor['contacto_responsable'])
                        
                        # Botones de acción
                        with dpg.group(horizontal=True):
                            btn_editar_tag = f"btn_editar_prov_{proveedor_id}"
                            btn_eliminar_tag = f"btn_eliminar_prov_{proveedor_id}"
                            
                            btn_editar = dpg.add_button(
                                label="Editar", 
                                tag=btn_editar_tag,
                                callback=self._callback_editar_proveedor,
                                user_data=proveedor_id,
                                width=60
                            )
                            dpg.bind_item_theme(btn_editar, "theme_boton_amarillo")
                            btn_eliminar = dpg.add_button(
                                label="Eliminar", 
                                tag=btn_eliminar_tag,
                                callback=self._callback_eliminar_proveedor,
                                user_data=proveedor_id,
                                width=60
                            )
                            dpg.bind_item_theme(btn_eliminar, "theme_boton_rojo")
            
            if dpg.does_item_exist("proveedores_status_msg"):
                if termino_busqueda:
                    dpg.set_value("proveedores_status_msg", f"✓ Encontrados {len(proveedores)} proveedores")
                else:
                    dpg.set_value("proveedores_status_msg", f"✓ Mostrando {len(proveedores)} proveedores")
        
        except Exception as e:
            logger.error(f"❌ Error cargando proveedores filtrados: {e}")
            if dpg.does_item_exist("proveedores_status_msg"):
                dpg.set_value("proveedores_status_msg", f"✗ Error cargando proveedores: {str(e)}")
    
    def cargar_proveedores(self):
        """Cargar todos los proveedores en la tabla."""
        self._cargar_proveedores_filtrados("")
    
    def obtener_todos_proveedores(self) -> List[Dict]:
        """
        Alias para obtener_todos_los_proveedores para compatibilidad con main.py.
        
        Returns:
            Lista de diccionarios con los datos de los proveedores
        """
        return self.obtener_todos_los_proveedores()
    
    def crear_interfaz_proveedores(self, parent):
        """
        Crear la interfaz de proveedores dentro de un tab específico.
        
        Args:
            parent: El elemento padre donde crear la interfaz
        """
        try:
            # Configurar temas para botones (solo una vez)
            self._configurar_temas_botones()
            
            with dpg.group(parent=parent):
                # Botones de acción
                with dpg.group(horizontal=True):
                    btn_agregar = dpg.add_button(
                        label="Agregar Proveedor",
                        callback=self._mostrar_modal_agregar_proveedor,
                        width=150
                    )
                    dpg.bind_item_theme(btn_agregar, "theme_boton_verde")
                    dpg.add_button(
                        label="Actualizar Lista",
                        callback=self._actualizar_lista_proveedores,
                        width=150
                    )
                    btn_imprimir = dpg.add_button(
                        label="Imprimir PDF",
                        callback=self._generar_pdf_proveedores,
                        width=150
                    )
                    dpg.bind_item_theme(btn_imprimir, "theme_boton_blanco")
                
                # Barra de búsqueda
                with dpg.group(horizontal=True):
                    dpg.add_text("Buscar:")
                    dpg.add_input_text(
                        tag="buscar_proveedor_input",
                        width=300,
                        callback=self._buscar_proveedores_callback
                    )
                    dpg.add_button(
                        label="Buscar",
                        callback=self._buscar_proveedores_callback,
                        width=80
                    )
                
                dpg.add_separator()
                
                # Mensaje de estado
                dpg.add_text("", tag="proveedores_status_msg")
                
                # Tabla de proveedores
                with dpg.table(
                    tag="tabla_proveedores",
                    header_row=True,
                    borders_innerH=True,
                    borders_outerH=True,
                    borders_innerV=True,
                    borders_outerV=True,
                    scrollY=True,
                    height=400
                ):
                    dpg.add_table_column(label="ID", width_fixed=True, init_width_or_weight=50)
                    dpg.add_table_column(label="Nombre/Razón Social", width_fixed=True, init_width_or_weight=200)
                    dpg.add_table_column(label="CUIT/RUT", width_fixed=True, init_width_or_weight=120)
                    dpg.add_table_column(label="Teléfono", width_fixed=True, init_width_or_weight=120)
                    dpg.add_table_column(label="Email", width_fixed=True, init_width_or_weight=150)
                    dpg.add_table_column(label="Contacto", width_fixed=True, init_width_or_weight=120)
                    dpg.add_table_column(label="Acciones", width_fixed=True, init_width_or_weight=140)
            
            # Cargar los datos iniciales
            self.cargar_proveedores()
            
        except Exception as e:
            logger.error(f"❌ Error creando interfaz de proveedores: {e}")
    
    def _generar_pdf_proveedores(self, sender=None, app_data=None):
        """Generar PDF con la lista de proveedores"""
        try:
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.lib import colors
            from datetime import datetime
            
            # Obtener proveedores
            proveedores = self.obtener_todos_proveedores()
            
            # Crear documento PDF
            fecha = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"proveedores_reporte_{fecha}.pdf"
            doc = SimpleDocTemplate(filename, pagesize=A4)
            
            # Estilos
            styles = getSampleStyleSheet()
            elements = []
            
            # Título
            titulo = Paragraph("Reporte de Proveedores", styles['Title'])
            elements.append(titulo)
            elements.append(Spacer(1, 12))
            
            # Fecha
            fecha_str = datetime.now().strftime("%d/%m/%Y %H:%M")
            fecha_p = Paragraph(f"Generado: {fecha_str}", styles['Normal'])
            elements.append(fecha_p)
            elements.append(Spacer(1, 12))
            
            # Tabla de proveedores
            data = [['ID', 'Nombre/Razón Social', 'CUIT/RUT', 'Teléfono', 'Email', 'Contacto']]
            
            for proveedor in proveedores:
                data.append([
                    str(proveedor['id']),  # id
                    proveedor['nombre_razon_social'],  # nombre_razon_social
                    proveedor['cuit_rut'],  # cuit_rut
                    proveedor['telefono'],  # telefono
                    proveedor['email'],  # email
                    proveedor['contacto_responsable']  # contacto
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