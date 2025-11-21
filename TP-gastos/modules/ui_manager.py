# ui_manager.py - Manager de la interfaz de usuario para el sistema de gastos
"""
UIManager: Clase para centralizar la creación y gestión de toda la interfaz de usuario.
Separa la lógica de GUI del main.py para mejor organización y mantenibilidad.
"""

import dearpygui.dearpygui as dpg
import sys
import os
import logging
from datetime import datetime, date
import logging

# Intentar importar helper opcional `getPositionX` desde carpeta `lib` (si existe)
try:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from lib.myfunctions.myscreen import getPositionX
except Exception:
    # Si no existe, usamos un fallback que devuelve 0
    def getPositionX():
        return 0

logger = logging.getLogger(__name__)

class UIManager:
    """Manager centralizado para la interfaz de usuario del sistema de gastos"""
    
    def __init__(self, app_instance):
        """Inicializar con referencia a la aplicación principal"""
        self.app = app_instance
        self.current_filter = {"tipo": None, "categoria": None, "fecha_desde": None, "fecha_hasta": None}
        self.transaccion_editando_id = None  # Para rastrear si estamos editando
        self.categoria_editando_id = None  # Para rastrear si estamos editando categoría
    
    def configurar_temas_globales(self):
        """Configurar temas globales para toda la aplicación"""
        # Verificar si los temas ya existen para evitar duplicados
        if not dpg.does_item_exist("theme_boton_verde"):
            with dpg.theme(tag="theme_boton_verde"):
                with dpg.theme_component(dpg.mvButton):
                    dpg.add_theme_color(dpg.mvThemeCol_Button, (0, 128, 0))
                    dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (0, 160, 0))
                    dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (0, 100, 0))
                    dpg.add_theme_color(dpg.mvThemeCol_Text, (255, 255, 255))
        
        if not dpg.does_item_exist("theme_boton_rojo"):
            with dpg.theme(tag="theme_boton_rojo"):
                with dpg.theme_component(dpg.mvButton):
                    dpg.add_theme_color(dpg.mvThemeCol_Button, (128, 0, 0))
                    dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (160, 0, 0))
                    dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (100, 0, 0))
                    dpg.add_theme_color(dpg.mvThemeCol_Text, (255, 255, 255))
        
        if not dpg.does_item_exist("theme_boton_azul"):
            with dpg.theme(tag="theme_boton_azul"):
                with dpg.theme_component(dpg.mvButton):
                    dpg.add_theme_color(dpg.mvThemeCol_Button, (0, 100, 200))
                    dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (0, 120, 220))
                    dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (0, 80, 180))
                    dpg.add_theme_color(dpg.mvThemeCol_Text, (255, 255, 255))
    
    def crear_interfaz_completa(self):
        """Crear toda la interfaz gráfica de la aplicación"""
        dpg.create_context()
        self.configurar_temas_globales()
        
        dpg.create_viewport(
            title='Sistema de Control de Gastos y Presupuesto Personal',
            width=1400,
            height=900,
            min_width=1000,
            min_height=700,
            x_pos=getPositionX(),
            resizable=True
        )
        
        # Crear la ventana principal
        with dpg.window(tag="ventana_principal", label="Sistema de Gastos", width=1400, height=900):
            self.crear_menu_principal()
            self.crear_tabs_principales()
        
        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.set_primary_window("ventana_principal", True)
    
    def crear_menu_principal(self):
        """Crear la barra de menú principal"""
        with dpg.menu_bar():
            with dpg.menu(label="Archivo"):
                dpg.add_menu_item(label="Exportar Datos", callback=self.exportar_datos)
                dpg.add_menu_item(label="Importar Datos", callback=self.importar_datos)
                dpg.add_separator()
                dpg.add_menu_item(label="Salir", callback=self.cerrar_aplicacion)
            
            with dpg.menu(label="Ayuda"):
                dpg.add_menu_item(label="Acerca de", callback=self.mostrar_acerca_de)
    
    def crear_tabs_principales(self):
        """Crear las pestañas principales de la aplicación"""
        with dpg.tab_bar():
            with dpg.tab(label="Transacciones"):
                self.crear_tab_transacciones()
            
            with dpg.tab(label="Categorías"):
                self.crear_tab_categorias()
            
            with dpg.tab(label="Reportes"):
                self.crear_tab_reportes()
    
    def crear_tab_transacciones(self):
        """Crear la pestaña de transacciones"""
        with dpg.group(horizontal=True):
            # Panel izquierdo - Formulario
            with dpg.child_window(width=400, height=600):
                dpg.add_text("Nueva Transacción")
                dpg.add_separator()
                
                # Tipo de transacción
                dpg.add_text("Tipo:")
                dpg.add_combo(
                    ["ingreso", "egreso"], 
                    default_value="egreso", 
                    tag="combo_tipo_transaccion",
                    width=200
                )
                
                # Monto
                dpg.add_text("Monto:")
                dpg.add_input_float(
                    tag="input_monto", 
                    default_value=0.0, 
                    min_value=0.01, 
                    step=0.01,
                    width=200
                )
                
                # Categoría
                dpg.add_text("Categoría:")
                dpg.add_combo(
                    self.app.categorias_manager.obtener_nombres_categorias(),
                    tag="combo_categoria_transaccion",
                    width=200
                )
                
                # Descripción
                dpg.add_text("Descripción:")
                dpg.add_input_text(
                    tag="input_descripcion", 
                    multiline=True, 
                    height=60,
                    width=380
                )
                
                # Fecha
                dpg.add_text("Fecha (YYYY-MM-DD):")
                dpg.add_input_text(
                    tag="input_fecha",
                    default_value=date.today().isoformat(),
                    width=200
                )
                
                # Botones
                with dpg.group(horizontal=True):
                    dpg.add_button(
                            tag="btn_accion_transaccion",
                            label="Agregar Transacción", 
                            callback=self.agregar_transaccion
                        )
                    dpg.add_button(
                            label="Limpiar Formulario", 
                            callback=self.limpiar_formulario_transaccion
                        )
            
            # Panel derecho - Lista y filtros
            with dpg.child_window(width=950, height=600):
                # Filtros
                with dpg.collapsing_header(label="Filtros", default_open=True):
                    with dpg.group(horizontal=True):
                        dpg.add_text("Tipo:")
                        dpg.add_combo(
                            ["", "ingreso", "egreso"], 
                            default_value="", 
                            tag="filtro_tipo",
                            callback=self.aplicar_filtros,
                            width=120
                        )
                        
                        dpg.add_text("Categoría:")
                        categorias = [""] + self.app.categorias_manager.obtener_nombres_categorias()
                        dpg.add_combo(
                            categorias, 
                            default_value="", 
                            tag="filtro_categoria",
                            callback=self.aplicar_filtros,
                            width=150
                        )
                        
                        dpg.add_text("Desde:")
                        dpg.add_input_text(
                            tag="filtro_fecha_desde",
                            width=120,
                            hint="YYYY-MM-DD"
                        )
                        
                        dpg.add_text("Hasta:")
                        dpg.add_input_text(
                            tag="filtro_fecha_hasta",
                            width=120,
                            hint="YYYY-MM-DD"
                        )
                        
                        dpg.add_button(
                            label="Aplicar Filtros", 
                            callback=self.aplicar_filtros
                        )
                        dpg.add_button(
                            label="Limpiar Filtros", 
                            callback=self.limpiar_filtros
                        )
                
                # Tabla de transacciones
                with dpg.child_window(height=450):
                    dpg.add_text("Transacciones")
                    dpg.add_separator()
                    
                    # Headers de la tabla
                    with dpg.table(
                        tag="tabla_transacciones",
                        header_row=True,
                        resizable=True,
                        borders_innerV=True,
                        borders_outerV=True,
                        borders_innerH=True,
                        borders_outerH=True
                    ):
                        dpg.add_table_column(label="ID", width_fixed=True, init_width_or_weight=50)
                        dpg.add_table_column(label="Tipo", width_fixed=True, init_width_or_weight=80)
                        dpg.add_table_column(label="Monto", width_fixed=True, init_width_or_weight=100)
                        dpg.add_table_column(label="Categoría", width_fixed=True, init_width_or_weight=120)
                        dpg.add_table_column(label="Descripción", width_fixed=True, init_width_or_weight=200)
                        dpg.add_table_column(label="Fecha", width_fixed=True, init_width_or_weight=100)
                        dpg.add_table_column(label="Acciones", width_fixed=True, init_width_or_weight=120)
                    
                    # No cargar datos aquí, se hará después de setup
    
    def crear_tab_categorias(self):
        """Crear la pestaña de categorías"""
        with dpg.group(horizontal=True):
            # Panel izquierdo - Formulario
            with dpg.child_window(width=400, height=400):
                dpg.add_text("Nueva Categoría")
                dpg.add_separator()
                
                dpg.add_text("Nombre:")
                dpg.add_input_text(tag="input_nombre_categoria", width=300)
                
                dpg.add_text("Descripción:")
                dpg.add_input_text(
                    tag="input_descripcion_categoria", 
                    multiline=True, 
                    height=60,
                    width=380
                )
                
                with dpg.group(horizontal=True):
                    dpg.add_button(
                        tag="btn_accion_categoria",
                        label="Agregar", 
                        callback=self.agregar_categoria
                    )
                    dpg.add_button(
                        label="Limpiar", 
                        callback=self.limpiar_formulario_categoria
                    )
            
            # Panel derecho - Lista
            with dpg.child_window(width=950, height=400):
                dpg.add_text("Categorías")
                dpg.add_separator()
                
                with dpg.table(
                    tag="tabla_categorias",
                    header_row=True,
                    resizable=True,
                    borders_innerV=True,
                    borders_outerV=True,
                    borders_innerH=True,
                    borders_outerH=True
                ):
                    dpg.add_table_column(label="ID", width_fixed=True, init_width_or_weight=50)
                    dpg.add_table_column(label="Nombre", width_fixed=True, init_width_or_weight=200)
                    dpg.add_table_column(label="Descripción", width_fixed=True, init_width_or_weight=300)
                    dpg.add_table_column(label="Acciones", width_fixed=True, init_width_or_weight=120)
                
                # No cargar datos aquí, se hará después de setup
    
    def crear_tab_reportes(self):
        """Crear la pestaña de reportes y gráficos"""
        with dpg.group(horizontal=True):
            # Panel izquierdo - Controles
            with dpg.child_window(width=300, height=700):
                dpg.add_text("Reportes y Gráficos")
                dpg.add_separator()
                
                # Balance actual
                balance = self.app.transacciones_manager.obtener_balance_actual()
                dpg.add_text(f"Balance Actual: ${balance:.2f}")
                dpg.add_separator()
                
                # Tipo de gráfico
                dpg.add_text("Tipo de Gráfico:")
                dpg.add_combo(
                    ["Categorías (Barras)", "Categorías (Barras Horizontal)", "Mensual (Barras)"],
                    default_value="Categorías (Barras)",
                    tag="combo_tipo_grafico",
                    callback=self.actualizar_grafico,
                    width=250
                )
                
                # Filtro por tipo
                dpg.add_text("Filtrar por tipo:")
                dpg.add_combo(
                    ["", "ingreso", "egreso"],
                    default_value="",
                    tag="filtro_grafico_tipo",
                    callback=self.actualizar_grafico,
                    width=250
                )
                
                dpg.add_button(
                    label="Actualizar Gráfico", 
                    callback=self.actualizar_grafico
                )
            
            # Panel derecho - Gráfico
            with dpg.child_window(width=1050, height=700, tag="panel_grafico"):
                with dpg.plot(
                    tag="plot_grafico",
                    label="Gráfico de Gastos",
                    height=650,
                    width=1000
                ):
                    dpg.add_plot_legend()
                    dpg.add_plot_axis(dpg.mvXAxis, label="Categorías/Meses")
                    dpg.add_plot_axis(dpg.mvYAxis, label="Monto ($)", tag="y_axis")
                
                # self.actualizar_grafico()  # Temporalmente deshabilitado
    
    def cargar_datos_iniciales(self):
        """Cargar datos iniciales en las tablas después de que la interfaz esté lista"""
        logger.info("📊 Cargando datos iniciales en las tablas...")
        try:
            self.actualizar_tabla_transacciones()
            self.actualizar_tabla_categorias()
            logger.info("✅ Datos iniciales cargados correctamente")
        except Exception as e:
            logger.error(f"❌ Error cargando datos iniciales: {e}")
            import traceback
            traceback.print_exc()
    
    # ================================
    # CALLBACKS PARA TRANSACCIONES
    # ================================
    
    def agregar_transaccion(self):
        """
        Callback para agregar una nueva transacción
        
        TODO: Implementa este método:
        1. Obtener valores del formulario usando dpg.get_value()
           - tipo: dpg.get_value("combo_tipo_transaccion")
           - monto: dpg.get_value("input_monto")
           - categoria_nombre: dpg.get_value("combo_categoria_transaccion")
           - descripcion: dpg.get_value("input_descripcion")
           - fecha: dpg.get_value("input_fecha")
        
        2. Validar que tipo y monto no estén vacíos
           if not tipo or not monto:
               self.mostrar_mensaje("Complete todos los campos obligatorios", error=True)
               return
        
        3. Si hay categoria_nombre, obtener su ID:
           - Obtener todas las categorías: self.app.categorias_manager.obtener_categorias()
           - Buscar en la lista la que tenga el nombre igual a categoria_nombre
           - Guardar su ID (índice 0 de la tupla)
        
        4. Llamar a agregar_transaccion del manager:
           self.app.transacciones_manager.agregar_transaccion(tipo, monto, categoria_id, descripcion, fecha)
        
        5. Si retorna True:
           - Limpiar formulario: self.limpiar_formulario_transaccion()
           - Actualizar tabla: self.actualizar_tabla_transacciones()
           - Actualizar gráfico: self.actualizar_grafico()
           - Mostrar mensaje de éxito
        
        6. Si retorna False, mostrar mensaje de error
        """
        # TODO: IMPLEMENTAR AQUÍ
        self.mostrar_mensaje("Agregar transacción - Funcionalidad pendiente")
    
    def limpiar_formulario_transaccion(self):
        """Limpia el formulario de transacción"""
        dpg.set_value("combo_tipo_transaccion", "Gasto")
        dpg.set_value("input_monto", 0.0)
        dpg.set_value("combo_categoria_transaccion", "")
        dpg.set_value("input_descripcion", "")
        dpg.set_value("input_fecha", "")
        
        # Resetear el botón a modo agregar
        dpg.configure_item(
            "btn_accion_transaccion",
            label="Agregar Transacción",
            callback=self.agregar_transaccion
        )
        self.transaccion_editando_id = None
    
    def aplicar_filtros(self):
        """
        Aplicar filtros a la tabla de transacciones
        
        TODO: Implementa este método:
        1. Obtener valores de los filtros:
           - tipo: dpg.get_value("filtro_tipo") o None si está vacío
           - categoria: dpg.get_value("filtro_categoria") o None si está vacío
           - fecha_desde: dpg.get_value("filtro_fecha_desde") o None si está vacío
           - fecha_hasta: dpg.get_value("filtro_fecha_hasta") o None si está vacío
        
        2. Guardar los filtros en self.current_filter (diccionario)
        
        3. Llamar a self.actualizar_tabla_transacciones() para aplicar los filtros
        
        PISTA: Para verificar si un valor está vacío:
            valor = dpg.get_value("tag")
            valor_final = valor if valor else None
        """
        # TODO: IMPLEMENTAR AQUÍ
        self.mostrar_mensaje("Aplicar filtros - Funcionalidad pendiente")
    
    def limpiar_filtros(self):
        """Limpiar todos los filtros"""
        dpg.set_value("filtro_tipo", "")
        dpg.set_value("filtro_categoria", "")
        dpg.set_value("filtro_fecha_desde", "")
        dpg.set_value("filtro_fecha_hasta", "")
        
        self.current_filter = {"tipo": None, "categoria": None, "fecha_desde": None, "fecha_hasta": None}
        self.actualizar_tabla_transacciones()
    
    def actualizar_tabla_transacciones(self):
        """Actualizar la tabla de transacciones"""
        # Verificar que la tabla existe
        if not dpg.does_item_exist("tabla_transacciones"):
            logger.warning("⚠️ La tabla 'tabla_transacciones' no existe")
            return
        
        # Limpiar solo las filas de la tabla (slot 1 contiene las filas)
        table_children = dpg.get_item_children("tabla_transacciones", slot=1)
        if table_children:
            for child in table_children:
                try:
                    dpg.delete_item(child)
                except:
                    pass  # Ignorar errores al eliminar
        
        # Obtener datos filtrados
        transacciones = self.app.transacciones_manager.filtrar_transacciones(
            self.current_filter["tipo"],
            self.current_filter["categoria"],
            self.current_filter["fecha_desde"],
            self.current_filter["fecha_hasta"]
        )
        
        logger.info(f"🔄 Actualizando tabla con {len(transacciones)} transacciones")
        
        # Agregar filas
        for trans in transacciones:
            with dpg.table_row(parent="tabla_transacciones"):
                dpg.add_text(str(trans[0]))  # ID
                dpg.add_text(trans[1])  # Tipo
                dpg.add_text(f"${trans[2]:.2f}")  # Monto
                dpg.add_text(trans[3] or "Sin categoría")  # Categoría
                dpg.add_text(trans[4] or "")  # Descripción
                dpg.add_text(trans[5])  # Fecha
                with dpg.group(horizontal=True):
                    dpg.add_button(
                        label="Editar", 
                        callback=lambda s, a, u: self.editar_transaccion(u), 
                        user_data=trans[0]
                    )
                    dpg.add_button(
                        label="Eliminar", 
                        callback=lambda s, a, u: self.eliminar_transaccion(u), 
                        user_data=trans[0]
                    )
    
    # ================================
    # CALLBACKS PARA CATEGORÍAS
    # ================================
    
    def agregar_categoria(self):
        """
        Callback para agregar una nueva categoría
        
        TODO: Implementa este método:
        1. Obtener valores del formulario:
           - nombre: dpg.get_value("input_nombre_categoria")
           - descripcion: dpg.get_value("input_descripcion_categoria")
        
        2. Llamar al manager:
           self.app.categorias_manager.agregar_categoria(nombre, descripcion)
        
        3. Si retorna True:
           - Limpiar formulario: self.limpiar_formulario_categoria()
           - Actualizar tabla: self.actualizar_tabla_categorias()
           - Actualizar combos: self.actualizar_combos_categorias()
           - Mostrar mensaje de éxito
        
        4. Si retorna False, mostrar mensaje de error
        """
        # TODO: IMPLEMENTAR AQUÍ
        self.mostrar_mensaje("Agregar categoría - Funcionalidad pendiente")
    
    def limpiar_formulario_categoria(self):
        """Limpiar el formulario de categoría"""
        dpg.set_value("input_nombre_categoria", "")
        dpg.set_value("input_descripcion_categoria", "")
        
        # Resetear el botón a modo agregar
        dpg.configure_item(
            "btn_accion_categoria",
            label="Agregar",
            callback=self.agregar_categoria
        )
        self.categoria_editando_id = None
    
    def actualizar_tabla_categorias(self):
        """Actualizar la tabla de categorías"""
        # Verificar que la tabla existe
        if not dpg.does_item_exist("tabla_categorias"):
            logger.warning("⚠️ La tabla 'tabla_categorias' no existe")
            return
        
        # Limpiar solo las filas de la tabla (slot 1 contiene las filas)
        table_children = dpg.get_item_children("tabla_categorias", slot=1)
        if table_children:
            for child in table_children:
                try:
                    dpg.delete_item(child)
                except:
                    pass  # Ignorar errores al eliminar
        
        categorias = self.app.categorias_manager.obtener_categorias()
        
        for cat in categorias:
            with dpg.table_row(parent="tabla_categorias"):
                dpg.add_text(str(cat[0]))  # ID
                dpg.add_text(cat[1])  # Nombre
                dpg.add_text(cat[2] or "")  # Descripción
                with dpg.group(horizontal=True):
                    dpg.add_button(
                        label="Editar", 
                        callback=lambda s, a, u: self.editar_categoria(u), 
                        user_data=cat[0]
                    )
                    dpg.add_button(
                        label="Eliminar", 
                        callback=lambda s, a, u: self.eliminar_categoria(u), 
                        user_data=cat[0]
                    )
    
    def actualizar_combos_categorias(self):
        """Actualizar los combos de categorías en toda la UI"""
        categorias = self.app.categorias_manager.obtener_nombres_categorias()
        
        dpg.configure_item("combo_categoria_transaccion", items=categorias)
        filtro_categorias = [""] + categorias
        dpg.configure_item("filtro_categoria", items=filtro_categorias)
    
    # ================================
    # CALLBACKS PARA GRÁFICOS
    # ================================
    
    def actualizar_grafico(self):
        """
        Actualizar el gráfico según el tipo seleccionado
        
        TODO: Implementa este método:
        1. Obtener el tipo de gráfico seleccionado:
           tipo_grafico = dpg.get_value("combo_tipo_grafico")
        
        2. Obtener el filtro de tipo (ingreso/egreso):
           filtro_tipo = dpg.get_value("filtro_grafico_tipo") o None si está vacío
        
        3. Limpiar gráfico existente:
           dpg.delete_item("plot_grafico")
        
        4. Según el tipo_grafico seleccionado, llamar al método apropiado:
           - Si contiene "Barras)": self.crear_grafico_barras_categorias(filtro_tipo)
           - Si contiene "Horizontal": self.crear_grafico_barras_categorias_horizontal(filtro_tipo)
           - Si contiene "Mensual": self.crear_grafico_barras_mensual(filtro_tipo)
        
        PISTA: Puedes usar el operador 'in' para verificar strings:
            if "Barras" in tipo_grafico:
                ...
        """
        # TODO: IMPLEMENTAR AQUÍ
        self.mostrar_mensaje("Actualizar gráfico - Funcionalidad pendiente")
    
    def crear_grafico_torta_categorias(self, tipo=None):
        """Crear gráfico de torta para categorías"""
        datos = self.app.transacciones_manager.obtener_datos_para_grafico_categorias(tipo)
        
        if not datos:
            return
        
        # Para DearPyGUI, usaremos un gráfico de barras apiladas como alternativa a la torta
        # ya que add_pie_series puede tener una API diferente
        etiquetas = [d[0] for d in datos]
        valores = [d[1] for d in datos]
        
        with dpg.plot(tag="plot_grafico", label="Gastos por Categoría", height=650, width=1000):
            dpg.add_plot_legend()
            dpg.add_plot_axis(dpg.mvXAxis, label="Categorías")
            with dpg.plot_axis(dpg.mvYAxis, label="Monto ($)", tag="y_axis"):
                # Usar barras en lugar de torta por compatibilidad
                dpg.add_bar_series(etiquetas, valores)
    
    def crear_grafico_barras_categorias(self, tipo=None):
        """Crear gráfico de barras verticales para categorías"""
        datos = self.app.transacciones_manager.obtener_datos_para_grafico_categorias(tipo)
        
        if not datos:
            return
        
        etiquetas = [d[0] for d in datos]
        valores = [float(d[1]) for d in datos]
        
        # Crear índices numéricos para el eje X
        x_values = [float(i) for i in range(len(etiquetas))]
        
        with dpg.plot(tag="plot_grafico", label="Gastos por Categoría", height=650, width=1000, parent="panel_grafico"):
            dpg.add_plot_legend()
            x_axis = dpg.add_plot_axis(dpg.mvXAxis, label="Categorías")
            # Configurar las etiquetas personalizadas para el eje X
            dpg.set_axis_ticks(x_axis, tuple([(etiquetas[i], float(i)) for i in range(len(etiquetas))]))
            with dpg.plot_axis(dpg.mvYAxis, label="Monto ($)", tag="y_axis"):
                dpg.add_bar_series(x_values, valores, label="Monto")
    
    def crear_grafico_barras_categorias_horizontal(self, tipo=None):
        """Crear gráfico de barras horizontal para categorías"""
        datos = self.app.transacciones_manager.obtener_datos_para_grafico_categorias(tipo)
        
        if not datos:
            return
        
        etiquetas = [d[0] for d in datos]
        valores = [float(d[1]) for d in datos]
        
        # Crear índices numéricos para el eje Y
        y_values = [float(i) for i in range(len(etiquetas))]
        
        with dpg.plot(tag="plot_grafico", label="Gastos por Categoría", height=650, width=1000, parent="panel_grafico"):
            dpg.add_plot_legend()
            dpg.add_plot_axis(dpg.mvXAxis, label="Monto ($)")
            y_axis = dpg.add_plot_axis(dpg.mvYAxis, label="Categorías", tag="y_axis")
            # Configurar las etiquetas personalizadas para el eje Y
            dpg.set_axis_ticks(y_axis, tuple([(etiquetas[i], float(i)) for i in range(len(etiquetas))]))
            # Barras horizontales
            dpg.add_bar_series(valores, y_values, horizontal=True, label="Monto")
    
    def crear_grafico_barras_mensual(self, tipo=None):
        """Crear gráfico de barras mensual"""
        datos = self.app.transacciones_manager.obtener_datos_para_grafico_mensual(tipo)
        
        if not datos:
            return
        
        etiquetas = [d[0] for d in datos]
        valores = [float(d[1]) for d in datos]
        
        # Crear índices numéricos para el eje X
        x_values = [float(i) for i in range(len(etiquetas))]
        
        with dpg.plot(tag="plot_grafico", label="Gastos Mensuales", height=650, width=1000, parent="panel_grafico"):
            dpg.add_plot_legend()
            x_axis = dpg.add_plot_axis(dpg.mvXAxis, label="Mes")
            # Configurar las etiquetas personalizadas para el eje X
            dpg.set_axis_ticks(x_axis, tuple([(etiquetas[i], float(i)) for i in range(len(etiquetas))]))
            with dpg.plot_axis(dpg.mvYAxis, label="Monto ($)", tag="y_axis"):
                dpg.add_bar_series(x_values, valores, label="Monto")
    
    # ================================
    # MÉTODOS DE UTILIDAD
    # ================================
    
    def mostrar_mensaje(self, mensaje, error=False):
        """Mostrar un mensaje al usuario mediante logging"""
        if error:
            logger.error(f"❌ {mensaje}")
        else:
            logger.info(f"✅ {mensaje}")
    
    def cerrar_aplicacion(self):
        """Cerrar la aplicación"""
        dpg.stop_dearpygui()
    
    def mostrar_acerca_de(self):
        """Mostrar información sobre la aplicación"""
        with dpg.window(label="Acerca de", modal=True, width=400, height=200):
            dpg.add_text("Sistema de Control de Gastos y Presupuesto Personal")
            dpg.add_text("Versión 1.0")
            dpg.add_text("Desarrollado con DearPyGUI")
    
    # Métodos placeholder para funcionalidades futuras
    def editar_transaccion(self, trans_id):
        """Cargar datos de una transacción para editar"""
        try:
            # Obtener datos de la transacción
            transaccion = self.app.transacciones_manager.obtener_transaccion_por_id(trans_id)
            
            if not transaccion:
                self.mostrar_mensaje("Transacción no encontrada", error=True)
                return
            
            # Cargar datos en el formulario
            # transaccion = (id, tipo, monto, categoria_id, categoria_nombre, descripcion, fecha, created_at, updated_at)
            dpg.set_value("combo_tipo_transaccion", transaccion[1])  # tipo
            dpg.set_value("input_monto", float(transaccion[2]))  # monto
            dpg.set_value("combo_categoria_transaccion", transaccion[4] or "")  # categoria_nombre (índice 4)
            dpg.set_value("input_descripcion", transaccion[5] or "")  # descripcion (índice 5)
            dpg.set_value("input_fecha", transaccion[6])  # fecha (índice 6)
            
            # Cambiar el botón a modo edición
            dpg.configure_item(
                "btn_accion_transaccion",
                label="Actualizar Transacción",
                callback=lambda: self.actualizar_transaccion(trans_id)
            )
            
            # Guardar el ID en modo edición
            self.transaccion_editando_id = trans_id
            
            logger.info(f"✏️ Transacción {trans_id} cargada para editar")
            
        except Exception as e:
            logger.error(f"❌ Error cargando transacción para editar: {e}")
            self.mostrar_mensaje(f"Error: {str(e)}", error=True)
    
    def actualizar_transaccion(self, trans_id):
        """Actualizar una transacción existente"""
        try:
            tipo = dpg.get_value("combo_tipo_transaccion")
            monto = dpg.get_value("input_monto")
            categoria_nombre = dpg.get_value("combo_categoria_transaccion")
            descripcion = dpg.get_value("input_descripcion")
            fecha = dpg.get_value("input_fecha")
            
            # Validaciones
            if not tipo or not monto:
                self.mostrar_mensaje("Complete todos los campos obligatorios", error=True)
                return
            
            # Obtener ID de categoría
            categoria_id = None
            if categoria_nombre:
                categorias = self.app.categorias_manager.obtener_categorias()
                for cat in categorias:
                    if cat[1] == categoria_nombre:
                        categoria_id = cat[0]
                        break
            
            # Actualizar transacción
            if self.app.transacciones_manager.actualizar_transaccion(
                trans_id, tipo, monto, categoria_id, descripcion, fecha
            ):
                self.actualizar_tabla_transacciones()
                self.actualizar_grafico()
                self.limpiar_formulario_transaccion()
                self.mostrar_mensaje("Transacción actualizada correctamente")
            else:
                self.mostrar_mensaje("Error al actualizar la transacción", error=True)
                
        except Exception as e:
            logger.error(f"❌ Error actualizando transacción: {e}")
            self.mostrar_mensaje(f"Error: {str(e)}", error=True)
    
    def eliminar_transaccion(self, trans_id):
        """Eliminar una transacción (placeholder)"""
        if self.app.transacciones_manager.soft_delete(trans_id):
            self.actualizar_tabla_transacciones()
            self.actualizar_grafico()
            self.mostrar_mensaje("Transacción eliminada correctamente")
        else:
            self.mostrar_mensaje("Error al eliminar la transacción", error=True)
    
    def editar_categoria(self, cat_id):
        """Cargar datos de una categoría para editar"""
        try:
            # Obtener datos de la categoría
            categoria = self.app.categorias_manager.obtener_categoria_por_id(cat_id)
            
            if not categoria:
                self.mostrar_mensaje("Categoría no encontrada", error=True)
                return
            
            # Cargar datos en el formulario
            # categoria = (id, nombre, descripcion)
            dpg.set_value("input_nombre_categoria", categoria[1])  # nombre
            dpg.set_value("input_descripcion_categoria", categoria[2] or "")  # descripcion
            
            # Cambiar el botón a modo edición
            dpg.configure_item(
                "btn_accion_categoria",
                label="Actualizar Categoría",
                callback=lambda: self.actualizar_categoria(cat_id)
            )
            
            # Guardar el ID en modo edición
            self.categoria_editando_id = cat_id
            
            logger.info(f"✏️ Categoría {cat_id} cargada para editar")
            
        except Exception as e:
            logger.error(f"❌ Error cargando categoría para editar: {e}")
            self.mostrar_mensaje(f"Error: {str(e)}", error=True)
    
    def actualizar_categoria(self, cat_id):
        """Actualizar una categoría existente"""
        try:
            nombre = dpg.get_value("input_nombre_categoria")
            descripcion = dpg.get_value("input_descripcion_categoria")
            
            # Validaciones
            if not nombre:
                self.mostrar_mensaje("El nombre es obligatorio", error=True)
                return
            
            # Actualizar categoría
            if self.app.categorias_manager.actualizar_categoria(cat_id, nombre, descripcion):
                self.actualizar_tabla_categorias()
                self.actualizar_combos_categorias()
                self.limpiar_formulario_categoria()
                self.mostrar_mensaje("Categoría actualizada correctamente")
            else:
                self.mostrar_mensaje("Error al actualizar la categoría", error=True)
                
        except Exception as e:
            logger.error(f"❌ Error actualizando categoría: {e}")
            self.mostrar_mensaje(f"Error: {str(e)}", error=True)
    
    def eliminar_categoria(self, cat_id):
        """Eliminar una categoría (placeholder)"""
        if self.app.categorias_manager.soft_delete(cat_id):
            self.actualizar_tabla_categorias()
            self.actualizar_combos_categorias()
            self.mostrar_mensaje("Categoría eliminada correctamente")
        else:
            self.mostrar_mensaje("Error al eliminar la categoría", error=True)
    
    def exportar_datos(self):
        """Exportar datos (placeholder)"""
        self.mostrar_mensaje("Exportar datos - Funcionalidad pendiente")
    
    def importar_datos(self):
        """Importar datos (placeholder)"""
        self.mostrar_mensaje("Importar datos - Funcionalidad pendiente")