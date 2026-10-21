# Despliegue en la nube (Odoo 18 + PostgreSQL 16 + HTTPS)

Todo corre en **una máquina virtual Ubuntu 24.04** con Docker: PostgreSQL (la base de datos
centralizada), Odoo Community 18 y Caddy (certificado HTTPS automático). El instalador es el mismo
en cualquier nube.

| Recurso | Mínimo recomendado |
|---|---|
| CPU / RAM | 2 vCPU / 4 GB |
| Disco | 30 GB |
| Puertos abiertos | 22 (SSH), 80 y 443 (web) |
| Costo aprox. | ~68 USD/mes encendida en AWS c7i-flex.large (cubierto por los créditos) |

> **Base de datos:** Odoo solo funciona con PostgreSQL. El enunciado menciona MySQL, Oracle o
> SQL Server como ejemplos de bases relacionales; confirme con el auxiliar que PostgreSQL es
> aceptado (es la base relacional que exige Odoo).

## Opción usada: AWS EC2 (capa gratuita)

1. Región **us-east-2 (Ohio)** ► EC2 ► **Lanzar instancia**:
   * AMI **Ubuntu Server 24.04 LTS**, 64 bits (x86).
   * Tipo **c7i-flex.large** (2 vCPU, 4 GiB; apto para la capa gratuita). Con 1 o 2 GiB Odoo no funciona.
   * Par de claves nuevo (guardar el `.pem`).
   * Grupo de seguridad: **SSH (22)**, **HTTP (80)** y **HTTPS (443)**.
   * Almacenamiento **30 GiB gp3** (con 8 GiB el disco se llena durante la instalación).
2. EC2 ► **Direcciones IP elásticas** ► Asignar ► Asociar a la instancia (la IP no cambia al
   detenerla). Hacerlo antes de `instalar.sh`, porque el dominio se arma con esa IP.
3. Billing ► **Budgets**: alerta al 80 % de los créditos. En la capa gratuita, si se acaban los
   créditos AWS cierra la cuenta: **detener la instancia** cuando no se use (detenida solo cobra
   disco e IP, unos 6 USD/mes; encendida unos 68 USD/mes).
4. Conectarse con **Conectar ► Conexión de la instancia EC2** (usuario `ubuntu`) o por SSH.

Si el disco quedó en 8 GiB: Volúmenes ► **Modificar** ► 30, y en la VM
`sudo growpart /dev/nvme0n1 1 && sudo resize2fs /dev/nvme0n1p1`.

## Otras nubes

El instalador funciona igual en cualquier VM Ubuntu 24.04 de 2 vCPU y 4 GB: Azure (tamaño B2s,
IP pública estática) o Google Cloud (`e2-medium`, IP externa reservada), abriendo 22, 80 y 443.

## Instalación (igual en cualquier nube)

```bash
ssh -i clave.pem ubuntu@IP_ELASTICA             # o Conectar desde la consola de AWS
sudo apt-get update && sudo apt-get install -y git
git clone -b claude/clever-turing-8emaf6 https://github.com/PabloMarroquinnn1/Geren2.git
cd Geren2/proyecto_sog2_quetzalmart/nube
sudo ./instalar.sh                               # dominio <ip>.sslip.io automático
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
