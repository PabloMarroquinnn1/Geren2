SELECT 'productos publicados' AS elemento, COUNT(*) AS cantidad
FROM product_product pp
JOIN product_template pt ON pt.id = pp.product_tmpl_id
WHERE pp.default_code LIKE 'QM-%' AND pt.is_published
UNION ALL
SELECT 'productos con imagen', COUNT(DISTINCT pt.id)
FROM product_product pp
JOIN product_template pt ON pt.id = pp.product_tmpl_id
JOIN ir_attachment ia
  ON ia.res_model = 'product.template'
 AND ia.res_id = pt.id
 AND ia.res_field = 'image_1920'
WHERE pp.default_code LIKE 'QM-%';

SELECT COALESCE(dc.name->>'es_419', dc.name->>'en_US') AS transportista,
       dc.delivery_type,
       dc.fixed_price,
       dc.free_over,
       dc.amount AS envio_gratis_desde,
       dc.is_published
FROM delivery_carrier dc
WHERE COALESCE(dc.name->>'es_419', dc.name->>'en_US') = 'Envío estándar QuetzalMart';

SELECT pp.code, pp.state
FROM payment_provider pp
WHERE pp.code = 'demo';

SELECT w.name, rl.code AS idioma_predeterminado, w.shop_ppg
FROM website w
JOIN res_lang rl ON rl.id = w.default_lang_id
ORDER BY w.id
LIMIT 1;

SELECT so.name AS pedido_web,
       so.state,
       so.amount_untaxed,
       so.amount_tax,
       so.amount_total,
       COALESCE(dc.name->>'es_419', dc.name->>'en_US') AS transportista,
       COUNT(DISTINCT am.id) AS facturas,
       STRING_AGG(DISTINCT am.name, ', ') AS numeros_factura
FROM sale_order so
LEFT JOIN delivery_carrier dc ON dc.id = so.carrier_id
LEFT JOIN sale_order_line sol ON sol.order_id = so.id
LEFT JOIN sale_order_line_invoice_rel rel ON rel.order_line_id = sol.id
LEFT JOIN account_move_line aml ON aml.id = rel.invoice_line_id
LEFT JOIN account_move am ON am.id = aml.move_id
WHERE so.name = 'S00171'
GROUP BY so.name, so.state, so.amount_untaxed, so.amount_tax,
         so.amount_total, dc.name;
