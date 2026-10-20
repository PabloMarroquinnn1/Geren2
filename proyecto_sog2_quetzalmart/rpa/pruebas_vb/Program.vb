' Arnés de prueba del robot: recorre una carpeta como lo hace Main.xaml y escribe
' los consolidados en CSV. Uso: dotnet run -- <carpeta_raiz> <carpeta_salida>
Imports System.Data
Imports System.IO
Imports System.IO.Compression
Imports System.Xml.Linq

Module Program
    Function Main(args As String()) As Integer
        Dim raiz As String = args(0)
        Dim salida As String = args(1)
        Directory.CreateDirectory(salida)
        Dim dtClientes As DataTable = Nothing
        Dim dtProductos As DataTable = Nothing
        Dim archivos = Directory.GetFiles(raiz, "*.xls*", SearchOption.AllDirectories).
            Where(Function(f) Not Path.GetFileName(f).StartsWith("~$")).OrderBy(Function(f) f).ToArray()
        Console.WriteLine($"Archivos Excel encontrados: {archivos.Length}")
        For Each archivo In archivos
            Dim hojas As String() = Nothing
            Try
                Fragmentos.ListarHojas(archivo, hojas)
            Catch ex As Exception
                Console.WriteLine($"  [omitido] {Path.GetFileName(archivo)}: {ex.Message}")
                Continue For
            End Try
            For Each tipo In {"clientes", "productos"}
                Dim hoja As String = Nothing, posicion As Integer
                Fragmentos.ElegirHoja(hojas, tipo, hoja, posicion)
                If hoja = "" Then Continue For
                Dim dt = LeerHoja(archivo, hoja)
                Dim agregados, omitidos As Integer
                If tipo = "clientes" Then
                    Fragmentos.NormalizarClientes(dt, archivo, dtClientes, agregados, omitidos)
                Else
                    Fragmentos.NormalizarProductos(dt, archivo, dtProductos, agregados, omitidos)
                End If
                Console.WriteLine($"  {Path.GetFileName(archivo)} -> hoja '{hoja}' (posición {posicion}): {agregados} agregados, {omitidos} omitidos")
            Next
        Next
        EscribirCsv(dtClientes, Path.Combine(salida, "consolidado_clientes.csv"))
        EscribirCsv(dtProductos, Path.Combine(salida, "consolidado_productos.csv"))
        Console.WriteLine($"Clientes consolidados: {If(dtClientes Is Nothing, 0, dtClientes.Rows.Count)}")
        Console.WriteLine($"Productos consolidados: {If(dtProductos Is Nothing, 0, dtProductos.Rows.Count)}")
        Return 0
    End Function

    ' Lector mínimo de .xlsx que imita "Leer rango" de UiPath: primera fila como
    ' encabezados, números como Double y textos como String.
    Function LeerHoja(ruta As String, nombreHoja As String) As DataTable
        Dim ns As XNamespace = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
        Dim nsR As XNamespace = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
        Dim nsRel As XNamespace = "http://schemas.openxmlformats.org/package/2006/relationships"
        Using zip = ZipFile.OpenRead(ruta)
            Dim compartidos As New List(Of String)
            Dim entradaTextos = zip.GetEntry("xl/sharedStrings.xml")
            If entradaTextos IsNot Nothing Then
                For Each si In XDocument.Load(entradaTextos.Open()).Descendants(ns + "si")
                    compartidos.Add(String.Concat(si.Descendants(ns + "t").Select(Function(t) t.Value)))
                Next
            End If
            Dim libro = XDocument.Load(zip.GetEntry("xl/workbook.xml").Open())
            Dim relId = libro.Descendants(ns + "sheet").First(Function(h) h.Attribute("name").Value = nombreHoja).Attribute(nsR + "id").Value
            Dim rels = XDocument.Load(zip.GetEntry("xl/_rels/workbook.xml.rels").Open())
            Dim destino = rels.Descendants(nsRel + "Relationship").First(Function(r) r.Attribute("Id").Value = relId).Attribute("Target").Value
            Dim rutaHoja = If(destino.StartsWith("/"), destino.TrimStart("/"c), "xl/" & destino)
            Dim filas As New List(Of Dictionary(Of Integer, Object))
            For Each fila In XDocument.Load(zip.GetEntry(rutaHoja).Open()).Descendants(ns + "row")
                Dim celdas As New Dictionary(Of Integer, Object)
                For Each c In fila.Elements(ns + "c")
                    Dim referencia = c.Attribute("r").Value
                    Dim letras = New String(referencia.TakeWhile(Function(ch) Char.IsLetter(ch)).ToArray())
                    Dim columna = letras.Aggregate(0, Function(acc, ch) acc * 26 + (AscW(ch) - 64)) - 1
                    Dim tipo = c.Attribute("t")?.Value
                    Dim v = c.Element(ns + "v")?.Value
                    Dim valor As Object = Nothing
                    If tipo = "s" Then
                        valor = compartidos(Integer.Parse(v))
                    ElseIf tipo = "inlineStr" Then
                        valor = String.Concat(c.Descendants(ns + "t").Select(Function(t) t.Value))
                    ElseIf tipo = "b" Then
                        valor = (v = "1")
                    ElseIf tipo = "str" Then
                        valor = v
                    ElseIf v IsNot Nothing Then
                        valor = Double.Parse(v, Globalization.CultureInfo.InvariantCulture)
                    End If
                    celdas(columna) = valor
                Next
                filas.Add(celdas)
            Next
            Dim dt As New DataTable()
            Dim encabezados = filas(0)
            Dim maximo = filas.SelectMany(Function(f) f.Keys).DefaultIfEmpty(0).Max()
            For i = 0 To maximo
                Dim nombre = If(encabezados.ContainsKey(i) AndAlso encabezados(i) IsNot Nothing, encabezados(i).ToString(), "Column" & (i + 1))
                dt.Columns.Add(nombre, GetType(Object))
            Next
            For Each f In filas.Skip(1)
                Dim r = dt.NewRow()
                For Each par In f
                    r(par.Key) = If(par.Value, DBNull.Value)
                Next
                dt.Rows.Add(r)
            Next
            Return dt
        End Using
    End Function

    Sub EscribirCsv(dt As DataTable, ruta As String)
        If dt Is Nothing Then Return
        Dim escapar = Function(s As String) """" & s.Replace("""", """""") & """"
        Using w As New StreamWriter(ruta, False, New Text.UTF8Encoding(False))
            w.WriteLine(String.Join(",", dt.Columns.Cast(Of DataColumn)().Select(Function(c) escapar(c.ColumnName))))
            For Each r As DataRow In dt.Rows
                w.WriteLine(String.Join(",", r.ItemArray.Select(Function(o) escapar(Convert.ToString(o)))))
            Next
        End Using
    End Sub
End Module
