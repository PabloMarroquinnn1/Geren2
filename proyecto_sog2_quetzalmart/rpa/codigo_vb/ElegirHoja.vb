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
