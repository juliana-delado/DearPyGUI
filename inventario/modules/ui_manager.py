# ui_manager.py - Manager de la interfaz de usuario
"""
UIManager: Clase para centralizar la creación y gestión de toda la interfaz de usuario.
Separa la lógica de GUI del main.py para mejor organización y mantenibilidad.
"""

import dearpygui.dearpygui as dpg
import sys
import os
from datetime import datetime

# Agregar el directorio padre al path para importar lib
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib.myfunctions.myscreen import getPositionX

class UIManager:
    """Manager centralizado para la interfaz de usuario"""
    
    def __init__(self, app_instance):
        """Inicializar con referencia a la aplicación principal"""
        self.app = app_instance
    
    def configurar_temas_globales(self):
        """Configurar temas globales para toda la aplicación"""
        # Verificar si los temas ya existen para evitar duplicados
        if not dpg.does_item_exist("theme_boton_verde"):
            # Tema para botones de aceptar/guardar/registrar (verde)
            with dpg.theme(tag="theme_boton_verde"):
                with dpg.theme_component(dpg.mvButton):
                    dpg.add_theme_color(dpg.mvThemeCol_Button, (0, 128, 0))  # Verde oscuro
                    dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (0, 160, 0))  # Verde más claro al hover
                    dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (0, 100, 0))  # Verde más oscuro al presionar
                    dpg.add_theme_color(dpg.mvThemeCol_Text, (255, 255, 255))  # Texto blanco
        
        if not dpg.does_item_exist("theme_boton_rojo"):
            # Tema para botones de cancelar/eliminar (rojo)
            with dpg.theme(tag="theme_boton_rojo"):
                with dpg.theme_component(dpg.mvButton):
                    dpg.add_theme_color(dpg.mvThemeCol_Button, (128, 0, 0))  # Rojo oscuro
                    dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (160, 0, 0))  # Rojo más claro al hover
                    dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (100, 0, 0))  # Rojo más oscuro al presionar
                    dpg.add_theme_color(dpg.mvThemeCol_Text, (255, 255, 255))  # Texto blanco
        
        if not dpg.does_item_exist("theme_boton_azul"):
            # Tema para botones de imprimir/exportar (azul)
            with dpg.theme(tag="theme_boton_azul"):
                with dpg.theme_component(dpg.mvButton):
                    dpg.add_theme_color(dpg.mvThemeCol_Button, (0, 100, 200))  # Azul oscuro
                    dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (0, 120, 220))  # Azul más claro al hover
                    dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (0, 80, 180))  # Azul más oscuro al presionar
                    dpg.add_theme_color(dpg.mvThemeCol_Text, (255, 255, 255))  # Texto blanco
        
        if not dpg.does_item_exist("theme_boton_amarillo"):
            # Tema para botones de actualizar/editar (amarillo)
            with dpg.theme(tag="theme_boton_amarillo"):
                with dpg.theme_component(dpg.mvButton):
                    dpg.add_theme_color(dpg.mvThemeCol_Button, (200, 160, 0))  # Amarillo oscuro
                    dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (220, 180, 0))  # Amarillo más claro al hover
                    dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (180, 140, 0))  # Amarillo más oscuro al presionar
                    dpg.add_theme_color(dpg.mvThemeCol_Text, (255, 255, 255))  # Texto blanco
        
        if not dpg.does_item_exist("theme_boton_blanco"):
            # Tema para botones de imprimir (blanco con letras negras)
            with dpg.theme(tag="theme_boton_blanco"):
                with dpg.theme_component(dpg.mvButton):
                    dpg.add_theme_color(dpg.mvThemeCol_Button, (255, 255, 255))  # Blanco
                    dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (240, 240, 240))  # Gris muy claro al hover
                    dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (220, 220, 220))  # Gris claro al presionar
                    dpg.add_theme_color(dpg.mvThemeCol_Text, (0, 0, 0))  # Texto negro
        
        if not dpg.does_item_exist("theme_tab_bar_gris_oscuro"):
            # Tema para la barra de pestañas (tab bar) con fondo gris oscuro
            with dpg.theme(tag="theme_tab_bar_gris_oscuro"):
                with dpg.theme_component(dpg.mvAll):
                    dpg.add_theme_color(dpg.mvThemeCol_Tab, (64, 64, 64))  # Tab inactiva
                    dpg.add_theme_color(dpg.mvThemeCol_TabHovered, (80, 80, 80))  # Tab al hover
                    dpg.add_theme_color(dpg.mvThemeCol_TabActive, (100, 100, 100))  # Tab activa
                    dpg.add_theme_color(dpg.mvThemeCol_TabUnfocused, (50, 50, 50))  # Tab sin foco
                    dpg.add_theme_color(dpg.mvThemeCol_TabUnfocusedActive, (70, 70, 70))  # Tab activa sin foco
    
    def crear_interfaz_completa(self):
        """Crear toda la interfaz gráfica de la aplicación"""
        # Crear el contexto de DearPyGUI
        dpg.create_context()
        
        # Configurar temas globales para toda la aplicación
        self.configurar_temas_globales()
        
        # Configurar el viewport
        dpg.create_viewport(
            title='Sistema de Inventario Empresarial',
            width=1200,
            height=800,
            min_width=800,
            min_height=600,
            x_pos=getPositionX(),
            resizable=True,
            small_icon="logo.png",
            large_icon="logo.png"
        )
        
        # Crear la ventana principal con pestañas
        with dpg.window(
            label="Sistema de Inventario Empresarial",
            no_close=True,
            width=dpg.get_viewport_width(),
            height=dpg.get_viewport_height(),
            tag="main_window"
        ) as main_window:
            with dpg.tab_bar() as tab_bar_principal:
                # ===== DASHBOARD =====
                with dpg.tab(label="Dashboard"):
                    self._crear_dashboard()
                
                # ===== PESTAÑAS PRINCIPALES =====
                # Productos
                tab_productos = dpg.add_tab(label="Productos")
                self.app.productos_manager.crear_interfaz_productos(tab_productos)
                
                # Categorías
                tab_categorias = dpg.add_tab(label="Categorias")
                self.app.categorias_manager.crear_interfaz_categorias(tab_categorias)
                
                # Proveedores
                tab_proveedores = dpg.add_tab(label="Proveedores")
                self.app.proveedores_manager.crear_interfaz_proveedores(tab_proveedores)
                
                # Movimientos
                tab_movimientos = dpg.add_tab(label="Movimientos")
                self.app.movimientos_manager.crear_interfaz_movimientos(tab_movimientos)
    
    def _crear_dashboard(self):
        """Crear el dashboard principal con métricas y resúmenes"""
        dpg.add_text("Dashboard del Sistema", color=(0, 255, 0))
        dpg.add_separator()
        
        # ===== METRICAS DEL SISTEMA =====
        with dpg.child_window(height=150):
            dpg.add_text("Metricas del Sistema")
            dpg.add_separator()
            
            with dpg.group(horizontal=True):
                # Productos
                with dpg.child_window(width=200, height=100):
                    dpg.add_text("Total Productos:", tag="metric_productos_label")
                    dpg.add_text("0", tag="metric_productos_value", color=(0, 255, 255))
                
                # Categorías
                with dpg.child_window(width=200, height=100):
                    dpg.add_text("Total Categorias:", tag="metric_categorias_label")
                    dpg.add_text("0", tag="metric_categorias_value", color=(0, 255, 255))
                
                # Proveedores
                with dpg.child_window(width=200, height=100):
                    dpg.add_text("Total Proveedores:", tag="metric_proveedores_label")
                    dpg.add_text("0", tag="metric_proveedores_value", color=(0, 255, 255))
        
        # ===== PRODUCTOS CON STOCK BAJO =====
        with dpg.child_window(height=200):
            dpg.add_text("Productos con Stock Bajo", color=(255, 255, 0))
            dpg.add_separator()
            
            with dpg.table(tag="table_stock_bajo", header_row=True,
                         borders_innerH=True, borders_outerH=True,
                         borders_innerV=True, borders_outerV=True):
                dpg.add_table_column(label="Codigo", parent="table_stock_bajo")
                dpg.add_table_column(label="Nombre", parent="table_stock_bajo")
                dpg.add_table_column(label="Stock Actual", parent="table_stock_bajo")
                dpg.add_table_column(label="Stock Minimo", parent="table_stock_bajo")
        
        # ===== ULTIMOS MOVIMIENTOS =====
        with dpg.child_window():
            dpg.add_text("Ultimos Movimientos", color=(255, 255, 0))
            dpg.add_separator()
            
            dpg.add_button(label="Actualizar Dashboard", callback=self.app.actualizar_dashboard)
            
            with dpg.table(tag="table_movimientos_recientes", header_row=True,
                         borders_innerH=True, borders_outerH=True,
                         borders_innerV=True, borders_outerV=True):
                dpg.add_table_column(label="Fecha", parent="table_movimientos_recientes")
                dpg.add_table_column(label="Producto", parent="table_movimientos_recientes")
                dpg.add_table_column(label="Tipo", parent="table_movimientos_recientes")
                dpg.add_table_column(label="Cantidad", parent="table_movimientos_recientes")
    
    def _crear_reportes(self):
        """Crear la pestaña de reportes y exportación"""
        dpg.add_text("Reportes y Exportacion")
        dpg.add_separator()
        
        with dpg.group(horizontal=True):
            btn_excel = dpg.add_button(label="Exportar Excel", callback=self.app.exportar_excel)
            dpg.bind_item_theme(btn_excel, "theme_boton_blanco")
            btn_stock = dpg.add_button(label="Reporte Stock Bajo", callback=self.app.reporte_stock_bajo)
            dpg.bind_item_theme(btn_stock, "theme_boton_blanco")
        
        dpg.add_separator()
        dpg.add_text("Reportes Disponibles:")
        dpg.add_text("• Inventario completo")
        dpg.add_text("• Productos con stock bajo")
        dpg.add_text("• Movimientos por periodo")
        dpg.add_text("• Analisis de categorias")
        dpg.add_text("• Analisis de proveedores")
        
        # Tabla para mostrar datos de reportes cuando sea necesario
        with dpg.table(tag="table_reportes", header_row=True,
                     borders_innerH=True, borders_outerH=True,
                     borders_innerV=True, borders_outerV=True,
                     height=400):
            dpg.add_table_column(label="Columna 1")
            dpg.add_table_column(label="Columna 2")
            dpg.add_table_column(label="Columna 3")
    
    def aplicar_temas_elementos(self, elemento, tipo_elemento="auto"):
        """
        Función centralizada para aplicar temas a elementos de la UI.
        
        Args:
            elemento: El elemento de DearPyGUI al que aplicar el tema
            tipo_elemento: Tipo de elemento ("ventana", "tabla", "boton_verde", "boton_rojo", 
                          "boton_amarillo", "boton_blanco", "boton_azul", "auto")
        
        Si tipo_elemento es "auto", intenta determinar el tipo automáticamente por el tag o tipo de elemento.
        """
        if not dpg.does_item_exist(elemento):
            return
        
        # Si es auto, intentar determinar el tipo por el tag o tipo
        if tipo_elemento == "auto":
            elemento_info = dpg.get_item_info(elemento)
            elemento_type = elemento_info.get("type", "")
            elemento_tag = dpg.get_item_alias(elemento) if dpg.does_alias_exist(dpg.get_item_alias(elemento)) else ""
            
            # Determinar tipo por tag
            if "ventana" in str(elemento_tag).lower() or elemento_type == "mvWindowAppItem":
                tipo_elemento = "ventana"
            elif "table" in str(elemento_tag).lower() or elemento_type in ["mvTable", "mvTableRow"]:
                tipo_elemento = "tabla"
            elif "btn" in str(elemento_tag).lower() and ("aceptar" in str(elemento_tag).lower() or "guardar" in str(elemento_tag).lower()):
                tipo_elemento = "boton_verde"
            elif "btn" in str(elemento_tag).lower() and ("cancelar" in str(elemento_tag).lower() or "eliminar" in str(elemento_tag).lower()):
                tipo_elemento = "boton_rojo"
            elif "btn" in str(elemento_tag).lower() and ("editar" in str(elemento_tag).lower() or "actualizar" in str(elemento_tag).lower()):
                tipo_elemento = "boton_amarillo"
            elif "btn" in str(elemento_tag).lower() and ("imprimir" in str(elemento_tag).lower() or "pdf" in str(elemento_tag).lower()):
                tipo_elemento = "boton_blanco"
            else:
                # Por defecto, si no se puede determinar, no aplicar tema
                return
        
        # Aplicar el tema correspondiente
        try:
            if tipo_elemento == "boton_verde":
                dpg.bind_item_theme(elemento, "theme_boton_verde")
            elif tipo_elemento == "boton_rojo":
                dpg.bind_item_theme(elemento, "theme_boton_rojo")
            elif tipo_elemento == "boton_amarillo":
                dpg.bind_item_theme(elemento, "theme_boton_amarillo")
            elif tipo_elemento == "boton_blanco":
                dpg.bind_item_theme(elemento, "theme_boton_blanco")
            elif tipo_elemento == "boton_azul":
                dpg.bind_item_theme(elemento, "theme_boton_azul")
        except Exception as e:
            # Si hay error aplicando el tema, continuar sin interrumpir
            pass