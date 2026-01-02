def includeme(config):
    config.add_static_view("static", "static", cache_max_age=3600)
    config.add_route("favicon", "/favicon.ico")
    config.add_route("robots", "/robots.txt")
    config.add_route("markup-editor-preview", "/markup-editor-preview")

    config.add_route("ask-for-on-demand-tls", "/ask-for-on-demand-tls")

    config.add_route("home", "/")
    config.add_route("search", "/search")

    config.add_route("log-out", "/log-out")
    config.add_route("join-or-log-in", "/join-or-log-in")
    config.add_route("verification-challenge", "/verification-challenge")

    # views with just a bunch of buttons to other pages.
    config.add_route("actions_view", "/actions/view")
    config.add_route("actions_new", "/actions/new")

    # billing routes.
    config.add_route("billing", "/billing")
    config.add_route("add-card", "/billing/add-card")
    config.add_route(
        "confirm-update-card", "/billing/confirm-update-card/{action}/{card_id}"
    )
    config.add_route("update-card", "/billing/update-card")
    config.add_route("disconnect-paypal", "/billing/disconnect-paypal")

    # PayPal routes
    config.add_route("paypal_create_order", "/paypal/create-order/{cart_id}")
    config.add_route("paypal_complete_checkout", "/paypal/complete-checkout/{cart_id}")

    # Adyen routes
    config.add_route("adyen_create_session", "/adyen/create-session/{cart_id}")
    config.add_route("adyen_complete_checkout", "/adyen/complete-checkout/{cart_id}")

    # Webhook routes
    config.add_route("paypal_webhook", "/webhooks/paypal")
    config.add_route("stripe_webhook", "/webhooks/stripe")
    config.add_route("adyen_webhook", "/webhooks/adyen")

    # user routes.
    config.add_route("user_settings", "/u/settings")
    config.add_route("user_crypto_settings", "/u/settings/crypto")
    config.add_route("user_crypto_settings_update", "/u/settings/crypto/{coin_type}")
    config.add_route("user_purchases", "/u/purchases")
    config.add_route("user_addresses", "/u/addresses")
    config.add_route("user_address_save", "/u/addresses/save")
    config.add_route("user_address_delete", "/u/addresses/{address_id}/delete")
    config.add_route("user_address_activate", "/u/addresses/{address_id}/activate")

    config.add_route("user_shops", "/u/shops")

    config.add_route("user_shop_activate", "/u/shop/{shop_id}/activate")

    config.add_route("user_cart_save", "/u/cart/save")
    config.add_route("user_carts", "/u/carts")
    config.add_route("user_cart_delete", "/u/cart/{cart_id}/delete")
    config.add_route("user_cart_activate", "/u/cart/{cart_id}/activate")

    config.add_route(
        "user_cart_complete_checkout", "/u/cart/{cart_id}/complete/checkout"
    )
    config.add_route("user_cart_checkout", "/u/cart/{cart_id}/checkout")

    config.add_route("user_cart_public", "/u/cart/{cart_id}/public")
    config.add_route("user_cart_unpublic", "/u/cart/{cart_id}/unpublic")

    # cart routes.
    config.add_route("cart", "/cart")
    config.add_route("cart_checkout", "/cart/checkout")

    config.add_route("cart_add_product", "/cart/add")
    config.add_route("cart_by_id", "/cart/{cart_id}")
    config.add_route("cart_remove_product", "/cart/{cart_id}/remove")
    config.add_route("cart_quantity_product", "/cart/{cart_id}/quantity")

    config.add_route("cart_handling_option", "/cart/{cart_id}/handling-option")

    config.add_route("view_invoice", "/invoice/{invoice_id}")
    config.add_route("view_invoice2", "/i/{invoice_id}")

    # coupon routes.
    config.add_route("coupon_new1", "/coupon/new")
    config.add_route("coupon_new2", "/s/{shop_id}/coupon/new")

    config.add_route("coupon_apply_to_cart", "/coupon/apply")
    config.add_route("coupon_remove_from_cart", "/coupon/remove")

    config.add_route("coupons", "/s/{shop_id}/coupons")
    config.add_route("coupon1", "/s/{shop_id}/coupon/{coupon_id}")
    config.add_route("coupon2", "/s/{shop_id}/coupon/{coupon_id}/{slug:.*}")

    # shop_location routes.
    config.add_route("shop_location_new", "/s/locations/new")
    config.add_route("shop_location_edit", "/s/{shop_id}/locations/{location_id}/edit")
    config.add_route("shop_locations", "/s/locations")
    config.add_route(
        "shop_location_switch", "/s/{shop_id}/location/{location_id}/switch"
    )

    # shop routes.
    config.add_route("shop_new", "/s/new")

    config.add_route("shop", "/s/{shop_id}")
    config.add_route("shop_products", "/s/{shop_id}/products")

    config.add_route("shop_sales", "/s/{shop_id}/sales")

    config.add_route("shop_settings", "/s/{shop_id}/settings")
    config.add_route(
        "crypto_processor_settings", "/s/{shop_id}/crypto-processor/{coin_type}"
    )

    config.add_route("shop_users", "/s/{shop_id}/users")
    config.add_route("shop_user_remove", "/s/{shop_id}/remove-user")

    config.add_route("shop_terms_of_service", "/s/terms")
    config.add_route("shop_terms_of_service2", "/s/{shop_id}/terms")
    config.add_route("shop_edit_terms_of_service", "/s/{shop_id}/terms/edit")

    config.add_route("shop_privacy_policy", "/s/privacy-policy")
    config.add_route("shop_privacy_policy2", "/s/{shop_id}/privacy-policy")
    config.add_route("shop_edit_privacy_policy", "/s/{shop_id}/privacy-policy/edit")

    config.add_route("shop_about", "/s/{shop_id}/about")
    config.add_route("shop_about_slug", "/s/{shop_id}/{slug:.*}/about")

    config.add_route("shop_slug", "/s/{shop_id}/{slug:.*}")

    # content routes.
    config.add_route("content_new", "/c/new")
    config.add_route("content", "/c/{content_id}")
    config.add_route("content_edit", "/c/{product_id}/edit")
    config.add_route("content_description_edit", "/c/{product_id}/description/edit")
    config.add_route("content_edit2", "/c/{product_id}/{slug:.*}/edit")
    config.add_route("content_slug", "/c/{product_id}/{slug:.*}")

    # product routes.
    config.add_route("product_new", "/p/new")
    config.add_route("product", "/p/{product_id}")
    config.add_route("product_description_edit", "/p/{product_id}/description/edit")
    config.add_route("product_inventory_edit", "/p/{product_id}/inventory/edit")
    config.add_route("product_bundle_edit", "/p/{product_id}/bundle/edit")
    config.add_route("product_bundle_edit2", "/p/{product_id}/{slug:.*}/bundle/edit")
    config.add_route(
        "product_remove_bundled_product",
        "/p/{product_id}/bundle/remove/{bundled_product_id}",
    )

    config.add_route("product_edit", "/p/{product_id}/edit")
    config.add_route("product_edit2", "/p/{product_id}/{slug:.*}/edit")
    config.add_route("product_slug", "/p/{product_id}/{slug:.*}")

    # comment routes.
    config.add_route("comment_new", "/comments/new")
    config.add_route("comment_reply", "/comments/{comment_id}/reply")
    config.add_route("comment_edit", "/comments/{comment_id}/edit")
    config.add_route("comment_delete", "/comments/{comment_id}/delete")
    config.add_route("comment_undelete", "/comments/{comment_id}/undelete")
    config.add_route("comment_approve", "/comments/{comment_id}/approve")
    config.add_route("comment_unapprove", "/comments/{comment_id}/unapprove")

    # cryptocurrency payment routes.
    config.add_route("crypto_xmr_start", "/crypto/xmr/start")
    config.add_route("crypto_xmr_status", "/crypto/xmr/status/{payment_id}")
    config.add_route("crypto_doge_start", "/crypto/doge/start")
    config.add_route("crypto_doge_status", "/crypto/doge/status/{payment_id}")
    config.add_route("crypto_quote", "/crypto/quote/{payment_id}")
    config.add_route("crypto_cancel", "/crypto/cancel/{payment_id}")
    config.add_route("crypto_quotes_history", "/u/crypto-quotes")
    config.add_route("crypto_debug_wallet_scan", "/crypto/debug/wallet-scan")
