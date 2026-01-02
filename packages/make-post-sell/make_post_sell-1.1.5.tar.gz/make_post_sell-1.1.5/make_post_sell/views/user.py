from pyramid.view import view_config

from pyramid.httpexceptions import HTTPFound

from . import user_required, shop_is_ready_required

from ..models.user import is_user_name_available, is_user_name_valid

from ..models.invoice import Invoice


@view_config(route_name="user_shops", renderer="shops.j2")
@user_required()
def user_shops(request):
    return {
        "the_title": "My Shops",
    }


@view_config(route_name="user_purchases", renderer="user_purchases.j2")
@user_required()
@shop_is_ready_required()
def user_purchases(request):
    user = request.user
    shop = request.shop  # Get the current shop from the request

    products = [p for p in request.user.products if p.shop == shop]

    invoices = (
        user.invoices.filter(Invoice.shop == shop)
        .order_by(Invoice.created_timestamp.desc())
        .all()
    )

    return {
        "products": products,
        "invoices": invoices,
        "the_title": "My Purchases",
    }


@view_config(route_name="user_settings", renderer="user_settings.j2")
@user_required(
    flash_msg="To view your settings, please verify your email address below.",
    flash_level="info",
    redirect_to_route_name="join-or-log-in",
)
def user_settings(request):
    user = request.user

    name = request.params.get("name", user.name).strip()
    full_name = request.params.get("full_name", user.full_name or "").strip()
    theme_id = request.params.get("theme_id", user.theme_id)

    if name and name != user.name:
        if not is_user_name_valid(name):
            msg = (
                "Sorry your display name is invalid. Please try again with only letters, numbers, spaces, dashes, and periods.",
                "error",
            )
            name = user.name
        elif not is_user_name_available(request.dbsession, name):
            msg = (
                "Sorry that display name is already taken. Please try again.",
                "error",
            )
            name = user.name
        else:
            user.name = name
            msg = ("You set your public display name.", "success")
        request.session.flash(msg)

    if full_name and full_name != user.full_name:
        user.full_name = full_name
        msg = ("You set your private full name.", "success")
        request.session.flash(msg)

    # Handle theme preference changes
    if theme_id and int(theme_id) != user.theme_id:
        user.theme_id = int(theme_id)
        theme_name = "Dark Mode" if int(theme_id) == 0 else "Light Mode"
        msg = (f"Theme preference set to {theme_name}.", "success")
        request.session.flash(msg)

    return {
        "name": name,
        "full_name": full_name,
        "theme_id": user.theme_id,
    }


@view_config(route_name="user_addresses", renderer="user_addresses.j2")
@user_required()
def user_addresses(request):
    return {}


@view_config(route_name="user_address_save")
@user_required()
def user_address_save(request):
    new_address = request.params.get("new_address", None)
    if new_address:
        user_address = request.user.new_address(new_address)
        request.dbsession.add(user_address)
        request.dbsession.flush()
        msg = ("You saved that address.", "success")
        request.session.flash(msg)

    return HTTPFound("/u/addresses")


@view_config(route_name="user_address_delete")
@user_required()
def user_address_delete(request):
    address_id = request.matchdict.get("address_id")

    if request.user.active_address.uuid_str == address_id:
        msg = ("You may not delete the active address.", "error")
        request.session.flash(msg)

    else:
        for address in request.user.addresses:
            if address.uuid_str == address_id:
                request.dbsession.delete(address)
                request.dbsession.flush()
                msg = ("You deleted that address.", "success")
                request.session.flash(msg)

    return HTTPFound("/u/addresses")


@view_config(route_name="user_address_activate")
@user_required()
def user_address_activate(request):
    address_id = request.matchdict.get("address_id")

    for address in request.user.addresses:
        if address.uuid_str == address_id:
            request.user.active_address_id = address_id
            request.dbsession.add(request.user)
            request.dbsession.flush()
            msg = ("You activated that address.", "success")
            request.session.flash(msg)

    return HTTPFound("/u/addresses")
