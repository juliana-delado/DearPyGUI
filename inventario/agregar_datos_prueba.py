#!/usr/bin/env python3
"""
Script para agregar datos de prueba al inventario
"""

from modules.productos_manager import ProductosManager
from modules.categorias_manager import CategoriasManager
from modules.proveedores_manager import ProveedoresManager

def main():
    """Agregar algunos datos de prueba"""
    try:
        # Inicializar managers
        productos_manager = ProductosManager("inventario.db")
        categorias_manager = CategoriasManager("inventario.db")
        proveedores_manager = ProveedoresManager("inventario.db")
        
        print("Agregando datos de prueba...")
        
        # Agregar algunas categorías si no existen
        categorias_manager.agregar_categoria("Electrónicos", "Productos electrónicos", "#3498db")
        categorias_manager.agregar_categoria("Hogar", "Productos para el hogar", "#2ecc71")
        
        # Agregar algunos proveedores si no existen
        proveedores_manager.agregar_proveedor(
            "TechCorp SA", "20-12345678-9", "Av. Tecnología 123", 
            "011-1234-5678", "ventas@techcorp.com", "Juan Pérez"
        )
        
        # Agregar algunos productos de prueba
        productos_manager.agregar_producto(
            codigo_barras="1111111111111",
            nombre="Teléfono Celular",
            descripcion="Smartphone básico",
            categoria_id=1,
            proveedor_id=1,
            stock_actual=10,
            stock_minimo=5,
            precio_venta=150.00
        )
        
        productos_manager.agregar_producto(
            codigo_barras="2222222222222", 
            nombre="Auriculares Bluetooth",
            descripcion="Auriculares inalámbricos de alta calidad",
            categoria_id=1,
            proveedor_id=1,
            stock_actual=25,
            stock_minimo=10,
            precio_venta=75.50
        )
        
        productos_manager.agregar_producto(
            codigo_barras="3333333333333",
            nombre="Lámpara de Mesa", 
            descripcion="Lámpara LED regulable",
            categoria_id=2,
            proveedor_id=1,
            stock_actual=8,
            stock_minimo=3,
            precio_venta=45.99
        )
        
        print("✅ Datos de prueba agregados exitosamente!")
        print("Productos en la base de datos:")
        
        productos = productos_manager.obtener_todos_productos()
        for producto in productos:
            print(f"  - {producto[0]}: {producto[1]} (Stock: {producto[6]}, Precio: ${producto[9]})")
            
    except Exception as e:
        print(f"❌ Error agregando datos: {e}")

if __name__ == "__main__":
    main()