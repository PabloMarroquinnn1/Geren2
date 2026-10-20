-- Bloque 9 — Consultas SQL de verificación QuetzalMart
-- Base esperada: quetzalmart
-- Todas las consultas son de solo lectura.
-- Las consultas 1 a 6 son verificaciones generales y no requieren cambiar valores.
-- Las consultas 7 a 7.3 usan prefijos de prueba; reemplázalos si el auxiliar
-- entrega otros nombres, referencias o prefijos en sus Excel.

-- 0. Contexto de la conexión
SELECT current_database() AS base_de_datos,
       current_user AS usuario,
       now() AS fecha_consulta;

-- 1. Ventas: resumen por estado
SELECT so.state AS estado,
       COUNT(*) AS cantidad,
       ROUND(COALESCE(SUM(so.amount_total), 0)::numeric, 2) AS total_gtq
FROM sale_order so
GROUP BY so.state
ORDER BY so.state;

-- 1.1 Ventas: detalle de las órdenes más recientes
SELECT so.name AS pedido,
       so.date_order AS fecha,
       rp.name AS cliente,
       ru.login AS vendedor,
       so.state AS estado,
       so.amount_total AS total_gtq,
       sw.name AS almacen
FROM sale_order so
JOIN res_partner rp ON rp.id = so.partner_id
LEFT JOIN res_users ru ON ru.id = so.user_id
LEFT JOIN stock_warehouse sw ON sw.id = so.warehouse_id
ORDER BY so.date_order DESC NULLS LAST, so.id DESC
LIMIT 100;

-- 2. Compras: resumen por estado
SELECT po.state AS estado,
       COUNT(*) AS cantidad,
       ROUND(COALESCE(SUM(po.amount_total), 0)::numeric, 2) AS total_gtq
FROM purchase_order po
GROUP BY po.state
ORDER BY po.state;

-- 2.1 Compras: detalle de las órdenes más recientes
SELECT po.name AS pedido,
       po.date_order AS fecha,
       rp.name AS proveedor,
       ru.login AS comprador,
       po.state AS estado,
       po.amount_total AS total_gtq
FROM purchase_order po
JOIN res_partner rp ON rp.id = po.partner_id
LEFT JOIN res_users ru ON ru.id = po.user_id
ORDER BY po.date_order DESC NULLS LAST, po.id DESC
LIMIT 100;

-- 3. Clientes activos
SELECT rp.id,
       rp.name AS cliente,
       rp.ref AS referencia,
       rp.email,
       rp.phone,
       rp.city AS ciudad,
       rc.code AS pais,
       rp.customer_rank,
       rp.active
FROM res_partner rp
LEFT JOIN res_country rc ON rc.id = rp.country_id
WHERE rp.active
  AND rp.customer_rank > 0
ORDER BY rp.name;

-- 4. Productos activos y sus existencias agregadas
SELECT pp.id,
       COALESCE(pt.name ->> 'es_GT', pt.name ->> 'en_US', '') AS producto,
       pp.default_code AS referencia_interna,
       pp.barcode AS codigo_barras,
       pt.list_price AS precio_venta,
       pp.standard_price AS costo,
       pt.active,
       COALESCE(SUM(sq.quantity), 0) AS cantidad_en_existencia,
       COALESCE(SUM(sq.reserved_quantity), 0) AS cantidad_reservada
FROM product_product pp
JOIN product_template pt ON pt.id = pp.product_tmpl_id
LEFT JOIN stock_quant sq ON sq.product_id = pp.id
GROUP BY pp.id, pt.id, pt.name, pp.default_code, pp.barcode,
         pt.list_price, pp.standard_price, pt.active
ORDER BY producto;

-- 5. Empleados activos con puesto y departamento
SELECT he.id,
       he.name AS empleado,
       he.work_email AS correo,
       he.work_phone AS telefono,
       hj.name AS puesto,
       hd.name AS departamento,
       he.active
FROM hr_employee he
LEFT JOIN hr_job hj ON hj.id = he.job_id
LEFT JOIN hr_department hd ON hd.id = he.department_id
WHERE he.active
ORDER BY he.name;

-- 6. Facturas de clientes y proveedores
SELECT am.name AS factura,
       am.move_type AS tipo,
       am.invoice_date AS fecha,
       rp.name AS tercero,
       am.state AS estado,
       am.payment_state AS estado_pago,
       am.amount_untaxed AS subtotal_gtq,
       am.amount_tax AS impuesto_gtq,
       am.amount_total AS total_gtq
FROM account_move am
JOIN res_partner rp ON rp.id = am.partner_id
WHERE am.move_type IN ('out_invoice', 'in_invoice', 'out_refund', 'in_refund')
ORDER BY am.invoice_date DESC NULLS LAST, am.id DESC
LIMIT 200;

-- 6.1 Conteo de facturas por tipo y estado
SELECT am.move_type AS tipo,
       am.state AS estado,
       COUNT(*) AS cantidad,
       ROUND(COALESCE(SUM(am.amount_total), 0)::numeric, 2) AS total_gtq
FROM account_move am
WHERE am.move_type IN ('out_invoice', 'in_invoice', 'out_refund', 'in_refund')
GROUP BY am.move_type, am.state
ORDER BY am.move_type, am.state;

-- 7. Datos cargados por el RPA: productos por referencia y nombre de prueba
SELECT pp.id,
       COALESCE(pt.name ->> 'es_GT', pt.name ->> 'en_US', '') AS producto,
       pp.default_code AS referencia_interna,
       pp.barcode AS codigo_barras,
       pt.list_price AS precio_venta,
       pp.standard_price AS costo,
       pt.active
FROM product_product pp
JOIN product_template pt ON pt.id = pp.product_tmpl_id
WHERE pp.default_code ILIKE 'RPA-DEMO-%'
   OR COALESCE(pt.name ->> 'es_GT', pt.name ->> 'en_US', '') ILIKE 'RPA Demo%'
   OR COALESCE(pt.name ->> 'es_GT', pt.name ->> 'en_US', '') ILIKE 'PRUEBA PRODUCTO SS%'
   OR pp.default_code ILIKE 'E-COM%'
ORDER BY pp.default_code, producto;

-- 7.1 Datos cargados por el RPA: clientes por referencia, nombre o correo de prueba
SELECT rp.id,
       rp.name AS cliente,
       rp.ref AS referencia,
       rp.email,
       rp.phone,
       rp.active
FROM res_partner rp
WHERE rp.ref ILIKE 'RPA-CLI-%'
   OR rp.name ILIKE 'RPA Cliente%'
   OR rp.email ILIKE 'rpa.cliente%'
   OR rp.name ILIKE 'PRUEBA SS%'
   OR rp.ref ILIKE 'CUST%'
ORDER BY rp.ref, rp.name;

-- 7.2 IDs externos asociados a productos o contactos cargados por prueba
SELECT imd.module,
       imd.name AS id_externo,
       imd.model,
       imd.res_id
FROM ir_model_data imd
WHERE (imd.model = 'product.template'
       AND (imd.name ILIKE 'rpa_demo_product_%'
            OR imd.name ILIKE 'PRUEBA_PRODUCT_SS_%'))
   OR (imd.model = 'res.partner'
       AND (imd.name ILIKE 'rpa_cliente%'
            OR imd.name ILIKE 'RPA-CLI-%'))
ORDER BY imd.model, imd.name;

-- 7.3 Existencias de los productos que cargó el RPA
SELECT COALESCE(pt.name ->> 'es_GT', pt.name ->> 'en_US', '') AS producto,
       pp.default_code AS referencia_interna,
       sl.complete_name AS ubicacion,
       sq.quantity AS cantidad,
       sq.reserved_quantity AS reservada
FROM stock_quant sq
JOIN product_product pp ON pp.id = sq.product_id
JOIN product_template pt ON pt.id = pp.product_tmpl_id
JOIN stock_location sl ON sl.id = sq.location_id
WHERE pp.default_code ILIKE 'RPA-DEMO-%'
   OR COALESCE(pt.name ->> 'es_GT', pt.name ->> 'en_US', '') ILIKE 'RPA Demo%'
   OR COALESCE(pt.name ->> 'es_GT', pt.name ->> 'en_US', '') ILIKE 'PRUEBA PRODUCTO SS%'
   OR pp.default_code ILIKE 'E-COM%'
ORDER BY producto, sl.complete_name;
