import dearpygui.dearpygui as dpg

def hex_to_rgba(hex_color):
    """Convierte color hexadecimal a tupla RGBA para DearPyGUI"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4)) + (255,)

def colorear_celda(table_id, row, column, hex_color):
    """Colorea una celda específica de la tabla"""
    rgba_color = hex_to_rgba(hex_color)
    
    # Crear un tema para el color de la celda
    with dpg.theme() as cell_theme:
        with dpg.theme_component(dpg.mvTable):
            dpg.add_theme_color(dpg.mvThemeCol_TableRowBg, rgba_color)
    
    # Aplicar el tema a la celda específica
    dpg.highlight_table_cell(table_id, row, column, rgba_color)

# Crear el contexto de DearPyGUI
dpg.create_context()

# Crear la ventana principal
with dpg.window(label="Tabla con Celdas Coloreadas", width=600, height=400):
    
    # Crear la tabla
    with dpg.table(header_row=True, tag="mi_tabla", 
                   borders_innerH=True, borders_outerH=True,
                   borders_innerV=True, borders_outerV=True):
        
        # Agregar columnas
        dpg.add_table_column(label="Nombre")
        dpg.add_table_column(label="Edad")
        dpg.add_table_column(label="Ciudad")
        dpg.add_table_column(label="Estado")
        
        # Agregar filas
        with dpg.table_row():
            dpg.add_text("Juan")
            dpg.add_text("25")
            dpg.add_text("Madrid")
            dpg.add_text("Activo")
        
        with dpg.table_row():
            dpg.add_text("María")
            dpg.add_text("30")
            dpg.add_text("Barcelona")
            dpg.add_text("Inactivo")
        
        with dpg.table_row():
            dpg.add_text("Carlos")
            dpg.add_text("28")
            dpg.add_text("Valencia")
            dpg.add_text("Activo")
    
    # Botones para colorear celdas con diferentes colores hexadecimales
    dpg.add_button(label="Colorear celda (1,1) Rojo", 
                   callback=lambda: colorear_celda("mi_tabla", 1, 1, "#FF0000"))
    
    dpg.add_button(label="Colorear celda (2,3) Verde", 
                   callback=lambda: colorear_celda("mi_tabla", 2, 3, "#00FF00"))
    
    dpg.add_button(label="Colorear celda (0,2) Azul", 
                   callback=lambda: colorear_celda("mi_tabla", 0, 2, "#0000FF"))
    
    dpg.add_button(label="Colorear celda (1,0) Amarillo", 
                   callback=lambda: colorear_celda("mi_tabla", 1, 0, "#FFFF00"))

# Configurar la ventana principal
dpg.create_viewport(title="DearPyGUI - Tabla con Colores", width=650, height=450)
dpg.setup_dearpygui()
dpg.show_viewport()

# Ejemplo de cómo colorear celdas al inicio (opcional)
def colorear_celdas_iniciales():
    # Colorear algunas celdas con colores específicos
    colorear_celda("mi_tabla", 0, 3, "#FFA500")  # Naranja
    colorear_celda("mi_tabla", 2, 1, "#800080")  # Púrpura

# Llamar después de mostrar la ventana
dpg.set_frame_callback(1, colorear_celdas_iniciales)

# Iniciar el bucle principal
dpg.start_dearpygui()
dpg.destroy_context()