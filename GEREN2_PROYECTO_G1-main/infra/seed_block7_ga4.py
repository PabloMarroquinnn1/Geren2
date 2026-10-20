"""Instala el seguimiento GA4 y eventos de comercio electrónico en el portal."""

env = env  # noqa: F821 - proporcionado por odoo shell
website = env["website"].search([], limit=1)
measurement_id = "G-ZB34R27HPD"

consent_bootstrap_js = r"""
(function () {
    // Consent Mode v2 must be declared before any Google tag or ecommerce event.
    window.dataLayer = window.dataLayer || [];
    window.gtag = window.gtag || function () { window.dataLayer.push(arguments); };
    window.gtag('consent', 'default', {
        analytics_storage: 'denied',
        ad_storage: 'denied',
        ad_user_data: 'denied',
        ad_personalization: 'denied'
    });
}());
"""

tracking_js = r"""
(function () {
    if (window.__qm_ga4_loaded) { return; }
    window.__qm_ga4_loaded = true;
    window.dataLayer = window.dataLayer || [];
    window.gtag = window.gtag || function () { window.dataLayer.push(arguments); };

    function optionalCookiesAccepted() {
        var match = document.cookie.match(/(?:^|;\s*)website_cookies_bar=([^;]+)/);
        if (!match) { return false; }
        try {
            var value = match[1];
            try { value = decodeURIComponent(value); } catch (_decodeError) {}
            return JSON.parse(value).optional === true;
        } catch (_cookieError) {
            return false;
        }
    }

    // Keep the original landing URL in memory: Odoo may remove tracking
    // parameters from the address bar while the cookie banner is still open.
    var landingPageLocation = window.__qm_ga4_campaign_landing_url || window.location.href;
    var trackingEnabled = false;
    var pageEventsRan = false;
    function startTracking() {
        if (trackingEnabled) { return; }
        trackingEnabled = true;
        var pageLocation = landingPageLocation || window.location.href;
        gtag('consent', 'update', {
            analytics_storage: 'granted'
        });
        gtag('js', new Date());
        var config = {
            send_page_view: false,
            transport_type: 'beacon',
            page_location: pageLocation
        };
        // Forward UTM values explicitly so Odoo navigation/cookie handling
        // cannot leave GA4 with a direct or unassigned session source.
        try {
            var landingUrl = new URL(pageLocation);
            var campaignFields = [
                ['utm_id', 'campaign_id'],
                ['utm_source', 'campaign_source'],
                ['utm_medium', 'campaign_medium'],
                ['utm_campaign', 'campaign_name'],
                ['utm_term', 'campaign_term'],
                ['utm_content', 'campaign_content']
            ];
            campaignFields.forEach(function (field) {
                var value = landingUrl.searchParams.get(field[0]);
                if (value) { config[field[1]] = value; }
            });
        } catch (_campaignError) {
            // Keep normal page tracking if the landing URL cannot be parsed.
        }
        gtag('config', 'G-ZB34R27HPD', config);
        gtag('event', 'page_view', {
            page_title: document.title,
            page_location: pageLocation,
            page_path: window.location.pathname
        });
        if (document.readyState !== 'loading') { runPageEvents(); }
    }

    document.addEventListener('optionalCookiesAccepted', startTracking);

    function text(selector) {
        var node = document.querySelector(selector);
        return node ? (node.textContent || '').trim().replace(/\s+/g, ' ') : '';
    }
    function number(value) {
        var raw = String(value || '').replace(/[^0-9,.-]/g, '').trim();
        if (raw.indexOf(',') >= 0 && raw.indexOf('.') >= 0) {
            if (/,[0-9]{1,2}$/.test(raw)) {
                raw = raw.replace(/\./g, '').replace(',', '.');
            } else {
                raw = raw.replace(/,/g, '');
            }
        } else if (raw.indexOf(',') >= 0) {
            raw = raw.replace(',', '.');
        }
        var result = parseFloat(raw);
        return isNaN(result) ? 0 : result;
    }
    function fire(name, params) {
        if (!trackingEnabled) { return; }
        params = params || {};
        params.currency = params.currency || 'GTQ';
        gtag('event', name, params);
    }
    function productId(scope) {
        var node = scope.querySelector('input[name="product_template_id"], input[name="product_id"], [data-product-id], [data-product-template-id]');
        var id = node ? (node.value || node.getAttribute('data-product-id') || node.getAttribute('data-product-template-id')) : '';
        if (!id) {
            var match = location.pathname.match(/-(\d+)\/?$/);
            id = match ? match[1] : '';
        }
        return id ? String(id) : '';
    }
    function itemFrom(scope) {
        scope = scope || document;
        var name = text('#product_details h1, h1[itemprop="name"], .o_wsale_product_name, .oe_product_name');
        if (!name && scope !== document) {
            var n = scope.querySelector('[itemprop="name"], .o_wsale_product_name, .td-product_name h6, .td-product_name, h6, h5');
            name = n ? (n.textContent || '').trim().replace(/^\s*\d+\s*x\s*/i, '').replace(/\s+/g, ' ') : '';
        }
        var priceNode = scope.querySelector('#product_details .oe_price .oe_currency_value, #product_details .oe_price, .oe_price .oe_currency_value, [itemprop="price"]');
        var price = priceNode ? (priceNode.getAttribute('content') || priceNode.textContent) : '';
        var qtyNode = scope.querySelector('#product_details input.js_quantity, #product_details input[name="add_qty"]');
        var quantity = qtyNode ? number(qtyNode.value) : 1;
        return {item_id: productId(scope), item_name: name || 'Producto QuetzalMart', price: number(price), quantity: quantity || 1};
    }
    function cartItems() {
        var rows = document.querySelectorAll('#cart_products .o_cart_product, #cart_products tr, .oe_cart .o_cart_product');
        var items = [];
        Array.prototype.forEach.call(rows, function (row) {
            var nameNode = row.querySelector('.td-product_name h6, .td-product_name, h6, [itemprop="name"], a[href*="/shop/"]');
            var name = nameNode ? (nameNode.textContent || '').trim().replace(/^\s*\d+\s*x\s*/i, '').replace(/\s+/g, ' ') : '';
            if (!name) { return; }
            var qtyNode = row.querySelector('input.js_quantity, input[name="add_qty"]');
            var quantity = qtyNode ? number(qtyNode.value) : 0;
            if (!quantity) {
                var qtyMatch = (nameNode.textContent || '').match(/^\s*(\d+)\s*x\s*/i);
                quantity = qtyMatch ? number(qtyMatch[1]) : 1;
            }
            var idNode = row.matches('[data-product-id]') ? row : row.querySelector('[data-product-id], input[name="product_id"], input[name="product_template_id"]');
            var id = idNode ? (idNode.getAttribute('data-product-id') || idNode.value || '') : '';
            var priceNode = row.querySelector('[name="website_sale_cart_line_price"], .td-price, .oe_currency_value');
            var price = priceNode ? number(priceNode.textContent) : 0;
            // Odoo cart lines render the extended line price; GA4 expects unit price.
            if (quantity > 0 && priceNode && !priceNode.matches('[itemprop="price"]')) { price = price / quantity; }
            items.push({item_id: id ? String(id) : undefined, item_name: name, price: price, quantity: quantity || 1});
        });
        if (!items.length && document.querySelector('#product_details')) {
            items.push(itemFrom(document));
        }
        return items;
    }
    function itemsValue(items) {
        return items.reduce(function (sum, item) { return sum + (number(item.price) * number(item.quantity || 1)); }, 0);
    }
    function pendingCheckoutItems() {
        try {
            var value = sessionStorage.getItem('qm_ga4_pending_checkout_items');
            return value ? JSON.parse(value) : [];
        } catch (_storageError) {
            return [];
        }
    }
    function fireBeginCheckout(items) {
        if (!items || !items.length) { return; }
        try {
            var now = Date.now();
            var last = Number(sessionStorage.getItem('qm_ga4_begin_checkout_sent_at') || 0);
            if (now - last < 5000) { return; }
            sessionStorage.setItem('qm_ga4_begin_checkout_sent_at', String(now));
            sessionStorage.removeItem('qm_ga4_pending_checkout_items');
        } catch (_storageError) {
            // GA4 still gets the event if browser storage is unavailable.
        }
        fire('begin_checkout', {value: itemsValue(items), items: items});
    }
    function productView() {
        // Odoo 19 usa /shop/<slug> para la ficha, no /shop/product/<slug>.
        var isProductPage = /^\/shop\/[^/]+$/.test(location.pathname)
            && !/^\/shop\/(cart|address|payment|confirm_order|confirmation|category|page)/.test(location.pathname)
            && !!document.querySelector('#product_details, #add_to_cart');
        if (isProductPage) {
            var item = itemFrom(document);
            fire('view_item', {value: item.price, items: [item]});
        }
    }
    function checkoutView() {
        // El flujo de compra de Odoo entra por /shop/address y continúa por
        // /shop/confirm_order o /shop/payment.
        if (/^\/shop\/(address|checkout|confirm_order|payment)/.test(location.pathname)) {
            var items = cartItems();
            if (!items.length) { items = pendingCheckoutItems(); }
            fireBeginCheckout(items);
        }
    }
    function purchaseView() {
        // Odoo expone el pedido confirmado en esta vista, incluso tras limpiar
        // la sesión del carrito, mediante data-order-tracking-info.
        if (location.pathname !== '/shop/confirmation') { return; }
        var status = document.querySelector('.oe_website_sale_tx_status[data-order-tracking-info]');
        if (!status) { return; }
        var order;
        try {
            order = JSON.parse(status.getAttribute('data-order-tracking-info') || '{}');
        } catch (_error) {
            return;
        }
        if (!order.transaction_id || !Array.isArray(order.items) || !order.items.length) {
            return;
        }
        // A free or negative test order is not a completed revenue transaction.
        // Keep legacy bad events in GA4 history, but prevent new ones from
        // contaminating purchase counts and revenue from this point forward.
        var purchaseValue = number(order.value);
        if (!isFinite(purchaseValue) || purchaseValue <= 0) { return; }
        var transactionId = String(order.transaction_id);
        var sentKey = 'qm_ga4_purchase_' + transactionId;
        try {
            if (window.localStorage.getItem(sentKey)) { return; }
            window.localStorage.setItem(sentKey, '1');
        } catch (_storageError) {
            // GA4 still gets the event if browser storage is unavailable.
        }
        fire('purchase', {
            transaction_id: transactionId,
            value: purchaseValue,
            tax: number(order.tax),
            shipping: number(order.shipping),
            currency: order.currency || 'GTQ',
            items: order.items.map(function (item) {
                return {
                    item_id: String(item.item_id || ''),
                    item_name: item.item_name || 'Producto QuetzalMart',
                    item_category: item.item_category || undefined,
                    price: number(item.price),
                    quantity: number(item.quantity) || 1
                };
            })
        });
    }
    function runPageEvents() {
        if (!trackingEnabled || pageEventsRan) { return; }
        pageEventsRan = true;
        productView();
        checkoutView();
        purchaseView();
    }
    document.addEventListener('click', function (event) {
        var control = event.target.closest && event.target.closest('a, button, input[type="submit"]');
        if (control && location.pathname === '/shop/cart') {
            var label = (control.textContent || control.value || '').trim().replace(/\s+/g, ' ').toLowerCase();
            var href = control.getAttribute('href') || '';
            var beginsCheckout = /finalizar compra|checkout|proceder al pago/.test(label)
                || /^\/shop\/(address|checkout)(?:[/?#]|$)/.test(href);
            if (beginsCheckout) {
                var checkoutItems = cartItems();
                if (checkoutItems.length) {
                    try {
                        sessionStorage.setItem('qm_ga4_pending_checkout_items', JSON.stringify(checkoutItems));
                    } catch (_storageError) {}
                    // Fire before navigation so the event is not lost while Odoo unloads the cart.
                    fireBeginCheckout(checkoutItems);
                }
            }
        }
        var add = event.target.closest && event.target.closest('#add_to_cart, a.a-submit, button.a-submit, [name="add_to_cart"], form[action*="/shop/cart/update"] button');
        if (add) {
            var form = add.closest('form') || add.closest('.oe_product') || document;
            var item = itemFrom(form);
            fire('add_to_cart', {value: item.price * item.quantity, items: [item]});
        }
    }, true);
    document.addEventListener('DOMContentLoaded', runPageEvents, {once: true});
    if (optionalCookiesAccepted()) { startTracking(); }
}());
"""

campaign_capture_js = r"""
(function () {
    try {
        var landingUrl = new URL(window.location.href);
        if (landingUrl.searchParams.has('utm_source')
            || landingUrl.searchParams.has('utm_medium')
            || landingUrl.searchParams.has('utm_campaign')
            || landingUrl.searchParams.has('utm_id')) {
            window.__qm_ga4_campaign_landing_url = landingUrl.href;
        }
    } catch (_campaignCaptureError) {}
}());
"""

arch = """<data inherit_id="website.layout" name="QuetzalMart GA4 tracking">
    <xpath expr="//head/*[1]" position="before">
        <script type="text/javascript"><![CDATA[%s]]></script>
        <script type="text/javascript"><![CDATA[%s]]></script>
    </xpath>
    <xpath expr="//head" position="inside">
        <script type="text/javascript"><![CDATA[%s]]></script>
        <script async="async" src="https://www.googletagmanager.com/gtag/js?id=G-ZB34R27HPD"></script>
    </xpath>
</data>""" % (consent_bootstrap_js, campaign_capture_js, tracking_js)

View = env["ir.ui.view"]
view = View.search([("key", "=", "qm_ga4_tracking")], limit=1)
values = {
    "name": "QuetzalMart GA4 tracking",
    "type": "qweb",
    "key": "qm_ga4_tracking",
    "arch": arch,
    "inherit_id": env.ref("website.layout").id,
    "website_id": website.id,
    "active": True,
}
if view:
    view.write(values)
else:
    View.create(values)
env.cr.commit()
print({"website": website.name, "measurement_id": measurement_id, "tracking_view": "qm_ga4_tracking"})
