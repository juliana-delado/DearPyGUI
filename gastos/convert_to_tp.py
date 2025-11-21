#!/usr/bin/env python3
"""
Script para convertir los managers en versión TP (con TODOs)
"""

import re

# Archivo categorias_manager.py
with open('/home/dcazabat/Documentos/Instituto/primero/Materia/DearPyGUI/TP-gastos/modules/categorias_manager.py', 'r') as f:
    content = f.read()

# Reemplazar métodos con versiones TODO
content = content.replace(
    '''    def agregar_categoria(self, nombre: str, descripcion: str = "") -> bool:
        """
        Agregar una nueva categoría
        
        Args:
            nombre (str): Nombre de la categoría
            descripcion (str): Descripción opcional
            
        Returns:
            bool: True si se agregó correctamente
        """
        try:
            if not nombre.strip():
                logger.warning("⚠️ El nombre de la categoría no puede estar vacío")
                return False
            
            rows_affected = self.execute_command(sql.INSERT_CATEGORIA, (nombre.strip(), descripcion.strip()))
            
            if rows_affected > 0:
                logger.info(f"✅ Categoría '{nombre}' agregada correctamente")
                return True
            else:
                logger.error("❌ No se pudo agregar la categoría")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error agregando categoría: {e}")
            return False''',
    '''    def agregar_categoria(self, nombre: str, descripcion: str = "") -> bool:
        """
        Agregar una nueva categoría
        
        Args:
            nombre (str): Nombre de la categoría
            descripcion (str): Descripción opcional
            
        Returns:
            bool: True si se agregó correctamente
            
        TODO: Implementa este método siguiendo estos pasos:
        1. Validar que el nombre no esté vacío (usar nombre.strip())
        2. Si está vacío, hacer logger.warning() y retornar False
        3. Ejecutar INSERT usando: self.execute_command(sql.INSERT_CATEGORIA, (nombre, descripcion))
        4. Si rows_affected > 0, hacer logger.info() y retornar True
        5. Si no, hacer logger.error() y retornar False
        6. Capturar excepciones con try-except, logger.error() y retornar False
        """
        # TODO: IMPLEMENTAR AQUÍ
        logger.info("✅ Agregar categoría - Funcionalidad pendiente")
        return False'''
)

content = content.replace(
    '''    def obtener_categorias(self) -> list:
        """
        Obtener todas las categorías activas
        
        Returns:
            list: Lista de tuplas con las categorías
        """
        return self.execute_query(sql.SELECT_CATEGORIAS_ACTIVAS)''',
    '''    def obtener_categorias(self) -> list:
        """
        Obtener todas las categorías activas
        
        Returns:
            list: Lista de tuplas con las categorías (id, nombre, descripcion)
            
        TODO: Implementa este método:
        1. Ejecutar consulta: self.execute_query(sql.SELECT_CATEGORIAS_ACTIVAS)
        2. Retornar directamente el resultado (es una lista de tuplas)
        """
        # TODO: IMPLEMENTAR AQUÍ
        logger.info("✅ Obtener categorías - Funcionalidad pendiente")
        return []'''
)

content = content.replace(
    '''    def obtener_nombres_categorias(self) -> list:
        """
        Obtener lista de nombres de categorías para combos
        
        Returns:
            list: Lista de strings con los nombres
        """
        categorias = self.obtener_categorias()
        return [cat[1] for cat in categorias]''',
    '''    def obtener_nombres_categorias(self) -> list:
        """
        Obtener lista de nombres de categorías para usar en combos/dropdowns
        
        Returns:
            list: Lista de strings con los nombres de categorías
            
        TODO: Implementa este método:
        1. Obtener todas las categorías usando self.obtener_categorias()
        2. De cada tupla (id, nombre, descripcion), extraer solo el nombre
        3. Retornar una lista solo con los nombres
        
        Ejemplo:
            categorias = self.obtener_categorias()
            return [cat[1] for cat in categorias]  # cat[1] es el nombre
        """
        # TODO: IMPLEMENTAR AQUÍ
        logger.info("✅ Obtener nombres de categorías - Funcionalidad pendiente")
        return []'''
)

# Guardar cambios
with open('/home/dcazabat/Documentos/Instituto/primero/Materia/DearPyGUI/TP-gastos/modules/categorias_manager.py', 'w') as f:
    f.write(content)

print("✅ categorias_manager.py convertido a TP")
