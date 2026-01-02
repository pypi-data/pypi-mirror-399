Changelog
=========

All notable changes to this project will be documented in this file.

2025-12-22 (2:30 PM)
--------------------

PayPal Integration
~~~~~~~~~~~~~~~~~~

* Added PayPal as a payment processor alongside Stripe and crypto payments
* New ``PayPalUserShop`` model for saved payment methods
* Invoice model extended with ``paypal_order_id`` and ``paypal_capture_id`` columns
* Shop settings now include PayPal client ID and secret configuration
* Checkout page supports PayPal payment option when enabled
* Added PayPal saved payment methods (vault) support
* Added ``/billing/disconnect-paypal`` route for users to manage saved PayPal
* See ``docs/PAYPAL.md`` for details

CSS Grid Lanes
~~~~~~~~~~~~~~

* Added toggleable CSS Grid Lanes (masonry layout) setting per shop
* New ``grid_lanes_enabled`` column on Shop model

Video Thumbnails
~~~~~~~~~~~~~~~~

* Added play button overlay on video thumbnails for unlocked content
* Styled video play overlay with red tint and click-to-play text

Meta Tags
~~~~~~~~~

* Added Twitter card meta tags for proper link unfurling on Matrix/Discord
* Increased meta description truncation to 500 chars
