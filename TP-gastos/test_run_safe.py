import logging
import traceback

def main():
    logging.basicConfig(level=logging.INFO)
    try:
        # Patch para evitar abrir la UI en este entorno de prueba
        import dearpygui.dearpygui as dpg
        from modules.ui_manager import UIManager

        dpg.start_dearpygui = lambda: None
        UIManager.crear_interfaz_completa = lambda self: None
        # Evitar que se intenten manipular widgets/tablas sin haber creado el contexto
        UIManager.cargar_datos_iniciales = lambda self: None

        # Importar y ejecutar la app
        from main import GastosApp

        app = GastosApp()
        print('Inicialización completada. Ejecutando app.run() (start_dearpygui parcheado)...')
        app.run()
        print('app.run() finalizó correctamente')
    except Exception as e:
        traceback.print_exc()
        print('ERROR durante ejecución:', e)

if __name__ == '__main__':
    main()
