"""Datos maestros de QuetzalMart (fuente única para plantillas, imágenes y cargas).

Todos los nombres de personas y empresas son ficticios. Los correos usan dominios
de ejemplo para no escribirle a nadie real durante las pruebas.
"""

# --------------------------------------------------------------------------
# Productos de venta: 6 categorías x 10 productos
# (sku, nombre, presentación, costo, precio con IVA incluido, peso kg, envase, color)
# --------------------------------------------------------------------------
CATEGORIAS_VENTA = {
    "despensa": {
        "nombre": "Despensa",
        "prefijo": "DES",
        "sector": "secos",
        "descripcion": "Granos, harinas, aceites y básicos de la cocina chapina.",
        "productos": [
            ("Arroz blanco grano largo", "2 lb", 7.10, 9.80, 0.91, "bolsa", "#F4F1E8"),
            ("Frijol negro entero", "2 lb", 8.40, 11.60, 0.91, "bolsa", "#2B2B2B"),
            ("Harina de maíz nixtamalizada", "1 kg", 6.30, 8.70, 1.0, "bolsa", "#F2C14E"),
            ("Aceite de girasol", "900 ml", 17.80, 24.50, 0.9, "botella", "#F6D55C"),
            ("Azúcar morena", "2 kg", 12.20, 16.90, 2.0, "bolsa", "#B5835A"),
            ("Pasta coditos", "400 g", 3.90, 5.40, 0.4, "paquete", "#E9B44C"),
            ("Avena en hojuelas", "400 g", 6.60, 9.10, 0.4, "caja", "#C9A66B"),
            ("Sardinas en salsa de tomate", "425 g", 9.20, 12.70, 0.43, "lata", "#C0392B"),
            ("Café molido de altura Huehuetenango", "400 g", 31.50, 43.80, 0.4, "bolsa", "#5D3A1A"),
            ("Sal yodada de mar", "1 kg", 2.80, 3.90, 1.0, "bolsa", "#5DADE2"),
        ],
    },
    "lacteos": {
        "nombre": "Lácteos y refrigerados",
        "prefijo": "LAC",
        "sector": "refrigerados",
        "descripcion": "Leche, quesos, cremas y productos de la cadena de frío.",
        "productos": [
            ("Leche entera UHT", "946 ml", 8.10, 11.20, 0.98, "carton", "#2E86C1"),
            ("Leche deslactosada", "946 ml", 9.30, 12.80, 0.98, "carton", "#76D7C4"),
            ("Queso fresco artesanal", "454 g", 18.70, 25.90, 0.46, "caja", "#FDFEFE"),
            ("Crema pura de rancho", "480 ml", 13.40, 18.50, 0.5, "frasco", "#FBEEE6"),
            ("Yogur bebible de fresa", "1 L", 12.60, 17.40, 1.03, "botella", "#F1948A"),
            ("Mantequilla con sal", "225 g", 14.10, 19.50, 0.23, "caja", "#F7DC6F"),
            ("Huevos rojos cartón", "30 unidades", 27.50, 38.00, 1.9, "caja", "#DC7633"),
            ("Queso mozzarella rallado", "200 g", 15.20, 21.00, 0.2, "bolsa", "#FCF3CF"),
            ("Jamón de pavo en rodajas", "250 g", 16.90, 23.40, 0.25, "paquete", "#F5B7B1"),
            ("Bebida de soya natural", "946 ml", 10.80, 14.90, 0.98, "carton", "#A9CCE3"),
        ],
    },
    "bebidas": {
        "nombre": "Bebidas",
        "prefijo": "BEB",
        "sector": "secos",
        "descripcion": "Agua, jugos, refrescos e hidratantes para toda la familia.",
        "productos": [
            ("Agua purificada", "5 L", 9.60, 13.30, 5.0, "botella", "#AED6F1"),
            ("Agua mineral con gas", "600 ml", 4.10, 5.70, 0.62, "botella", "#85C1E9"),
            ("Jugo de naranja 100 %", "1.75 L", 19.30, 26.70, 1.8, "botella", "#F39C12"),
            ("Néctar de durazno", "1 L", 9.70, 13.40, 1.03, "carton", "#F8C471"),
            ("Refresco de cola", "3 L", 14.30, 19.80, 3.1, "botella", "#7B241C"),
            ("Bebida isotónica de limón", "600 ml", 6.10, 8.40, 0.62, "botella", "#58D68D"),
            ("Té verde con limón", "500 ml", 5.40, 7.50, 0.52, "botella", "#ABEBC6"),
            ("Horchata en polvo", "400 g", 11.20, 15.50, 0.4, "bolsa", "#FAE5D3"),
            ("Concentrado de rosa de jamaica", "1 L", 12.50, 17.30, 1.05, "botella", "#922B3E"),
            ("Agua de coco natural", "330 ml", 7.30, 10.10, 0.34, "lata", "#F0F3F4"),
        ],
    },
    "snacks": {
        "nombre": "Snacks y dulces",
        "prefijo": "SNK",
        "sector": "secos",
        "descripcion": "Boquitas, galletas y dulces para compartir.",
        "productos": [
            ("Tortillitas de maíz tostadas", "180 g", 7.90, 10.90, 0.18, "bolsa", "#D4AC0D"),
            ("Manías saladas", "200 g", 8.60, 11.90, 0.2, "bolsa", "#A04000"),
            ("Galletas de avena con pasas", "300 g", 9.40, 13.00, 0.3, "paquete", "#CA6F1E"),
            ("Chocolate oscuro 70 % cacao", "100 g", 13.70, 18.90, 0.1, "caja", "#4A235A"),
            ("Platanitos fritos con sal", "150 g", 6.50, 9.00, 0.15, "bolsa", "#F7DC6F"),
            ("Palomitas para microondas", "3 sobres", 10.10, 13.90, 0.3, "caja", "#E74C3C"),
            ("Gomitas de frutas", "250 g", 8.20, 11.30, 0.25, "bolsa", "#AF7AC5"),
            ("Barras de granola con miel", "6 unidades", 14.80, 20.40, 0.25, "caja", "#B9770E"),
            ("Galletas saladas", "6 paquetes", 7.60, 10.50, 0.27, "paquete", "#F5CBA7"),
            ("Dulce de leche", "450 g", 15.90, 21.90, 0.45, "frasco", "#A0522D"),
        ],
    },
    "limpieza": {
        "nombre": "Limpieza del hogar",
        "prefijo": "LIM",
        "sector": "quimicos",
        "descripcion": "Detergentes, desinfectantes y todo para un hogar limpio.",
        "productos": [
            ("Detergente líquido para ropa", "3 L", 38.40, 53.20, 3.1, "botella", "#3498DB"),
            ("Jabón en barra para ropa", "4 unidades", 12.30, 17.00, 1.4, "paquete", "#48C9B0"),
            ("Lavaplatos líquido de limón", "750 ml", 10.20, 14.10, 0.78, "botella", "#82E0AA"),
            ("Cloro desinfectante", "3.8 L", 16.70, 23.10, 3.9, "botella", "#D6EAF8"),
            ("Limpiador multiusos de lavanda", "1 L", 11.60, 16.00, 1.05, "botella", "#A569BD"),
            ("Suavizante de telas", "1.7 L", 21.50, 29.80, 1.75, "botella", "#F5B7B1"),
            ("Esponjas de doble uso", "3 unidades", 6.90, 9.50, 0.08, "paquete", "#F4D03F"),
            ("Bolsas para basura de 30 galones", "10 unidades", 9.80, 13.50, 0.4, "caja", "#1C2833"),
            ("Papel toalla de cocina", "2 rollos", 13.10, 18.10, 0.5, "paquete", "#FDFEFE"),
            ("Desengrasante para cocina", "650 ml", 14.40, 19.90, 0.68, "botella", "#E67E22"),
        ],
    },
    "cuidado": {
        "nombre": "Cuidado personal",
        "prefijo": "CUI",
        "sector": "bazar",
        "descripcion": "Higiene y cuidado personal para todos los días.",
        "productos": [
            ("Champú de sábila", "400 ml", 18.20, 25.20, 0.42, "botella", "#7DCEA0"),
            ("Acondicionador nutritivo", "400 ml", 18.90, 26.10, 0.42, "botella", "#BB8FCE"),
            ("Jabón de tocador de avena", "3 unidades", 11.40, 15.80, 0.33, "caja", "#E5CBA0"),
            ("Pasta dental triple acción", "100 ml", 9.90, 13.70, 0.15, "tubo", "#E74C3C"),
            ("Cepillos de dientes suaves", "2 unidades", 12.80, 17.70, 0.06, "caja", "#5DADE2"),
            ("Desodorante roll-on", "50 ml", 16.10, 22.30, 0.07, "botella", "#2C3E50"),
            ("Papel higiénico doble hoja", "12 rollos", 29.60, 41.00, 1.3, "paquete", "#EBF5FB"),
            ("Crema corporal humectante", "400 ml", 22.70, 31.40, 0.43, "frasco", "#F9E79F"),
            ("Toallas húmedas para bebé", "80 unidades", 14.60, 20.20, 0.5, "paquete", "#AED6F1"),
            ("Protector solar FPS 50", "120 ml", 48.30, 66.90, 0.14, "tubo", "#F5B041"),
        ],
    },
}

# --------------------------------------------------------------------------
# 60 materiales operativos (no se venden): lo que cada sucursal necesita.
# (nombre, unidad de compra, costo, stock por sucursal)
# --------------------------------------------------------------------------
CATEGORIAS_MATERIALES = {
    "empaque": ("Empaque y bolsas", [
        ("Bolsa plástica tipo camiseta mediana", "millar", 145.00, 40),
        ("Bolsa de papel kraft #20", "paquete de 500", 210.00, 15),
        ("Bolsa reutilizable QuetzalMart", "unidad", 9.50, 300),
        ("Cinta adhesiva transparente 2 pulgadas", "rollo", 11.00, 60),
        ("Caja de cartón corrugado para despacho", "paquete de 25", 185.00, 12),
        ("Papel burbuja", "rollo de 50 m", 132.00, 8),
        ("Film stretch para tarimas 18 pulgadas", "rollo", 96.00, 20),
        ("Etiqueta de envío térmica 4x6", "rollo de 250", 58.00, 25),
        ("Bandeja de duroport para carnes", "paquete de 100", 64.00, 30),
        ("Bolsa con cierre hermético", "paquete de 100", 47.00, 25),
    ]),
    "punto_venta": ("Punto de venta y papelería", [
        ("Rollo de papel térmico 80 x 80 mm", "caja de 50", 395.00, 10),
        ("Etiquetas adhesivas para precio", "rollo de 1,000", 18.00, 50),
        ("Pistola etiquetadora de precios", "unidad", 165.00, 6),
        ("Lector de código de barras USB", "unidad", 420.00, 6),
        ("Papel bond tamaño carta", "resma", 42.00, 30),
        ("Tóner para impresora láser", "unidad", 610.00, 4),
        ("Marcadores permanentes", "caja de 12", 54.00, 12),
        ("Cajón de dinero para caja registradora", "unidad", 780.00, 4),
        ("Portaprecios para góndola", "paquete de 50", 125.00, 10),
        ("Talonario de vales de caja", "paquete de 10", 35.00, 20),
    ]),
    "higiene_tienda": ("Limpieza e higiene de tienda", [
        ("Trapeador industrial de algodón", "unidad", 68.00, 12),
        ("Escoba de cerda dura", "unidad", 39.00, 15),
        ("Cubeta con exprimidor", "unidad", 245.00, 6),
        ("Desinfectante de amonio cuaternario", "galón", 89.00, 20),
        ("Guantes de nitrilo", "caja de 100", 72.00, 25),
        ("Toalla de papel interdoblada", "caja de 2,400", 255.00, 10),
        ("Jabón antibacterial para manos", "galón", 76.00, 15),
        ("Bolsa industrial para basura 55 galones", "paquete de 25", 98.00, 20),
        ("Atomizador plástico de 1 L", "unidad", 14.50, 30),
        ("Señal de piso mojado", "unidad", 85.00, 8),
    ]),
    "seguridad": ("Seguridad industrial y uniformes", [
        ("Camisa polo de uniforme", "unidad", 95.00, 60),
        ("Gabacha con logo QuetzalMart", "unidad", 58.00, 60),
        ("Gorra de uniforme", "unidad", 32.00, 60),
        ("Chaleco reflectivo", "unidad", 38.00, 20),
        ("Botas de seguridad con punta de acero", "par", 365.00, 12),
        ("Casco de seguridad", "unidad", 64.00, 10),
        ("Guantes de carga reforzados", "par", 27.00, 40),
        ("Faja de soporte lumbar", "unidad", 115.00, 12),
        ("Extintor ABC de 10 lb", "unidad", 395.00, 8),
        ("Botiquín de primeros auxilios", "unidad", 230.00, 4),
    ]),
    "bodega": ("Bodega y exhibición", [
        ("Tarima plástica 1.20 x 1.00 m", "unidad", 285.00, 30),
        ("Transpaleta manual de 2.5 t", "unidad", 3150.00, 2),
        ("Carrito de supermercado", "unidad", 1250.00, 25),
        ("Canasta plástica de mano", "unidad", 48.00, 60),
        ("Estantería metálica de 5 niveles", "unidad", 980.00, 10),
        ("Escalera de aluminio de 6 peldaños", "unidad", 640.00, 3),
        ("Termómetro digital para cámara fría", "unidad", 155.00, 6),
        ("Exhibidor de frutas de 3 niveles", "unidad", 1450.00, 3),
        ("Contenedor rojo para producto en cuarentena", "unidad", 210.00, 4),
        ("Báscula digital de 30 kg", "unidad", 890.00, 5),
    ]),
    "mantenimiento": ("Mantenimiento y energía", [
        ("Panel LED 60 x 60 cm", "unidad", 195.00, 20),
        ("Tubo LED T8 de 18 W", "unidad", 34.00, 50),
        ("Filtro para aire acondicionado", "unidad", 120.00, 12),
        ("Batería de respaldo para UPS 12 V", "unidad", 265.00, 6),
        ("Regleta industrial de 6 tomas", "unidad", 145.00, 10),
        ("Cinta de aislar", "rollo", 9.00, 30),
        ("Juego de herramientas de 82 piezas", "unidad", 725.00, 2),
        ("Aceite lubricante multiuso", "frasco", 42.00, 12),
        ("Candado de seguridad de 50 mm", "unidad", 88.00, 15),
        ("Pilas alcalinas AA", "paquete de 4", 31.00, 25),
    ]),
}

# --------------------------------------------------------------------------
# Sucursales (almacenes) y sectores de almacenamiento
# --------------------------------------------------------------------------
SUCURSALES = [
    # codigo, nombre, ciudad, calle, país, estado, cp, teléfono
    ("GUA", "Sucursal Guatemala", "Ciudad de Guatemala", "Avenida Bolívar 32-17, Zona 4",
     "gt", "Guatemala", "01004", "+502 2385 7700"),
    ("MEX", "Sucursal México", "Tapachula", "Boulevard Belisario Domínguez 1420",
     "mx", "Chiapas", "30700", "+52 962 118 4500"),
    ("SAL", "Sucursal El Salvador", "Santa Ana", "Avenida Independencia Sur 25",
     "sv", None, "02101", "+503 2447 8800"),
]

SECTORES = [
    # código interno, nombre de la ubicación
    ("secos", "Abarrotes secos"),
    ("refrigerados", "Cámara de refrigeración"),
    ("quimicos", "Químicos y limpieza"),
    ("bazar", "Bazar y cuidado personal"),
    ("materiales", "Materiales operativos"),
    ("cuarentena", "Cuarentena (producto no conforme)"),
]

# --------------------------------------------------------------------------
# Recursos humanos: 5 departamentos, 7 puestos, 35 empleados
# --------------------------------------------------------------------------
DEPARTAMENTOS = [
    ("direccion", "Dirección General"),
    ("tiendas", "Operaciones de Tienda"),
    ("logistica", "Logística e Inventario"),
    ("comercial", "Comercial y Marketing"),
    ("finanzas", "Finanzas y Administración"),
]

PUESTOS = [
    # código, nombre, departamento, salario base mensual (GTQ)
    ("director", "Director(a) General", "direccion", 18500.0),
    ("gerente_sucursal", "Gerente de Sucursal", "tiendas", 11200.0),
    ("cajero", "Cajero(a)", "tiendas", 4100.0),
    ("bodega", "Encargado(a) de Bodega", "logistica", 5600.0),
    ("inventario", "Auxiliar de Inventario", "logistica", 4300.0),
    ("marketing", "Analista de Marketing Digital", "comercial", 7800.0),
    ("contabilidad", "Contador(a) General", "finanzas", 8900.0),
]

# nombre, puesto, sucursal (GUA/MEX/SAL), género (male/female)
EMPLEADOS = [
    ("Mariana Lucía Ajú Cotí", "director", "GUA", "female"),
    ("Rodrigo Esteban Monterroso Paz", "gerente_sucursal", "GUA", "male"),
    ("Itzel Guadalupe Hernández Cruz", "gerente_sucursal", "MEX", "female"),
    ("Óscar Alberto Menjívar Rauda", "gerente_sucursal", "SAL", "male"),
    ("Ana Sofía Xicará Tum", "cajero", "GUA", "female"),
    ("Kevin Josué Ordóñez Batz", "cajero", "GUA", "male"),
    ("Brenda Marisol Cifuentes López", "cajero", "GUA", "female"),
    ("José Daniel Pérez Chacón", "cajero", "MEX", "male"),
    ("Fernanda Itzayana Ruiz Gómez", "cajero", "MEX", "female"),
    ("Luis Ángel Domínguez Rosas", "cajero", "MEX", "male"),
    ("Karla Beatriz Portillo Alas", "cajero", "SAL", "female"),
    ("Diego Alejandro Mejía Ayala", "cajero", "SAL", "male"),
    ("Gabriela Estefanía Rivas Mendoza", "cajero", "SAL", "female"),
    ("Walter Iván Coy Caal", "bodega", "GUA", "male"),
    ("Adriana Paola Solís Vázquez", "bodega", "MEX", "female"),
    ("Manuel Enrique Campos Orellana", "bodega", "SAL", "male"),
    ("Héctor Rolando Tzul Yax", "inventario", "GUA", "male"),
    ("Silvia Noemí Barrios Estrada", "inventario", "GUA", "female"),
    ("Ricardo Emilio Santiago Pérez", "inventario", "MEX", "male"),
    ("Jacqueline Ivette Flores Castro", "inventario", "SAL", "female"),
    ("Pablo Andrés Recinos Morales", "marketing", "GUA", "male"),
    ("Daniela Michelle Toledo Arana", "marketing", "GUA", "female"),
    ("Erick Fabián Jiménez Ochoa", "marketing", "MEX", "male"),
    ("Claudia Verónica Juárez Sic", "contabilidad", "GUA", "female"),
    ("Mario René Escobar Guzmán", "contabilidad", "SAL", "male"),
    ("Lesly Yohana Sapón Ixcoy", "cajero", "GUA", "female"),
    ("Juan Carlos Garrido Méndez", "inventario", "MEX", "male"),
    ("Rosa María Aguilar Quiñónez", "cajero", "GUA", "female"),
    ("Edwin Rafael Morán Lemus", "bodega", "GUA", "male"),
    ("Paula Andrea Castañeda Reyes", "marketing", "SAL", "female"),
    ("Sergio Antonio Velásquez Ramos", "inventario", "SAL", "male"),
    ("Mónica Alejandra Trujillo Ruiz", "contabilidad", "MEX", "female"),
    ("Gerson Eduardo Saquic Tuy", "cajero", "GUA", "male"),
    ("Valeria Nicole Orantes Díaz", "cajero", "MEX", "female"),
    ("Josué Benjamín Hernández Vides", "cajero", "SAL", "male"),
]

# --------------------------------------------------------------------------
# Clientes (personas y empresas) y proveedores
# nombre, tipo (person/company), país, ciudad, estado, NIT/RFC
# --------------------------------------------------------------------------
CLIENTES = [
    ("Comedor Doña Chayito", "company", "gt", "Mixco", "Guatemala", "4521876-3"),
    ("Hotel Posada del Cerro", "company", "gt", "Antigua Guatemala", "Sacatepéquez", "7788120-1"),
    ("Cafetería La Ceiba Universitaria", "company", "gt", "Ciudad de Guatemala", "Guatemala", "3359014-K"),
    ("Restaurante Sabor Quetzalteco", "company", "gt", "Quetzaltenango", "Quetzaltenango", "6102347-5"),
    ("Colegio Mixto Los Pinos", "company", "gt", "Villa Nueva", "Guatemala", "2877465-0"),
    ("Tienda El Buen Vecino", "company", "gt", "Escuintla", "Escuintla", "5590012-8"),
    ("Abarrotería San Judas", "company", "gt", "Cobán", "Alta Verapaz", "8834501-2"),
    ("Clínica Familiar Santa Fe", "company", "gt", "Chimaltenango", "Chimaltenango", "1278843-9"),
    ("Lucía Fernanda Batres Sosa", "person", "gt", "Ciudad de Guatemala", "Guatemala", "9081234-1"),
    ("Carlos Humberto Tejada Rivas", "person", "gt", "Mixco", "Guatemala", "6610457-7"),
    ("Andrea Celeste Morales Pineda", "person", "gt", "Quetzaltenango", "Quetzaltenango", "3326019-4"),
    ("Jorge Mario Castillo Aldana", "person", "gt", "Antigua Guatemala", "Sacatepéquez", "4458810-6"),
    ("Sandra Elizabeth Choc Pop", "person", "gt", "Cobán", "Alta Verapaz", "7712058-3"),
    ("Héctor Iván Lemus Arriaga", "person", "gt", "Escuintla", "Escuintla", "2093341-0"),
    ("María José Rodas Figueroa", "person", "gt", "Villa Nueva", "Guatemala", "5560127-2"),
    ("Byron Estuardo Ramírez Gil", "person", "gt", "Huehuetenango", "Huehuetenango", "1185903-8"),
    ("Abarrotes La Frontera", "company", "mx", "Tapachula", "Chiapas", "AFR190512KJ3"),
    ("Cocina Económica Soconusco", "company", "mx", "Tapachula", "Chiapas", "CES170823PQ1"),
    ("Hotel Real del Tacaná", "company", "mx", "Tuxtla Gutiérrez", "Chiapas", "HRT150304AB7"),
    ("Minisúper Las Palmas", "company", "mx", "Huixtla", "Chiapas", "MPA200117HT5"),
    ("Escuela Primaria Benito Juárez", "company", "mx", "Ciudad Hidalgo", "Chiapas", "EPB991001SD2"),
    ("Guadalupe Itzel Velázquez Ruiz", "person", "mx", "Tapachula", "Chiapas", "VERG900312MC4"),
    ("Juan Pablo Mendoza Toledo", "person", "mx", "Tuxtla Gutiérrez", "Chiapas", "METJ880725HT9"),
    ("Ximena Alejandra Ortiz Cano", "person", "mx", "Tapachula", "Chiapas", "OICX950118MC1"),
    ("Arturo Iván Gómez Salgado", "person", "mx", "Huixtla", "Chiapas", "GOSA870904HC6"),
    ("Daniela Monserrat Cruz Pérez", "person", "mx", "San Cristóbal de las Casas", "Chiapas", "CUPD990215MC8"),
    ("Pupusería La Esquina Santaneca", "company", "sv", "Santa Ana", None, "0210-150385-101-3"),
    ("Hotel Lago de Coatepeque", "company", "sv", "El Congo", None, "0207-200790-102-5"),
    ("Tienda Doña Mila", "company", "sv", "Chalchuapa", None, "0202-110278-103-1"),
    ("Cafetín Universitario Occidente", "company", "sv", "Santa Ana", None, "0210-050601-104-9"),
    ("Despensa Familiar Metapán", "company", "sv", "Metapán", None, "0207-180995-105-0"),
    ("Karla Yamileth Martínez Rauda", "person", "sv", "Santa Ana", None, "05123456-7"),
    ("Néstor Alfredo Portillo Henríquez", "person", "sv", "San Salvador", None, "04456789-1"),
    ("Brenda Carolina Aguilar Mejía", "person", "sv", "Chalchuapa", None, "06234567-8"),
    ("Mauricio Ernesto Guardado Lima", "person", "sv", "Metapán", None, "03345678-2"),
    ("Fátima Beatriz Rivas Alfaro", "person", "sv", "Santa Ana", None, "05987654-3"),
    ("Consumidor Final Guatemala", "person", "gt", "Ciudad de Guatemala", "Guatemala", "CF"),
    ("Consumidor Final México", "person", "mx", "Tapachula", "Chiapas", "XAXX010101000"),
    ("Consumidor Final El Salvador", "person", "sv", "Santa Ana", None, "CF-SV"),
    ("Panadería y Repostería El Trigal", "company", "gt", "Ciudad de Guatemala", "Guatemala", "6654320-1"),
]

# nombre, país, ciudad, NIT, qué provee (categoría de catálogo o "materiales")
PROVEEDORES = [
    ("Distribuidora de Granos El Altiplano, S.A.", "gt", "Ciudad de Guatemala", "1234560-7", "despensa"),
    ("Molinos y Harinas San Cristóbal, S.A.", "gt", "Mixco", "2345671-8", "despensa"),
    ("Aceites y Grasas de Centroamérica, S.A.", "gt", "Escuintla", "3456782-9", "despensa"),
    ("Finca Cafetalera Cumbres de Huehue", "gt", "Huehuetenango", "4567893-0", "despensa"),
    ("Lácteos La Pradera, S.A.", "gt", "Chimaltenango", "5678904-1", "lacteos"),
    ("Granja Avícola Los Encinos", "gt", "Villa Nueva", "6789015-2", "lacteos"),
    ("Embutidos del Pacífico, S.A. de C.V.", "sv", "Sonsonate", "0614-010180-101-1", "lacteos"),
    ("Embotelladora Volcán de Agua, S.A.", "gt", "Ciudad de Guatemala", "7890126-3", "bebidas"),
    ("Jugos Tropicales del Soconusco, S.A. de C.V.", "mx", "Tapachula", "JTS100512AB1", "bebidas"),
    ("Bebidas Naturales Cuscatlán, S.A. de C.V.", "sv", "San Salvador", "0614-020290-102-2", "bebidas"),
    ("Boquitas y Botanas Chapinas, S.A.", "gt", "Ciudad de Guatemala", "8901237-4", "snacks"),
    ("Confitería La Abuelita, S.A. de C.V.", "mx", "Tuxtla Gutiérrez", "CLA080817CD3", "snacks"),
    ("Galletera Industrial Maya, S.A.", "gt", "Amatitlán", "9012348-5", "snacks"),
    ("Químicos Limpios de Centroamérica, S.A.", "gt", "Ciudad de Guatemala", "1123459-6", "limpieza"),
    ("Papelera Industrial del Norte, S.A. de C.V.", "mx", "Tuxtla Gutiérrez", "PIN120304EF5", "limpieza"),
    ("Detergentes y Jabones La Espuma, S.A.", "sv", "Santa Ana", "0210-030385-103-3", "limpieza"),
    ("Cosméticos Naturales Sábila Verde, S.A.", "gt", "Quetzaltenango", "2234560-7", "cuidado"),
    ("Higiene Personal Integral, S.A. de C.V.", "mx", "Tapachula", "HPI150720GH7", "cuidado"),
    ("Farmacéutica Regional de Occidente, S.A.", "sv", "Santa Ana", "0210-040495-104-4", "cuidado"),
    ("Empaques y Plásticos Kakaw, S.A.", "gt", "Mixco", "3345671-8", "materiales"),
    ("Tecnología para Comercios POS-GT, S.A.", "gt", "Ciudad de Guatemala", "4456782-9", "materiales"),
    ("Suministros Industriales El Faro, S.A. de C.V.", "sv", "San Salvador", "0614-050505-105-5", "materiales"),
    ("Uniformes y Bordados La Aguja de Oro", "gt", "Ciudad de Guatemala", "5567893-0", "materiales"),
    ("Equipos para Bodega Montacargas del Sur, S.A. de C.V.", "mx", "Tapachula", "EBM110909JK2", "materiales"),
    ("Ferretería y Eléctricos El Volcán, S.A.", "gt", "Escuintla", "6678904-1", "materiales"),
]

# Proveedores de servicios tercerizados (contratos de outsourcing del DMS).
SERVICIOS_OUTSOURCING = [
    ("Seguridad Privada Centinela, S.A.", "Vigilancia y monitoreo de las tres sucursales", 18500.00),
    ("Limpieza Profesional Brillo Total, S.A.", "Limpieza profunda nocturna de piso de venta y bodegas", 12400.00),
    ("Transportes Refrigerados Ruta Maya, S.A.", "Distribución refrigerada entre bodegas y sucursales", 26800.00),
    ("Soluciones TI Nube Chapina, S.A.", "Soporte del ERP, respaldos y mesa de ayuda", 9600.00),
    ("Fumigaciones y Control de Plagas Ecosano", "Control de plagas mensual con certificado sanitario", 4200.00),
]
