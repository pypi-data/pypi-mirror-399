from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

from . import shop_owner_required
from ..models.shop import get_shop_by_id
from ..models.shop_location import ShopLocation

from ..lib.currency import validate_float


def checkbox_to_bool(checkbox):
    return checkbox == "on"


def bool_to_checkbox(boolean):
    return "on" if boolean else "off"


@view_config(route_name="shop_location_new", renderer="shop_location_form.j2")
@view_config(route_name="shop_location_edit", renderer="shop_location_form.j2")
@shop_owner_required()
def shop_location_form(request):
    shop = request.shop
    location_id = request.matchdict.get("location_id")
    shop_location = None

    if location_id:
        shop_location = (
            request.dbsession.query(ShopLocation)
            .filter_by(id=location_id, shop_id=shop.id)
            .one_or_none()
        )
        if not shop_location:
            request.session.flash(("Shop location not found.", "error"))
            return HTTPFound(
                location=request.route_url("shop_locations", shop_id=shop.id)
            )

    if request.method == "POST":
        name = request.params.get("name", "").strip()
        address = request.params.get("address", "").strip()
        city = request.params.get("city", "").strip()
        state = request.params.get("state", "").strip()
        country = request.params.get("country", "").strip()
        postal_code = request.params.get("postal_code", "").strip()
        days_open = request.params.get("days_open", "").strip()
        hours_open = request.params.get("hours_open", "").strip()
        local_pickup = checkbox_to_bool(request.params.get("local_pickup", "off"))
        local_delivery = checkbox_to_bool(request.params.get("local_delivery", "off"))
        local_delivery_rate = request.params.get("local_delivery_rate", "0.00")
        local_shipping = checkbox_to_bool(request.params.get("local_shipping", "off"))
        local_shipping_rate = request.params.get("local_shipping_rate", "0.00")
        international_shipping = checkbox_to_bool(
            request.params.get("international_shipping", "off")
        )
        international_shipping_rate = request.params.get(
            "international_shipping_rate", "0.00"
        )

        # Convert numeric fields to appropriate types for validation
        try:
            local_delivery_rate = validate_float(local_delivery_rate)
            local_shipping_rate = validate_float(local_shipping_rate)
            international_shipping_rate = validate_float(international_shipping_rate)
        except Exception as e:
            request.session.flash((f"Invalid input for numeric fields. {e}", "error"))
            return request.params

        # Check for negative values
        if (
            local_delivery_rate < 0
            or local_shipping_rate < 0
            or international_shipping_rate < 0
        ):
            request.session.flash(("Numeric fields must not be negative.", "error"))
        # Check for required text fields
        elif (
            not name
            or not address
            or not city
            or not state
            or not country
            or not postal_code
            or not days_open
            or not hours_open
        ):
            request.session.flash(("Please submit all required fields.", "error"))
        else:
            if not shop_location:
                shop_location = ShopLocation(
                    shop=shop,
                    name=name,
                    address=address,
                    city=city,
                    state=state,
                    country=country,
                    postal_code=postal_code,
                )
                request.session.flash(
                    ("Shop location created successfully.", "success")
                )
            else:
                shop_location.name = name
                shop_location.address = address
                shop_location.city = city
                shop_location.state = state
                shop_location.country = country
                shop_location.postal_code = postal_code
                request.session.flash(
                    ("Shop location updated successfully.", "success")
                )

            shop_location.days_open = days_open
            shop_location.hours_open = hours_open
            shop_location.local_pickup = local_pickup
            shop_location.local_delivery = local_delivery
            shop_location.local_delivery_rate = local_delivery_rate
            shop_location.local_shipping = local_shipping
            shop_location.local_shipping_rate = local_shipping_rate
            shop_location.international_shipping = international_shipping
            shop_location.international_shipping_rate = international_shipping_rate

            request.dbsession.add(shop_location)
            request.dbsession.flush()

            return HTTPFound(
                location=request.route_url("shop_locations", shop_id=shop.id)
            )

    if location_id:
        action_url = request.route_url(
            "shop_location_edit", shop_id=shop.id, location_id=location_id
        )
    else:
        action_url = request.route_url(
            "shop_location_new",
            shop_id=shop.id,
        )

    return {
        "action_url": action_url,
        "location_id": location_id,
        "name": shop_location.name if shop_location else "",
        "address": shop_location.address if shop_location else "",
        "city": shop_location.city if shop_location else "",
        "state": shop_location.state if shop_location else "",
        "country": shop_location.country if shop_location else "",
        "postal_code": shop_location.postal_code if shop_location else "",
        "days_open": shop_location.days_open if shop_location else "",
        "hours_open": shop_location.hours_open if shop_location else "",
        "local_pickup": shop_location.local_pickup if shop_location else False,
        "local_delivery": shop_location.local_delivery if shop_location else False,
        "local_delivery_rate": (
            shop_location.local_delivery_rate if shop_location else "0.00"
        ),
        "local_shipping": shop_location.local_shipping if shop_location else False,
        "local_shipping_rate": (
            shop_location.local_shipping_rate if shop_location else "0.00"
        ),
        "international_shipping": (
            shop_location.international_shipping if shop_location else False
        ),
        "international_shipping_rate": (
            shop_location.international_shipping_rate if shop_location else "0.00"
        ),
    }


@view_config(route_name="shop_locations", renderer="shop_locations.j2")
def shop_locations(request):
    return {
        "shop": request.shop,
        "locations": request.shop.shop_locations,
    }


@view_config(route_name="shop_location_switch")
def shop_location_switch(request):
    shop_id = request.shop.id
    location_id = request.matchdict.get("location_id")
    next_url = request.params.get("next", request.route_url("shop", shop_id=shop_id))

    # Fetch the location to ensure it exists and belongs to the shop
    location = (
        request.dbsession.query(ShopLocation)
        .filter_by(id=location_id, shop_id=shop_id)
        .first()
    )

    if not location:
        request.session.flash(
            ("Location not found or does not belong to this shop.", "error")
        )
        return HTTPFound(request.route_url("shop_locations"))

    # Update the session with the selected location
    request.session["shop_location_id"] = str(location.id)
    request.session.flash(
        (f"You are now viewing the {location.name} shop location", "success")
    )

    # Recalculate the handling cost based on the new location
    cart = request.active_cart
    cart.update_handling_cost(location)
    request.dbsession.add(cart)
    request.dbsession.flush()

    # Redirect to the next URL or the shop home page
    return HTTPFound(next_url)
