from pyramid.view import view_config

from . import (
    shop_owner_required,
    get_referer_or_home,
)

from ..models.coupon import (
    Coupon,
    get_coupon_by_id,
)

from ..models.cart import get_cart_by_id

from pyramid.httpexceptions import HTTPFound

from datetime import datetime, timedelta


from ..lib.currency import (
    validate_int,
    validate_float,
)


# Define the maximum expiration date (10 years from now)
MAX_EXPIRATION_DATE = datetime.now() + timedelta(days=365 * 10)


def get_coupon_from_matchdict(request):
    """
    This function uses the coupon_id from the url path
    and returns a Coupon object from the database or None.
    """
    return get_coupon_by_id(request.dbsession, request.matchdict["coupon_id"])


@view_config(route_name="coupons", renderer="coupons.j2")
@shop_owner_required()
def coupons(request):
    return {"coupons": request.shop.coupons.all()}


@view_config(route_name="coupon1", renderer="coupon.j2")
@view_config(route_name="coupon2", renderer="coupon.j2")
def coupon(request):
    if not request.is_saas_domain and request.domain != request.shop.domain_name:
        # The coupond uuid in the URI matchdict is mismatched with request shop.
        request.session.flash(("Refusing to display another shop's coupons.", "error"))
        return HTTPFound(get_referer_or_home(request))

    coupon = get_coupon_from_matchdict(request)
    return {"coupon": coupon}


@view_config(route_name="coupon_new1", renderer="coupon_new.j2")
@view_config(route_name="coupon_new2", renderer="coupon_new.j2")
@shop_owner_required()
def coupon_new(request):
    code = request.params.get("code", "").strip()
    description = request.params.get("description", "").strip()
    action_type = request.params.get("action_type")
    action_value = request.params.get("action_value")
    max_redemptions = request.params.get("max_redemptions")
    max_redemptions_per_user = request.params.get("max_redemptions_per_user")
    expiration_date = request.params.get("expiration_date")
    cart_qualifier = request.params.get("cart_qualifier")

    if request.params:
        # Convert numeric fields to float or integers for validation.
        try:
            action_value = validate_float(action_value) if action_value else None
            max_redemptions = validate_int(max_redemptions) if max_redemptions else None
            max_redemptions_per_user = (
                validate_int(max_redemptions_per_user)
                if max_redemptions_per_user
                else None
            )
            cart_qualifier = validate_float(cart_qualifier) if cart_qualifier else None
        except Exception as e:
            request.session.flash((f"Invalid input for numeric fields. {e}", "error"))
            return request.params

        if expiration_date:
            expiration_datetime = datetime.strptime(expiration_date, "%Y-%m-%d")
            if expiration_datetime > MAX_EXPIRATION_DATE:
                request.session.flash(
                    (
                        f"Expiration date is too far in the future. The maximum allowed date is { MAX_EXPIRATION_DATE.strftime('%Y-%m-%d') }.",
                        "error",
                    )
                )
                return request.params

        # check for required fields.
        if not code or not description or not action_type or not action_value:
            request.session.flash(("Please submit all required fields.", "error"))

        # check for negative or zero values.
        elif (
            action_value <= 0
            or (max_redemptions is not None and max_redemptions <= 0)
            or (max_redemptions_per_user is not None and max_redemptions_per_user <= 0)
            or (cart_qualifier is not None and cart_qualifier <= 0)
        ):
            request.session.flash(
                ("Numeric fields must be greater than zero.", "error")
            )
        else:
            request.session.flash(("You created a new coupon!", "success"))
            coupon = Coupon(
                shop=request.shop,
                code=code,
                description=description,
                action_type=action_type,
                action_value=action_value,
                max_redemptions=max_redemptions,
                max_redemptions_per_user=max_redemptions_per_user,
                expiration_date=expiration_date,
                cart_qualifier=cart_qualifier,
            )
            request.dbsession.add(coupon)
            request.dbsession.flush()
            return HTTPFound(f"/s/{request.shop.id}/coupons")

    return request.params


@view_config(route_name="coupon_apply_to_cart", request_method="POST")
def coupon_apply_to_cart(request):
    coupon_id = request.params.get("coupon_id")

    coupon = get_coupon_by_id(request.dbsession, coupon_id)

    if coupon is None:
        msg = ("That coupon_id does not exist.", "error")
        request.session.flash(msg)
        return HTTPFound(f"/cart/{request.active_cart.id}")

    if coupon not in request.active_cart.coupons:
        msg = ("The coupon was applied to your cart.", "success")
        request.active_cart.coupons.append(coupon)
        # Clear cached discount calculations
        request.active_cart._bust_memoized_attributes()
        request.dbsession.add(request.active_cart)
        request.dbsession.flush()
    else:
        msg = ("The coupon was already applied to your cart.", "success")

    request.session.flash(msg)
    return HTTPFound(f"/cart/{request.active_cart.id}")


@view_config(route_name="coupon_remove_from_cart", request_method="POST")
def coupon_remove_from_cart(request):
    cart_id = request.params.get("cart_id")
    coupon_id = request.params.get("coupon_id")

    cart = get_cart_by_id(request.dbsession, cart_id)
    coupon = get_coupon_by_id(request.dbsession, coupon_id)

    if cart is None:
        msg = ("That cart_id does not exist.", "error")

    elif coupon is None:
        msg = ("That coupon_id does not exist.", "error")

    elif request.user and request.user.does_not_own_cart(cart):
        msg = ("You do not own that cart.", "error")

    elif request.user is None and cart.user is not None:
        msg = ("You do not own this cart.", "error")

    else:
        if coupon in cart.coupons:
            msg = ("The coupon was removed from your cart.", "success")
            cart.coupons.remove(coupon)
            # Clear cached discount calculations
            cart._bust_memoized_attributes()
            request.dbsession.add(cart)
            request.dbsession.flush()
        else:
            msg = ("The coupon was already removed from your cart.", "success")
        request.session.flash(msg)
        return HTTPFound(f"/cart/{cart_id}")

    request.session.flash(msg)
    return HTTPFound(get_referer_or_home(request))
