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
