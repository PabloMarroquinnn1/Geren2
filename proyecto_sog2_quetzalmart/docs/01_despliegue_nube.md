# Despliegue en la nube (Odoo 18 + PostgreSQL 16 + HTTPS)

Todo corre en **una máquina virtual Ubuntu 24.04** con Docker: PostgreSQL (la base de datos
centralizada), Odoo Community 18 y Caddy (certificado HTTPS automático). El instalador es el mismo
en cualquier nube.

| Recurso | Mínimo recomendado |
|---|---|
| CPU / RAM | 2 vCPU / 4 GB |
| Disco | 30 GB |
| Puertos abiertos | 22 (SSH), 80 y 443 (web) |
| Costo aprox. | 25-35 USD/mes (cubierto por los créditos de estudiante) |

> **Base de datos:** Odoo solo funciona con PostgreSQL. El enunciado menciona MySQL, Oracle o
> SQL Server como ejemplos de bases relacionales; confirme con el auxiliar que PostgreSQL es
> aceptado (es la base relacional que exige Odoo).

## Opción A: Azure for Students (sin tarjeta de crédito)

1. Activar <https://azure.microsoft.com/es-es/free/students> con el correo de la universidad
   (100 USD de crédito).
2. **Máquinas virtuales ► Crear**: imagen *Ubuntu Server 24.04 LTS*, tamaño **B2s** (2 vCPU, 4 GB),
   autenticación con **clave SSH** (descargue el `.pem`), puertos de entrada **SSH, HTTP, HTTPS**.
3. Al terminar: VM ► **Dirección IP pública** ► *Configuración*: asignación **Estática** y
   **Etiqueta de nombre DNS** (por ejemplo `quetzalmart-g1`). El dominio queda como
   `quetzalmart-g1.eastus.cloudapp.azure.com`.

## Opción B: Google Cloud (300 USD de prueba)

1. Compute Engine ► **Crear instancia**: `e2-medium` (2 vCPU, 4 GB), Ubuntu 24.04 LTS, disco 30 GB,
   marcar **Permitir tráfico HTTP y HTTPS**.
2. Red de VPC ► **Direcciones IP** ► reservar como estática la IP externa de la VM.
3. Dominio gratuito: `quetzalmart.<IP-con-guiones>.sslip.io` (el instalador lo arma solo).

## Instalación (igual en cualquier nube)

```bash
ssh -i clave.pem azureuser@IP_DE_LA_VM          # en GCP: botón SSH de la consola
sudo apt-get update && sudo apt-get install -y git
git clone https://github.com/pablomarroquinnn1/geren2.git    # repositorio privado: use un token de GitHub como clave
cd geren2/proyecto_sog2_quetzalmart/nube
sudo ./instalar.sh                               # dominio <ip>.sslip.io automático
# o: sudo ./instalar.sh quetzalmart-g1.eastus.cloudapp.azure.com
```

El instalador (5-10 minutos) instala Docker, crea contraseñas aleatorias en `nube/.env`, descarga
OCA DMS, crea la base `quetzalmart` en español con la compañía en Guatemala, instala
`qm_implementacion` (que instala todos los módulos) y obtiene el certificado HTTPS. Al final
muestra la URL y las credenciales, que también quedan en `nube/credenciales.txt` (no se suben al
repositorio).

## Cargar los datos (desde su computadora)

```bash
pip install openpyxl reportlab
python carga_masiva/cargar_quetzalmart.py --url https://SU-DOMINIO --clave CLAVE_ADMIN \
    --ga4 G-XXXXXXXXXX \
    --correo-remitente ventas.quetzalmart@gmail.com \
    --smtp-servidor smtp.gmail.com --smtp-usuario ventas.quetzalmart@gmail.com --smtp-clave "CLAVE DE APLICACION"
```

Tarda unos 15 minutos y deja todo lo que pide el enunciado (ver `docs/02_carga_de_datos.md`).
El correo se explica en `docs/04_correo_y_marketing.md`.

## Ver la base de datos con DBeaver (para las consultas SQL)

PostgreSQL no se expone a Internet; DBeaver entra por un túnel SSH:

1. Nueva conexión ► PostgreSQL. **Host** `localhost`, **Puerto** `5432`, **Base** `quetzalmart`,
   **Usuario** `consulta`, **Clave**: la de `credenciales.txt` (solo lectura).
2. Pestaña **SSH**: usar túnel, host = IP de la VM, puerto 22, usuario de la VM, autenticación
   con la clave privada (`.pem`).
3. Abrir `sql/consultas_calificacion.sql` y ejecutar cada bloque.

Sin DBeaver: `sudo ./consola_sql.sh < ../sql/consultas_calificacion.sql` dentro de la VM.

## Mantenimiento

| Tarea | Comando (en `nube/`) |
|---|---|
| Aplicar cambios de los módulos tras `git pull` | `sudo ./actualizar.sh` |
| Copia de seguridad (base + archivos) | `sudo ./respaldo.sh` |
| Ver registros | `sudo docker compose logs -f odoo` |
| Reiniciar | `sudo docker compose restart` |

Haga un respaldo antes de la calificación. Al terminar el semestre, **detenga o elimine la VM**
para no consumir créditos.
