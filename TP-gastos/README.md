# Trabajo Práctico: Sistema de Control de Gastos

## 🎯 Objetivo

Completar la implementación de un Sistema de Control de Gastos y Presupuesto Personal desarrollado con Python y DearPyGUI.

## 📚 Contenido

Este Trabajo Práctico contiene:
- ✅ Base de datos SQLite completamente configurada
- ✅ Interfaz gráfica completa con DearPyGUI
- ✅ Estructura de módulos y managers
- 🔧 **Funciones CRUD a completar por el alumno**
- 🔧 **Callbacks de interfaz a implementar**
- 🔧 **Filtros y reportes a desarrollar**

## 📖 Instrucciones Completas

Lee el archivo **`INSTRUCCIONES.md`** para obtener:
- Descripción detallada del proyecto
- Lista completa de funcionalidades a implementar
- Guía paso a paso con ejemplos
- Criterios de evaluación
- Casos de prueba recomendados

## 🚀 Inicio Rápido

### 1. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 2. Cargar Datos de Prueba

```bash
python datos_prueba.py
```

Este script creará:
- 10 categorías de ejemplo
- 41 transacciones variadas
- Una base de datos lista para usar

### 3. Ejecutar la Aplicación

```bash
python main.py
```

## 📁 Archivos a Modificar

Debes completar los métodos marcados con `# TODO:` en:

1. **`modules/categorias_manager.py`** - CRUD de categorías
2. **`modules/transacciones_manager.py`** - CRUD de transacciones y reportes
3. **`modules/ui_manager.py`** - Callbacks de la interfaz

## ⚠️ Archivos que NO Debes Modificar

- `main.py` - Punto de entrada (ya completo)
- `modules/database_manager.py` - Gestión de BD (ya completo)
- `modules/sqlstatement.py` - Consultas SQL (ya definidas)
- `lib/myfunctions/myscreen.py` - Utilidades (ya completo)

## ✅ Funcionalidades Requeridas

### Gestión de Categorías
- [ ] Agregar categoría
- [ ] Actualizar categoría
- [ ] Listar categorías
- [ ] Obtener categoría por ID
- [ ] Eliminar categoría (soft delete)

### Gestión de Transacciones
- [ ] Agregar transacción (ingreso/egreso)
- [ ] Actualizar transacción
- [ ] Listar transacciones
- [ ] Obtener transacción por ID
- [ ] Eliminar transacción (soft delete)
- [ ] Filtrar por tipo, categoría y fechas

### Reportes
- [ ] Resumen de balance (ingresos - egresos)
- [ ] Datos para gráfico de barras por categoría
- [ ] Datos para gráfico circular

### Interfaz
- [ ] Callback agregar transacción
- [ ] Callback agregar categoría
- [ ] Aplicar filtros
- [ ] Actualizar gráficos

## 🧪 Cómo Probar

1. **Agregar Categoría**
   - Ir a pestaña "Categorías"
   - Llenar formulario y hacer clic en "Agregar"
   - Verificar que aparece en la tabla

2. **Agregar Transacción**
   - Ir a pestaña "Transacciones"
   - Llenar formulario y hacer clic en "Agregar Transacción"
   - Verificar que aparece en la tabla

3. **Filtrar Transacciones**
   - Seleccionar filtros (tipo, categoría, fechas)
   - Hacer clic en "Aplicar Filtros"
   - Verificar que solo muestra las transacciones que cumplen

4. **Ver Reportes**
   - Ir a pestaña "Reportes"
   - Seleccionar tipo de gráfico
   - Verificar que se muestra correctamente

## 💡 Consejos

- Lee primero **TODO** el código antes de empezar
- Implementa en orden: Categorías → Transacciones → UI
- Prueba cada función individualmente
- Usa `logger.info()` para debugging
- Consulta `sqlstatement.py` para ver las queries disponibles

## 📊 Evaluación

- **60%** - Funcionalidad (CRUD completo)
- **30%** - Código (validaciones, manejo de errores)
- **10%** - Interfaz (actualización de tablas y mensajes)

## 📦 Entrega

Comprimir la carpeta completa:
```bash
zip -r TP_Gastos_ApellidoNombre.zip TP-gastos/
```

**Excluir:**
- `gastos.db` (base de datos)
- `__pycache__/` (archivos temporales)
- `exports/` (exportaciones)

## 🆘 Ayuda

Si tienes dudas:
1. Lee primero las **INSTRUCCIONES.md** completas
2. Revisa los ejemplos de código comentados
3. Consulta con el docente en horario de clase

---

**¡Éxitos con el Trabajo Práctico!** 🚀
