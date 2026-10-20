import fs from "node:fs/promises";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const outputDir = "C:/Users/Vela/Desktop/GEREN2/LAB/PROYECTO/outputs/01a0bd2a-76e4-7741-88fc-59fb5a78b4ce";
await fs.mkdir(outputDir, { recursive: true });

const workbook = Workbook.create();
const sheet = workbook.worksheets.add("clientes");

const headers = [
  "Name", "Company Type", "Related Company", "Email", "Phone", "Street", "Street2",
  "City", "State", "Zip", "Country", "Tax ID", "Website", "Tags", "Reference", "Notes",
];

const row = [
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
];

sheet.getRange("A1:P2").values = [headers, row];
sheet.getRange("A1:P2").format.font = { name: "Arial", size: 10 };
sheet.getRange("A1:P1").format = {
  fill: "#5B3A79",
  font: { name: "Arial", size: 10, bold: true, color: "#FFFFFF" },
  horizontalAlignment: "center",
  verticalAlignment: "center",
  wrapText: true,
};
sheet.getRange("A2:P2").format.verticalAlignment = "center";
sheet.getRange("A2:P2").format.wrapText = true;
sheet.getRange("A1:P2").format.borders = { preset: "all", style: "thin", color: "#D9D9D9" };
sheet.getRange("A1:P1").format.rowHeight = 28;
sheet.getRange("A2:P2").format.rowHeight = 48;

const widths = {
  A: 30, B: 16, C: 26, D: 34, E: 15, F: 26, G: 28, H: 20,
  I: 18, J: 12, K: 16, L: 18, M: 36, N: 22, O: 22, P: 55,
};
for (const [col, width] of Object.entries(widths)) {
  sheet.getRange(`${col}1:${col}2`).format.columnWidth = width;
}
sheet.freezePanes.freezeRows(1);
sheet.showGridLines = false;

const inspect = await workbook.inspect({
  kind: "table,region",
  sheetId: "clientes",
  range: "A1:P2",
  include: "values,formulas",
  tableMaxRows: 3,
  tableMaxCols: 16,
  maxChars: 10000,
});
console.log(inspect.ndjson);

const preview = await workbook.render({ sheetName: "clientes", range: "A1:P2", scale: 1, format: "png" });
await fs.writeFile(`${outputDir}/clientes_prueba_completa_preview.png`, new Uint8Array(await preview.arrayBuffer()));

const output = await SpreadsheetFile.exportXlsx(workbook);
await output.save(`${outputDir}/clientes_prueba_completa.xlsx`);
console.log(`SAVED ${outputDir}/clientes_prueba_completa.xlsx`);
