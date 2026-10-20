# Correo y campaña de marketing

## Lo que pide el enunciado y cómo se cumple

> El auxiliar se registrará al CRM, comprará y recibirá **dos correos**: el de la compra y después
> el de marketing, con asuntos distintos y **no enviados desde un correo personal**.

1. **Registro en el CRM:** al crear su cuenta en la tienda (*Iniciar sesión ► Crear una cuenta*),
   el módulo `qm_crm_postventa` crea un **lead** "Registro en la tienda: …" con la etiqueta
   *Registro web* y lo suscribe a la lista *Registros web*. (Si compra como invitado, el contacto
   igual queda en el CRM con la compra.)
2. **Compra:** al pagar, Odoo confirma el pedido, crea y publica la factura y envía el
   **comprobante de compra** con la plantilla propia *QuetzalMart: comprobante de compra*
   (asunto `QuetzalMart · Comprobante de compra INV/2026/…`, PDF adjunto). El lead del registro se
   convierte en una **oportunidad ganada** "Compra en línea S00…" ligada al pedido.
3. **Marketing:** 45 segundos después se envía la **campaña postcompra** (asunto
   `🎁 <Nombre>, tu próxima compra en QuetzalMart tiene 10% de descuento`) con el código
   **QUETZAL10** (descuento real de 10 % configurado en Odoo), productos recomendados de las mismas
   categorías que compró, las sucursales y enlaces con UTM (`utm_source=correo_postcompra`,
   `utm_medium=email`, `utm_campaign=temporada_quetzalmart`) para medir la campaña en GA4.

Además está lista la **campaña masiva** "QuetzalMart llegó a tu casa" en *Marketing por correo*
para la lista *Clientes QuetzalMart* (40 clientes); se envía con el botón **Enviar**.

## Cuenta de correo de la empresa (no personal)

Opción recomendada: crear una cuenta de Gmail **solo para la empresa** (por ejemplo
`ventas.quetzalmart.g1@gmail.com`).

1. En esa cuenta: **Gestionar tu cuenta ► Seguridad ► Verificación en dos pasos** (activar).
2. **Contraseñas de aplicaciones** ► crear una para "Odoo" ► copiar la clave de 16 letras.
3. Configurar Odoo (una vez):

```bash
python carga_masiva/cargar_quetzalmart.py --url https://SU-DOMINIO --clave CLAVE_ADMIN --paso configurar \
  --correo-remitente ventas.quetzalmart.g1@gmail.com \
  --smtp-servidor smtp.gmail.com --smtp-puerto 587 \
  --smtp-usuario ventas.quetzalmart.g1@gmail.com --smtp-clave "abcd efgh ijkl mnop"
```

También puede hacerse a mano en *Ajustes ► Técnico ► Servidores de correo saliente*
(`smtp.gmail.com`, puerto 587, TLS/STARTTLS, usuario y clave de aplicación) y poniendo el mismo
correo en *Ajustes ► Compañías ► QuetzalMart ► Correo*.

Alternativa sin Gmail: Brevo (300 correos diarios gratis) con `smtp-relay.brevo.com`, puerto 587,
y un remitente verificado.

## Prueba antes de la calificación

1. Abrir la tienda en una ventana privada, crear una cuenta con su correo, comprar un producto
   y pagar con la tarjeta de prueba.
2. Deben llegar: confirmación del pedido, **comprobante de compra** y, menos de un minuto
   después, la **campaña** (revise también *Promociones/Spam* la primera vez).
3. En Odoo: *CRM* (oportunidad ganada), *Ventas* (pedido), *Contabilidad* (factura pagada),
   *Documentos ► Facturas de venta* (el PDF) y *Ajustes ► Técnico ► Correos* (los dos correos
   en estado *Enviado*). SQL: sección 11 de `sql/consultas_calificacion.sql`.

Si un correo queda en *Excepción*, revise la clave de aplicación y que el remitente sea el mismo
correo autenticado.
