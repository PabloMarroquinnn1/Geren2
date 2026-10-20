/** @odoo-module **/

// Completa el embudo de comercio electrónico de GA4.
// Odoo ya envía view_item, add_to_cart y purchase (website_sale_tracking.js);
// aquí se agregan view_cart, begin_checkout, remove_from_cart,
// add_shipping_info y add_payment_info usando los datos de #qm_ga4_carrito.

import publicWidget from "@web/legacy/js/public/public_widget";
import "@website_sale/js/website_sale_tracking";

// Odoo vuelve a enviar view_item cada vez que recalcula la variante (por
// ejemplo, al cambiar la cantidad): se cuenta una sola vista por página.
publicWidget.registry.websiteSaleTracking.include({
    _onViewItem(event, productTrackingInfo) {
        this._qmVistos = this._qmVistos || new Set();
        const producto = productTrackingInfo && productTrackingInfo.item_id;
        if (this._qmVistos.has(producto)) {
            return;
        }
        this._qmVistos.add(producto);
        return this._super(...arguments);
    },
});

const PASOS_PAGO = ["/shop/checkout", "/shop/address", "/shop/extra_info", "/shop/payment"];

function enviarGA4(evento, parametros) {
    if (typeof window.gtag === "function") {
        window.gtag("event", evento, parametros);
    }
}

function soloUnaVez(clave, accion) {
    try {
        if (window.sessionStorage.getItem(clave)) {
            return;
        }
        window.sessionStorage.setItem(clave, "1");
    } catch {
        // Sin sessionStorage (modo privado estricto) se envía de todas formas.
    }
    accion();
}

publicWidget.registry.QuetzalMartGa4Embudo = publicWidget.Widget.extend({
    selector: "#qm_ga4_carrito",

    start() {
        let carrito;
        try {
            carrito = JSON.parse(this.el.dataset.carrito || "{}");
        } catch {
            return this._super(...arguments);
        }
        if (!carrito.items || !carrito.items.length) {
            return this._super(...arguments);
        }
        const ruta = window.location.pathname;
        const base = { currency: carrito.currency, value: carrito.value, items: carrito.items };

        if (ruta === "/shop/cart") {
            enviarGA4("view_cart", base);
            this._escucharEliminaciones(carrito);
            // "Finalizar compra": se envía al hacer clic, antes de cambiar de página.
            const botonPagar = document.querySelector("a[name='website_sale_main_button']");
            if (botonPagar) {
                botonPagar.addEventListener("click", () =>
                    soloUnaVez(`qm_ga4_begin_checkout_${carrito.order_id}`, () =>
                        enviarGA4("begin_checkout", { ...base, transport_type: "beacon" })
                    )
                );
            }
        }
        if (PASOS_PAGO.includes(ruta)) {
            // Respaldo si se entra al pago sin pasar por el carrito; una sola vez por pedido.
            soloUnaVez(`qm_ga4_begin_checkout_${carrito.order_id}`, () =>
                enviarGA4("begin_checkout", base)
            );
        }
        if (ruta === "/shop/payment") {
            soloUnaVez(`qm_ga4_shipping_${carrito.order_id}`, () =>
                enviarGA4("add_shipping_info", { ...base, shipping_tier: carrito.shipping_tier })
            );
            this._escucharPago(base);
        }
        return this._super(...arguments);
    },

    _escucharEliminaciones(carrito) {
        document.addEventListener(
            "click",
            (ev) => {
                const boton = ev.target.closest(".js_delete_product");
                const linea = boton && boton.closest("[data-product-id]");
                if (!linea) {
                    return;
                }
                const indice = carrito.product_ids.indexOf(parseInt(linea.dataset.productId));
                const item = carrito.items[indice];
                if (item) {
                    enviarGA4("remove_from_cart", {
                        currency: carrito.currency,
                        value: item.price * item.quantity,
                        items: [item],
                    });
                }
            },
            true
        );
    },

    _escucharPago(base) {
        document.addEventListener(
            "click",
            (ev) => {
                if (!ev.target.closest('button[name="o_payment_submit_button"]')) {
                    return;
                }
                const metodo = document.querySelector('input[name="o_payment_radio"]:checked');
                const etiqueta = metodo && metodo.closest("li, .o_payment_option");
                enviarGA4("add_payment_info", {
                    ...base,
                    payment_type: etiqueta ? etiqueta.innerText.trim().split("\n")[0] : "",
                    transport_type: "beacon",
                });
            },
            true
        );
    },
});

export default publicWidget.registry.QuetzalMartGa4Embudo;
