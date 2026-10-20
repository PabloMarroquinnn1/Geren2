' Devuelve los nombres de las hojas de un .xlsx en el orden de sus pestañas.
' Lee xl/workbook.xml dentro del archivo (un .xlsx es un ZIP): no necesita Excel
' instalado y funciona aunque el libro esté abierto por otra persona.
' Entrada: rutaArchivo (String)   Salida: hojas (String())
Dim nombres As New System.Collections.Generic.List(Of String)
Using flujo As New System.IO.FileStream(rutaArchivo, System.IO.FileMode.Open, System.IO.FileAccess.Read, System.IO.FileShare.ReadWrite)
    Using zip As New System.IO.Compression.ZipArchive(flujo, System.IO.Compression.ZipArchiveMode.Read)
        Dim libro As System.IO.Compression.ZipArchiveEntry = zip.GetEntry("xl/workbook.xml")
        If libro IsNot Nothing Then
            Using contenido As System.IO.Stream = libro.Open()
                Dim documento As System.Xml.Linq.XDocument = System.Xml.Linq.XDocument.Load(contenido)
                Dim ns As System.Xml.Linq.XNamespace = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
                For Each hoja As System.Xml.Linq.XElement In documento.Descendants(ns + "sheet")
                    nombres.Add(hoja.Attribute("name").Value)
                Next
            End Using
        End If
    End Using
End Using
hojas = nombres.ToArray()
