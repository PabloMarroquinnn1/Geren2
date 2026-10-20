-- Las cotizaciones permanecen en borrador y son adicionales a las transacciones.
SELECT 'cotizaciones de venta' AS elemento, COUNT(*) AS cantidad
FROM sale_order
WHERE client_order_ref LIKE 'B5-SQ-%' AND state IN ('draft', 'sent')
UNION ALL
SELECT 'cotizaciones de compra', COUNT(*)
FROM purchase_order
WHERE partner_ref LIKE 'B5-PQ-%' AND state IN ('draft', 'sent');

-- Ventas y compras confirmadas.
SELECT 'ventas confirmadas' AS elemento, COUNT(*) AS cantidad
FROM sale_order
WHERE client_order_ref LIKE 'B5-SALE-%' AND state IN ('sale', 'done')
UNION ALL
SELECT 'compras confirmadas', COUNT(*)
FROM purchase_order
WHERE partner_ref LIKE 'B5-PO-%' AND state IN ('purchase', 'done');

-- Facturas de clientes y proveedores publicadas vinculadas a sus órdenes.
SELECT 'facturas de cliente publicadas' AS elemento,
       COUNT(DISTINCT am.id) AS cantidad
FROM account_move am
JOIN account_move_line aml ON aml.move_id = am.id
JOIN sale_order_line_invoice_rel solir ON solir.invoice_line_id = aml.id
JOIN sale_order_line sol ON sol.id = solir.order_line_id
JOIN sale_order so ON so.id = sol.order_id
WHERE am.move_type = 'out_invoice'
  AND am.state = 'posted'
  AND so.client_order_ref LIKE 'B5-SALE-%'
UNION ALL
SELECT 'facturas de proveedor publicadas', COUNT(DISTINCT am.id)
FROM account_move am
JOIN account_move_line aml ON aml.move_id = am.id
JOIN purchase_order_line pol ON pol.id = aml.purchase_line_id
JOIN purchase_order po ON po.id = pol.order_id
WHERE am.move_type = 'in_invoice'
  AND am.state = 'posted'
  AND po.partner_ref LIKE 'B5-PO-%';

-- Distribución de transacciones por sucursal.
SELECT sw.name AS sucursal, COUNT(*) AS ventas
FROM sale_order so
JOIN stock_warehouse sw ON sw.id = so.warehouse_id
WHERE so.client_order_ref LIKE 'B5-SALE-%'
  AND so.state IN ('sale', 'done')
GROUP BY sw.name
ORDER BY sw.name;
