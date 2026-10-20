-- =====================================================================
-- QuetzalMart · Consultas SQL para la calificación
-- Base: quetzalmart (PostgreSQL 16, Odoo 18 Community)
--
-- Conexión con DBeaver: túnel SSH a la VM y PostgreSQL en localhost:5432,
-- usuario de solo lectura "consulta" (ver docs/01_despliegue_nube.md).
-- Ejecute cada bloque por separado (Ctrl+Enter sobre la consulta).
-- Los nombres traducibles de Odoo se guardan como JSON por idioma: por eso
-- se usa COALESCE(nombre->>'es_419', nombre->>'en_US').
-- =====================================================================

-- 0. Conexión
SELECT current_database() AS base, current_user AS usuario, version() AS servidor, now() AS fecha;


-- =====================================================================
-- 1. VENTAS (enunciado: al menos 150 ventas con distintos productos y clientes)
-- =====================================================================

-- 1.1 Total de ventas confirmadas, clientes y productos distintos
SELECT COUNT(DISTINCT so.id)          AS ventas_confirmadas,
       COUNT(DISTINCT so.partner_id)  AS clientes_distintos,
       COUNT(DISTINCT sol.product_id) AS productos_distintos,
       ROUND(SUM(sol.price_total), 2) AS total_vendido_gtq
FROM sale_order so
JOIN sale_order_line sol ON sol.order_id = so.id AND sol.display_type IS NULL
WHERE so.state = 'sale';

-- 1.2 Ventas por sucursal (almacén) y equipo de ventas
SELECT sw.name AS sucursal,
       COALESCE(ct.name->>'es_419', ct.name->>'en_US') AS equipo,
       COUNT(*) AS ventas,
       ROUND(SUM(so.amount_total), 2) AS total_gtq
FROM sale_order so
JOIN stock_warehouse sw ON sw.id = so.warehouse_id
LEFT JOIN crm_team ct ON ct.id = so.team_id
WHERE so.state = 'sale'
GROUP BY sw.name, equipo
ORDER BY ventas DESC;

-- 1.3 Detalle de ventas (pedido, fecha, cliente, productos, total, factura)
SELECT so.name AS pedido,
       so.date_order::date AS fecha,
       rp.name AS cliente,
       sw.code AS sucursal,
       STRING_AGG(COALESCE(pt.name->>'es_419', pt.name->>'en_US') || ' x' || sol.product_uom_qty::int, ', ') AS productos,
       so.amount_total AS total,
       (SELECT STRING_AGG(am.name, ', ') FROM account_move am
          JOIN account_move_line aml ON aml.move_id = am.id
          JOIN sale_order_line_invoice_rel r ON r.invoice_line_id = aml.id
          JOIN sale_order_line l2 ON l2.id = r.order_line_id
         WHERE l2.order_id = so.id AND am.move_type = 'out_invoice') AS factura
FROM sale_order so
JOIN res_partner rp ON rp.id = so.partner_id
JOIN stock_warehouse sw ON sw.id = so.warehouse_id
JOIN sale_order_line sol ON sol.order_id = so.id AND sol.display_type IS NULL
JOIN product_product pp ON pp.id = sol.product_id
JOIN product_template pt ON pt.id = pp.product_tmpl_id
WHERE so.state = 'sale'
GROUP BY so.id, rp.name, sw.code
ORDER BY so.date_order DESC;

-- 1.4 Productos más vendidos
SELECT pp.default_code AS sku,
       COALESCE(pt.name->>'es_419', pt.name->>'en_US') AS producto,
       SUM(sol.product_uom_qty) AS unidades,
       ROUND(SUM(sol.price_total), 2) AS ingresos_gtq
FROM sale_order_line sol
JOIN sale_order so ON so.id = sol.order_id AND so.state = 'sale'
JOIN product_product pp ON pp.id = sol.product_id
JOIN product_template pt ON pt.id = pp.product_tmpl_id
WHERE pt.type = 'consu' AND pt.sale_ok
GROUP BY pp.default_code, producto
ORDER BY unidades DESC
LIMIT 10;


-- =====================================================================
-- 2. COTIZACIONES (enunciado: al menos 20 a clientes y proveedores)
-- =====================================================================

-- 2.1 Conteo de cotizaciones de venta (a clientes) y de compra (a proveedores)
SELECT 'Cotizaciones de venta' AS tipo, COUNT(*) AS cantidad FROM sale_order WHERE state IN ('draft', 'sent')
UNION ALL
SELECT 'Solicitudes de cotización de compra', COUNT(*) FROM purchase_order WHERE state IN ('draft', 'sent');

-- 2.2 Detalle de cotizaciones de venta
SELECT so.name AS cotizacion, so.create_date::date AS fecha, rp.name AS cliente,
       so.validity_date AS valida_hasta, so.amount_total AS total,
       CASE so.state WHEN 'draft' THEN 'Borrador' ELSE 'Enviada' END AS estado
FROM sale_order so JOIN res_partner rp ON rp.id = so.partner_id
WHERE so.state IN ('draft', 'sent')
ORDER BY so.name;

-- 2.3 Detalle de solicitudes de cotización a proveedores
SELECT po.name AS solicitud, po.partner_ref AS referencia, rp.name AS proveedor,
       po.amount_total AS total,
       CASE po.state WHEN 'draft' THEN 'Borrador' ELSE 'Enviada' END AS estado
FROM purchase_order po JOIN res_partner rp ON rp.id = po.partner_id
WHERE po.state IN ('draft', 'sent')
ORDER BY po.name;


-- =====================================================================
-- 3. EMPLEADOS (enunciado: al menos 35 empleados, 6 cargos y 5 departamentos)
-- =====================================================================

-- 3.1 Conteos
SELECT (SELECT COUNT(*) FROM hr_employee WHERE active)   AS empleados,
       (SELECT COUNT(*) FROM hr_job WHERE active)        AS cargos,
       (SELECT COUNT(*) FROM hr_department WHERE active) AS departamentos,
       (SELECT COUNT(*) FROM hr_contract WHERE state = 'open') AS contratos_vigentes;

-- 3.2 Empleados con cargo, departamento, sucursal y jefe inmediato
SELECT e.name AS empleado,
       COALESCE(j.name->>'es_419', j.name->>'en_US') AS cargo,
       COALESCE(d.name->>'es_419', d.name->>'en_US') AS departamento,
       wl.name AS sucursal,
       jefe.name AS jefe_inmediato,
       e.work_email AS correo
FROM hr_employee e
LEFT JOIN hr_job j ON j.id = e.job_id
LEFT JOIN hr_department d ON d.id = e.department_id
LEFT JOIN hr_work_location wl ON wl.id = e.work_location_id
LEFT JOIN hr_employee jefe ON jefe.id = e.parent_id
WHERE e.active
ORDER BY departamento, cargo, empleado;

-- 3.3 Empleados por cargo y por departamento
SELECT COALESCE(d.name->>'es_419', d.name->>'en_US') AS departamento,
       COALESCE(j.name->>'es_419', j.name->>'en_US') AS cargo,
       COUNT(e.id) AS empleados,
       ROUND(AVG(c.wage), 2) AS salario_promedio_gtq
FROM hr_job j
LEFT JOIN hr_department d ON d.id = j.department_id
LEFT JOIN hr_employee e ON e.job_id = j.id AND e.active
LEFT JOIN hr_contract c ON c.employee_id = e.id AND c.state = 'open'
GROUP BY departamento, cargo
ORDER BY departamento, cargo;


-- =====================================================================
-- 4. COMPRAS (enunciado: al menos 100 compras y sus facturas)
-- =====================================================================

-- 4.1 Compras confirmadas y facturas de proveedor publicadas
SELECT (SELECT COUNT(*) FROM purchase_order WHERE state IN ('purchase', 'done')) AS compras_confirmadas,
       (SELECT COUNT(*) FROM account_move WHERE move_type = 'in_invoice' AND state = 'posted') AS facturas_proveedor,
       (SELECT COUNT(*) FROM stock_picking sp JOIN stock_picking_type spt ON spt.id = sp.picking_type_id
         WHERE spt.code = 'incoming' AND sp.state = 'done') AS recepciones_validadas;

-- 4.2 Detalle: compra, proveedor, sucursal que recibe, factura y estado de pago
SELECT po.name AS compra, po.date_approve::date AS fecha, rp.name AS proveedor,
       sw.name AS sucursal, po.amount_total AS total,
       am.name AS factura_odoo, am.ref AS factura_proveedor,
       CASE am.payment_state WHEN 'paid' THEN 'Pagada' WHEN 'in_payment' THEN 'En pago'
            WHEN 'not_paid' THEN 'Pendiente' ELSE am.payment_state END AS pago
FROM purchase_order po
JOIN res_partner rp ON rp.id = po.partner_id
JOIN stock_picking_type spt ON spt.id = po.picking_type_id
JOIN stock_warehouse sw ON sw.id = spt.warehouse_id
LEFT JOIN account_move am ON am.move_type = 'in_invoice' AND am.invoice_origin = po.name
WHERE po.state IN ('purchase', 'done')
ORDER BY po.date_approve DESC;


-- =====================================================================
-- 5. MATERIALES (enunciado: al menos 60 materiales para que cada sucursal funcione)
-- =====================================================================

-- 5.1 Materiales por categoría
SELECT pc.name AS categoria, COUNT(*) AS materiales
FROM product_template pt JOIN product_category pc ON pc.id = pt.categ_id
WHERE pt.default_code LIKE 'MAT-%'
GROUP BY pc.name ORDER BY pc.name;

-- 5.2 Existencias de materiales en cada sucursal
SELECT pp.default_code AS codigo,
       COALESCE(pt.name->>'es_419', pt.name->>'en_US') AS material,
       SUM(sq.quantity) FILTER (WHERE sw.code = 'GUA') AS guatemala,
       SUM(sq.quantity) FILTER (WHERE sw.code = 'MEX') AS mexico,
       SUM(sq.quantity) FILTER (WHERE sw.code = 'SAL') AS el_salvador
FROM product_product pp
JOIN product_template pt ON pt.id = pp.product_tmpl_id
LEFT JOIN stock_quant sq ON sq.product_id = pp.id
LEFT JOIN stock_location sl ON sl.id = sq.location_id AND sl.usage = 'internal'
LEFT JOIN stock_warehouse sw ON sw.id = sl.warehouse_id
WHERE pp.default_code LIKE 'MAT-%'
GROUP BY pp.default_code, material
ORDER BY pp.default_code;


-- =====================================================================
-- 6. FACTURAS (enunciado: al menos 50 facturas y su PDF en una carpeta)
-- =====================================================================

-- 6.1 Facturas publicadas por tipo
SELECT CASE move_type WHEN 'out_invoice' THEN 'Factura de cliente' WHEN 'in_invoice' THEN 'Factura de proveedor'
            ELSE move_type END AS tipo,
       COUNT(*) AS cantidad, ROUND(SUM(amount_total), 2) AS total_gtq
FROM account_move
WHERE state = 'posted' AND move_type IN ('out_invoice', 'in_invoice')
GROUP BY move_type;

-- 6.2 PDF de facturas guardados en la carpeta "Facturas de venta" del gestor documental
SELECT dd.name AS carpeta, COUNT(df.id) AS pdf_archivados, MAX(df.create_date) AS ultimo_archivado
FROM dms_directory dd LEFT JOIN dms_file df ON df.directory_id = dd.id AND df.active
WHERE dd.name = 'Facturas de venta'
GROUP BY dd.name;

-- 6.3 Últimas facturas con su PDF (las generadas durante la calificación aparecen primero)
SELECT am.name AS factura, am.invoice_date AS fecha, rp.name AS cliente, am.amount_total AS total,
       df.name AS pdf_en_documentos, df.create_date AS archivado
FROM account_move am
JOIN res_partner rp ON rp.id = am.partner_id
LEFT JOIN dms_file df ON df.id = am.qm_documento_id
WHERE am.move_type = 'out_invoice' AND am.state = 'posted'
ORDER BY am.id DESC
LIMIT 20;


-- =====================================================================
-- 7. TIENDA EN LÍNEA (catálogo publicado y pedidos web)
-- =====================================================================

-- 7.1 Productos publicados por categoría de la tienda
SELECT COALESCE(c.name->>'es_419', c.name->>'en_US') AS categoria_web, COUNT(*) AS publicados
FROM product_template pt
JOIN product_public_category_product_template_rel r ON r.product_template_id = pt.id
JOIN product_public_category c ON c.id = r.product_public_category_id
WHERE pt.is_published
GROUP BY categoria_web ORDER BY categoria_web;

-- 7.2 Pedidos hechos en la tienda en línea, con pago, factura y oportunidad del CRM
SELECT so.name AS pedido, so.date_order AS fecha, rp.name AS cliente, rp.email,
       so.amount_total AS total, pt.state AS pago, pt.provider_reference AS transaccion,
       lead.name AS oportunidad_crm
FROM sale_order so
JOIN res_partner rp ON rp.id = so.partner_id
LEFT JOIN sale_order_transaction_rel str ON str.sale_order_id = so.id
LEFT JOIN payment_transaction pt ON pt.id = str.transaction_id
LEFT JOIN crm_lead lead ON lead.id = so.opportunity_id
WHERE so.website_id IS NOT NULL AND so.state = 'sale'
ORDER BY so.date_order DESC;


-- =====================================================================
-- 8. INVENTARIO POR SUCURSAL Y SECTOR
-- =====================================================================
SELECT sw.name AS sucursal, sl.name AS sector,
       COUNT(DISTINCT sq.product_id) AS productos, ROUND(SUM(sq.quantity)::numeric, 0) AS unidades
FROM stock_quant sq
JOIN stock_location sl ON sl.id = sq.location_id AND sl.usage = 'internal'
JOIN stock_warehouse sw ON sw.id = sl.warehouse_id
WHERE sq.quantity > 0
GROUP BY sw.name, sl.name
ORDER BY sw.name, sl.name;


-- =====================================================================
-- 9. RPA (información cargada por el robot de UiPath)
-- =====================================================================

-- 9.1 Resumen por archivo de origen
SELECT 'Cliente' AS tipo, qm_origen_rpa AS archivo, COUNT(*) AS registros
FROM res_partner WHERE qm_origen_rpa IS NOT NULL GROUP BY qm_origen_rpa
UNION ALL
SELECT 'Producto', qm_origen_rpa, COUNT(*)
FROM product_template WHERE qm_origen_rpa IS NOT NULL GROUP BY qm_origen_rpa
ORDER BY tipo, archivo;

-- 9.2 Clientes cargados por el robot (con país, estado, empresa y etiquetas ya resueltos)
SELECT p.name AS cliente,
       CASE WHEN p.is_company THEN 'Empresa' ELSE 'Persona' END AS tipo,
       p.email, p.phone, p.vat AS nit, p.city AS ciudad,
       s.name AS estado, COALESCE(c.name->>'es_419', c.name->>'en_US') AS pais,
       empresa.name AS empresa_relacionada, p.ref AS referencia,
       (SELECT STRING_AGG(COALESCE(t.name->>'es_419', t.name->>'en_US'), ', ')
          FROM res_partner_res_partner_category_rel r JOIN res_partner_category t ON t.id = r.category_id
         WHERE r.partner_id = p.id) AS etiquetas,
       p.create_date AS cargado
FROM res_partner p
LEFT JOIN res_country c ON c.id = p.country_id
LEFT JOIN res_country_state s ON s.id = p.state_id
LEFT JOIN res_partner empresa ON empresa.id = p.parent_id
WHERE p.qm_origen_rpa IS NOT NULL
ORDER BY p.create_date DESC, p.name;

-- 9.3 Productos cargados por el robot (con existencias y publicación en la web)
SELECT pt.default_code AS referencia,
       COALESCE(pt.name->>'es_419', pt.name->>'en_US') AS producto,
       CASE pt.type WHEN 'consu' THEN 'Bien' WHEN 'service' THEN 'Servicio' ELSE pt.type END AS tipo,
       pp.barcode AS codigo_barras, pt.list_price AS precio,
       (pp.standard_price->>'1')::numeric AS costo,  -- Odoo 18 guarda el costo por compañía (id 1)
       pt.weight AS peso,
       pt.qm_cantidad_inicial AS cantidad_excel,
       (SELECT SUM(sq.quantity) FROM stock_quant sq JOIN stock_location sl ON sl.id = sq.location_id
         WHERE sq.product_id = pp.id AND sl.usage = 'internal') AS cantidad_a_la_mano,
       pt.is_published AS publicado_en_web,
       imd.module || '.' || imd.name AS id_externo
FROM product_template pt
JOIN product_product pp ON pp.product_tmpl_id = pt.id
LEFT JOIN ir_model_data imd ON imd.model = 'product.template' AND imd.res_id = pt.id
WHERE pt.qm_origen_rpa IS NOT NULL
ORDER BY pt.create_date DESC;


-- =====================================================================
-- 10. CRM
-- =====================================================================

-- 10.1 Embudo por etapa
SELECT COALESCE(s.name->>'es_419', s.name->>'en_US') AS etapa,
       COUNT(*) FILTER (WHERE l.type = 'lead') AS leads,
       COUNT(*) FILTER (WHERE l.type = 'opportunity') AS oportunidades,
       ROUND(SUM(l.expected_revenue), 2) AS ingreso_esperado
FROM crm_lead l LEFT JOIN crm_stage s ON s.id = l.stage_id
WHERE l.active
GROUP BY etapa, s.sequence ORDER BY s.sequence;

-- 10.2 Registros en la tienda (leads) y compras en línea (oportunidades ganadas)
SELECT l.create_date AS fecha, l.name, l.type, l.email_from, l.probability,
       COALESCE(t.name->>'es_419', t.name->>'en_US') AS etiqueta
FROM crm_lead l
JOIN crm_tag_rel r ON r.lead_id = l.id
JOIN crm_tag t ON t.id = r.tag_id
WHERE COALESCE(t.name->>'es_419', t.name->>'en_US') IN ('Registro web', 'Cliente tienda en línea')
ORDER BY l.create_date DESC;


-- =====================================================================
-- 11. MARKETING: correos enviados (comprobante de compra y campaña)
-- Cambie el correo del auxiliar en la línea marcada.
-- =====================================================================
SELECT mm.id, msg.subject AS asunto, mm.email_to, rp.email AS destinatario,
       mm.state AS estado, mm.scheduled_date AS programado, msg.date AS creado,
       msg.model AS documento
FROM mail_mail mm
JOIN mail_message msg ON msg.id = mm.mail_message_id
LEFT JOIN mail_mail_res_partner_rel rel ON rel.mail_mail_id = mm.id
LEFT JOIN res_partner rp ON rp.id = rel.res_partner_id
WHERE (msg.subject ILIKE '%Comprobante de compra%' OR msg.subject ILIKE '%descuento%')
--  AND (mm.email_to ILIKE '%correo.del.auxiliar%' OR rp.email ILIKE '%correo.del.auxiliar%')
ORDER BY mm.id DESC
LIMIT 20;

-- 11.1 Listas de correo y contactos suscritos
SELECT ml.name AS lista, COUNT(ms.id) AS contactos
FROM mailing_list ml LEFT JOIN mailing_subscription ms ON ms.list_id = ml.id AND NOT ms.opt_out
GROUP BY ml.name ORDER BY ml.name;


-- =====================================================================
-- 12. GESTIÓN DOCUMENTAL (OCA DMS integrado a Odoo)
-- =====================================================================

-- 12.1 Documentos por carpeta y categoría
SELECT dd.name AS carpeta, COALESCE(dc.name->>'es_419', dc.name->>'en_US') AS categoria, COUNT(df.id) AS documentos
FROM dms_file df
JOIN dms_directory dd ON dd.id = df.directory_id
LEFT JOIN dms_category dc ON dc.id = df.category_id
WHERE df.active
GROUP BY dd.name, categoria ORDER BY dd.name;

-- 12.2 Facturas de proveedores, contratos de outsourcing y contratos de empleados con sus etiquetas
SELECT dd.name AS carpeta, df.name AS documento,
       STRING_AGG(COALESCE(dt.name->>'es_419', dt.name->>'en_US'), ', ') AS etiquetas,
       ROUND((df.size / 1024.0)::numeric, 1) AS kb, df.create_date AS subido
FROM dms_file df
JOIN dms_directory dd ON dd.id = df.directory_id
LEFT JOIN dms_file_tag_rel r ON r.fid = df.id
LEFT JOIN dms_tag dt ON dt.id = r.tid
WHERE dd.name IN ('Facturas de proveedores', 'Contratos de outsourcing', 'Contratos de empleados')
GROUP BY dd.name, df.id ORDER BY dd.name, df.name;


-- =====================================================================
-- 13. BÚSQUEDAS QUE PUEDE PEDIR EL AUXILIAR (cambie el texto entre % %)
-- =====================================================================

-- 13.1 Cliente o contacto por nombre
SELECT id, name AS nombre, email, phone, vat AS nit, city AS ciudad, ref AS referencia, qm_origen_rpa
FROM res_partner WHERE active AND name ILIKE '%PRUEBA%' ORDER BY name;

-- 13.2 Producto por nombre, referencia o código de barras
SELECT pt.id, pp.default_code AS referencia, COALESCE(pt.name->>'es_419', pt.name->>'en_US') AS producto,
       pp.barcode, pt.list_price AS precio, pt.is_published AS publicado
FROM product_template pt JOIN product_product pp ON pp.product_tmpl_id = pt.id
WHERE COALESCE(pt.name->>'es_419', pt.name->>'en_US') ILIKE '%PRUEBA%'
   OR pp.default_code ILIKE '%PRUEBA%' OR pp.barcode ILIKE '%PRUEBA%';

-- 13.3 Pedido por número (por ejemplo, el que hizo el auxiliar en la tienda)
SELECT so.name, so.state, so.amount_total, rp.name AS cliente, rp.email, so.date_order
FROM sale_order so JOIN res_partner rp ON rp.id = so.partner_id
WHERE so.name ILIKE '%S00%' ORDER BY so.id DESC LIMIT 10;
