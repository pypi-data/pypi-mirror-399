from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

from ..models.user_crypto_refund_address import (
    UserCryptoRefundAddress,
    get_user_crypto_refund_address,
)
from ..models.meta import now_timestamp
from . import user_required


def get_enabled_coins(request):
    """Get list of enabled cryptocurrency types from all shops."""
    from ..models.crypto_processor import CryptoProcessor

    # Get distinct coin types from all enabled crypto processors
    enabled_coins = (
        request.dbsession.query(CryptoProcessor.coin_type)
        .filter(CryptoProcessor.enabled == True)
        .distinct()
        .all()
    )

    # Return list of coin type strings
    return [coin_type for (coin_type,) in enabled_coins]


@view_config(
    route_name="user_crypto_settings",
    request_method="GET",
    renderer="user_crypto_settings.j2",
)
@user_required()
def user_crypto_settings_view(request):
    """Display crypto payment preferences."""
    user = request.user
    enabled_coins = get_enabled_coins(request)

    # Get all user's crypto addresses for current shop
    addresses = {}
    for coin in enabled_coins:
        addr = get_user_crypto_refund_address(
            request.dbsession, user, request.shop, coin
        )
        if addr:
            addresses[coin] = addr

    return {
        "enabled_coins": enabled_coins,
        "addresses": addresses,
    }


@view_config(route_name="user_crypto_settings_update", request_method="POST")
@user_required()
def user_crypto_settings_update(request):
    """Update crypto refund address for a specific coin."""
    user = request.user
    coin_type = request.matchdict.get("coin_type", "").upper()

    # Validate coin type
    enabled_coins = get_enabled_coins(request)
    if coin_type not in enabled_coins:
        request.session.flash(("Invalid or disabled cryptocurrency type", "error"))
        return HTTPFound("/u/settings/crypto")

    # Get form data
    address = request.params.get("address", "").strip()
    label = request.params.get("label", "").strip()

    if not address:
        # If address is empty, treat it as a delete
        addr = get_user_crypto_refund_address(
            request.dbsession, user, request.shop, coin_type
        )
        if addr:
            request.dbsession.delete(addr)
            request.session.flash((f"{coin_type} refund address cleared", "success"))
        return HTTPFound("/u/settings/crypto")

    # TODO: Add address validation for each coin type
    # For now, just basic length check
    if len(address) < 10 or len(address) > 256:
        request.session.flash(("Invalid address format", "error"))
        return HTTPFound("/u/settings/crypto")

    # Get existing or create new
    addr_obj = get_user_crypto_refund_address(
        request.dbsession, user, request.shop, coin_type
    )

    if addr_obj:
        # Update existing
        addr_obj.address = address
        addr_obj.label = label if label else None
        addr_obj.updated_timestamp = now_timestamp()
        request.session.flash((f"{coin_type} refund address updated", "success"))
    else:
        # Create new
        addr_obj = UserCryptoRefundAddress(
            user=user,
            shop=request.shop,
            coin_type=coin_type,
            address=address,
            label=label if label else None,
        )
        request.dbsession.add(addr_obj)
        request.session.flash((f"{coin_type} refund address saved", "success"))

    request.dbsession.flush()
    return HTTPFound("/u/settings/crypto")
