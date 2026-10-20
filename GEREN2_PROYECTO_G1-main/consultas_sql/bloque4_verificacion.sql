-- Verificación de módulos instalados.
SELECT name, state
FROM ir_module_module
WHERE name IN (
    'sale_management', 'purchase_stock', 'stock', 'account', 'hr',
    'hr_contract', 'crm', 'website_sale', 'mass_mailing', 'l10n_gt',
    'dms', 'payment_demo'
)
ORDER BY name;

-- Conteos principales del bloque 4.
SELECT 'almacenes' AS elemento, COUNT(*) AS cantidad
FROM stock_warehouse
UNION ALL
SELECT 'departamentos activos', COUNT(*) FROM hr_department WHERE active
UNION ALL
SELECT 'puestos', COUNT(*) FROM hr_job
UNION ALL
SELECT 'empleados activos', COUNT(*) FROM hr_employee WHERE active
UNION ALL
SELECT 'contratos', COUNT(*) FROM hr_contract
UNION ALL
SELECT 'clientes', COUNT(*) FROM res_partner WHERE active AND customer_rank > 0
UNION ALL
SELECT 'proveedores', COUNT(*) FROM res_partner WHERE active AND supplier_rank > 0
UNION ALL
SELECT 'productos QuetzalMart', COUNT(*) FROM product_product WHERE default_code LIKE 'QM-%'
UNION ALL
SELECT 'directorios DMS', COUNT(*) FROM dms_directory
ORDER BY elemento;

-- Almacenes y existencias agregadas.
SELECT sw.name, sw.code, ROUND(SUM(sq.quantity)::numeric, 2) AS unidades
FROM stock_warehouse sw
JOIN stock_location sl ON sl.id = sw.lot_stock_id
LEFT JOIN stock_quant sq ON sq.location_id = sl.id
GROUP BY sw.name, sw.code
ORDER BY sw.code;

-- Impuestos configurados para Guatemala.
SELECT name, amount, type_tax_use
FROM account_tax
WHERE active
ORDER BY type_tax_use, amount DESC;

