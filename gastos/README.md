# Sistema de Control de Gastos y Presupuesto Personal

Un sistema completo para el control de ingresos y egresos personales, desarrollado con DearPyGUI.

## Características

- ✅ **Control de Ingresos y Egresos**: Registra todos tus movimientos financieros
- ✅ **Categorización**: Organiza tus gastos por categorías personalizables
- ✅ **Filtrado Avanzado**: Filtra por categorías y rangos de fechas
- ✅ **Gráficos Interactivos**: Visualiza tus finanzas con gráficos de barras y torta
- ✅ **Interfaz Moderna**: UI intuitiva desarrollada con DearPyGUI
- ✅ **Base de Datos SQLite**: Almacenamiento local y seguro

## Estructura del Proyecto

```
gastos/
├── main.py                 # Aplicación principal
├── datos_prueba.py         # Script para poblar datos de prueba
├── lib/
│   └── myfunctions/
│       ├── __init__.py
│       └── myscreen.py     # Utilidades de pantalla
├── modules/
│   ├── __init__.py
│   ├── base_model.py       # Clase base con soft delete
│   ├── database_manager.py # Gestión de base de datos
│   ├── categorias_manager.py # Gestión de categorías
│   ├── transacciones_manager.py # Gestión de transacciones
│   ├── ui_manager.py       # Gestión de interfaz de usuario
│   └── sqlstatement.py     # Sentencias SQL
├── images/                 # Imágenes y recursos
├── exports/                # Archivos exportados
└── README.md              # Este archivo
```

## Instalación

1. **Requisitos previos**:

   ```bash
   pip install dearpygui screeninfo
   ```

2. **Ejecutar la aplicación**:

   ```bash
   python main.py
   ```

3. **Poblar datos de prueba** (opcional):

   ```bash
   python datos_prueba.py
   ```

## Uso

### Agregar Transacciones

1. Ve a la pestaña "Transacciones"
2. Selecciona el tipo (ingreso/egreso)
3. Ingresa el monto
4. Selecciona una categoría
5. Agrega una descripción
6. Elige la fecha
7. Haz clic en "Agregar"

### Gestionar Categorías

1. Ve a la pestaña "Categorías"
2. Ingresa el nombre y descripción
3. Haz clic en "Agregar"

### Visualizar Reportes

1. Ve a la pestaña "Reportes"
2. Selecciona el tipo de gráfico:
   - **Categorías (Torta)**: Distribución de gastos por categoría
   - **Categorías (Barras)**: Comparación de montos por categoría
   - **Mensual (Barras)**: Evolución mensual de ingresos/egresos
3. Opcionalmente filtra por tipo (ingreso/egreso)

### Filtrar Transacciones

- Usa los controles de filtro en la pestaña "Transacciones"
- Filtra por tipo, categoría y rango de fechas
- Los resultados se actualizan automáticamente

## Funcionalidades Técnicas

- **Soft Delete**: Los registros eliminados se marcan como tales, no se borran físicamente
- **Auditoría**: Seguimiento automático de creación y modificación
- **Índices Optimizados**: Consultas rápidas en campos frecuentemente usados
- **Vistas SQL**: Simplificación de consultas complejas
- **Transacciones ACID**: Integridad de datos garantizada

## Uso

### Agregar Transacciones

1. En la pestaña "Transacciones", selecciona el tipo (Ingreso/Gasto)
2. Ingresa el monto
3. Selecciona una categoría
4. Agrega una descripción (opcional)
5. Ingresa la fecha en formato YYYY-MM-DD (ej: 2025-10-22)
6. Haz clic en "Agregar Transacción"

### Filtrar Transacciones

- Filtra por tipo (Ingreso/Gasto)
- Filtra por categoría
- Filtra por rango de fechas (formato: YYYY-MM-DD)
- Haz clic en "Aplicar Filtros"

### Ver Gráficos

1. Ve a la pestaña "Reportes"
2. Selecciona el tipo de gráfico
3. Opcionalmente filtra por tipo de transacción
4. Haz clic en "Actualizar Gráfico"

### Gestionar Categorías

1. Ve a la pestaña "Categorías"
2. Agrega, edita o elimina categorías
3. Cada categoría puede tener un nombre y descripción

## Notas Técnicas

### Formato de Fechas

El sistema utiliza campos de texto para las fechas en lugar de date pickers por compatibilidad con todas las versiones de DearPyGUI. Formato esperado: **YYYY-MM-DD** (ej: 2025-10-22)

### Gráficos

Los gráficos utilizan índices numéricos con etiquetas personalizadas en los ejes para mostrar correctamente las categorías y meses. Todos los valores se convierten explícitamente a `float` para compatibilidad con DearPyGUI.

## Tecnologías Utilizadas

- **DearPyGUI**: Framework para interfaz gráfica
- **SQLite**: Base de datos local
- **Python**: Lenguaje de programación
- **Screeninfo**: Gestión de múltiples monitores

## Desarrollo

El proyecto sigue la misma estructura y patrones que los sistemas `biblio` e `inventario`, manteniendo consistencia en el código y arquitectura.

## Contribución

Para contribuir al proyecto:

1. Sigue la estructura existente
2. Mantén la separación de responsabilidades
3. Agrega documentación a nuevas funciones
4. Prueba los cambios antes de enviar

## Licencia

Este proyecto está bajo la Licencia MIT. Ver archivo `LICENSE` en el directorio raíz.
