import sys
import logging

# Evitar modificaciones en sys.path si ejecutamos desde el mismo directorio
def main():
    logging.basicConfig(level=logging.INFO)

    # Evitar crear la UI durante la prueba
    try:
        # Import after setting up logging to capture messages
        from main import GastosApp
        from modules.ui_manager import UIManager

        # Monkeypatch: evitar que la UI sea creada (no abrir ventanas)
        UIManager.crear_interfaz_completa = lambda self: None

        app = GastosApp()
        ui = app.ui_manager

        print("+++ Verificando managers en UIManager +++")
        print("categorias_manager:", type(ui.categorias_manager).__name__ if ui.categorias_manager else None)
        print("transacciones_manager:", type(ui.transacciones_manager).__name__ if ui.transacciones_manager else None)

        if ui.categorias_manager is None or ui.transacciones_manager is None:
            print("ERROR: faltan managers en UIManager")
            sys.exit(2)

        print("OK: UIManager tiene referencias a categorias_manager y transacciones_manager")
        sys.exit(0)

    except Exception as e:
        import traceback
        traceback.print_exc()
        print("EXCEPCION:", e)
        sys.exit(1)

if __name__ == '__main__':
    main()
