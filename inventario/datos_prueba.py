# datos_prueba.py - Sets de datos de prueba para el sistema de inventario
"""
Sets de datos de prueba en formato de listas de diccionarios
para su uso posterior en carga de datos iniciales.
"""

# =============================================================================
# CATEGORÍAS DE EJEMPLO
# =============================================================================

CATEGORIAS_PRUEBA = [
    {
        'nombre': 'Electrónicos',
        'descripcion': 'Dispositivos electrónicos, computadoras, tablets y smartphones',
        'color': '#3498db'
    },
    {
        'nombre': 'Oficina y Papelería',
        'descripcion': 'Suministros de oficina, papelería y material administrativo',
        'color': '#2ecc71'
    },
    {
        'nombre': 'Mobiliario',
        'descripcion': 'Muebles de oficina, escritorios, sillas y almacenamiento',
        'color': '#8e44ad'
    },
    {
        'nombre': 'Herramientas',
        'descripcion': 'Herramientas manuales y eléctricas para mantenimiento',
        'color': '#e67e22'
    },
    {
        'nombre': 'Limpieza',
        'descripcion': 'Productos de limpieza y mantenimiento de instalaciones',
        'color': '#f39c12'
    },
    {
        'nombre': 'Seguridad',
        'descripcion': 'Equipos de protección personal y seguridad industrial',
        'color': '#e74c3c'
    },
    {
        'nombre': 'Alimentación',
        'descripcion': 'Productos comestibles para cafetería y eventos corporativos',
        'color': '#27ae60'
    },
    {
        'nombre': 'Textiles',
        'descripcion': 'Uniformes, ropa de trabajo y textiles corporativos',
        'color': '#9b59b6'
    },
    {
        'nombre': 'Comunicaciones',
        'descripcion': 'Equipos de telecomunicaciones y redes',
        'color': '#34495e'
    },
    {
        'nombre': 'Automotriz',
        'descripcion': 'Repuestos y accesorios para vehículos corporativos',
        'color': '#16a085'
    }
]

# =============================================================================
# PROVEEDORES DE EJEMPLO
# =============================================================================

PROVEEDORES_PRUEBA = [
    {
        'nombre': 'TecnoSoft S.A.',
        'cuit': '30-68521479-8',
        'direccion': 'Av. Corrientes 1234, CABA, Buenos Aires',
        'telefono': '+54 11 4567-8901',
        'email': 'ventas@tecnosoft.com.ar',
        'contacto': 'Juan Pérez - Gerente de Ventas'
    },
    {
        'nombre': 'OficiMax Distribuciones',
        'cuit': '33-71234567-9',
        'direccion': 'Calle San Martín 567, Rosario, Santa Fe',
        'telefono': '+54 341 456-7890',
        'email': 'pedidos@oficimax.com',
        'contacto': 'María González - Coordinadora Comercial'
    },
    {
        'nombre': 'MueblesPro Ltda.',
        'cuit': '30-85647123-5',
        'direccion': 'Zona Industrial Norte, Lote 45, Córdoba',
        'telefono': '+54 351 789-0123',
        'email': 'corporativo@mueblespro.com.ar',
        'contacto': 'Carlos Rodríguez - Director Comercial'
    },
    {
        'nombre': 'Herramientas del Sur',
        'cuit': '27-38459267-4',
        'direccion': 'Ruta 3 Km 15, La Plata, Buenos Aires',
        'telefono': '+54 221 567-8901',
        'email': 'info@herramientasdelsur.com',
        'contacto': 'Ana López - Jefa de Ventas'
    },
    {
        'nombre': 'CleanMax Productos',
        'cuit': '30-92345678-1',
        'direccion': 'Parque Industrial, Manzana 12, Mendoza',
        'telefono': '+54 261 234-5678',
        'email': 'ventas@cleanmax.com.ar',
        'contacto': 'Roberto Silva - Gerente Regional'
    },
    {
        'nombre': 'SafeTech Seguridad',
        'cuit': '33-46789012-3',
        'direccion': 'Av. 9 de Julio 2890, CABA, Buenos Aires',
        'telefono': '+54 11 9876-5432',
        'email': 'seguridad@safetech.com.ar',
        'contacto': 'Laura Martínez - Especialista en EPP'
    },
    {
        'nombre': 'AlimentAR Distribuidora',
        'cuit': '30-75395148-7',
        'direccion': 'Mercado Central, Nave 23, Buenos Aires',
        'telefono': '+54 11 4321-0987',
        'email': 'corporativo@alimentar.com',
        'contacto': 'Diego Fernández - Coordinador B2B'
    },
    {
        'nombre': 'TextilCorp S.R.L.',
        'cuit': '27-65432109-8',
        'direccion': 'Distrito Textil, Calle Industria 456, Tucumán',
        'telefono': '+54 381 654-3210',
        'email': 'uniformes@textilcorp.com.ar',
        'contacto': 'Patricia Morales - Ejecutiva de Cuentas'
    },
    {
        'nombre': 'Conecta Telecomunicaciones',
        'cuit': '30-54321987-6',
        'direccion': 'Polo Tecnológico, Edificio A, Piso 8, CABA',
        'telefono': '+54 11 2345-6789',
        'email': 'enterprise@conecta.net.ar',
        'contacto': 'Martín Castro - Gerente Técnico'
    },
    {
        'nombre': 'AutoParts Nacional',
        'cuit': '33-98765432-1',
        'direccion': 'Autopista Panamericana Km 32, Buenos Aires',
        'telefono': '+54 11 8765-4321',
        'email': 'flota@autoparts.com.ar',
        'contacto': 'Alejandro Ruiz - Especialista en Flotas'
    }
]

# =============================================================================
# PRODUCTOS DE EJEMPLO
# =============================================================================

PRODUCTOS_PRUEBA = [
    {
        'codigo_barras': '7891234567890',
        'nombre': 'Laptop Dell Inspiron 15 3000',
        'descripcion': 'Intel i5, 8GB RAM, 256GB SSD, Windows 11 Pro',
        'categoria_id': 1,
        'proveedor_id': 1,
        'stock_actual': 25,
        'stock_minimo': 5,
        'precio_compra': 850000.00,
        'precio_venta': 1200000.00,
        'ubicacion': 'Estante A-01',
        'imagen': 'laptop_dell_inspiron.jpg'
    },
    {
        'codigo_barras': '7891234567891',
        'nombre': 'Monitor Samsung 24" Full HD',
        'descripcion': 'Panel IPS, 75Hz, HDMI/VGA, ajustable en altura',
        'categoria_id': 1,
        'proveedor_id': 1,
        'stock_actual': 18,
        'stock_minimo': 8,
        'precio_compra': 180000.00,
        'precio_venta': 250000.00,
        'ubicacion': 'Estante A-02',
        'imagen': 'monitor_samsung_24.jpg'
    },
    {
        'codigo_barras': '7891234567892',
        'nombre': 'Teclado Logitech MK540 Inalámbrico',
        'descripcion': 'Combo teclado + mouse, receptor unificado USB',
        'categoria_id': 1,
        'proveedor_id': 1,
        'stock_actual': 35,
        'stock_minimo': 10,
        'precio_compra': 45000.00,
        'precio_venta': 68000.00,
        'ubicacion': 'Estante A-03',
        'imagen': 'teclado_logitech_mk540.jpg'
    },
    {
        'codigo_barras': '7891234567893',
        'nombre': 'Resma A4 Autor 75g x 500 hojas',
        'descripcion': 'Papel bond blanco, ideal para impresión y fotocopiado',
        'categoria_id': 2,
        'proveedor_id': 2,
        'stock_actual': 120,
        'stock_minimo': 20,
        'precio_compra': 4500.00,
        'precio_venta': 6800.00,
        'ubicacion': 'Estante B-01',
        'imagen': 'resma_autor_a4.jpg'
    },
    {
        'codigo_barras': '7891234567894',
        'nombre': 'Carpeta A-Z Oficio con Elástico',
        'descripcion': 'Cartón reforzado, 24 divisiones alfabéticas',
        'categoria_id': 2,
        'proveedor_id': 2,
        'stock_actual': 45,
        'stock_minimo': 15,
        'precio_compra': 8500.00,
        'precio_venta': 12500.00,
        'ubicacion': 'Estante B-02',
        'imagen': 'carpeta_az_oficio.jpg'
    },
    {
        'codigo_barras': '7891234567895',
        'nombre': 'Set Lapiceras Bic Cristal x 50 unidades',
        'descripcion': 'Tinta azul, escritura suave, cuerpo transparente',
        'categoria_id': 2,
        'proveedor_id': 2,
        'stock_actual': 8,
        'stock_minimo': 12,
        'precio_compra': 28000.00,
        'precio_venta': 42000.00,
        'ubicacion': 'Estante B-03',
        'imagen': 'lapiceras_bic_cristal.jpg'
    },
    {
        'codigo_barras': '7891234567896',
        'nombre': 'Silla Ejecutiva Ergonómica Premium',
        'descripcion': 'Base cromada, apoyabrazos regulables, respaldo mesh',
        'categoria_id': 3,
        'proveedor_id': 3,
        'stock_actual': 12,
        'stock_minimo': 5,
        'precio_compra': 320000.00,
        'precio_venta': 480000.00,
        'ubicacion': 'Área de exhibición',
        'imagen': 'silla_ejecutiva_premium.jpg'
    },
    {
        'codigo_barras': '7891234567897',
        'nombre': 'Escritorio L 140x120cm Melamina',
        'descripcion': 'Color roble, con cajonera móvil, patas metálicas',
        'categoria_id': 3,
        'proveedor_id': 3,
        'stock_actual': 6,
        'stock_minimo': 3,
        'precio_compra': 280000.00,
        'precio_venta': 420000.00,
        'ubicacion': 'Depósito mobiliario',
        'imagen': 'escritorio_l_roble.jpg'
    },
    {
        'codigo_barras': '7891234567898',
        'nombre': 'Taladro Bosch Professional 650W',
        'descripcion': 'Con percutor, mandril 13mm, maletin + accesorios',
        'categoria_id': 4,
        'proveedor_id': 4,
        'stock_actual': 8,
        'stock_minimo': 4,
        'precio_compra': 95000.00,
        'precio_venta': 142000.00,
        'ubicacion': 'Herramientas eléctricas',
        'imagen': 'taladro_bosch_650w.jpg'
    },
    {
        'codigo_barras': '7891234567899',
        'nombre': 'Set Destornilladores Profesional 12 piezas',
        'descripcion': 'Mango ergonómico, punta magnética, varios tamaños',
        'categoria_id': 4,
        'proveedor_id': 4,
        'stock_actual': 2,
        'stock_minimo': 6,
        'precio_compra': 35000.00,
        'precio_venta': 52500.00,
        'ubicacion': 'Herramientas manuales',
        'imagen': 'set_destornilladores.jpg'
    },
    {
        'codigo_barras': '7891234567900',
        'nombre': 'Detergente Multiuso Concentrado 5L',
        'descripcion': 'Biodegradable, aroma cítrico, rendimiento 1:10',
        'categoria_id': 5,
        'proveedor_id': 5,
        'stock_actual': 28,
        'stock_minimo': 10,
        'precio_compra': 12000.00,
        'precio_venta': 18500.00,
        'ubicacion': 'Productos químicos',
        'imagen': 'detergente_multiuso_5l.jpg'
    },
    {
        'codigo_barras': '7891234567901',
        'nombre': 'Papel Higiénico Institucional x 12 rollos',
        'descripcion': 'Doble hoja, 30m por rollo, color blanco',
        'categoria_id': 5,
        'proveedor_id': 5,
        'stock_actual': 45,
        'stock_minimo': 15,
        'precio_compra': 18500.00,
        'precio_venta': 27000.00,
        'ubicacion': 'Papel y absorbentes',
        'imagen': 'papel_higienico_institucional.jpg'
    },
    {
        'codigo_barras': '7891234567902',
        'nombre': 'Casco de Seguridad Blanco MSA',
        'descripcion': 'Norma IRAM, ajustable, ventilado, incluye barbijo',
        'categoria_id': 6,
        'proveedor_id': 6,
        'stock_actual': 15,
        'stock_minimo': 8,
        'precio_compra': 25000.00,
        'precio_venta': 38000.00,
        'ubicacion': 'EPP - Cascos',
        'imagen': 'casco_seguridad_msa.jpg'
    },
    {
        'codigo_barras': '7891234567903',
        'nombre': 'Guantes de Nitrilo Descartables x 100 unidades',
        'descripcion': 'Talla M, polvo libre, no estériles',
        'categoria_id': 6,
        'proveedor_id': 6,
        'stock_actual': 22,
        'stock_minimo': 10,
        'precio_compra': 8500.00,
        'precio_venta': 12800.00,
        'ubicacion': 'EPP - Guantes',
        'imagen': 'guantes_nitrilo.jpg'
    },
    {
        'codigo_barras': '7891234567904',
        'nombre': 'Café Premium Molido 1kg',
        'descripcion': 'Mezcla especial, tueste medio, grano arábico',
        'categoria_id': 7,
        'proveedor_id': 7,
        'stock_actual': 16,
        'stock_minimo': 8,
        'precio_compra': 22000.00,
        'precio_venta': 33000.00,
        'ubicacion': 'Cafetería - Café',
        'imagen': 'cafe_premium_1kg.jpg'
    },
    {
        'codigo_barras': '7891234567905',
        'nombre': 'Azúcar Refinada x 25kg',
        'descripcion': 'Tipo A, granulada fina, en bolsa industrial',
        'categoria_id': 7,
        'proveedor_id': 7,
        'stock_actual': 34,
        'stock_minimo': 12,
        'precio_compra': 18500.00,
        'precio_venta': 27800.00,
        'ubicacion': 'Cafetería - Endulzantes',
        'imagen': 'azucar_refinada_25kg.jpg'
    },
    {
        'codigo_barras': '7891234567906',
        'nombre': 'Uniforme Corporativo Completo',
        'descripcion': 'Camisa + pantalón, tela antialérgica, varios talles',
        'categoria_id': 8,
        'proveedor_id': 8,
        'stock_actual': 9,
        'stock_minimo': 5,
        'precio_compra': 45000.00,
        'precio_venta': 68000.00,
        'ubicacion': 'Textiles - Uniformes',
        'imagen': 'uniforme_corporativo.jpg'
    },
    {
        'codigo_barras': '7891234567907',
        'nombre': 'Router WiFi 6 TP-Link AX55',
        'descripcion': 'Dual band, 4 antenas, velocidad hasta 2400Mbps',
        'categoria_id': 9,
        'proveedor_id': 9,
        'stock_actual': 11,
        'stock_minimo': 6,
        'precio_compra': 125000.00,
        'precio_venta': 188000.00,
        'ubicacion': 'Redes - Routers',
        'imagen': 'router_tp_link_ax55.jpg'
    },
    {
        'codigo_barras': '7891234567908',
        'nombre': 'Aceite Motor Sintético 5W30 1L',
        'descripcion': 'Para motores a gasolina, API SN, bajo consumo',
        'categoria_id': 10,
        'proveedor_id': 10,
        'stock_actual': 27,
        'stock_minimo': 10,
        'precio_compra': 8500.00,
        'precio_venta': 12800.00,
        'ubicacion': 'Automotriz - Lubricantes',
        'imagen': 'aceite_motor_5w30.jpg'
    }
]

# =============================================================================
# MOVIMIENTOS DE STOCK DE EJEMPLO
# =============================================================================

MOVIMIENTOS_PRUEBA = [
    {
        'codigo_barras': '7891234567890',
        'tipo': 'Entrada',
        'cantidad': 10,
        'precio_unitario': 850000.00,
        'descripcion': 'Compra inicial a proveedor',
        'documento': 'FAC-001-2024',
        'usuario': 'Admin'
    },
    {
        'codigo_barras': '7891234567891',
        'tipo': 'Entrada',
        'cantidad': 15,
        'precio_unitario': 180000.00,
        'descripcion': 'Reposición de stock',
        'documento': 'FAC-002-2024',
        'usuario': 'Juan Pérez'
    },
    {
        'codigo_barras': '7891234567895',
        'tipo': 'Salida',
        'cantidad': 5,
        'precio_unitario': 560.00,
        'descripcion': 'Venta a departamento administrativo',
        'documento': 'REM-001-2024',
        'usuario': 'María González'
    },
    {
        'codigo_barras': '7891234567899',
        'tipo': 'Ajuste',
        'cantidad': -3,
        'precio_unitario': 2916.67,
        'descripcion': 'Corrección por inventario físico',
        'documento': 'AJU-001-2024',
        'usuario': 'Carlos López'
    },
    {
        'codigo_barras': '7891234567901',
        'tipo': 'Entrada',
        'cantidad': 20,
        'precio_unitario': 925.00,
        'descripcion': 'Compra mensual de suministros',
        'documento': 'FAC-003-2024',
        'usuario': 'Ana Martínez'
    },
    {
        'codigo_barras': '7891234567896',
        'tipo': 'Salida',
        'cantidad': 2,
        'precio_unitario': 240000.00,
        'descripcion': 'Entrega a nuevo empleado',
        'documento': 'REM-002-2024',
        'usuario': 'Admin'
    },
    {
        'codigo_barras': '7891234567898',
        'tipo': 'Entrada',
        'cantidad': 5,
        'precio_unitario': 95000.00,
        'descripcion': 'Compra de herramientas',
        'documento': 'FAC-004-2024',
        'usuario': 'Juan Pérez'
    },
    {
        'codigo_barras': '7891234567900',
        'tipo': 'Salida',
        'cantidad': 8,
        'precio_unitario': 2312.50,
        'descripcion': 'Uso en limpieza general',
        'documento': 'CON-001-2024',
        'usuario': 'María González'
    },
    {
        'codigo_barras': '7891234567902',
        'tipo': 'Entrada',
        'cantidad': 10,
        'precio_unitario': 25000.00,
        'descripcion': 'Reposición EPP',
        'documento': 'FAC-005-2024',
        'usuario': 'Carlos López'
    },
    {
        'codigo_barras': '7891234567904',
        'tipo': 'Ajuste',
        'cantidad': 2,
        'precio_unitario': 22000.00,
        'descripcion': 'Ajuste por merma',
        'documento': 'AJU-002-2024',
        'usuario': 'Ana Martínez'
    }
]
