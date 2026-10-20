' ARCHIVO GENERADO por rpa/construir.py a partir de rpa/codigo_vb/. No editar a mano.
Imports System.Data

Module Fragmentos
    Sub CrearReporte(ByRef dtReporte As DataTable)
        ' Tabla con el resultado de cada hoja procesada (se guarda en reporte_robot.xlsx).
        ' Salida: dtReporte (DataTable)
        dtReporte = New System.Data.DataTable("reporte")
        For Each columna As String In {"archivo", "hoja", "posicion", "tipo", "agregados", "omitidos", "estado"}
            dtReporte.Columns.Add(columna, GetType(String))
        Next
    End Sub

    Sub ListarHojas(rutaArchivo As String, ByRef hojas As String())
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
    End Sub

    Sub ElegirHoja(hojas As String(), tipo As String, ByRef hoja As String, ByRef posicion As Integer)
        ' Regla del enunciado: la hoja "clientes" o "productos" viene en la 5.a posición.
        ' Si en la 5.a posición no está, se busca por nombre en el resto del libro
        ' (sin distinguir mayúsculas, tildes ni espacios) para no perder información.
        ' Entrada: hojas (String()), tipo (String: "clientes" o "productos")
        ' Salida: hoja (String, vacío si no existe), posicion (Int32, base 1)
        Dim normalizar As System.Func(Of String, String) = Function(texto As String)
            Dim limpio As String = texto.Trim().ToLowerInvariant().Replace("á", "a").Replace("é", "e").Replace("í", "i").Replace("ó", "o").Replace("ú", "u").Replace("ü", "u").Replace("ñ", "n").Normalize(System.Text.NormalizationForm.FormD)
            Dim sb As New System.Text.StringBuilder()
            For Each c As Char In limpio
                If System.Globalization.CharUnicodeInfo.GetUnicodeCategory(c) <> System.Globalization.UnicodeCategory.NonSpacingMark AndAlso Not Char.IsWhiteSpace(c) Then sb.Append(c)
            Next
            Return sb.ToString()
        End Function
        hoja = ""
        posicion = 0
        Dim buscado As String = normalizar(tipo)
        If hojas.Length >= 5 AndAlso normalizar(hojas(4)) = buscado Then
            hoja = hojas(4)
            posicion = 5
        Else
            For i As Integer = 0 To hojas.Length - 1
                If normalizar(hojas(i)) = buscado Then
                    hoja = hojas(i)
                    posicion = i + 1
                    Exit For
                End If
            Next
        End If
    End Sub

    Sub NormalizarClientes(dtEntrada As DataTable, archivoOrigen As String, ByRef dtConsolidado As DataTable, ByRef agregados As Integer, ByRef omitidos As Integer)
        ' Convierte la hoja "clientes" al formato de importación de Odoo y la agrega al
        ' consolidado. Los encabezados del Excel se reconocen en inglés o español; las
        ' columnas de salida usan los nombres técnicos de Odoo para que "Importar
        ' registros" las relacione solas.
        ' Entrada: dtEntrada (DataTable), archivoOrigen (String)
        ' Entrada/Salida: dtConsolidado (DataTable)   Salida: agregados, omitidos (Int32)
        Dim columnas As String() = {"id", "name", "company_type", "qm_empresa_relacionada", "email", "phone", "street", "street2", "city", "qm_estado_texto", "zip", "qm_pais_texto", "vat", "qm_sitio_web", "qm_etiquetas_texto", "ref", "comment", "qm_origen_rpa"}
        Dim sinonimos As New System.Collections.Generic.Dictionary(Of String, String) From {
            {"name", "name"}, {"nombre", "name"}, {"nombrecompleto", "name"}, {"cliente", "name"},
            {"companytype", "company_type"}, {"tipodecompania", "company_type"}, {"tipodeempresa", "company_type"}, {"tipo", "company_type"}, {"tipodecontacto", "company_type"},
            {"relatedcompany", "qm_empresa_relacionada"}, {"empresarelacionada", "qm_empresa_relacionada"}, {"companiarelacionada", "qm_empresa_relacionada"}, {"empresa", "qm_empresa_relacionada"},
            {"email", "email"}, {"e-mail", "email"}, {"correo", "email"}, {"correoelectronico", "email"},
            {"phone", "phone"}, {"telefono", "phone"}, {"celular", "phone"},
            {"street", "street"}, {"calle", "street"}, {"direccion", "street"},
            {"street2", "street2"}, {"calle2", "street2"}, {"direccion2", "street2"},
            {"city", "city"}, {"ciudad", "city"}, {"municipio", "city"},
            {"state", "qm_estado_texto"}, {"estado", "qm_estado_texto"}, {"departamento", "qm_estado_texto"}, {"provincia", "qm_estado_texto"},
            {"zip", "zip"}, {"codigopostal", "zip"}, {"cp", "zip"},
            {"country", "qm_pais_texto"}, {"pais", "qm_pais_texto"},
            {"taxid", "vat"}, {"nit", "vat"}, {"rfc", "vat"}, {"numerodeidentificacionfiscal", "vat"}, {"vat", "vat"},
            {"website", "qm_sitio_web"}, {"sitioweb", "qm_sitio_web"}, {"web", "qm_sitio_web"},
            {"tags", "qm_etiquetas_texto"}, {"etiquetas", "qm_etiquetas_texto"},
            {"reference", "ref"}, {"referencia", "ref"}, {"ref", "ref"},
            {"notes", "comment"}, {"notas", "comment"}, {"comentarios", "comment"}, {"observaciones", "comment"}}

        Dim clave As System.Func(Of String, String) = Function(entrada As String)
            Dim limpio As String = If(entrada, "").Replace("*", "").Trim().ToLowerInvariant().Replace("á", "a").Replace("é", "e").Replace("í", "i").Replace("ó", "o").Replace("ú", "u").Replace("ü", "u").Replace("ñ", "n").Normalize(System.Text.NormalizationForm.FormD)
            Dim sb As New System.Text.StringBuilder()
            For Each c As Char In limpio
                If System.Globalization.CharUnicodeInfo.GetUnicodeCategory(c) <> System.Globalization.UnicodeCategory.NonSpacingMark AndAlso Not Char.IsWhiteSpace(c) AndAlso c <> "_"c Then sb.Append(c)
            Next
            Return sb.ToString()
        End Function
        Dim texto As System.Func(Of Object, String) = Function(valor As Object)
            If valor Is Nothing OrElse TypeOf valor Is System.DBNull Then Return ""
            If TypeOf valor Is Double Then
                Dim numero As Double = CDbl(valor)
                If Math.Abs(numero - Math.Round(numero)) < 0.0001 Then Return Math.Round(numero).ToString("0", System.Globalization.CultureInfo.InvariantCulture)
                Return numero.ToString(System.Globalization.CultureInfo.InvariantCulture)
            End If
            If TypeOf valor Is DateTime Then Return CDate(valor).ToString("yyyy-MM-dd")
            Return valor.ToString().Trim()
        End Function
        Dim identificador As System.Func(Of String, String) = Function(base As String)
            Return System.Text.RegularExpressions.Regex.Replace(clave(base), "[^a-z0-9.@-]", "").Replace("@", "_").Replace(".", "_")
        End Function

        If dtConsolidado Is Nothing Then
            dtConsolidado = New System.Data.DataTable("clientes")
            For Each nombreColumna As String In columnas
                dtConsolidado.Columns.Add(nombreColumna, GetType(String))
            Next
        End If

        ' Qué columna del Excel corresponde a cada campo de Odoo.
        Dim mapa As New System.Collections.Generic.Dictionary(Of String, System.Data.DataColumn)
        For Each columna As System.Data.DataColumn In dtEntrada.Columns
            Dim campo As String = Nothing
            If sinonimos.TryGetValue(clave(columna.ColumnName), campo) AndAlso Not mapa.ContainsKey(campo) Then mapa(campo) = columna
        Next

        agregados = 0
        omitidos = 0
        Dim existentes As New System.Collections.Generic.HashSet(Of String)
        For Each filaExistente As System.Data.DataRow In dtConsolidado.Rows
            existentes.Add(filaExistente("id").ToString())
        Next
        For Each fila As System.Data.DataRow In dtEntrada.Rows
            Dim valores As New System.Collections.Generic.Dictionary(Of String, String)
            For Each par As System.Collections.Generic.KeyValuePair(Of String, System.Data.DataColumn) In mapa
                valores(par.Key) = texto(fila(par.Value))
            Next
            Dim nombre As String = If(valores.ContainsKey("name"), valores("name"), "")
            If nombre = "" Then
                omitidos += 1
                Continue For
            End If
            Dim tipoContacto As String = clave(If(valores.ContainsKey("company_type"), valores("company_type"), ""))
            valores("company_type") = If(tipoContacto.StartsWith("compan") OrElse tipoContacto.StartsWith("empresa") OrElse tipoContacto.StartsWith("juridic"), "company", "person")
            Dim baseId As String = If(valores.ContainsKey("ref") AndAlso valores("ref") <> "", valores("ref"), If(valores.ContainsKey("email") AndAlso valores("email") <> "", valores("email"), nombre))
            valores("id") = "rpa_cliente_" & identificador(baseId)
            valores("qm_origen_rpa") = archivoOrigen
            If existentes.Contains(valores("id")) Then
                omitidos += 1
                Continue For
            End If
            Dim nueva As System.Data.DataRow = dtConsolidado.NewRow()
            For Each nombreColumna As String In columnas
                nueva(nombreColumna) = If(valores.ContainsKey(nombreColumna), valores(nombreColumna), "")
            Next
            dtConsolidado.Rows.Add(nueva)
            existentes.Add(valores("id"))
            agregados += 1
        Next
    End Sub

    Sub NormalizarProductos(dtEntrada As DataTable, archivoOrigen As String, ByRef dtConsolidado As DataTable, ByRef agregados As Integer, ByRef omitidos As Integer)
        ' Convierte la hoja "productos" al formato de importación de Odoo y la agrega al
        ' consolidado. "Cantidad a la mano" va al campo puente qm_cantidad_inicial, que
        ' registra el ajuste de inventario al importar.
        ' Entrada: dtEntrada (DataTable), archivoOrigen (String)
        ' Entrada/Salida: dtConsolidado (DataTable)   Salida: agregados, omitidos (Int32)
        Dim columnas As String() = {"id", "name", "type", "default_code", "barcode", "list_price", "standard_price", "weight", "description_sale", "qm_valores_producto", "qm_cantidad_inicial", "is_published", "qm_origen_rpa"}
        Dim sinonimos As New System.Collections.Generic.Dictionary(Of String, String) From {
            {"idexterno", "id"}, {"externalid", "id"}, {"id", "id"},
            {"name", "name"}, {"nombre", "name"}, {"producto", "name"}, {"nombredelproducto", "name"},
            {"producttype", "type"}, {"tipodeproducto", "type"}, {"tipo", "type"},
            {"internalreference", "default_code"}, {"referenciainterna", "default_code"}, {"codigo", "default_code"}, {"sku", "default_code"},
            {"barcode", "barcode"}, {"codigodebarras", "barcode"},
            {"salesprice", "list_price"}, {"preciodeventa", "list_price"}, {"precio", "list_price"},
            {"cost", "standard_price"}, {"costo", "standard_price"},
            {"weight", "weight"}, {"peso", "weight"},
            {"salesdescription", "description_sale"}, {"descripciondeventa", "description_sale"}, {"descripcion", "description_sale"},
            {"productvalues", "qm_valores_producto"}, {"valoresdelproducto", "qm_valores_producto"}, {"valores", "qm_valores_producto"},
            {"cantidadalamano", "qm_cantidad_inicial"}, {"quantityonhand", "qm_cantidad_inicial"}, {"cantidad", "qm_cantidad_inicial"}, {"existencias", "qm_cantidad_inicial"},
            {"estapublicado", "is_published"}, {"ispublished", "is_published"}, {"publicado", "is_published"}}

        Dim clave As System.Func(Of String, String) = Function(entrada As String)
            Dim limpio As String = If(entrada, "").Replace("*", "").Trim().ToLowerInvariant().Replace("á", "a").Replace("é", "e").Replace("í", "i").Replace("ó", "o").Replace("ú", "u").Replace("ü", "u").Replace("ñ", "n").Normalize(System.Text.NormalizationForm.FormD)
            Dim sb As New System.Text.StringBuilder()
            For Each c As Char In limpio
                If System.Globalization.CharUnicodeInfo.GetUnicodeCategory(c) <> System.Globalization.UnicodeCategory.NonSpacingMark AndAlso Not Char.IsWhiteSpace(c) AndAlso c <> "_"c Then sb.Append(c)
            Next
            Return sb.ToString()
        End Function
        Dim texto As System.Func(Of Object, String) = Function(valor As Object)
            If valor Is Nothing OrElse TypeOf valor Is System.DBNull Then Return ""
            If TypeOf valor Is Double Then
                Dim numero As Double = CDbl(valor)
                If Math.Abs(numero - Math.Round(numero)) < 0.0001 Then Return Math.Round(numero).ToString("0", System.Globalization.CultureInfo.InvariantCulture)
                Return numero.ToString(System.Globalization.CultureInfo.InvariantCulture)
            End If
            If TypeOf valor Is DateTime Then Return CDate(valor).ToString("yyyy-MM-dd")
            Return valor.ToString().Trim()
        End Function
        ' "Q 1,250.50", "9,99" o "9.99" -> "1250.5" / "9.99" (formato que entiende Odoo).
        Dim numeroOdoo As System.Func(Of String, String) = Function(valor As String)
            Dim limpio As String = System.Text.RegularExpressions.Regex.Replace(valor, "[^0-9,.\-]", "")
            If limpio = "" Then Return ""
            If limpio.Contains(",") AndAlso limpio.Contains(".") Then
                limpio = limpio.Replace(",", "")
            ElseIf limpio.Contains(",") Then
                limpio = limpio.Replace(",", ".")
            End If
            Dim numero As Double
            If Double.TryParse(limpio, System.Globalization.NumberStyles.Float, System.Globalization.CultureInfo.InvariantCulture, numero) Then Return numero.ToString(System.Globalization.CultureInfo.InvariantCulture)
            Return ""
        End Function
        Dim identificador As System.Func(Of String, String) = Function(base As String)
            Return System.Text.RegularExpressions.Regex.Replace(base.Trim(), "[^A-Za-z0-9_\-]", "_")
        End Function

        If dtConsolidado Is Nothing Then
            dtConsolidado = New System.Data.DataTable("productos")
            For Each nombreColumna As String In columnas
                dtConsolidado.Columns.Add(nombreColumna, GetType(String))
            Next
        End If

        Dim mapa As New System.Collections.Generic.Dictionary(Of String, System.Data.DataColumn)
        For Each columna As System.Data.DataColumn In dtEntrada.Columns
            Dim campo As String = Nothing
            If sinonimos.TryGetValue(clave(columna.ColumnName), campo) AndAlso Not mapa.ContainsKey(campo) Then mapa(campo) = columna
        Next

        agregados = 0
        omitidos = 0
        Dim existentes As New System.Collections.Generic.HashSet(Of String)
        For Each filaExistente As System.Data.DataRow In dtConsolidado.Rows
            existentes.Add(filaExistente("id").ToString())
        Next
        For Each fila As System.Data.DataRow In dtEntrada.Rows
            Dim valores As New System.Collections.Generic.Dictionary(Of String, String)
            For Each par As System.Collections.Generic.KeyValuePair(Of String, System.Data.DataColumn) In mapa
                valores(par.Key) = texto(fila(par.Value))
            Next
            Dim nombre As String = If(valores.ContainsKey("name"), valores("name"), "")
            If nombre = "" Then
                omitidos += 1
                Continue For
            End If
            ' Tipo de producto: Goods/Bien -> consu, Service/Servicio -> service.
            Dim tipoProducto As String = clave(If(valores.ContainsKey("type"), valores("type"), ""))
            If tipoProducto.StartsWith("serv") Then
                valores("type") = "service"
            ElseIf tipoProducto.StartsWith("combo") Then
                valores("type") = "combo"
            Else
                valores("type") = "consu"
            End If
            For Each campoNumerico As String In {"list_price", "standard_price", "weight", "qm_cantidad_inicial"}
                If valores.ContainsKey(campoNumerico) Then valores(campoNumerico) = numeroOdoo(valores(campoNumerico))
            Next
            ' Un servicio no tiene existencias.
            If valores("type") <> "consu" Then valores("qm_cantidad_inicial") = ""
            ' Código de barras: Excel lo guarda como número (54398267125.00001).
            If valores.ContainsKey("barcode") AndAlso System.Text.RegularExpressions.Regex.IsMatch(valores("barcode"), "^[0-9]+([.,][0-9]+)?(E\+?[0-9]+)?$", System.Text.RegularExpressions.RegexOptions.IgnoreCase) Then
                Dim codigo As Double
                If Double.TryParse(valores("barcode").Replace(",", "."), System.Globalization.NumberStyles.Float, System.Globalization.CultureInfo.InvariantCulture, codigo) Then valores("barcode") = Math.Round(codigo).ToString("0", System.Globalization.CultureInfo.InvariantCulture)
            End If
            Dim publicado As String = clave(If(valores.ContainsKey("is_published"), valores("is_published"), ""))
            valores("is_published") = If({"true", "verdadero", "1", "si", "yes", "x"}.Contains(publicado), "1", "0")
            Dim externo As String = If(valores.ContainsKey("id"), valores("id"), "")
            If externo = "" Then externo = "rpa_producto_" & If(valores.ContainsKey("default_code") AndAlso valores("default_code") <> "", valores("default_code"), nombre)
            valores("id") = identificador(externo)
            valores("qm_origen_rpa") = archivoOrigen
            If existentes.Contains(valores("id")) Then
                omitidos += 1
                Continue For
            End If
            Dim nueva As System.Data.DataRow = dtConsolidado.NewRow()
            For Each nombreColumna As String In columnas
                nueva(nombreColumna) = If(valores.ContainsKey(nombreColumna), valores(nombreColumna), "")
            Next
            dtConsolidado.Rows.Add(nueva)
            existentes.Add(valores("id"))
            agregados += 1
        Next
    End Sub

End Module
