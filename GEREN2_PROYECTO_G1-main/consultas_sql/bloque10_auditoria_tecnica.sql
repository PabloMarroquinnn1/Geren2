-- Bloque 10 - auditoría técnica previa a la evidencia.
-- Solo lectura. Ejecutar en la base quetzalmart.
-- Las salidas de estas consultas sirven para decidir qué capturas faltan.

-- 1. Módulos técnicos instalados y activos.
SELECT name, state
FROM ir_module_module
WHERE name IN (
    'sale_management', 'purchase_stock', 'stock', 'account', 'hr',
    'hr_contract', 'crm', 'website_sale', 'mass_mailing', 'l10n_gt',
    'dms', 'payment_demo', 'delivery'
)
ORDER BY name;

-- 2. Compañía y almacenes; el auxiliar indicó que tres almacenes son suficientes.
SELECT rc.id, rc.name AS compania, rc.currency_id
FROM res_company rc
ORDER BY rc.id;

SELECT sw.name AS almacen, sw.code, rc.name AS compania
FROM stock_warehouse sw
JOIN res_company rc ON rc.id = sw.company_id
ORDER BY sw.code;

-- 3. Conteos de datos maestros solicitados.
SELECT 'departamentos activos' AS elemento, COUNT(*) AS cantidad
FROM hr_department WHERE active
UNION ALL
SELECT 'cargos', COUNT(*) FROM hr_job
UNION ALL
SELECT 'empleados activos', COUNT(*) FROM hr_employee WHERE active
UNION ALL
SELECT 'contratos', COUNT(*) FROM hr_contract
UNION ALL
SELECT 'clientes comerciales', COUNT(*) FROM res_partner WHERE active AND customer_rank > 0
UNION ALL
SELECT 'proveedores comerciales', COUNT(*) FROM res_partner WHERE active AND supplier_rank > 0
UNION ALL
SELECT 'productos QM', COUNT(*) FROM product_product WHERE default_code LIKE 'QM-%'
UNION ALL
SELECT 'materiales operativos internos QMI', COUNT(*)
FROM product_product WHERE default_code LIKE 'QMI-%'
ORDER BY elemento;

-- Materiales internos: 60 registros, con imagen, no publicables y con existencias por sucursal.
SELECT COUNT(*) AS materiales,
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

-- 4. Existencias agregadas por almacén.
SELECT sw.name AS almacen,
       ROUND(COALESCE(SUM(sq.quantity), 0)::numeric, 2) AS unidades,
       COUNT(DISTINCT sq.product_id) AS productos_con_existencia
FROM stock_warehouse sw
JOIN stock_location sl ON sl.id = sw.lot_stock_id
LEFT JOIN stock_quant sq ON sq.location_id = sl.id
GROUP BY sw.id, sw.name
ORDER BY sw.name;

-- 5. Cotizaciones de venta y compra; deben ser 20 de cada tipo.
SELECT 'cotizaciones de venta' AS elemento, COUNT(*) AS cantidad
FROM sale_order WHERE state IN ('draft', 'sent')
UNION ALL
SELECT 'cotizaciones de compra', COUNT(*)
FROM purchase_order WHERE state IN ('draft', 'sent');

-- 6. Ventas confirmadas; el mínimo es 150.
SELECT COUNT(*) AS ventas_confirmadas,
       COUNT(DISTINCT partner_id) AS clientes_con_venta,
       COUNT(DISTINCT warehouse_id) AS almacenes_con_venta
FROM sale_order
WHERE state IN ('sale', 'done');

-- 7. Compras confirmadas y compras con factura de proveedor publicada.
SELECT COUNT(*) AS compras_confirmadas
FROM purchase_order
WHERE state IN ('purchase', 'done');

SELECT COUNT(DISTINCT po.id) AS compras_con_factura_publicada
FROM purchase_order po
JOIN purchase_order_line pol ON pol.order_id = po.id
JOIN account_move_line aml ON aml.purchase_line_id = pol.id
JOIN account_move am ON am.id = aml.move_id
WHERE po.state IN ('purchase', 'done')
  AND am.move_type = 'in_invoice'
  AND am.state = 'posted';

-- 8. Facturas publicadas; el mínimo del enunciado es 50.
SELECT move_type AS tipo, COUNT(*) AS cantidad
FROM account_move
WHERE state = 'posted'
  AND move_type IN ('out_invoice', 'in_invoice')
GROUP BY move_type
ORDER BY move_type;

-- 9. Impuestos activos.
SELECT name, amount, type_tax_use, active
FROM account_tax
WHERE active
ORDER BY type_tax_use, amount DESC;

-- 10. Configuración técnica de la tienda, envío y pago de prueba.
SELECT w.name AS sitio_web,
       rl.code AS idioma,
       w.shop_ppg AS productos_por_pagina
FROM website w
LEFT JOIN res_lang rl ON rl.id = w.default_lang_id
ORDER BY w.id
LIMIT 1;

SELECT name, delivery_type, fixed_price, free_over,
       amount AS envio_gratis_desde, is_published
FROM delivery_carrier
WHERE is_published
ORDER BY name;

SELECT code, state, name
FROM payment_provider
WHERE code = 'demo';

-- 11. CRM y marketing: existencia de equipos, oportunidades y campañas.
SELECT 'equipos CRM' AS elemento, COUNT(*) AS cantidad FROM crm_team
UNION ALL
SELECT 'oportunidades/leads', COUNT(*) FROM crm_lead
UNION ALL
SELECT 'campañas de correo', COUNT(*) FROM mailing_mailing
UNION ALL
SELECT 'contactos de marketing', COUNT(*) FROM mailing_contact;

-- 12. Servidores de correo configurados, sin mostrar contraseñas.
SELECT name, smtp_host, smtp_port, smtp_user, active
FROM ir_mail_server
ORDER BY id;

-- 13. Gestión documental: directorios y archivos almacenados.
SELECT 'directorios DMS' AS elemento, COUNT(*) AS cantidad FROM dms_directory
UNION ALL
SELECT 'archivos DMS', COUNT(*) FROM dms_file;

-- 14. Seguimiento GA4 instalado en vistas QWeb.
SELECT id, name, key
FROM ir_ui_view
WHERE arch_db::text ILIKE '%G-ZB34R27HPD%'
   OR arch_db::text ILIKE '%view_item%'
   OR arch_db::text ILIKE '%add_to_cart%'
   OR arch_db::text ILIKE '%begin_checkout%'
   OR arch_db::text ILIKE '%purchase%'
ORDER BY id;

-- 15. Productos y clientes de prueba cargados por el RPA.
SELECT pp.default_code AS referencia,
       COALESCE(pt.name ->> 'es_GT', pt.name ->> 'en_US', '') AS producto,
       pp.barcode,
       pt.is_published
FROM product_product pp
JOIN product_template pt ON pt.id = pp.product_tmpl_id
WHERE pp.default_code ILIKE 'RPA-DEMO-%'
   OR pp.default_code ILIKE 'E-COM%'
   OR COALESCE(pt.name ->> 'es_GT', pt.name ->> 'en_US', '') ILIKE 'PRUEBA PRODUCTO SS%'
ORDER BY referencia;

SELECT id, name AS cliente, ref, email, active
FROM res_partner
WHERE name ILIKE 'PRUEBA SS%'
   OR name ILIKE 'RPA Cliente%'
   OR ref ILIKE 'RPA-CLI-%'
   OR ref ILIKE 'CUST%'
ORDER BY name;
