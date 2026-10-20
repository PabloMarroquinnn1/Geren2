import fs from "node:fs/promises";
import { FileBlob, SpreadsheetFile } from "@oai/artifact-tool";

const inputPath = "C:/Users/Vela/Desktop/GEREN2/LAB/PROYECTO/datos/prueba_rpa/lote_demo/subcarpeta/entrada_demo.xlsx";
const outputDir = "C:/Users/Vela/Desktop/GEREN2/LAB/PROYECTO/outputs/01a0bd2a-76e4-7741-88fc-59fb5a78b4ce";
const outputPath = `${outputDir}/entrada_demo.xlsx`;

await fs.mkdir(outputDir, { recursive: true });
const workbook = await SpreadsheetFile.importXlsx(await FileBlob.load(inputPath));
const clients = workbook.worksheets.getItem("clientes");

clients.getRange("A1:P2").values = [
  [
    "Name", "Company Type", "Related Company", "Email", "Phone", "Street", "Street2",
    "City", "State", "Zip", "Country", "Tax ID", "Website", "Tags", "Reference", "Notes",
  ],
  [
    "RPA Cliente Prueba Completa 2026",
    "Individual",
    "Empresa RPA Demo 2026",
    "rpa.cliente.completo.2026@example.com",
    "5555-2030",
    "Avenida Reforma 10-10",
    "Edificio Central, oficina 4",
    "Guatemala City",
    "Guatemala",
    "01010",
    "Guatemala",
    "CF-2026-002",
    "https://rpa-prueba-2026.example.com",
    "RPA Prueba 2026",
    "RPA-CLI-2026-002",
    "Cliente de prueba con los 16 campos completos para validar la importación en Odoo.",
  ],
];

const checkClients = await workbook.inspect({
  kind: "table",
  sheetId: "clientes",
  range: "A1:P2",
  include: "values,formulas",
  tableMaxRows: 3,
  tableMaxCols: 16,
  maxChars: 12000,
});
console.log(checkClients.ndjson);

const checkProducts = await workbook.inspect({
  kind: "table",
  sheetId: "productos",
  range: "A1:L2",
  include: "values,formulas",
  tableMaxRows: 3,
  tableMaxCols: 12,
  maxChars: 8000,
});
console.log(checkProducts.ndjson);

for (const sheetName of ["clientes", "productos"]) {
  const preview = await workbook.render({ sheetName, autoCrop: "all", scale: 1, format: "png" });
  await fs.writeFile(`${outputDir}/${sheetName}_entrada_demo_verificada.png`, new Uint8Array(await preview.arrayBuffer()));
}

const output = await SpreadsheetFile.exportXlsx(workbook);
await output.save(outputPath);
console.log(`SAVED ${outputPath}`);
