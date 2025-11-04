# sqlstatement.py - Declaraciones SQL para el sistema de inventario empresarial
"""
Este módulo contiene todas las consultas SQL necesarias para el sistema de inventario.
Incluye soporte para soft delete con campos created_at, updated_at, deleted_at
"""

# =============================================================================
# CREACIÓN DE TABLAS CON SOFT DELETE Y AUDITORÍA
# =============================================================================

CREATE_TABLE_CATEGORIAS = """
CREATE TABLE IF NOT EXISTS categorias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL UNIQUE,
    descripcion TEXT,
    color_identificador TEXT DEFAULT '#3498db',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL
);
"""

CREATE_TABLE_PROVEEDORES = """
CREATE TABLE IF NOT EXISTS proveedores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_razon_social TEXT NOT NULL,
    cuit_rut TEXT UNIQUE,
    direccion TEXT,
    telefono TEXT,
    email TEXT,
    contacto_responsable TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL
);
"""

CREATE_TABLE_PRODUCTOS = """
CREATE TABLE IF NOT EXISTS productos (
    codigo_barras TEXT PRIMARY KEY,
    nombre TEXT NOT NULL,
    descripcion TEXT,
    categoria_id INTEGER,
    proveedor_id INTEGER,
    stock_actual INTEGER DEFAULT 0,
    stock_minimo INTEGER DEFAULT 0,
    precio_compra DECIMAL(10,2) DEFAULT 0.00,
    precio_venta DECIMAL(10,2) DEFAULT 0.00,
    fecha_ingreso DATE DEFAULT CURRENT_DATE,
    imagen_producto TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL,
    FOREIGN KEY (categoria_id) REFERENCES categorias(id),
    FOREIGN KEY (proveedor_id) REFERENCES proveedores(id)
);
"""

CREATE_TABLE_MOVIMIENTOS_STOCK = """
CREATE TABLE IF NOT EXISTS movimientos_stock (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo_barras_producto TEXT NOT NULL,
    tipo TEXT CHECK(tipo IN ('Entrada', 'Salida', 'Ajuste')) NOT NULL,
    cantidad INTEGER NOT NULL,
    precio_unitario DECIMAL(10,2) DEFAULT 0.00,
    motivo_descripcion TEXT,
    usuario_responsable TEXT DEFAULT 'Sistema',
    numero_documento_factura TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL,
    FOREIGN KEY (codigo_barras_producto) REFERENCES productos(codigo_barras)
);
"""

# =============================================================================
# TRIGGERS PARA ACTUALIZAR AUTOMÁTICAMENTE UPDATED_AT
# =============================================================================

CREATE_TRIGGER_CATEGORIAS_UPDATED_AT = """
CREATE TRIGGER IF NOT EXISTS trigger_categorias_updated_at
AFTER UPDATE ON categorias
FOR EACH ROW
WHEN NEW.updated_at = OLD.updated_at
BEGIN
    UPDATE categorias SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;
"""

CREATE_TRIGGER_PROVEEDORES_UPDATED_AT = """
CREATE TRIGGER IF NOT EXISTS trigger_proveedores_updated_at
AFTER UPDATE ON proveedores
FOR EACH ROW
WHEN NEW.updated_at = OLD.updated_at
BEGIN
    UPDATE proveedores SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;
"""

CREATE_TRIGGER_PRODUCTOS_UPDATED_AT = """
CREATE TRIGGER IF NOT EXISTS trigger_productos_updated_at
AFTER UPDATE ON productos
FOR EACH ROW
WHEN NEW.updated_at = OLD.updated_at
BEGIN
    UPDATE productos SET updated_at = CURRENT_TIMESTAMP WHERE codigo_barras = NEW.codigo_barras;
END;
"""

CREATE_TRIGGER_MOVIMIENTOS_UPDATED_AT = """
CREATE TRIGGER IF NOT EXISTS trigger_movimientos_updated_at
AFTER UPDATE ON movimientos_stock
FOR EACH ROW
WHEN NEW.updated_at = OLD.updated_at
BEGIN
    UPDATE movimientos_stock SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;
"""

# =============================================================================
# TRIGGER PARA ACTUALIZAR STOCK AUTOMÁTICAMENTE
# =============================================================================

CREATE_TRIGGER_ACTUALIZAR_STOCK = """
CREATE TRIGGER IF NOT EXISTS trigger_actualizar_stock
AFTER INSERT ON movimientos_stock
FOR EACH ROW
WHEN NEW.deleted_at IS NULL
BEGIN
    UPDATE productos 
    SET stock_actual = CASE 
        WHEN NEW.tipo = 'Entrada' THEN stock_actual + NEW.cantidad
        WHEN NEW.tipo = 'Salida' THEN stock_actual - NEW.cantidad
        WHEN NEW.tipo = 'Ajuste' THEN NEW.cantidad
        ELSE stock_actual
    END
    WHERE codigo_barras = NEW.codigo_barras_producto
    AND deleted_at IS NULL;
END;
"""

# =============================================================================
# ÍNDICES PARA OPTIMIZAR CONSULTAS
# =============================================================================

CREATE_INDEX_PRODUCTOS_DELETED_AT = "CREATE INDEX IF NOT EXISTS idx_productos_deleted_at ON productos(deleted_at);"
CREATE_INDEX_CATEGORIAS_DELETED_AT = "CREATE INDEX IF NOT EXISTS idx_categorias_deleted_at ON categorias(deleted_at);"
CREATE_INDEX_PROVEEDORES_DELETED_AT = "CREATE INDEX IF NOT EXISTS idx_proveedores_deleted_at ON proveedores(deleted_at);"
CREATE_INDEX_MOVIMIENTOS_DELETED_AT = "CREATE INDEX IF NOT EXISTS idx_movimientos_deleted_at ON movimientos_stock(deleted_at);"
CREATE_INDEX_PRODUCTOS_CATEGORIA = "CREATE INDEX IF NOT EXISTS idx_productos_categoria ON productos(categoria_id);"
CREATE_INDEX_PRODUCTOS_PROVEEDOR = "CREATE INDEX IF NOT EXISTS idx_productos_proveedor ON productos(proveedor_id);"
CREATE_INDEX_MOVIMIENTOS_PRODUCTO = "CREATE INDEX IF NOT EXISTS idx_movimientos_producto ON movimientos_stock(codigo_barras_producto);"

# =============================================================================
# VISTAS PARA SIMPLIFICAR CONSULTAS SIN REGISTROS ELIMINADOS
# =============================================================================

CREATE_VIEW_PRODUCTOS_ACTIVOS = """
CREATE VIEW IF NOT EXISTS v_productos_activos AS
SELECT 
    p.codigo_barras,
    p.nombre,
    p.descripcion,
    c.nombre as categoria_nombre,
    c.color_identificador as categoria_color,
    pr.nombre_razon_social as proveedor_nombre,
    p.stock_actual,
    p.stock_minimo,
    p.precio_compra,
    p.precio_venta,
    p.fecha_ingreso,
    p.imagen_producto,
    p.created_at,
    p.updated_at,
    CASE WHEN p.stock_actual <= p.stock_minimo THEN 1 ELSE 0 END as alerta_stock
FROM productos p
LEFT JOIN categorias c ON p.categoria_id = c.id AND c.deleted_at IS NULL
LEFT JOIN proveedores pr ON p.proveedor_id = pr.id AND pr.deleted_at IS NULL
WHERE p.deleted_at IS NULL;
"""

CREATE_VIEW_MOVIMIENTOS_ACTIVOS = """
CREATE VIEW IF NOT EXISTS v_movimientos_activos AS
SELECT 
    m.id,
    m.codigo_barras_producto,
    p.nombre as producto_nombre,
    m.tipo,
    m.cantidad,
    m.precio_unitario,
    m.motivo_descripcion,
    m.usuario_responsable,
    m.numero_documento_factura,
    m.created_at,
    m.updated_at
FROM movimientos_stock m
LEFT JOIN productos p ON m.codigo_barras_producto = p.codigo_barras AND p.deleted_at IS NULL
WHERE m.deleted_at IS NULL
ORDER BY m.created_at DESC;
"""

# =============================================================================
# CONSULTAS BÁSICAS CON SOFT DELETE
# =============================================================================

# CATEGORÍAS
SELECT_ALL_CATEGORIAS_ACTIVAS = "SELECT * FROM categorias WHERE deleted_at IS NULL ORDER BY nombre;"
SELECT_CATEGORIA_BY_ID = "SELECT * FROM categorias WHERE id = ? AND deleted_at IS NULL;"
INSERT_CATEGORIA = """
INSERT INTO categorias (nombre, descripcion, color_identificador) 
VALUES (?, ?, ?);
"""
UPDATE_CATEGORIA = """
UPDATE categorias SET nombre = ?, descripcion = ?, color_identificador = ? 
WHERE id = ? AND deleted_at IS NULL;
"""
SOFT_DELETE_CATEGORIA = "UPDATE categorias SET deleted_at = CURRENT_TIMESTAMP WHERE id = ?;"
RESTORE_CATEGORIA = "UPDATE categorias SET deleted_at = NULL WHERE id = ?;"

# Consultas adicionales para categorías
SELECT_BUSCAR_CATEGORIAS = """
SELECT * FROM categorias 
WHERE (nombre LIKE ? OR descripcion LIKE ?) AND deleted_at IS NULL
ORDER BY nombre;
"""
SELECT_PRODUCTOS_POR_CATEGORIA = """
SELECT COUNT(*) FROM productos 
WHERE categoria_id = ? AND deleted_at IS NULL;
"""

# PROVEEDORES
SELECT_ALL_PROVEEDORES_ACTIVOS = "SELECT * FROM proveedores WHERE deleted_at IS NULL ORDER BY nombre_razon_social;"
SELECT_PROVEEDOR_BY_ID = "SELECT * FROM proveedores WHERE id = ? AND deleted_at IS NULL;"
INSERT_PROVEEDOR = """
INSERT INTO proveedores (nombre_razon_social, cuit_rut, direccion, telefono, email, contacto_responsable) 
VALUES (?, ?, ?, ?, ?, ?);
"""
UPDATE_PROVEEDOR = """
UPDATE proveedores SET nombre_razon_social = ?, cuit_rut = ?, direccion = ?, 
telefono = ?, email = ?, contacto_responsable = ? 
WHERE id = ? AND deleted_at IS NULL;
"""
SOFT_DELETE_PROVEEDOR = "UPDATE proveedores SET deleted_at = CURRENT_TIMESTAMP WHERE id = ?;"
DELETE_PROVEEDOR = "UPDATE proveedores SET deleted_at = CURRENT_TIMESTAMP WHERE id = ?;"  # Alias para compatibilidad
RESTORE_PROVEEDOR = "UPDATE proveedores SET deleted_at = NULL WHERE id = ?;"

# Consultas adicionales para proveedores
SELECT_PROVEEDOR_BY_NAME = """
SELECT * FROM proveedores WHERE nombre_razon_social = ? AND deleted_at IS NULL;
"""

BUSCAR_PROVEEDORES = """
SELECT * FROM proveedores 
WHERE (nombre_razon_social LIKE ? OR cuit_rut LIKE ? OR email LIKE ?) AND deleted_at IS NULL
ORDER BY nombre_razon_social;
"""

# PRODUCTOS
SELECT_ALL_PRODUCTOS_ACTIVOS = "SELECT * FROM v_productos_activos ORDER BY nombre;"
SELECT_PRODUCTO_BY_CODIGO = "SELECT * FROM productos WHERE codigo_barras = ? AND deleted_at IS NULL;"
SELECT_PRODUCTOS_STOCK_BAJO = """
SELECT * FROM v_productos_activos 
WHERE stock_actual <= stock_minimo 
ORDER BY stock_actual ASC;
"""
INSERT_PRODUCTO = """
INSERT INTO productos (codigo_barras, nombre, descripcion, categoria_id, proveedor_id, 
stock_actual, stock_minimo, precio_compra, precio_venta, fecha_ingreso, imagen_producto) 
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
"""
UPDATE_PRODUCTO = """
UPDATE productos SET nombre = ?, descripcion = ?, categoria_id = ?, proveedor_id = ?, 
stock_minimo = ?, precio_compra = ?, precio_venta = ?, imagen_producto = ? 
WHERE codigo_barras = ? AND deleted_at IS NULL;
"""
SOFT_DELETE_PRODUCTO = "UPDATE productos SET deleted_at = CURRENT_TIMESTAMP WHERE codigo_barras = ?;"
RESTORE_PRODUCTO = "UPDATE productos SET deleted_at = NULL WHERE codigo_barras = ?;"

# Consultas adicionales para productos
SELECT_BUSCAR_PRODUCTOS = """
SELECT * FROM v_productos_activos 
WHERE codigo_barras LIKE ? OR nombre LIKE ? OR descripcion LIKE ?
ORDER BY nombre;
"""
SELECT_MOVIMIENTOS_RECIENTES_PRODUCTO = """
SELECT COUNT(*) FROM movimientos_stock 
WHERE codigo_barras_producto = ? 
AND deleted_at IS NULL 
AND created_at >= date('now', '-30 days');
"""

# MOVIMIENTOS DE STOCK
SELECT_ALL_MOVIMIENTOS_ACTIVOS = "SELECT * FROM v_movimientos_activos LIMIT 1000;"
SELECT_MOVIMIENTOS_BY_PRODUCTO = """
SELECT * FROM v_movimientos_activos 
WHERE codigo_barras_producto = ? 
ORDER BY created_at DESC;
"""
INSERT_MOVIMIENTO = """
INSERT INTO movimientos_stock (codigo_barras_producto, tipo, cantidad, precio_unitario, 
motivo_descripcion, usuario_responsable, numero_documento_factura) 
VALUES (?, ?, ?, ?, ?, ?, ?);
"""
SOFT_DELETE_MOVIMIENTO = "UPDATE movimientos_stock SET deleted_at = CURRENT_TIMESTAMP WHERE id = ?;"

# =============================================================================
# CONSULTAS PARA REPORTES Y ANÁLISIS
# =============================================================================

# Valor total del inventario
SELECT_VALOR_TOTAL_INVENTARIO = """
SELECT SUM(stock_actual * precio_venta) as valor_total
FROM productos 
WHERE deleted_at IS NULL AND stock_actual > 0;
"""

# Productos más vendidos (por cantidad de salidas)
SELECT_PRODUCTOS_MAS_VENDIDOS = """
SELECT 
    p.codigo_barras,
    p.nombre,
    SUM(m.cantidad) as total_vendido
FROM productos p
JOIN movimientos_stock m ON p.codigo_barras = m.codigo_barras_producto
WHERE p.deleted_at IS NULL 
AND m.deleted_at IS NULL 
AND m.tipo = 'Salida'
AND m.created_at >= date('now', '-30 days')
GROUP BY p.codigo_barras, p.nombre
ORDER BY total_vendido DESC
LIMIT 10;
"""

# Movimientos por tipo y fecha
SELECT_MOVIMIENTOS_POR_FECHA = """
SELECT 
    DATE(created_at) as fecha,
    tipo,
    COUNT(*) as cantidad_movimientos,
    SUM(cantidad) as cantidad_total
FROM movimientos_stock 
WHERE deleted_at IS NULL
AND created_at >= date('now', '-30 days')
GROUP BY DATE(created_at), tipo
ORDER BY fecha DESC, tipo;
"""

# Alertas de stock crítico
SELECT_ALERTAS_STOCK_CRITICO = """
SELECT COUNT(*) as productos_criticos
FROM productos 
WHERE deleted_at IS NULL 
AND stock_actual <= stock_minimo;
"""

# =============================================================================
# CONSULTAS ESPECÍFICAS DEL MÓDULO PRODUCTOS_MANAGER
# =============================================================================

# Consultas para combos y selects
SELECT_CATEGORIAS_NOMBRES = """
SELECT nombre FROM categorias WHERE deleted_at IS NULL ORDER BY nombre;
"""

SELECT_PROVEEDORES_NOMBRES = """
SELECT nombre_razon_social FROM proveedores WHERE deleted_at IS NULL ORDER BY nombre_razon_social;
"""

SELECT_CATEGORIA_ID_BY_NOMBRE = """
SELECT id FROM categorias WHERE nombre = ? AND deleted_at IS NULL;
"""

SELECT_PROVEEDOR_ID_BY_NOMBRE = """
SELECT id FROM proveedores WHERE nombre_razon_social = ? AND deleted_at IS NULL;
"""

# Consultas de actualización
UPDATE_PRODUCTO_COMPLETO = """
UPDATE productos SET 
    codigo_barras = ?,
    nombre = ?, 
    descripcion = ?,
    categoria_id = ?,
    proveedor_id = ?,
    stock_actual = ?,
    stock_minimo = ?,
    precio_compra = ?,
    precio_venta = ?,
    imagen_producto = ?,
    updated_at = CURRENT_TIMESTAMP
WHERE codigo_barras = ? AND deleted_at IS NULL;
"""

# Consulta de eliminación (soft delete)
DELETE_PRODUCTO_SOFT = """
UPDATE productos SET 
    deleted_at = CURRENT_TIMESTAMP,
    updated_at = CURRENT_TIMESTAMP
WHERE codigo_barras = ? AND deleted_at IS NULL;
"""