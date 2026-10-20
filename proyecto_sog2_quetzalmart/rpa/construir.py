"""Inserta los fragmentos de codigo_vb/ en el arnés de pruebas y en los XAML de UiPath.

Así el código que corre en "Invocar código" es exactamente el que se probó.
Uso:  python rpa/construir.py
"""
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

AQUI = Path(__file__).resolve().parent
CODIGO = AQUI / "codigo_vb"
PLANTILLAS = AQUI / "plantillas_xaml"
PROYECTO = AQUI / "QuetzalMart_Robot"

FIRMAS = {
    "CrearReporte": "ByRef dtReporte As DataTable",
    "ListarHojas": "rutaArchivo As String, ByRef hojas As String()",
    "ElegirHoja": "hojas As String(), tipo As String, ByRef hoja As String, ByRef posicion As Integer",
    "NormalizarClientes": "dtEntrada As DataTable, archivoOrigen As String, ByRef dtConsolidado As DataTable, "
                          "ByRef agregados As Integer, ByRef omitidos As Integer",
    "NormalizarProductos": "dtEntrada As DataTable, archivoOrigen As String, ByRef dtConsolidado As DataTable, "
                           "ByRef agregados As Integer, ByRef omitidos As Integer",
}


def fragmento(nombre):
    return (CODIGO / f"{nombre}.vb").read_text(encoding="utf-8")


def arnes():
    partes = ["' ARCHIVO GENERADO por rpa/construir.py a partir de rpa/codigo_vb/. No editar a mano.",
              "Imports System.Data", "", "Module Fragmentos"]
    for nombre, firma in FIRMAS.items():
        cuerpo = "\n".join("        " + linea if linea.strip() else "" for linea in fragmento(nombre).splitlines())
        partes += [f"    Sub {nombre}({firma})", cuerpo, "    End Sub", ""]
    partes.append("End Module")
    (AQUI / "pruebas_vb" / "Fragmentos.vb").write_text("\n".join(partes) + "\n", encoding="utf-8")
    print("Generado pruebas_vb/Fragmentos.vb")


def atributo_xml(texto):
    """Escapa el código para el atributo Code="..." de la actividad Invocar código."""
    return (texto.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;").replace("\r", "").replace("\n", "&#xA;"))


def proyecto():
    PROYECTO.mkdir(exist_ok=True)
    for plantilla in PLANTILLAS.glob("*.xaml"):
        contenido = plantilla.read_text(encoding="utf-8")
        for nombre in FIRMAS:
            contenido = contenido.replace(f"__CODIGO_{nombre}__", atributo_xml(fragmento(nombre)))
        faltantes = re.findall(r"__CODIGO_\w+__", contenido)
        if faltantes:
            raise SystemExit(f"Fragmentos sin código en {plantilla.name}: {faltantes}")
        ET.fromstring(contenido)  # falla si el XAML no es XML válido
        (PROYECTO / plantilla.name).write_text(contenido, encoding="utf-8")
        print("Generado QuetzalMart_Robot/" + plantilla.name)
    identificador = "5b0c9d61-7f3e-4c2a-9e2b-51a3c6e0b2d4"
    (PROYECTO / "project.json").write_text(json.dumps({
        "name": "QuetzalMart_Robot",
        "projectId": identificador,
        "description": "Recorre carpetas de Excel, consolida las hojas clientes y productos y las importa en Odoo.",
        "main": "Main.xaml",
        "dependencies": {
            "UiPath.Excel.Activities": "[3.6.1]",
            "UiPath.System.Activities": "[25.10.3]",
            "UiPath.UIAutomation.Activities": "[26.10.4]",
        },
        "webServices": [],
        "entitiesStores": [],
        "schemaVersion": "4.0",
        "studioVersion": "26.0.180.0",
        "projectVersion": "1.0.0",
        "runtimeOptions": {
            "autoDispose": False, "netFrameworkLazyLoading": False, "isPausable": True,
            "isAttended": True, "requiresUserInteraction": True, "supportsPersistence": False,
            "workflowSerialization": "NewtonsoftJson", "excludedLoggedData": ["Private:*", "*password*", "*clave*"],
            "executionType": "Workflow", "readyForPiP": False, "startsInPiP": False,
            "mustRestoreAllDependencies": True, "pipType": "ChildSession",
        },
        "designOptions": {
            "projectProfile": "Developement", "outputType": "Process",
            "libraryOptions": {"privateWorkflows": []},
            "processOptions": {"ignoredFiles": []},
            "fileInfoCollection": [], "saveToCloud": False,
        },
        "expressionLanguage": "VisualBasic",
        "entryPoints": [{"filePath": "Main.xaml", "uniqueId": "9d2f4b7a-3c1e-4f8a-b6d5-0e7a2c9f1b34",
                         "input": [], "output": []}],
        "isTemplate": False,
        "templateProjectData": {},
        "publishData": {},
        "targetFramework": "Windows",
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (PROYECTO / "project.uiproj").write_text(json.dumps({
        "Name": "QuetzalMart_Robot", "ProjectType": "Process",
        "Description": "Robot de carga de clientes y productos de QuetzalMart", "MainFile": "Main.xaml",
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("Generado QuetzalMart_Robot/project.json y project.uiproj")


if __name__ == "__main__":
    arnes()
    proyecto()
