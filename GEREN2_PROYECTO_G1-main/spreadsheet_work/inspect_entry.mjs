import fs from "node:fs/promises";
import { FileBlob, SpreadsheetFile } from "@oai/artifact-tool";

const inputPath = "C:/Users/Vela/Desktop/GEREN2/LAB/PROYECTO/datos/prueba_rpa/lote_demo/subcarpeta/entrada_demo.xlsx";
const input = await FileBlob.load(inputPath);
const workbook = await SpreadsheetFile.importXlsx(input);
const summary = await workbook.inspect({ kind: "workbook,sheet,table", maxChars: 12000, tableMaxRows: 4, tableMaxCols: 20 });
console.log(summary.ndjson);
for (const sheetName of ["clientes", "productos"]) {
  const preview = await workbook.render({ sheetName, autoCrop: "all", scale: 1, format: "png" });
  await fs.writeFile(`C:/Users/Vela/Desktop/GEREN2/LAB/PROYECTO/outputs/01a0bd2a-76e4-7741-88fc-59fb5a78b4ce/${sheetName}_entrada_original.png`, new Uint8Array(await preview.arrayBuffer()));
}
