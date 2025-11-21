# datos_prueba.py - Datos de prueba para el sistema de gastos
"""
Script para poblar la base de datos con datos de prueba.
Ejecutar después de inicializar la aplicación por primera vez.
"""

import sys
import os
from datetime import datetime, timedelta
import random

# Agregar el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.database_manager import DatabaseManager
from modules.categorias_manager import CategoriasManager
from modules.transacciones_manager import TransaccionesManager

def poblar_datos_prueba():
    """Poblar la base de datos con datos de prueba"""
    
    print("🌱 Poblando datos de prueba...")
    
    # Inicializar managers
    db_manager = DatabaseManager()
    categorias_manager = CategoriasManager()
    transacciones_manager = TransaccionesManager()
    
    # Categorías de prueba
    categorias = [
        ("Alimentación", "Gastos en comida y restaurantes"),
        ("Transporte", "Gastos en transporte público y combustible"),
        ("Vivienda", "Alquiler, servicios, mantenimiento"),
        ("Salud", "Médicos, medicamentos, seguros"),
        ("Educación", "Cursos, libros, materiales"),
        ("Entretenimiento", "Cine, música, hobbies"),
        ("Ropa", "Vestimenta y accesorios"),
        ("Tecnología", "Electrónicos, software, internet"),
        ("Viajes", "Vacaciones y viajes"),
        ("Otros", "Gastos varios")
    ]
    
    print("📂 Creando categorías...")
    for nombre, descripcion in categorias:
        if categorias_manager.agregar_categoria(nombre, descripcion):
            print(f"✅ Categoría '{nombre}' creada")
        else:
            print(f"⚠️ Categoría '{nombre}' ya existe")
    
    # Obtener IDs de categorías
    cats = categorias_manager.obtener_categorias()
    cat_dict = {cat[1]: cat[0] for cat in cats}
    
    # Transacciones de prueba
    print("💰 Creando transacciones de prueba...")
    
    # Ingresos
    ingresos = [
        ("Salario", 2500.00, "2024-01-01"),
        ("Freelance", 800.00, "2024-01-15"),
        ("Salario", 2500.00, "2024-02-01"),
        ("Bonificación", 300.00, "2024-02-10"),
        ("Salario", 2500.00, "2024-03-01"),
    ]
    
    # Egresos por categoría
    egresos = {
        "Alimentación": [
            ("Supermercado", 150.50, "2024-01-05"),
            ("Restaurante", 45.00, "2024-01-12"),
            ("Café", 8.50, "2024-01-18"),
            ("Supermercado", 120.30, "2024-02-02"),
            ("Restaurante", 32.00, "2024-02-15"),
            ("Café", 6.00, "2024-02-20"),
            ("Supermercado", 145.75, "2024-03-01"),
        ],
        "Transporte": [
            ("Gasolina", 60.00, "2024-01-08"),
            ("Transporte público", 25.00, "2024-01-08"),
            ("Gasolina", 55.00, "2024-02-05"),
            ("Transporte público", 25.00, "2024-02-08"),
            ("Gasolina", 58.00, "2024-03-03"),
        ],
        "Vivienda": [
            ("Alquiler", 800.00, "2024-01-01"),
            ("Electricidad", 75.00, "2024-01-10"),
            ("Internet", 50.00, "2024-01-15"),
            ("Alquiler", 800.00, "2024-02-01"),
            ("Electricidad", 72.00, "2024-02-10"),
            ("Internet", 50.00, "2024-02-15"),
            ("Alquiler", 800.00, "2024-03-01"),
        ],
        "Salud": [
            ("Consulta médica", 80.00, "2024-01-20"),
            ("Medicamentos", 25.00, "2024-01-22"),
            ("Seguro médico", 120.00, "2024-02-01"),
        ],
        "Entretenimiento": [
            ("Cine", 15.00, "2024-01-14"),
            ("Streaming", 12.99, "2024-01-01"),
            ("Concierto", 40.00, "2024-02-18"),
            ("Streaming", 12.99, "2024-02-01"),
        ],
        "Tecnología": [
            ("Software", 29.99, "2024-01-25"),
            ("Accesorios", 45.00, "2024-02-12"),
        ],
        "Otros": [
            ("Regalos", 35.00, "2024-01-30"),
            ("Donaciones", 20.00, "2024-02-14"),
        ]
    }
    
    # Agregar ingresos
    for desc, monto, fecha in ingresos:
        cat_id = cat_dict.get("Otros")  # Ingresos sin categoría específica
        if transacciones_manager.agregar_transaccion("ingreso", monto, cat_id, desc, fecha):
            print(f"✅ Ingreso: {desc} - ${monto} ({fecha})")
    
    # Agregar egresos
    for categoria, gastos in egresos.items():
        cat_id = cat_dict.get(categoria)
        for desc, monto, fecha in gastos:
            if transacciones_manager.agregar_transaccion("egreso", monto, cat_id, desc, fecha):
                print(f"✅ Egreso: {desc} - ${monto} en {categoria} ({fecha})")
    
    print("🎉 Datos de prueba creados exitosamente!")
    print(f"📊 Balance actual: ${transacciones_manager.obtener_balance_actual():.2f}")

if __name__ == "__main__":
    poblar_datos_prueba()