' Tabla con el resultado de cada hoja procesada (se guarda en reporte_robot.xlsx).
' Salida: dtReporte (DataTable)
dtReporte = New System.Data.DataTable("reporte")
For Each columna As String In {"archivo", "hoja", "posicion", "tipo", "agregados", "omitidos", "estado"}
    dtReporte.Columns.Add(columna, GetType(String))
Next
