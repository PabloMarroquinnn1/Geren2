import fs from 'node:fs/promises';
import { SpreadsheetFile, Workbook } from '@oai/artifact-tool';

const outputDir = 'C:/Users/Vela/Desktop/GEREN2/LAB/PROYECTO/outputs/01a0bd2a-76e4-7741-88fc-59fb5a78b4ce';
const previewDir = 'C:/Users/Vela/Desktop/GEREN2/LAB/PROYECTO/tmp/block1-previews';
await fs.mkdir(outputDir, { recursive: true });
await fs.mkdir(previewDir, { recursive: true });

const workbook = Workbook.create();
const font = 'Aptos';
const headerFill = '#1F4E78';
const headerFont = { name: font, size: 10, bold: true, color: '#FFFFFF' };
const bodyFont = { name: font, size: 10, color: '#1F2937' };

function addTemplate(name, headers, tabColor = '#5B9BD5') {
  const sheet = workbook.worksheets.add(name);
  sheet.tabColor = tabColor;
  sheet.showGridLines = false;
  const header = sheet.getRangeByIndexes(0, 0, 1, headers.length);
  header.values = [headers];
  header.format = {
    fill: headerFill,
    font: headerFont,
    horizontalAlignment: 'center',
    verticalAlignment: 'center',
    wrapText: true,
    borders: { preset: 'outside', style: 'thin', color: '#FFFFFF' },
  };
  header.format.rowHeight = 34;
  const body = sheet.getRangeByIndexes(1, 0, 20, headers.length);
  body.format = { font: bodyFont, verticalAlignment: 'center' };
  body.format.rowHeight = 22;
  sheet.freezePanes.freezeRows(1);
  sheet.getUsedRange().format.autofitColumns();
  return sheet;
}

const readme = workbook.worksheets.add('Inicio');
readme.tabColor = '#17365D';
readme.showGridLines = false;
readme.getRange('A1:D1').merge();
readme.getRange('A1').values = [['QuetzalMart - Plantillas de carga']];
readme.getRange('A1:D1').format = { fill: '#17365D', font: { name: font, size: 16, bold: true, color: '#FFFFFF' }, horizontalAlignment: 'left', verticalAlignment: 'center' };
readme.getRange('A1:D1').format.rowHeight = 32;
readme.getRange('A3:B14').values = [
  ['Propósito', 'Plantillas base para preparar datos de Odoo y pruebas del RPA.'],
  ['Empresa', 'QuetzalMart'],
  ['Base de datos', 'PostgreSQL administrado por Odoo en la nube'],
  ['Regla RPA', 'Procesar únicamente archivos Excel con hojas llamadas exactamente clientes y productos.'],
  ['Carga RPA', 'UiPath debe utilizar la interfaz web de importación de Odoo; no API.'],
  ['Ventas mínimas', 150],
  ['Cotizaciones de venta', 20],
  ['Cotizaciones de compra', 20],
  ['Compras confirmadas con factura', 100],
  ['Empleados', 35],
  ['Materiales/productos', 60],
  ['Facturas PDF', 50],
];
readme.getRange('A3:A14').format = { fill: '#D9EAF7', font: { name: font, size: 10, bold: true, color: '#1F2937' }, verticalAlignment: 'center' };
readme.getRange('B3:B14').format = { font: bodyFont, wrapText: true, verticalAlignment: 'center' };
readme.getRange('A3:B14').format.borders = { preset: 'all', style: 'thin', color: '#D9E2F3' };
readme.getRange('A3:B14').format.rowHeight = 24;
readme.getRange('A3:A14').format.columnWidth = 30;
readme.getRange('B3:B14').format.columnWidth = 78;

addTemplate('Clientes', ['Name', 'Company Type', 'Related Company', 'Email', 'Phone', 'Street', 'Street2', 'City', 'State', 'Zip', 'Country', 'Tax ID', 'Website', 'Tags', 'Reference', 'Notes'], '#70AD47');
addTemplate('Productos', ['ID Externo', 'Name', 'Product Type', 'Internal Reference', 'Barcode', 'Sales Price', 'Cost', 'Weight', 'Sales Description', 'Product Values', 'Cantidad a la mano', 'Está publicado'], '#ED7D31');
addTemplate('Empleados', ['Name', 'Work Email', 'Job', 'Department', 'Work Phone', 'Mobile', 'Company', 'Street', 'City', 'Country'], '#A5A5A5');
addTemplate('Cargos_Departamentos', ['Tipo', 'Name', 'Description'], '#FFC000');
addTemplate('Ventas', ['Order Reference', 'Customer', 'Order Date', 'Product', 'Quantity', 'Unit Price', 'Warehouse', 'Status'], '#4472C4');
addTemplate('Compras', ['Purchase Reference', 'Vendor', 'Order Date', 'Product', 'Quantity', 'Unit Price', 'Warehouse', 'Status', 'Vendor Bill'], '#8064A2');
addTemplate('Documentos', ['File Name', 'Category', 'Tags', 'Branch', 'Document Date', 'Expiration Date', 'Notes'], '#C00000');

for (const sheet of workbook.worksheets.items) {
  const preview = await workbook.render({ sheetName: sheet.name, autoCrop: 'all', scale: 1, format: 'png' });
  await fs.writeFile(`${previewDir}/${sheet.name}.png`, new Uint8Array(await preview.arrayBuffer()));
}

const output = await SpreadsheetFile.exportXlsx(workbook);
await output.save(`${outputDir}/Plantillas_Carga_QuetzalMart.xlsx`);
console.log(`Created ${outputDir}/Plantillas_Carga_QuetzalMart.xlsx`);
