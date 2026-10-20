-- Consultas SQL solicitadas directamente por el enunciado del proyecto.
-- Base: quetzalmart | Odoo Community 18 | PostgreSQL
--
-- Ejecuta cada consulta por separado en DBeaver con Ctrl+Enter.
-- Estas consultas son independientes de bloque9_verificacion.sql y
-- consultas_practicas_evaluacion.sql.
-- Los conteos y estados del enunciado no se cambian.
-- En las consultas de búsqueda, cambia únicamente los valores marcados.

-- 0. Confirmar la base y el usuario de la conexión.
SELECT current_database() AS base_de_datos,
       current_user AS usuario,
       now() AS fecha_consulta;
--------------------------------------------- 1.01---------------------------
-- 1. Enunciado: al menos 150 ventas.
SELECT COUNT(*) AS ventas_confirmadas
FROM sale_order
WHERE state IN ('sale', 'done');

-- 1.1. Enunciado: ventas con distintos clientes y productos.
SELECT COUNT(DISTINCT so.id) AS ventas,
       COUNT(DISTINCT so.partner_id) AS clientes_distintos,
       COUNT(DISTINCT sol.product_id) AS productos_distintos
FROM sale_order so
JOIN sale_order_line sol ON sol.order_id = so.id
WHERE so.state IN ('sale', 'done');

-- 1.2. Detalle de ventas para mostrarlo en la evaluación.
SELECT so.name AS pedido,
       so.date_order AS fecha,
       rp.name AS cliente,
       COALESCE(pt.name ->> 'es_GT', pt.name ->> 'en_US', '') AS producto,
       sol.product_uom_qty AS cantidad,
       so.amount_total AS total,
       so.state AS estado
FROM sale_order so
JOIN res_partner rp ON rp.id = so.partner_id
JOIN sale_order_line sol ON sol.order_id = so.id
LEFT JOIN product_product pp ON pp.id = sol.product_id
LEFT JOIN product_template pt ON pt.id = pp.product_tmpl_id
WHERE so.state IN ('sale', 'done')
ORDER BY so.date_order DESC, so.name
LIMIT 150;
--------------------------------------------- 1.02---------------------------
-- 2. Enunciado: al menos 20 cotizaciones de venta.
SELECT COUNT(*) AS cotizaciones_venta
FROM sale_order
WHERE state IN ('draft', 'sent');

-- 2.1. Enunciado: cotizaciones de compra.
SELECT COUNT(*) AS cotizaciones_compra
FROM purchase_order
WHERE state IN ('draft', 'sent');

-- 2.2. Detalle de cotizaciones de venta y compra.
SELECT so.name AS cotizacion,
       so.date_order AS fecha,
       rp.name AS cliente,
       so.amount_total AS total,
       so.state AS estado
FROM sale_order so
JOIN res_partner rp ON rp.id = so.partner_id
WHERE so.state IN ('draft', 'sent')
ORDER BY so.date_order DESC
LIMIT 20;

SELECT po.name AS cotizacion,
       po.date_order AS fecha,
       rp.name AS proveedor,
       po.amount_total AS total,
       po.state AS estado
FROM purchase_order po
JOIN res_partner rp ON rp.id = po.partner_id
WHERE po.state IN ('draft', 'sent')
ORDER BY po.date_order DESC
LIMIT 20;
--------------------------------------------- 1.03 & 1.04 & 1.05 ---------------------------
-- 3. Enunciado: al menos 35 empleados, 6 cargos y 5 departamentos.
SELECT 'empleados activos' AS elemento, COUNT(*) AS cantidad
FROM hr_employee
WHERE active
UNION ALL
SELECT 'cargos', COUNT(*)
FROM hr_job
UNION ALL
SELECT 'departamentos activos', COUNT(*)
FROM hr_department
WHERE active;

-- 3.1. Detalle de empleados, cargos y departamentos.
SELECT he.id,
       he.name AS empleado,
       hj.name AS cargo,
       hd.name AS departamento,
       he.work_email AS correo,
       he.work_phone AS telefono,
       he.active
FROM hr_employee he
LEFT JOIN hr_job hj ON hj.id = he.job_id
LEFT JOIN hr_department hd ON hd.id = he.department_id
WHERE he.active
ORDER BY he.name;
--------------------------------------------- 1.06---------------------------
-- 4. Enunciado: al menos 100 compras realizadas.
SELECT COUNT(*) AS compras_confirmadas
FROM purchase_order
WHERE state IN ('purchase', 'done');

-- 4.1. Compras confirmadas con factura de proveedor publicada.
SELECT COUNT(DISTINCT po.id) AS compras_con_factura
FROM purchase_order po
JOIN purchase_order_line pol ON pol.order_id = po.id
JOIN account_move_line aml ON aml.purchase_line_id = pol.id
JOIN account_move am ON am.id = aml.move_id
WHERE po.state IN ('purchase', 'done')
  AND am.move_type = 'in_invoice'
  AND am.state = 'posted';

-- 4.2. Detalle de compras y sus facturas.
SELECT po.name AS compra,
       po.date_order AS fecha,
       rp.name AS proveedor,
       po.state AS estado_compra,
       am.name AS factura,
       am.state AS estado_factura,
       po.amount_total AS total_compra
FROM purchase_order po
JOIN res_partner rp ON rp.id = po.partner_id
LEFT JOIN purchase_order_line pol ON pol.order_id = po.id
LEFT JOIN account_move_line aml ON aml.purchase_line_id = pol.id
LEFT JOIN account_move am
       ON am.id = aml.move_id
      AND am.move_type = 'in_invoice'
WHERE po.state IN ('purchase', 'done')
ORDER BY po.date_order DESC, po.name
LIMIT 100;
--------------------------------------------- 1.07---------------------------
-- 5. Enunciado: al menos 60 materiales/productos.
SELECT COUNT(*) AS materiales_quetzalmart
FROM product_product
WHERE default_code LIKE 'QM-%';

-- 5.1. Detalle de los materiales/productos cargados.
SELECT pp.id,
       COALESCE(pt.name ->> 'es_GT', pt.name ->> 'en_US', '') AS producto,
       pt.type AS tipo_producto,
       pp.default_code AS referencia_interna,
       pp.barcode AS codigo_barras,
       pt.list_price AS precio_venta,
       pp.standard_price AS costo,
       pt.weight AS peso,
       pt.is_published AS publicado,
       pt.active
FROM product_product pp
JOIN product_template pt ON pt.id = pp.product_tmpl_id
WHERE pp.default_code LIKE 'QM-%'
ORDER BY pp.default_code;

-- 5.2. Materiales operativos internos agregados para las sucursales.
-- Deben ser 60, tener imagen y no estar publicados ni habilitados para la venta.
SELECT COUNT(*) AS materiales_operativos,
       COUNT(*) FILTER (WHERE NOT pt.sale_ok) AS no_vendibles,
       COUNT(*) FILTER (WHERE NOT pt.is_published) AS no_publicados,
       COUNT(*) FILTER (WHERE EXISTS (
           SELECT 1 FROM ir_attachment ia
           WHERE ia.res_model = 'product.template'
             AND ia.res_id = pt.id
             AND ia.res_field = 'image_1920'
       )) AS con_imagen
FROM product_product pp
JOIN product_template pt ON pt.id = pp.product_tmpl_id
WHERE pp.default_code LIKE 'QMI-%';

-- 5.3. Existencias de los materiales operativos en cada sucursal.
SELECT sw.name AS sucursal,
       COUNT(DISTINCT pp.id) AS materiales_con_existencia,
       ROUND(COALESCE(SUM(sq.quantity), 0)::numeric, 2) AS unidades_internas
FROM stock_warehouse sw
JOIN stock_quant sq ON sq.location_id = sw.lot_stock_id
JOIN product_product pp ON pp.id = sq.product_id
WHERE sw.code IN ('GT', 'MX', 'SV')
  AND pp.default_code LIKE 'QMI-%'
  AND sq.quantity > 0
GROUP BY sw.id, sw.name
ORDER BY sw.code;

-- 5.4. Listado de artículos internos, categoría, costo, publicación e imagen.
SELECT pp.default_code AS codigo,
       COALESCE(pt.name ->> 'es_GT', pt.name ->> 'en_US', '') AS material,
       pc.name AS categoria,
       pp.standard_price AS costo,
       pt.sale_ok AS vendible,
       pt.is_published AS publicado,
       EXISTS (
           SELECT 1 FROM ir_attachment ia
           WHERE ia.res_model = 'product.template'
             AND ia.res_id = pt.id
             AND ia.res_field = 'image_1920'
       ) AS tiene_imagen
FROM product_product pp
JOIN product_template pt ON pt.id = pp.product_tmpl_id
LEFT JOIN product_category pc ON pc.id = pt.categ_id
WHERE pp.default_code LIKE 'QMI-%'
ORDER BY pp.default_code;

-- 6. Enunciado: al menos 50 facturas.
SELECT COUNT(*) AS facturas_publicadas
FROM account_move
WHERE state = 'posted'
  AND move_type IN ('out_invoice', 'in_invoice');

-- 6.1. Facturas de clientes y proveedores por tipo.
SELECT move_type AS tipo,
       COUNT(*) AS cantidad,
       SUM(amount_total) AS total
FROM account_move
WHERE state = 'posted'
  AND move_type IN ('out_invoice', 'in_invoice')
GROUP BY move_type
ORDER BY move_type;

-- 6.2. Detalle de las primeras 50 facturas publicadas.
SELECT am.name AS factura,
       am.invoice_date AS fecha,
       rp.name AS tercero,
       am.move_type AS tipo,
       am.amount_untaxed AS subtotal,
       am.amount_tax AS impuesto,
       am.amount_total AS total,
       am.payment_state AS estado_pago
FROM account_move am
JOIN res_partner rp ON rp.id = am.partner_id
WHERE am.state = 'posted'
  AND am.move_type IN ('out_invoice', 'in_invoice')
ORDER BY am.invoice_date, am.id
LIMIT 50;

-- 7. Búsqueda normal de cliente/contacto por nombre, como puede pedir el auxiliar.
-- VALOR A CAMBIAR: 'PRUEBA SS' por el nombre o parte del nombre.
SELECT id, name AS cliente, vat AS nit, email, phone,
       street, city, zip, website, ref AS referencia, active
FROM res_partner
WHERE active
  AND name ILIKE '%PRUEBA SS%'
ORDER BY name;

-- 8. Búsqueda normal de producto por nombre, referencia o código de barras.
-- VALORES A CAMBIAR: 'Arroz', 'QM-001' y '54398267125'.
-- Usa el nombre, referencia o código que te entregue el auxiliar.
SELECT pp.id,
       COALESCE(pt.name ->> 'es_GT', pt.name ->> 'en_US', '') AS producto,
       pp.default_code AS referencia,
       pp.barcode AS codigo_barras,
       pt.list_price AS precio_venta,
       pp.standard_price AS costo,
       pt.weight AS peso,
       pt.is_published AS publicado
FROM product_product pp
JOIN product_template pt ON pt.id = pp.product_tmpl_id
WHERE COALESCE(pt.name ->> 'es_GT', pt.name ->> 'en_US', '') ILIKE '%Arroz%'
   OR pp.default_code ILIKE '%QM-001%'
   OR pp.barcode = '54398267125'
ORDER BY producto;

-- 9. RPA: clientes cargados y campos principales solicitados.
-- Los prefijos son ejemplos de los archivos de prueba actuales.
-- Si el auxiliar usa otros prefijos, reemplázalos en estas condiciones.
SELECT rp.id,
       rp.name AS nombre,
       CASE WHEN rp.is_company THEN 'company' ELSE 'person' END AS tipo_compania,
       rp.email,
       rp.phone,
       rp.street,
       rp.street2,
       rp.city,
       rp.zip,
       rp.vat AS tax_id,
       rp.website,
       rp.ref AS referencia,
       rp.comment AS notas,
       rp.active
FROM res_partner rp
WHERE rp.ref ILIKE 'RPA-CLI-%'
   OR rp.name ILIKE 'RPA Cliente%'
   OR rp.email ILIKE 'rpa.cliente%'
   OR rp.name ILIKE 'PRUEBA SS%'
   OR rp.ref ILIKE 'CUST%'
ORDER BY rp.ref, rp.name;

-- 10. RPA: productos cargados y campos principales solicitados.
-- Los prefijos son ejemplos de los archivos de prueba actuales.
-- Agrega o reemplaza el prefijo/nombre que traiga el Excel auxiliar.
SELECT pp.id,
       COALESCE(pt.name ->> 'es_GT', pt.name ->> 'en_US', '') AS nombre,
       pt.type AS tipo_producto,
       pp.default_code AS referencia_interna,
       pp.barcode AS codigo_barras,
       pt.list_price AS precio_venta,
       pp.standard_price AS costo,
       pt.weight AS peso,
       pt.description_sale AS descripcion_ventas,
       pt.is_published AS esta_publicado,
       COALESCE(SUM(sq.quantity), 0) AS cantidad_a_la_mano
FROM product_product pp
JOIN product_template pt ON pt.id = pp.product_tmpl_id
LEFT JOIN stock_quant sq ON sq.product_id = pp.id
WHERE pp.default_code ILIKE 'RPA-DEMO-%'
   OR pp.default_code ILIKE 'E-COM%'
   OR COALESCE(pt.name ->> 'es_GT', pt.name ->> 'en_US', '') ILIKE 'RPA Demo%'
   OR COALESCE(pt.name ->> 'es_GT', pt.name ->> 'en_US', '') ILIKE 'PRUEBA PRODUCTO SS%'
GROUP BY pp.id, pt.id, pt.name, pt.type, pp.default_code,
         pp.barcode, pt.list_price, pp.standard_price, pt.weight,
         pt.description_sale, pt.is_published
ORDER BY pp.default_code;

-- 11. RPA: IDs externos de productos y contactos cargados.
SELECT module,
       name AS id_externo,
       model,
       res_id
FROM ir_model_data
WHERE (model = 'product.template' AND name ILIKE 'rpa_demo_product_%')
   OR (model = 'product.template' AND name ILIKE 'PRUEBA_PRODUCT_SS_%')
   OR (model = 'res.partner' AND name ILIKE 'rpa_cliente%')
ORDER BY model, name;
