"""Inserta los fragmentos de codigo_vb/ en el arnés de pruebas y en los XAML de UiPath.

Así el código que corre en "Invocar código" es exactamente el que se probó.
Uso:  python rpa/construir.py
"""
from pathlib import Path

AQUI = Path(__file__).resolve().parent
CODIGO = AQUI / "codigo_vb"

FIRMAS = {
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


if __name__ == "__main__":
    arnes()
