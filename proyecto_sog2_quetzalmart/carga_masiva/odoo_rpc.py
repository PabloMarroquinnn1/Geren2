"""Cliente JSON-RPC mínimo para Odoo (solo librería estándar de Python)."""
import json
import ssl
import urllib.request


class ErrorOdoo(Exception):
    pass


class Odoo:
    def __init__(self, url, base, usuario, clave, verificar_ssl=True):
        self.url = url.rstrip("/")
        self.base = base
        self._contexto_ssl = None if verificar_ssl else ssl._create_unverified_context()
        self._id = 0
        self.uid = self._llamar("common", "login", base, usuario, clave)
        if not self.uid:
            raise ErrorOdoo("Usuario o clave incorrectos para %s" % self.url)
        self.clave = clave

    def _llamar(self, servicio, metodo, *argumentos):
        self._id += 1
        carga = json.dumps({
            "jsonrpc": "2.0", "method": "call", "id": self._id,
            "params": {"service": servicio, "method": metodo, "args": argumentos},
        }).encode()
        peticion = urllib.request.Request(
            self.url + "/jsonrpc", data=carga, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(peticion, timeout=900, context=self._contexto_ssl) as respuesta:
            datos = json.loads(respuesta.read())
        if datos.get("error"):
            error = datos["error"].get("data", {})
            raise ErrorOdoo(error.get("message") or datos["error"].get("message"))
        return datos.get("result")

    def ejecutar(self, modelo, metodo, *argumentos, **opciones):
        return self._llamar("object", "execute_kw", self.base, self.uid, self.clave,
                            modelo, metodo, list(argumentos), opciones)

    # Atajos de uso frecuente
    def buscar(self, modelo, dominio, **opciones):
        return self.ejecutar(modelo, "search", dominio, **opciones)

    def leer(self, modelo, dominio, campos, **opciones):
        return self.ejecutar(modelo, "search_read", dominio, campos, **opciones)

    def contar(self, modelo, dominio):
        return self.ejecutar(modelo, "search_count", dominio)

    def crear(self, modelo, valores, contexto=None):
        return self.ejecutar(modelo, "create", valores, context=contexto or {})

    def escribir(self, modelo, ids, valores):
        return self.ejecutar(modelo, "write", ids, valores)

    def ref(self, xmlid):
        modulo, nombre = xmlid.split(".")
        registro = self.leer("ir.model.data", [("module", "=", modulo), ("name", "=", nombre)],
                             ["res_id"], limit=1)
        if not registro:
            raise ErrorOdoo("No existe el identificador externo %s" % xmlid)
        return registro[0]["res_id"]
