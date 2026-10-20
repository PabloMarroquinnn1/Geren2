-- Consultas prácticas para la evaluación de QuetzalMart
--
-- Estas consultas son independientes del bloque9_verificacion.sql.
-- En DBeaver puedes ejecutar una consulta a la vez con Ctrl+Enter.
-- Las consultas con la marca "VALOR A CAMBIAR" tienen ejemplos.
-- Reemplaza únicamente el texto entre comillas por el nombre, referencia,
-- código, pedido, proveedor o factura que quieras buscar.
-- El símbolo % significa "contiene". Ejemplo: '%arroz%' encuentra
-- "Arroz premium 1 kg" aunque el texto no sea idéntico.

-- 1. Buscar clientes/contactos por nombre.
-- VALOR A CAMBIAR: 'PRUEBA SS' por el nombre o parte del nombre.
SELECT id, name AS cliente, vat AS nit, email, phone, city, active
FROM res_partner
WHERE active
  AND name ILIKE '%PRUEBA SS%'
ORDER BY name;

-- 2. Buscar un cliente por correo, NIT o referencia.
-- VALORES A CAMBIAR: 'rpa.cliente', '123' y 'RPA-CLI' por los datos conocidos.
-- Puedes dejar en blanco una condición si no tienes ese dato.
SELECT id, name AS cliente, vat AS nit, ref AS referencia,
       email, phone, active
FROM res_partner
WHERE email ILIKE '%rpa.cliente%'
   OR vat ILIKE '%123%'
   OR ref ILIKE '%RPA-CLI%'
ORDER BY name;

-- 3. Ver todos los clientes/contactos activos.
SELECT id, name AS cliente, vat AS nit, email, phone, city
FROM res_partner
WHERE active
ORDER BY name;

-- 4. Buscar productos por nombre.
-- VALOR A CAMBIAR: 'Arroz' por el nombre o parte del nombre del producto.
SELECT pp.id,
       COALESCE(pt.name ->> 'es_GT', pt.name ->> 'en_US', '') AS producto,
       pp.default_code AS referencia,
       pp.barcode AS codigo_barras,
       pt.list_price AS precio_venta,
       pp.standard_price AS costo,
       pt.active
FROM product_product pp
JOIN product_template pt ON pt.id = pp.product_tmpl_id
WHERE COALESCE(pt.name ->> 'es_GT', pt.name ->> 'en_US', '') ILIKE '%Arroz%'
ORDER BY producto;

-- 5. Buscar un producto por referencia o código de barras.
-- VALORES A CAMBIAR: 'QM-001' por la referencia y '54398267125'
-- por el código de barras. Si solo tienes uno, elimina la otra condición.
SELECT pp.id,
       COALESCE(pt.name ->> 'es_GT', pt.name ->> 'en_US', '') AS producto,
       pp.default_code AS referencia,
       pp.barcode AS codigo_barras,
       pt.list_price AS precio_venta,
       pp.standard_price AS costo,
       pt.is_published AS publicado
FROM product_product pp
JOIN product_template pt ON pt.id = pp.product_tmpl_id
WHERE pp.default_code ILIKE '%QM-001%'
   OR pp.barcode = '54398267125'
ORDER BY producto;

-- 6. Ver productos publicados en la tienda web.
SELECT pp.default_code AS referencia,
       COALESCE(pt.name ->> 'es_GT', pt.name ->> 'en_US', '') AS producto,
       pt.list_price AS precio_venta,
       pt.is_published AS publicado
FROM product_product pp
JOIN product_template pt ON pt.id = pp.product_tmpl_id
WHERE pt.is_published
ORDER BY producto;

-- 7. Ver existencias de un producto por ubicación.
-- VALOR A CAMBIAR: 'QM-001' por la referencia interna del producto.
SELECT COALESCE(pt.name ->> 'es_GT', pt.name ->> 'en_US', '') AS producto,
       pp.default_code AS referencia,
       sl.complete_name AS ubicacion,
       sq.quantity AS cantidad,
       sq.reserved_quantity AS reservada
FROM stock_quant sq
JOIN product_product pp ON pp.id = sq.product_id
JOIN product_template pt ON pt.id = pp.product_tmpl_id
JOIN stock_location sl ON sl.id = sq.location_id
WHERE pp.default_code = 'QM-001'
ORDER BY sl.complete_name;

-- 8. Buscar empleados por nombre.
-- VALOR A CAMBIAR: 'Ana' por el nombre o parte del nombre del empleado.
SELECT he.id, he.name AS empleado, he.work_email AS correo,
       he.work_phone AS telefono, hj.name AS puesto,
       hd.name AS departamento, he.active
FROM hr_employee he
LEFT JOIN hr_job hj ON hj.id = he.job_id
LEFT JOIN hr_department hd ON hd.id = he.department_id
WHERE he.name ILIKE '%Ana%'
ORDER BY he.name;

-- 9. Listar empleados por departamento.
-- VALOR A CAMBIAR: 'Ventas' por el nombre o parte del departamento.
SELECT he.name AS empleado, hd.name AS departamento,
       hj.name AS puesto, he.work_email AS correo
FROM hr_employee he
LEFT JOIN hr_department hd ON hd.id = he.department_id
LEFT JOIN hr_job hj ON hj.id = he.job_id
WHERE he.active
  AND COALESCE(hd.name ->> 'es_GT', hd.name ->> 'en_US', '') ILIKE '%Ventas%'
ORDER BY he.name;

-- 10. Buscar una venta por cliente.
-- VALOR A CAMBIAR: 'Cliente QuetzalMart 01' por el nombre del cliente.
SELECT so.name AS pedido, so.date_order AS fecha,
       rp.name AS cliente, so.state AS estado,
       so.amount_total AS total
FROM sale_order so
JOIN res_partner rp ON rp.id = so.partner_id
WHERE rp.name ILIKE '%Cliente QuetzalMart 01%'
ORDER BY so.date_order DESC;

-- 11. Buscar una venta por número de pedido.
-- VALOR A CAMBIAR: 'S00171' por el número exacto del pedido.
SELECT so.name AS pedido, so.date_order AS fecha,
       rp.name AS cliente, so.state AS estado,
       so.amount_untaxed AS subtotal,
       so.amount_tax AS impuesto,
       so.amount_total AS total
FROM sale_order so
JOIN res_partner rp ON rp.id = so.partner_id
WHERE so.name = 'S00171';

-- 12. Ventas confirmadas del período más reciente.
SELECT so.name AS pedido, so.date_order AS fecha,
       rp.name AS cliente, so.amount_total AS total
FROM sale_order so
JOIN res_partner rp ON rp.id = so.partner_id
WHERE so.state IN ('sale', 'done')
ORDER BY so.date_order DESC
LIMIT 20;

-- 13. Buscar una compra por proveedor.
-- VALOR A CAMBIAR: 'Proveedor Regional' por el nombre o parte del proveedor.
SELECT po.name AS pedido, po.date_order AS fecha,
       rp.name AS proveedor, po.state AS estado,
       po.amount_total AS total
FROM purchase_order po
JOIN res_partner rp ON rp.id = po.partner_id
WHERE rp.name ILIKE '%Proveedor Regional%'
ORDER BY po.date_order DESC;

-- 14. Ver cotizaciones de venta pendientes.
SELECT so.name AS cotizacion, so.date_order AS fecha,
       rp.name AS cliente, so.amount_total AS total,
       so.state AS estado
FROM sale_order so
JOIN res_partner rp ON rp.id = so.partner_id
WHERE so.state IN ('draft', 'sent')
ORDER BY so.date_order DESC;

-- 15. Ver cotizaciones de compra pendientes.
SELECT po.name AS cotizacion, po.date_order AS fecha,
       rp.name AS proveedor, po.amount_total AS total,
       po.state AS estado
FROM purchase_order po
JOIN res_partner rp ON rp.id = po.partner_id
WHERE po.state IN ('draft', 'sent')
ORDER BY po.date_order DESC;

-- 16. Buscar una factura por número, cliente o proveedor.
-- VALORES A CAMBIAR: 'INV/2026' por el número o parte de la factura,
-- y 'Cliente QuetzalMart 01' por el nombre del tercero.
SELECT am.name AS factura, am.invoice_date AS fecha,
       rp.name AS tercero, am.move_type AS tipo,
       am.state AS estado, am.payment_state AS estado_pago,
       am.amount_total AS total
FROM account_move am
JOIN res_partner rp ON rp.id = am.partner_id
WHERE am.name ILIKE '%INV/2026%'
   OR rp.name ILIKE '%Cliente QuetzalMart 01%'
ORDER BY am.invoice_date DESC;

-- 17. Ver facturas publicadas que aún no están pagadas.
SELECT am.name AS factura, am.invoice_date AS fecha,
       rp.name AS tercero, am.move_type AS tipo,
       am.payment_state AS estado_pago,
       am.amount_total AS total
FROM account_move am
JOIN res_partner rp ON rp.id = am.partner_id
WHERE am.state = 'posted'
  AND am.payment_state IN ('not_paid', 'partial')
  AND am.move_type IN ('out_invoice', 'in_invoice')
ORDER BY am.invoice_date DESC;

-- 18. Productos cargados por el RPA.
-- VALORES A CAMBIAR: 'RPA-DEMO-%', 'E-COM%' y 'RPA Demo%'
-- por los prefijos o nombres que traiga el Excel auxiliar.
SELECT pp.id,
       COALESCE(pt.name ->> 'es_GT', pt.name ->> 'en_US', '') AS producto,
       pp.default_code AS referencia,
       pp.barcode AS codigo_barras,
       pt.list_price AS precio_venta
FROM product_product pp
JOIN product_template pt ON pt.id = pp.product_tmpl_id
WHERE pp.default_code ILIKE 'RPA-DEMO-%'
   OR pp.default_code ILIKE 'E-COM%'
   OR COALESCE(pt.name ->> 'es_GT', pt.name ->> 'en_US', '') ILIKE 'RPA Demo%'
ORDER BY referencia;

-- 19. Clientes cargados por el RPA.
-- VALORES A CAMBIAR: 'RPA-CLI-%', 'RPA Cliente%', 'rpa.cliente%',
-- 'PRUEBA SS%' y 'CUST%' por los prefijos usados en el Excel.
SELECT id, name AS cliente, ref AS referencia,
       vat AS nit, email, phone, active
FROM res_partner
WHERE ref ILIKE 'RPA-CLI-%'
   OR name ILIKE 'RPA Cliente%'
   OR email ILIKE 'rpa.cliente%'
   OR name ILIKE 'PRUEBA SS%'
   OR ref ILIKE 'CUST%'
ORDER BY referencia, cliente;

-- 20. Resumen rápido de cantidades principales.
SELECT 'clientes comerciales activos' AS elemento, COUNT(*) AS cantidad
FROM res_partner
WHERE active AND customer_rank > 0
UNION ALL
SELECT 'productos activos', COUNT(*)
FROM product_product pp
JOIN product_template pt ON pt.id = pp.product_tmpl_id
WHERE pt.active
UNION ALL
SELECT 'empleados activos', COUNT(*)
FROM hr_employee
WHERE active
UNION ALL
SELECT 'ventas confirmadas', COUNT(*)
FROM sale_order
WHERE state IN ('sale', 'done')
UNION ALL
SELECT 'compras confirmadas', COUNT(*)
FROM purchase_order
WHERE state IN ('purchase', 'done');
