from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

from ..models.crypto_processor import CryptoProcessor
from . import shop_owner_required


def validate_dogecoin_address(address):
    """Basic Dogecoin address validation."""
    if not address:
        return False
    # Dogecoin addresses start with 'D' and are typically 34 characters long
    if not address.startswith("D") or len(address) != 34:
        return False
    # Basic character set validation (base58)
    valid_chars = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
    return all(c in valid_chars for c in address)


@view_config(route_name="crypto_processor_settings", request_method="POST")
@shop_owner_required()
def crypto_processor_settings(request):
    """Handle crypto processor configuration for a specific coin type."""
    shop = request.shop
    coin_type = request.matchdict.get("coin_type", "").upper()

    # Validate coin type
    if coin_type not in ["XMR", "DOGE", "LTC", "BTC", "BCH"]:
        request.session.flash(("Invalid cryptocurrency type", "error"))
        return HTTPFound(f"/s/{shop.id}/settings")

    # Get or create processor
    processor = (
        request.dbsession.query(CryptoProcessor)
        .filter(
            CryptoProcessor.shop_id == shop.id, CryptoProcessor.coin_type == coin_type
        )
        .first()
    )

    # Handle disable action
    if request.params.get("disable"):
        if processor:
            processor.enabled = False
            # Keep the sweep address but it will be grayed out in UI
            request.dbsession.add(processor)
            request.session.flash((f"{coin_type} payments disabled", "success"))
        return HTTPFound(f"/s/{shop.id}/settings")

    # Get sweep address
    sweep_to_address = request.params.get("sweep_to_address", "").strip()

    # Check if processor exists with a sweep address already set
    if processor and processor.sweep_to_address and not sweep_to_address:
        request.session.flash(
            (
                f"Cannot remove {coin_type} cold wallet address. You can only replace it with a new address or disable {coin_type} payments.",
                "error",
            )
        )
        return HTTPFound(f"/s/{shop.id}/settings")

    if not sweep_to_address:
        request.session.flash(("Cold wallet address is required", "error"))
        return HTTPFound(f"/s/{shop.id}/settings")

    # Validate address based on coin type
    if coin_type == "XMR":
        from ..lib.monero_address import validate_monero_address

        is_valid, error_msg = validate_monero_address(sweep_to_address)
        if not is_valid:
            request.session.flash((f"Invalid Monero address: {error_msg}", "error"))
            return HTTPFound(f"/s/{shop.id}/settings")
    elif coin_type == "DOGE":
        is_valid = validate_dogecoin_address(sweep_to_address)
        if not is_valid:
            request.session.flash(("Invalid Dogecoin address format", "error"))
            return HTTPFound(f"/s/{shop.id}/settings")
    # TODO: Add validation for other coin types

    if processor:
        # Update existing
        processor.sweep_to_address = sweep_to_address
        processor.enabled = True
        request.session.flash((f"{coin_type} settings updated", "success"))
    else:
        # Create new processor
        processor = CryptoProcessor(
            shop_id=shop.id, coin_type=coin_type, sweep_to_address=sweep_to_address
        )

        # Assign wallet label based on coin type
        if coin_type == "XMR":
            # Create new Monero account via RPC
            try:
                from ..lib.crypto_watcher.crypto_clients import get_client_from_settings

                client = get_client_from_settings(request.registry.settings)

                # Create new account with shop UUID as label
                account_label = f"mps-shop-{shop.uuid_str}"
                result = client._call("create_account", {"label": account_label})
                account_index = result.get("account_index")

                if account_index is not None:
                    processor.wallet_label = str(account_index)

                    # Tag the account with the shop name for easier identification
                    try:
                        client._call(
                            "tag_accounts",
                            {"tag": shop.name, "accounts": [account_index]},
                        )
                    except Exception as tag_error:
                        # Don't fail account creation if tagging fails
                        pass
                else:
                    raise Exception("Failed to get account_index from create_account")

            except Exception as e:
                request.session.flash(
                    (f"Failed to create Monero account: {str(e)}", "error")
                )
                return HTTPFound(f"/s/{shop.id}/settings")
        else:
            # For Bitcoin-like coins, use shop UUID as label base
            processor.wallet_label = f"shop_{shop.id}_{coin_type.lower()}"

        processor.enabled = True
        request.dbsession.add(processor)
        request.session.flash((f"{coin_type} payments enabled", "success"))

    request.dbsession.flush()
    return HTTPFound(f"/s/{shop.id}/settings")
