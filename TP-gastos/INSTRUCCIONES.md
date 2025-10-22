# Trabajo Práctico: Sistema de Control de Gastos y Presupuesto Personal

## 📋 Descripción

En este trabajo práctico deberás completar las funcionalidades faltantes de un Sistema de Control de Gastos y Presupuesto Personal desarrollado con Python y DearPyGUI.

El sistema ya cuenta con la estructura básica, la base de datos SQLite configurada, y la interfaz gráfica completa. Tu tarea será implementar las operaciones CRUD (Create, Read, Update, Delete) y funcionalidades de filtrado y reportes.

## 🎯 Objetivos de Aprendizaje

- Trabajar con bases de datos SQLite desde Python
- Implementar operaciones CRUD completas
- Manejar interfaces gráficas con DearPyGUI
- Aplicar filtros y generar reportes
- Trabajar con estructuras de datos (listas, tuplas, diccionarios)
- Validar datos de entrada del usuario

## 📁 Estructura del Proyecto

```
TP-gastos/
├── main.py                          # Punto de entrada de la aplicación
├── datos_prueba.py                  # Script para cargar datos de prueba
├── modules/
│   ├── database_manager.py          # ✅ COMPLETO - Gestión de base de datos
│   ├── categorias_manager.py        # 🔧 COMPLETAR - CRUD de categorías
│   ├── transacciones_manager.py     # 🔧 COMPLETAR - CRUD de transacciones
│   ├── ui_manager.py                # 🔧 COMPLETAR - Callbacks y filtros
│   └── sqlstatement.py              # ✅ COMPLETO - Sentencias SQL
├── lib/
│   └── myfunctions/
│       └── myscreen.py              # ✅ COMPLETO - Utilidades de pantalla
└── INSTRUCCIONES.md                 # Este archivo

```

## 🔧 Funcionalidades a Implementar

### 1. **Gestión de Categorías** (`modules/categorias_manager.py`)

Deberás completar los siguientes métodos:

- ✏️ `agregar_categoria()` - Agregar una nueva categoría
- ✏️ `actualizar_categoria()` - Modificar una categoría existente
- ✏️ `obtener_categorias()` - Listar todas las categorías activas
- ✏️ `obtener_categoria_por_id()` - Obtener una categoría específica
- ✏️ `obtener_nombres_categorias()` - Obtener lista de nombres para combos
- ✏️ `soft_delete()` - Marcar categoría como eliminada (borrado lógico)

### 2. **Gestión de Transacciones** (`modules/transacciones_manager.py`)

Deberás completar los siguientes métodos:

- ✏️ `agregar_transaccion()` - Registrar ingreso o egreso
- ✏️ `actualizar_transaccion()` - Modificar una transacción
- ✏️ `obtener_transaccion_por_id()` - Obtener datos de una transacción
- ✏️ `filtrar_transacciones()` - Aplicar filtros múltiples
- ✏️ `soft_delete()` - Marcar transacción como eliminada
- ✏️ `obtener_resumen_balance()` - Calcular balance (ingresos - egresos)
- ✏️ `obtener_datos_para_grafico_categorias()` - Datos para gráfico de barras
- ✏️ `obtener_datos_para_grafico_pie()` - Datos para gráfico circular

### 3. **Callbacks de la Interfaz** (`modules/ui_manager.py`)

Deberás completar los siguientes métodos de callback:

- ✏️ `agregar_transaccion()` - Procesar formulario de nueva transacción
- ✏️ `actualizar_transaccion()` - Guardar cambios de transacción editada
- ✏️ `agregar_categoria()` - Procesar formulario de nueva categoría
- ✏️ `actualizar_categoria()` - Guardar cambios de categoría editada
- ✏️ `aplicar_filtros()` - Filtrar transacciones por criterios
- ✏️ `limpiar_filtros()` - Resetear filtros aplicados
- ✏️ `actualizar_grafico()` - Regenerar gráficos con datos actuales

## 📝 Instrucciones Detalladas

### Paso 1: Entender la Base de Datos

Revisa el archivo `modules/sqlstatement.py` para entender:
- Estructura de las tablas `categorias` y `transacciones`
- Las consultas SQL ya definidas que puedes usar
- El sistema de borrado lógico (soft delete) con `deleted_at`

### Paso 2: Implementar CRUD de Categorías

1. Abre `modules/categorias_manager.py`
2. Busca los comentarios `# TODO:` que indican dónde debes trabajar
3. Implementa cada método siguiendo el patrón de ejemplo proporcionado
4. Usa los métodos heredados de `BaseModel`:
   - `execute_command(sql, params)` - Para INSERT, UPDATE, DELETE
   - `execute_query(sql, params)` - Para SELECT

**Ejemplo de implementación:**

```python
def agregar_categoria(self, nombre: str, descripcion: str = "") -> bool:
    """Agregar una nueva categoría"""
    try:
        # Validar que el nombre no esté vacío
        if not nombre or not nombre.strip():
            logger.warning("⚠️ El nombre de la categoría es obligatorio")
            return False
        
        # Ejecutar INSERT
        rows = self.execute_command(
            sql.INSERT_CATEGORIA, 
            (nombre.strip(), descripcion.strip())
        )
        
        if rows > 0:
            logger.info(f"✅ Categoría '{nombre}' agregada correctamente")
            return True
        return False
        
    except Exception as e:
        logger.error(f"❌ Error agregando categoría: {e}")
        return False
```

### Paso 3: Implementar CRUD de Transacciones

1. Abre `modules/transacciones_manager.py`
2. Implementa los métodos marcados con `# TODO:`
3. Presta atención a:
   - Validación del tipo ('ingreso' o 'egreso')
   - Validación de montos positivos
   - Manejo de fechas (usa `date.today().isoformat()`)
   - Verificación de existencia de categorías antes de asignar

### Paso 4: Implementar Callbacks de UI

1. Abre `modules/ui_manager.py`
2. Completa los métodos de callback que procesan las acciones del usuario
3. Cada callback debe:
   - Obtener valores de los widgets con `dpg.get_value(tag)`
   - Validar los datos
   - Llamar al método correspondiente del manager
   - Actualizar la interfaz (tablas, gráficos)
   - Mostrar mensaje de resultado

**Ejemplo de callback:**

```python
def agregar_transaccion(self):
    """Callback para agregar una nueva transacción"""
    try:
        # Obtener valores del formulario
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
        
        # Agregar transacción
        if self.app.transacciones_manager.agregar_transaccion(
            tipo, monto, categoria_id, descripcion, fecha
        ):
            self.actualizar_tabla_transacciones()
            self.actualizar_grafico()
            self.limpiar_formulario_transaccion()
            self.mostrar_mensaje("Transacción agregada correctamente")
        else:
            self.mostrar_mensaje("Error al agregar la transacción", error=True)
            
    except Exception as e:
        logger.error(f"❌ Error agregando transacción: {e}")
        self.mostrar_mensaje(f"Error: {str(e)}", error=True)
```

### Paso 5: Implementar Filtros

El método `filtrar_transacciones()` debe aceptar criterios opcionales:
- `tipo`: 'ingreso', 'egreso' o None
- `categoria`: nombre de categoría o None
- `fecha_desde`: fecha inicial o None
- `fecha_hasta`: fecha final o None

Usa la consulta SQL dinámica construyendo las condiciones WHERE según los parámetros recibidos.

### Paso 6: Implementar Reportes

Los métodos de reportes deben:
- `obtener_resumen_balance()`: Sumar ingresos y egresos, calcular diferencia
- `obtener_datos_para_grafico_categorias()`: Agrupar por categoría y sumar montos
- `obtener_datos_para_grafico_pie()`: Similar al anterior pero formato para gráfico circular

## ✅ Criterios de Evaluación

### Funcionalidad (60%)
- ✅ CRUD de categorías completo (15%)
- ✅ CRUD de transacciones completo (20%)
- ✅ Filtros funcionando correctamente (10%)
- ✅ Reportes con datos correctos (15%)

### Código (30%)
- ✅ Validaciones de datos apropiadas (10%)
- ✅ Manejo de errores con try-except (10%)
- ✅ Logging informativo (5%)
- ✅ Código limpio y comentado (5%)

### Interfaz (10%)
- ✅ Tablas se actualizan correctamente (5%)
- ✅ Mensajes claros al usuario (5%)

## 🧪 Pruebas

### Cargar Datos de Prueba

```bash
python datos_prueba.py
```

Esto creará:
- 10 categorías de ejemplo
- 41 transacciones variadas
- Balance inicial para probar

### Ejecutar la Aplicación

```bash
python main.py
```

### Casos de Prueba Recomendados

1. **Categorías**
   - ✅ Agregar categoría nueva
   - ✅ Editar categoría existente
   - ✅ Eliminar categoría (verificar soft delete)
   - ❌ Intentar agregar categoría sin nombre (debe fallar)

2. **Transacciones**
   - ✅ Agregar ingreso con categoría
   - ✅ Agregar egreso sin categoría
   - ✅ Editar transacción cambiando monto
   - ✅ Eliminar transacción (verificar soft delete)
   - ❌ Intentar agregar transacción con monto negativo (debe fallar)
   - ❌ Intentar agregar transacción sin tipo (debe fallar)

3. **Filtros**
   - ✅ Filtrar por tipo (solo ingresos)
   - ✅ Filtrar por categoría específica
   - ✅ Filtrar por rango de fechas
   - ✅ Combinar múltiples filtros
   - ✅ Limpiar filtros (mostrar todo)

4. **Reportes**
   - ✅ Verificar balance total correcto
   - ✅ Gráfico de barras muestra categorías con montos
   - ✅ Gráfico circular (pie) muestra proporciones

## 📚 Recursos Útiles

### Documentación DearPyGUI
- `dpg.get_value(tag)` - Obtener valor de widget
- `dpg.set_value(tag, value)` - Establecer valor de widget
- `dpg.configure_item(tag, **kwargs)` - Modificar propiedades

### SQLite con Python
- `cursor.execute(sql, params)` - Ejecutar consulta con parámetros
- `cursor.fetchall()` - Obtener todos los resultados
- `cursor.rowcount` - Número de filas afectadas

### Validaciones Comunes
```python
# Validar string no vacío
if not texto or not texto.strip():
    return False

# Validar número positivo
if valor <= 0:
    return False

# Validar tipo en opciones
if tipo not in ['ingreso', 'egreso']:
    return False
```

## 🚀 Entrega

### Formato de Entrega
- Comprimir la carpeta `TP-gastos` completa
- Nombre del archivo: `TP_Gastos_ApellidoNombre.zip`
- Incluir todos los archivos Python modificados
- NO incluir la base de datos (`gastos.db`)
- NO incluir `__pycache__` ni archivos temporales

### Contenido del ZIP
```
TP_Gastos_ApellidoNombre.zip
├── main.py
├── datos_prueba.py
├── modules/
│   ├── categorias_manager.py
│   ├── transacciones_manager.py
│   └── ui_manager.py
├── lib/
└── README.md (opcional con observaciones)
```

## ⚠️ Notas Importantes

1. **NO modifiques** los siguientes archivos:
   - `database_manager.py` (ya está completo)
   - `sqlstatement.py` (consultas SQL ya definidas)
   - `main.py` (estructura principal completa)

2. **Usa los métodos heredados** de `BaseModel` para interactuar con la BD

3. **Respeta las firmas de los métodos** (no cambies nombres ni parámetros)

4. **Todos los métodos deben retornar valores** apropiados (bool, list, dict, etc.)

5. **Incluye logging** en cada método para facilitar debugging

6. **Valida SIEMPRE** los datos antes de insertarlos en la BD

## 💡 Consejos

- Lee primero TODO el código antes de empezar
- Implementa en orden: Categorías → Transacciones → UI
- Prueba cada función individual antes de integrar
- Usa print() o logging para ver qué datos recibes
- Revisa los ejemplos ya implementados (eliminar, editar)
- Consulta con tus compañeros pero NO copies código
- Si algo no funciona, lee los mensajes de error con atención

## 🎓 Criterios de Aprobación

- **Nota mínima:** 60/100 puntos
- **Fecha de entrega:** [A definir por el docente]
- **Penalización por retraso:** [A definir por el docente]

---

**¡Éxitos con el Trabajo Práctico!** 🚀

Si tienes dudas, consulta con el docente durante las clases prácticas.
