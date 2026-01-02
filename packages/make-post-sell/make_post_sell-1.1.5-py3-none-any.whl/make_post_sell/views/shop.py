import re

import mimetypes

from pyramid.view import view_config

from . import (
    get_referer_or_home,
    user_required,
    shop_owner_required,
    shop_editor_required,
)

from ..models.shop import (
    Shop,
    get_shop_by_id,
    get_shop_by_domain_name,
    is_shop_name_valid,
    is_shop_name_available,
)

from ..models.product import (
    get_products_from_a_shop,
    get_all_products_from_a_shop,
    get_products_by_keywords,
)

from ..models.user import (
    get_user_by_id,
    get_or_create_user_by_email,
)

from ..models.shop_search_request import (
    ShopSearchRequest,
)

from ..lib.mail import send_invite_email

from ..lib.phone_numbers import is_phone_number_valid

from ..lib.currency import dollars_to_cents, cents_to_dollars

from pyramid.httpexceptions import HTTPFound

# feel free to come up with a better plan, GPT-4 made this regex.
DOMAIN_NAME_REGEX = re.compile(
    r"^(?=.{1,253}$)(?:(?!-)[A-Za-z0-9-]{1,63}(?<!-)\.)+[A-Za-z]{2,9}$"
)


def checkbox_to_bool(checkbox):
    return checkbox == "on"


def bool_to_checkbox(boolean):
    return "on" if boolean else "off"


def get_shop_from_matchdict(request, prefetched_shop=None):
    """
    This function uses the shop_id from the url path
    and returns a Shop object from the database or None.

    This protects the database from querying the same shop object twice,
    if the optional prefetched_shop Shop object has the same id as the
    matchdict in the route's path.
    """
    if prefetched_shop and str(prefetched_shop.id) == request.matchdict["shop_id"]:
        return prefetched_shop
    else:
        # returns None if shop_id is an invalid uuid.
        return get_shop_by_id(request.dbsession, request.matchdict["shop_id"])


@view_config(route_name="home", renderer="home.j2")
def home(request):
    products = None
    if request.shop:
        products = get_products_from_a_shop(request.shop)
    return {
        "products": products,
    }


@view_config(route_name="shop", renderer="shop.j2")
@view_config(route_name="shop_slug", renderer="shop.j2")
def shop(request):
    shop = get_shop_from_matchdict(request)
    if "slug" not in request.matchdict:
        return HTTPFound(f"/s/{shop.id}/{shop.slug}")

    return {
        "products": get_products_from_a_shop(shop),
    }


@view_config(route_name="shop_products", renderer="shop_products.j2")
@shop_editor_required()
def shop_products(request):
    msg = None
    shop = get_shop_from_matchdict(request)

    if shop is None:
        msg = ("That shop_id does not exist.", "error")

    if msg:
        request.session.flash(msg)
        return HTTPFound(get_referer_or_home(request))

    return {
        "products": get_all_products_from_a_shop(shop),
    }


@view_config(route_name="shop_about", renderer="shop_about.j2")
@view_config(route_name="shop_about_slug", renderer="shop_about.j2")
def shop_about(request):
    shop = get_shop_from_matchdict(request)
    if "slug" not in request.matchdict:
        return HTTPFound(f"/s/{shop.id}/{shop.slug}/about")
    return {}


@view_config(route_name="search", renderer="home.j2")
def search(request):
    keywords = request.params.get("keywords", None)

    if keywords is None:
        return HTTPFound(get_referer_or_home(request))

    products = get_products_by_keywords(
        request.dbsession, keywords.split(" "), request.shop
    )

    hit_count = len(products)

    # log search_request for later reporting.
    search_request = ShopSearchRequest(
        keywords,
        hit_count,
        shop=request.shop,
        user=request.user,
    )
    request.dbsession.add(search_request)
    request.dbsession.flush()

    if hit_count == 1:
        # redirect to only match, the title slugified node uri.
        return HTTPFound(products[0].absolute_url(request))

    return {
        "products": products,
        "keywords": keywords,
    }


@view_config(route_name="shop_new", renderer="shop_new.j2")
@user_required(
    flash_msg="To create a new shop, please verify your email address below.",
    flash_level="info",
    redirect_to_route_name="join-or-log-in",
)
def shop_new(request):
    name = request.params.get("name", "").strip()
    phone_number = request.params.get("phone_number", "").strip()
    billing_address = request.params.get("billing_address", "").strip()
    description = request.params.get("description", "").strip()

    if name and description and billing_address and phone_number:
        if not is_shop_name_valid(name):
            msg = (
                "Invalid shop name, only use alpha numeric, spaces, dashes, or periods.",
                "error",
            )
            request.session.flash(msg)
        elif not is_shop_name_available(request.dbsession, name):
            msg = ("That shop name is already in use. Please pick another.", "error")
            request.session.flash(msg)
        elif not is_phone_number_valid(phone_number):
            msg = ("Invalid phone number. We accept: -.() and numbers.", "error")
            request.session.flash(msg)

        else:
            shop = Shop(name, phone_number, billing_address, description)
            shop.add_user_to_shop(request.user)
            request.user.set_active_shop(shop)
            request.dbsession.add(shop)
            request.dbsession.add(request.user)
            request.dbsession.flush()
            msg = (
                "Great work, you created a shop! You may continue to setup your shop or start posting products!",
                "success",
            )
            request.session.flash(msg)
            return HTTPFound(f"/s/{shop.id}/settings")

    elif name or description or billing_address or phone_number:
        msg = ("You must fill out all fields.", "error")
        request.session.flash(msg)

    return {
        "name": name,
        "description": description,
        "billing_address": billing_address,
        "phone_number": phone_number,
    }


@view_config(route_name="user_shop_activate")
@shop_editor_required()
def shop_activate(request):
    shop = get_shop_from_matchdict(request, prefetched_shop=request.user.active_shop)

    if shop is None:
        msg = ("That shop_id does not exist.", "error")

    elif shop == request.user.active_shop:
        msg = ("This shop is already your active shop.", "success")

    else:
        msg = ("You activated that shop.", "success")
        request.user.active_shop_id = shop.id
        request.dbsession.add(request.user)
        request.dbsession.flush()

    request.session.flash(msg)
    return HTTPFound("/")


@view_config(route_name="shop_terms_of_service", renderer="markup_renderer.j2")
@view_config(route_name="shop_terms_of_service2", renderer="markup_renderer.j2")
def shop_terms_of_service(request):
    return {
        "markup_rendered": request.shop.terms_of_service_html,
        "markup_path": "terms",
    }


@view_config(route_name="shop_privacy_policy", renderer="markup_renderer.j2")
@view_config(route_name="shop_privacy_policy2", renderer="markup_renderer.j2")
def shop_privacy_policy(request):
    return {
        "markup_rendered": request.shop.privacy_policy_html,
        "markup_path": "privacy-policy",
    }


@view_config(route_name="shop_edit_terms_of_service", renderer="markup_editor.j2")
@shop_owner_required()
def shop_edit_terms_of_service(request):
    shop = request.user.active_shop
    if request.shop:
        shop = request.shop

    raw_markup_data = request.params.get(
        "markup-editor-textarea", shop.terms_of_service_raw
    )

    if raw_markup_data and raw_markup_data != shop.terms_of_service_raw:
        shop.terms_of_service = raw_markup_data
        msg = ("You set the shop's Terms of Service!", "success")
        request.session.flash(msg)
        request.dbsession.add(shop)
        request.dbsession.flush()

    return {
        "markup_subject": "Terms of Service",
        "markup_rendered": shop.terms_of_service_html,
        "markup_raw": shop.terms_of_service_raw,
        "markup_form_path": shop.absolute_terms_url(request),
    }


@view_config(route_name="shop_edit_privacy_policy", renderer="markup_editor.j2")
@shop_owner_required()
def shop_edit_privacy_policy(request):
    shop = request.user.active_shop
    if request.shop:
        shop = request.shop

    raw_markup_data = request.params.get(
        "markup-editor-textarea", shop.privacy_policy_raw
    )

    if raw_markup_data and raw_markup_data != shop.privacy_policy_raw:
        shop.privacy_policy = raw_markup_data
        msg = ("You set the shop's Privacy Policy!", "success")
        request.session.flash(msg)
        request.dbsession.add(shop)
        request.dbsession.flush()

    return {
        "markup_subject": "Privacy Policy",
        "markup_rendered": shop.privacy_policy_html,
        "markup_raw": shop.privacy_policy_raw,
        "markup_form_path": shop.absolute_privacy_policy_url(request),
    }


@view_config(route_name="shop_users", renderer="shop_users.j2")
@shop_owner_required()
def shop_users(request):
    shop = request.shop
    email_to_invite = request.params.get("email-to-invite", "")
    role_id = request.params.get("role-id")

    _email_regex = re.compile(r"^[^@]+@[^@]+\.[^.@]+$")

    if "submit" in request.params:
        if not email_to_invite:
            request.session.flash(("Please choose an email to invite.", "error"))
        elif not role_id:
            request.session.flash(("Please choose a role.", "error"))
        elif email_to_invite and _email_regex.match(email_to_invite) is None:
            # posted email does not pass regex the match object is None.
            request.session.flash(("That email address is invalid.", "error"))
        elif email_to_invite and role_id:
            # get or create new user if it doesn't exist.
            user = get_or_create_user_by_email(request.dbsession, email_to_invite)

            # make new user a shop user of the proper role.
            request.shop.add_user_to_shop(user, role_id)

            # commit changes to database.
            request.dbsession.add(user)
            request.dbsession.flush()

            # send an invitation email to the new user.
            send_invite_email(request, email_to_invite, request.user, request.shop)

            msg = (f"You invited {email_to_invite} to the shop.", "success")
            request.session.flash(msg)

    return {
        "email": email_to_invite or "",
        "owners": list(set(shop.owners)),
        "editors": list(set(shop.editors)),
        "members": list(set(shop.members)),
    }


@view_config(route_name="shop_user_remove")
@shop_owner_required()
def shop_user_remove(request):
    user_id = request.params.get("user_id", None)
    if user_id:
        user = get_user_by_id(request.dbsession, user_id)
        if user:
            if user == request.user:
                msg = (
                    f"Sheepishly refusing to remove myself! {user.email}",
                    "error",
                )
                request.session.flash(msg)
            else:
                user_shop = request.shop.get_usershop_for_user(user)
                request.dbsession.delete(user_shop)
                msg = (f"You removed {user.email} from the shop.", "success")
                request.session.flash(msg)
    return HTTPFound(f"/s/{request.shop.id}/users")


@view_config(route_name="shop_settings", renderer="shop_settings.j2")
@shop_owner_required()
def shop_settings(request):
    shop = request.shop
    name = request.params.get("name", shop.name).strip()
    phone_number = request.params.get("phone_number", shop.phone_number).strip()
    billing_address = request.params.get(
        "billing_address", shop.billing_address
    ).strip()
    description = request.params.get("description", shop.description).strip()
    domain_name = (
        request.params.get("domain_name", shop.domain_name or "").strip().lower()
    )

    # announcement ribbon settings.
    ribbon_text = request.params.get("ribbon_text", shop.ribbon_text).strip()
    ribbon_text_color = request.params.get(
        "ribbon_text_color", shop.ribbon_text_color
    ).strip()
    ribbon_color_1 = request.params.get("ribbon_color_1", shop.ribbon_color_1).strip()
    ribbon_color_2 = request.params.get("ribbon_color_2", shop.ribbon_color_2).strip()

    # Theme settings
    default_theme = request.params.get("default_theme", shop.default_theme)

    # Grid lanes setting (keep current value by default)
    grid_lanes_enabled = shop.grid_lanes_enabled

    google_analytics_id = request.params.get(
        "google_analytics_id", shop.google_analytics_id
    )
    plausible_domain_name = request.params.get(
        "plausible_domain_name", shop.plausible_domain_name or ""
    ).strip()

    stripe_test_mode = request.app.get("stripe.test_mode", False)
    stripe_public_api_key = request.params.get(
        "stripe_public_api_key", shop.stripe_public_api_key
    )
    stripe_secret_api_key = request.params.get(
        "stripe_secret_api_key", shop.stripe_secret_api_key
    )

    # maint_mode_checkbox = request.params.get("maint-mode-checkbox", bool_to_checkbox(shop.maint_mode))
    maint_mode_checkbox = request.params.get("maint-mode-checkbox", "off")
    maint_mode = checkbox_to_bool(maint_mode_checkbox)

    # Determine which form was submitted
    form_section = request.params.get("form_section", "")

    # Comment system settings
    comments_enabled = shop.comments_enabled  # Keep current value by default
    comments_require_purchase = shop.comments_require_purchase
    comments_require_approval = shop.comments_require_approval

    # Only update comment settings if the comment form was submitted
    if form_section == "comment-settings":
        comments_enabled_checkbox = request.params.get(
            "comments-enabled-checkbox", "off"
        )
        comments_enabled = checkbox_to_bool(comments_enabled_checkbox)
        comments_require_purchase_checkbox = request.params.get(
            "comments-require-purchase-checkbox", "off"
        )
        comments_require_purchase = checkbox_to_bool(comments_require_purchase_checkbox)
        comments_require_approval_checkbox = request.params.get(
            "comments-require-approval-checkbox", "off"
        )
        comments_require_approval = checkbox_to_bool(comments_require_approval_checkbox)

    # Crypto settings
    crypto_quote_expiry_seconds = request.params.get(
        "crypto_quote_expiry_seconds", shop.crypto_quote_expiry_seconds
    )
    # Get dollar values from form
    payment_risk_threshold_mid_dollars = request.params.get(
        "payment_risk_threshold_mid_dollars"
    )
    payment_risk_threshold_high_dollars = request.params.get(
        "payment_risk_threshold_high_dollars"
    )

    s3_webhook_key = request.params.get("key")
    s3_webhook_bucket = request.params.get("bucket")
    s3_webhook_etag = request.params.get("etag")

    uploaded_file_key = request.params.get("uploaded", "")

    if uploaded_file_key:
        request.session.flash(
            (
                f"You successfully uploaded a new {uploaded_file_key} file!",
                "success",
            )
        )

    if request.method == "POST":
        # Handle shop settings form
        if form_section == "shop-settings":
            if name != shop.name:
                if not is_shop_name_valid(name):
                    msg = (
                        "Invalid shop name, only use alpha numeric, spaces, dashes, or periods.",
                        "error",
                    )
                elif not is_shop_name_available(request.dbsession, name):
                    msg = (
                        "That shop name is already in use. Please pick another.",
                        "error",
                    )
                else:
                    shop.name = name
                    msg = ("You set the shop's name.", "success")
                request.session.flash(msg)

            if phone_number != shop.phone_number:
                if is_phone_number_valid(phone_number):
                    shop.phone_number = phone_number
                    msg = ("You set the shop's phone number.", "success")
                else:
                    msg = (
                        "Invalid phone number. We accept: -.() and numbers.",
                        "error",
                    )
                request.session.flash(msg)

            if billing_address and billing_address != shop.billing_address:
                shop.billing_address = billing_address
                msg = ("You set the shop's billing address.", "success")
                request.session.flash(msg)

            if description and description != shop.description:
                shop.description = description
                msg = ("You set the shop's description.", "success")
                request.session.flash(msg)

        # Handle integration settings form
        if form_section == "integration-settings":
            if domain_name != shop.domain_name:
                if not domain_name:
                    # clear the domain name.
                    shop.domain_name = domain_name
                    msg = ("You cleared the shop's domain name.", "success")
                elif DOMAIN_NAME_REGEX.match(domain_name):
                    existing_shop = get_shop_by_domain_name(
                        request.dbsession, domain_name
                    )
                    if existing_shop:
                        msg = (
                            "That domain name is already in use. Please pick another.",
                            "error",
                        )
                    else:
                        shop.domain_name = domain_name
                        msg = ("You set the shop's domain name.", "success")
                else:
                    msg = ("Invalid domain name. Please enter a valid domain.", "error")
                request.session.flash(msg)

            if google_analytics_id != (shop.google_analytics_id or ""):
                shop.google_analytics_id = google_analytics_id
                msg = ("You set the shop's Google Analytics Id.", "success")
                request.session.flash(msg)

            if plausible_domain_name != (shop.plausible_domain_name or ""):
                shop.plausible_domain_name = plausible_domain_name
                msg = ("You set the shop's Plausible Analytics Domain Name.", "success")
                request.session.flash(msg)

        # Handle ribbon settings form
        if form_section == "ribbon-settings":
            if ribbon_text != (shop.ribbon_text or ""):
                shop.ribbon_text = ribbon_text
                msg = ("You set the shop's announcement ribbon text.", "success")
                request.session.flash(msg)

            if ribbon_text_color != (shop.ribbon_text_color or ""):
                shop.ribbon_text_color = ribbon_text_color
                msg = ("You set the shop's announcement ribbon text color.", "success")
                request.session.flash(msg)

            if ribbon_color_1 != (shop.ribbon_color_1 or ""):
                shop.ribbon_color_1 = ribbon_color_1
                msg = (
                    "You set the shop's announcement ribbon background color 1.",
                    "success",
                )
                request.session.flash(msg)

            if ribbon_color_2 != (shop.ribbon_color_2 or ""):
                shop.ribbon_color_2 = ribbon_color_2
                msg = (
                    "You set the shop's announcement ribbon background color 2.",
                    "success",
                )
                request.session.flash(msg)

            # Handle default theme setting
            if default_theme and int(default_theme) != shop.default_theme:
                shop.default_theme = int(default_theme)
                theme_name = "Dark Mode" if int(default_theme) == 0 else "Light Mode"
                msg = (
                    f"Shop default theme set to {theme_name}.",
                    "success",
                )
                request.session.flash(msg)

            # Handle grid lanes setting
            grid_lanes_checkbox = request.params.get("grid-lanes-checkbox", "off")
            grid_lanes_enabled = checkbox_to_bool(grid_lanes_checkbox)
            if shop.grid_lanes_enabled != grid_lanes_enabled:
                shop.grid_lanes_enabled = grid_lanes_enabled
                status = "enabled" if grid_lanes_enabled else "disabled"
                request.session.flash(
                    (
                        f"Masonry layout (Grid Lanes) {status}",
                        "success",
                    )
                )

        # Handle stripe settings form
        if form_section == "stripe-settings":
            # Handle disable action
            if request.params.get("disable_stripe"):
                shop.stripe_enabled = False
                request.session.flash(("Stripe payments disabled", "success"))

            # Handle re-enable action - if stripe is disabled and we're submitting stripe settings
            elif not shop.stripe_enabled:
                shop.stripe_enabled = True
                request.session.flash(("Stripe payments re-enabled", "success"))

            elif stripe_public_api_key != shop.stripe_public_api_key:
                if stripe_public_api_key.startswith("pk_"):
                    if not stripe_test_mode and "_test_" in stripe_public_api_key:
                        msg = (
                            "Test Stripe keys are not allowed. Please create a test shop at test.makepostsell.com.",
                            "error",
                        )
                    else:
                        shop.stripe_public_api_key = stripe_public_api_key
                        # Re-enable Stripe if it was disabled and we're setting valid keys
                        if not shop.stripe_enabled:
                            shop.stripe_enabled = True
                            msg = (
                                "Stripe payments re-enabled and public key updated.",
                                "success",
                            )
                        else:
                            msg = (
                                "You set the shop's stripe_public_api_key.",
                                "success",
                            )
                else:
                    msg = (
                        "The shop's stripe_public_api_key must start with 'pk_'.",
                        "error",
                    )
                request.session.flash(msg)

            if stripe_secret_api_key != shop.stripe_secret_api_key:
                if stripe_secret_api_key.startswith("sk_"):
                    if not stripe_test_mode and "_test_" in stripe_secret_api_key:
                        msg = (
                            "Test Stripe keys are not allowed. Please create a test shop at test.makepostsell.com.",
                            "error",
                        )
                    else:
                        shop.stripe_secret_api_key = stripe_secret_api_key
                        # Re-enable Stripe if it was disabled and we're setting valid keys
                        if not shop.stripe_enabled:
                            shop.stripe_enabled = True
                            msg = (
                                "Stripe payments re-enabled and secret key updated.",
                                "success",
                            )
                        else:
                            msg = (
                                "You set the shop's stripe_secret_api_key.",
                                "success",
                            )
                else:
                    msg = (
                        "The shop's stripe_secret_api_key must start with 'sk_'.",
                        "error",
                    )
                request.session.flash(msg)

        # Handle PayPal settings form
        if form_section == "paypal-settings":
            paypal_client_id = request.params.get("paypal_client_id", "").strip()
            paypal_secret = request.params.get("paypal_secret", "").strip()

            # Handle disable action
            if request.params.get("disable_paypal"):
                shop.paypal_enabled = False
                request.session.flash(("PayPal payments disabled", "success"))
            # Handle re-enable action
            elif not shop.paypal_enabled:
                shop.paypal_enabled = True
                request.session.flash(("PayPal payments re-enabled", "success"))
            else:
                if paypal_client_id and paypal_client_id != shop.paypal_client_id:
                    shop.paypal_client_id = paypal_client_id
                    request.session.flash(("You set the shop's PayPal Client ID.", "success"))

                if paypal_secret and paypal_secret != shop.paypal_secret:
                    shop.paypal_secret = paypal_secret
                    request.session.flash(("You set the shop's PayPal Secret.", "success"))

        # Handle Adyen settings form
        if form_section == "adyen-settings":
            adyen_api_key = request.params.get("adyen_api_key", "").strip()
            adyen_merchant_account = request.params.get("adyen_merchant_account", "").strip()
            adyen_client_key = request.params.get("adyen_client_key", "").strip()
            adyen_hmac_key = request.params.get("adyen_hmac_key", "").strip()

            # Handle disable action
            if request.params.get("disable_adyen"):
                shop.adyen_enabled = False
                request.session.flash(("Adyen payments disabled", "success"))
            # Handle re-enable action
            elif not shop.adyen_enabled:
                shop.adyen_enabled = True
                request.session.flash(("Adyen payments re-enabled", "success"))
            else:
                if adyen_api_key and adyen_api_key != shop.adyen_api_key:
                    shop.adyen_api_key = adyen_api_key
                    request.session.flash(("You set the shop's Adyen API Key.", "success"))

                if adyen_merchant_account and adyen_merchant_account != shop.adyen_merchant_account:
                    shop.adyen_merchant_account = adyen_merchant_account
                    request.session.flash(("You set the shop's Adyen Merchant Account.", "success"))

                if adyen_client_key and adyen_client_key != shop.adyen_client_key:
                    shop.adyen_client_key = adyen_client_key
                    request.session.flash(("You set the shop's Adyen Client Key.", "success"))

                if adyen_hmac_key and adyen_hmac_key != shop.adyen_hmac_key:
                    shop.adyen_hmac_key = adyen_hmac_key
                    request.session.flash(("You set the shop's Adyen HMAC Key.", "success"))

        # Handle maintenance settings form
        if form_section == "maintenance-settings":
            if shop.maint_mode != maint_mode:
                shop.maint_mode = maint_mode
                request.session.flash(
                    (
                        f"You turned {'on' if maint_mode else 'off'} maintenance mode",
                        "success",
                    )
                )

        # Handle comment system settings only if comment form was submitted
        if form_section == "comment-settings":
            if shop.comments_enabled != comments_enabled:
                shop.comments_enabled = comments_enabled
                status = "enabled" if comments_enabled else "disabled"
                request.session.flash(
                    (
                        f"Comments {status} for this shop",
                        "success",
                    )
                )

            if shop.comments_require_purchase != comments_require_purchase:
                shop.comments_require_purchase = comments_require_purchase
                status = "enabled" if comments_require_purchase else "disabled"
                request.session.flash(
                    (
                        f"Purchase requirement for comments {status}",
                        "success",
                    )
                )

            if shop.comments_require_approval != comments_require_approval:
                shop.comments_require_approval = comments_require_approval
                status = "enabled" if comments_require_approval else "disabled"
                request.session.flash(
                    (
                        f"Comment approval requirement {status}",
                        "success",
                    )
                )

        # Handle crypto settings only if crypto form was submitted
        if form_section == "crypto-settings":
            try:
                seconds = int(crypto_quote_expiry_seconds)
                if seconds != shop.crypto_quote_expiry_seconds:
                    if 300 <= seconds <= 7200:
                        shop.crypto_quote_expiry_seconds = seconds
                        request.session.flash(
                            (
                                f"Cryptocurrency quote expiry set to {seconds} seconds",
                                "success",
                            )
                        )
                    else:
                        request.session.flash(
                            (
                                "Quote expiry must be between 300 and 7200 seconds",
                                "error",
                            )
                        )
            except (ValueError, TypeError):
                request.session.flash(("Invalid quote expiry time", "error"))

            # Handle payment risk thresholds
            if payment_risk_threshold_mid_dollars is not None:
                try:
                    dollars = float(payment_risk_threshold_mid_dollars)
                    cents = dollars_to_cents(dollars)
                    if 100 <= cents <= 100000:
                        if cents != shop.payment_risk_threshold_mid_cents:
                            shop.payment_risk_threshold_mid_cents = cents
                            request.session.flash(
                                (
                                    f"Medium risk threshold set to ${dollars:.2f}",
                                    "success",
                                )
                            )
                    else:
                        request.session.flash(
                            (
                                "Medium risk threshold must be between $1 and $1000",
                                "error",
                            )
                        )
                except (ValueError, TypeError):
                    request.session.flash(("Invalid medium risk threshold", "error"))

            if payment_risk_threshold_high_dollars is not None:
                try:
                    dollars = float(payment_risk_threshold_high_dollars)
                    cents = dollars_to_cents(dollars)
                    if 1000 <= cents <= 1000000:
                        if cents != shop.payment_risk_threshold_high_cents:
                            shop.payment_risk_threshold_high_cents = cents
                            request.session.flash(
                                (
                                    f"High risk threshold set to ${dollars:.2f}",
                                    "success",
                                )
                            )
                    else:
                        request.session.flash(
                            (
                                "High risk threshold must be between $10 and $10000",
                                "error",
                            )
                        )
                except (ValueError, TypeError):
                    request.session.flash(("Invalid high risk threshold", "error"))

    # If we processed any form submission, redirect to prevent re-submission
    if form_section:
        return HTTPFound(f"/s/{shop.id}/settings")

    # TODO: Dry out this block, it's a copy pasta from views/product.py
    if s3_webhook_key and s3_webhook_bucket and s3_webhook_etag:
        # Check if the file exists and has a non-zero size
        try:
            response = request.secure_uploads_client.head_object(
                Bucket=s3_webhook_bucket,
                Key=s3_webhook_key,
            )
            file_size = response.get("ContentLength", 0)
            if file_size == 0:
                raise ValueError("File size is zero")
        except Exception:
            request.session.flash(
                ("File upload failed. Pick a file and try again.", "error")
            )
            return HTTPFound(request.route_url("shop_settings", shop_id=shop.id))

        # get file_from S3 service posted params.
        file_key = s3_webhook_key.split("/")[-1].split(".")[0]

        acl = "public-read"

        # don't allow proxies to cache and set the max age to 2 days.
        cache_control = "private, max-age=172800"

        # determine content type from extension.
        file_ext = s3_webhook_key.split(".")[-1]
        # print(file_ext)
        content_type = mimetypes.types_map.get("." + file_ext)
        # print(content_type)

        # copy upload to our system defined s3 location.
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Client.copy_object
        request.secure_uploads_client.copy_object(
            ACL=acl,
            Bucket=request.app["bucket.secure_uploads"],
            CopySource={
                "Bucket": s3_webhook_bucket,
                "Key": s3_webhook_key,
            },
            ContentDisposition=f"inline; filename={file_key}",
            ContentType=content_type,
            CacheControl=cache_control,
            Key=f"{shop.id}/meta/{file_key}",
            MetadataDirective="REPLACE",
        )

        # delete original upload key.
        request.secure_uploads_client.delete_object(
            Bucket=s3_webhook_bucket,
            Key=s3_webhook_key,
        )

        if file_key == "shop-favicon":
            shop.favicon = True

        if file_key == "shop-logo-banner":
            shop.logo_banner = True

        shop.stamp_updated_timestamp()

        # redirect back to this page to clear
        # the params posted by the s3 webhooks.
        return HTTPFound(f"/s/{shop.id}/settings?uploaded={file_key}")

    signed_posts = {}
    get_endpoints = {}

    for file_key in ["shop-logo-banner", "shop-logo-avatar", "shop-favicon"]:
        # conditionally sign the ability to POST to the object path when the
        # object path start's with the shop's s3 namespace (uuid) and only for
        # particular file keys. This prevents a user from writing files into
        # a shops namespace which is owned by a different user.
        key_starts_with = f"{shop.id}/meta/{file_key}.$filename"
        conditions = [
            {"success_action_redirect": shop.absolute_settings_url(request)},
            ["starts-with", "$key", key_starts_with],
        ]

        signed_posts[file_key] = request.secure_uploads_client.generate_presigned_post(
            Bucket=request.app["bucket.secure_uploads"],
            # uploads to /<shop-uuid>/meta/shop-logo-banner.the-users-file.png
            Key=key_starts_with + "${filename}",
            ExpiresIn=900,
            Conditions=conditions,
        )
        get_endpoints[file_key] = "{}/{}/meta/{}".format(
            request.app["bucket.secure_uploads.get_endpoint"],
            shop.id,
            file_key,
        )

        # We must create a field key/value for each extra condition.
        # unfortunately `conditions` is a list of single key/value dicts
        # and/or 2/3 item lists so we flatten them into a single fields dict.
        # [{1:2}, [3,4]] -> {1:2, 3:4}
        for condition in conditions:
            if isinstance(condition, list):
                if len(condition) == 2:
                    # convert list into dict.
                    condition = {condition[0]: condition[1]}
                else:
                    continue
            signed_posts[file_key]["fields"].update(condition)

    # Get crypto processor for Monero if enabled
    xmr_processor = None
    if request.monero_enabled:
        from ..models.crypto_processor import CryptoProcessor

        xmr_processor = (
            request.dbsession.query(CryptoProcessor)
            .filter(
                CryptoProcessor.shop_id == shop.id, CryptoProcessor.coin_type == "XMR"
            )
            .first()
        )

    # Get crypto processor for Dogecoin if enabled
    doge_processor = None
    if request.dogecoin_enabled:
        from ..models.crypto_processor import CryptoProcessor

        doge_processor = (
            request.dbsession.query(CryptoProcessor)
            .filter(
                CryptoProcessor.shop_id == shop.id, CryptoProcessor.coin_type == "DOGE"
            )
            .first()
        )

    return {
        "name": shop.name,
        "description": shop.description,
        "billing_address": shop.billing_address,
        "phone_number": shop.phone_number,
        "domain_name": shop.domain_name or "",
        "ribbon_text": shop.ribbon_text or "",
        "ribbon_text_color": shop.ribbon_text_color or "",
        "ribbon_color_1": shop.ribbon_color_1 or "",
        "ribbon_color_2": shop.ribbon_color_2 or "",
        "default_theme": shop.default_theme,
        "google_analytics_id": shop.google_analytics_id or "",
        "plausible_domain_name": shop.plausible_domain_name or "",
        "stripe_public_api_key": shop.stripe_public_api_key or "",
        "stripe_secret_api_key": shop.stripe_secret_api_key or "",
        "paypal_client_id": shop.paypal_client_id or "",
        "paypal_secret": shop.paypal_secret or "",
        "adyen_api_key": shop.adyen_api_key or "",
        "adyen_merchant_account": shop.adyen_merchant_account or "",
        "adyen_client_key": shop.adyen_client_key or "",
        "adyen_hmac_key": shop.adyen_hmac_key or "",
        "adyen_enabled": shop.adyen_enabled,
        "crypto_quote_expiry_seconds": shop.crypto_quote_expiry_seconds,
        "payment_risk_threshold_mid_dollars": cents_to_dollars(
            shop.payment_risk_threshold_mid_cents
        ),
        "payment_risk_threshold_high_dollars": cents_to_dollars(
            shop.payment_risk_threshold_high_cents
        ),
        "xmr_processor": xmr_processor,
        "doge_processor": doge_processor,
        "signed_posts": signed_posts,
        "get_endpoints": get_endpoints,
    }
