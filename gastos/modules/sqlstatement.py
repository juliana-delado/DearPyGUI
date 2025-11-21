# sqlstatement.py - Sentencias SQL para el Sistema de Control de Gastos y Presupuesto Personal

# ================================
# CREACIÓN DE TABLAS
# ================================

CREATE_TABLE_CATEGORIAS = '''
CREATE TABLE IF NOT EXISTS categorias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL UNIQUE,
    descripcion TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    deleted_at DATETIME NULL
)
'''

CREATE_TABLE_TRANSACCIONES = '''
CREATE TABLE IF NOT EXISTS transacciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo TEXT NOT NULL CHECK(tipo IN ('ingreso', 'egreso')),
    monto REAL NOT NULL,
    categoria_id INTEGER,
    descripcion TEXT,
    fecha DATE NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    deleted_at DATETIME NULL,
    FOREIGN KEY (categoria_id) REFERENCES categorias(id)
)
'''

# ================================
# TRIGGERS PARA AUDITORÍA
# ================================

CREATE_TRIGGER_UPDATE_CATEGORIAS = '''
CREATE TRIGGER IF NOT EXISTS update_categorias_updated_at
AFTER UPDATE ON categorias
FOR EACH ROW
BEGIN
    UPDATE categorias SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;
'''

CREATE_TRIGGER_UPDATE_TRANSACCIONES = '''
CREATE TRIGGER IF NOT EXISTS update_transacciones_updated_at
AFTER UPDATE ON transacciones
FOR EACH ROW
BEGIN
    UPDATE transacciones SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;
'''

# ================================
# ÍNDICES PARA OPTIMIZACIÓN
# ================================

CREATE_INDEX_TRANSACCIONES_FECHA = '''
CREATE INDEX IF NOT EXISTS idx_transacciones_fecha ON transacciones(fecha);
'''

CREATE_INDEX_TRANSACCIONES_TIPO = '''
CREATE INDEX IF NOT EXISTS idx_transacciones_tipo ON transacciones(tipo);
'''

CREATE_INDEX_TRANSACCIONES_CATEGORIA = '''
CREATE INDEX IF NOT EXISTS idx_transacciones_categoria ON transacciones(categoria_id);
'''

# ================================
# VISTAS PARA REPORTES
# ================================

CREATE_VIEW_RESUMEN_MENSUAL = '''
CREATE VIEW IF NOT EXISTS resumen_mensual AS
SELECT
    strftime('%Y-%m', fecha) as mes,
    tipo,
    SUM(monto) as total,
    COUNT(*) as cantidad
FROM transacciones
WHERE deleted_at IS NULL
GROUP BY strftime('%Y-%m', fecha), tipo
ORDER BY mes DESC, tipo;
'''

CREATE_VIEW_RESUMEN_CATEGORIAS = '''
CREATE VIEW IF NOT EXISTS resumen_categorias AS
SELECT
    c.nombre as categoria,
    t.tipo,
    SUM(t.monto) as total,
    COUNT(*) as cantidad
FROM transacciones t
JOIN categorias c ON t.categoria_id = c.id
WHERE t.deleted_at IS NULL AND c.deleted_at IS NULL
GROUP BY c.nombre, t.tipo
ORDER BY total DESC;
'''

# ================================
# OPERACIONES CRUD - CATEGORIAS
# ================================

INSERT_CATEGORIA = '''
INSERT INTO categorias (nombre, descripcion)
VALUES (?, ?)
'''

UPDATE_CATEGORIA = '''
UPDATE categorias
SET nombre = ?, descripcion = ?, updated_at = CURRENT_TIMESTAMP
WHERE id = ? AND deleted_at IS NULL
'''

SELECT_CATEGORIAS_ACTIVAS = '''
SELECT id, nombre, descripcion, created_at, updated_at
FROM categorias
WHERE deleted_at IS NULL
ORDER BY nombre
'''

SELECT_CATEGORIA_BY_ID = '''
SELECT id, nombre, descripcion, created_at, updated_at
FROM categorias
WHERE id = ? AND deleted_at IS NULL
'''

# ================================
# OPERACIONES CRUD - TRANSACCIONES
# ================================

INSERT_TRANSACCION = '''
INSERT INTO transacciones (tipo, monto, categoria_id, descripcion, fecha)
VALUES (?, ?, ?, ?, ?)
'''

UPDATE_TRANSACCION = '''
UPDATE transacciones
SET tipo = ?, monto = ?, categoria_id = ?, descripcion = ?, fecha = ?, updated_at = CURRENT_TIMESTAMP
WHERE id = ? AND deleted_at IS NULL
'''

SELECT_TRANSACCIONES_ACTIVAS = '''
SELECT t.id, t.tipo, t.monto, c.nombre as categoria, t.descripcion, t.fecha, t.created_at, t.updated_at
FROM transacciones t
LEFT JOIN categorias c ON t.categoria_id = c.id
WHERE t.deleted_at IS NULL AND (c.deleted_at IS NULL OR c.id IS NULL)
ORDER BY t.fecha DESC, t.created_at DESC
'''

SELECT_TRANSACCIONES_BY_FILTRO = '''
SELECT t.id, t.tipo, t.monto, c.nombre as categoria, t.descripcion, t.fecha, t.created_at, t.updated_at
FROM transacciones t
LEFT JOIN categorias c ON t.categoria_id = c.id
WHERE t.deleted_at IS NULL AND (c.deleted_at IS NULL OR c.id IS NULL)
AND (? IS NULL OR t.tipo = ?)
AND (? IS NULL OR c.nombre = ?)
AND (? IS NULL OR t.fecha >= ?)
AND (? IS NULL OR t.fecha <= ?)
ORDER BY t.fecha DESC, t.created_at DESC
'''

SELECT_TRANSACCION_BY_ID = '''
SELECT t.id, t.tipo, t.monto, t.categoria_id, c.nombre as categoria, t.descripcion, t.fecha, t.created_at, t.updated_at
FROM transacciones t
LEFT JOIN categorias c ON t.categoria_id = c.id
WHERE t.id = ? AND t.deleted_at IS NULL AND (c.deleted_at IS NULL OR c.id IS NULL)
'''

# ================================
# REPORTES Y ESTADÍSTICAS
# ================================

SELECT_TOTALES_POR_TIPO = '''
SELECT tipo, SUM(monto) as total
FROM transacciones
WHERE deleted_at IS NULL
GROUP BY tipo
'''

SELECT_TOTALES_POR_CATEGORIA = '''
SELECT c.nombre as categoria, t.tipo, SUM(t.monto) as total
FROM transacciones t
JOIN categorias c ON t.categoria_id = c.id
WHERE t.deleted_at IS NULL AND c.deleted_at IS NULL
GROUP BY c.nombre, t.tipo
ORDER BY total DESC
'''

SELECT_TOTALES_POR_MES = '''
SELECT strftime('%Y-%m', fecha) as mes, tipo, SUM(monto) as total
FROM transacciones
WHERE deleted_at IS NULL
GROUP BY strftime('%Y-%m', fecha), tipo
ORDER BY mes DESC
'''

SELECT_BALANCE_ACTUAL = '''
SELECT
    (SELECT COALESCE(SUM(monto), 0) FROM transacciones WHERE tipo = 'ingreso' AND deleted_at IS NULL) -
    (SELECT COALESCE(SUM(monto), 0) FROM transacciones WHERE tipo = 'egreso' AND deleted_at IS NULL) as balance
'''