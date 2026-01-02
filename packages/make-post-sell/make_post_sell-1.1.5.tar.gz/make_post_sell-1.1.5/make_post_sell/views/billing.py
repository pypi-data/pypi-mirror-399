from pyramid.view import view_config

from pyramid.httpexceptions import HTTPFound, HTTPBadRequest

from . import (
    user_required,
    shop_is_ready_required,
    get_referer_or_home,
)


@view_config(route_name="billing", renderer="billing.j2")
@user_required(
    flash_msg="Verify your email to access Payment Preferences.",
    flash_level="info",
    redirect_to_route_name="join-or-log-in",
)
@shop_is_ready_required()
def billing(request):
    # Check if shop exists and has Stripe configured
    if request.shop is None or request.shop.stripe is None:
        request.session.flash(("This shop doesn't accept credit cards yet.", "info"))
        return HTTPFound(get_referer_or_home(request))

    stripe_user_shop = request.shop.stripe_user_shop(request.user)

    if stripe_user_shop is None:
        # create a record for this user for holding stripe billing data.
        request.shop.stripe_customer(request.user, create=True)
        stripe_user_shop = request.shop.stripe_user_shop(request.user)

    cards = saved_cards = stripe_user_shop.stripe_cards
    active_card = stripe_user_shop.active_card

    if active_card is not None:
        for i, card in enumerate(saved_cards):
            if card.id == active_card.id:
                del cards[i]

    setup_intent = request.shop.stripe.SetupIntent.create(
        payment_method_types=["card"], customer=stripe_user_shop.cus_id
    )

    # Get PayPal saved payment method if exists
    paypal_user_shop = None
    if request.shop.is_paypal_ready:
        paypal_user_shop = request.shop.paypal_user_shop(request.user)

    return {
        "client_secret": setup_intent.client_secret,
        "cards": cards,
        "active_card": active_card,
        "paypal_user_shop": paypal_user_shop,
        "paypal_enabled": request.paypal_enabled if hasattr(request, 'paypal_enabled') else False,
    }


@view_config(route_name="add-card")
@user_required()
@shop_is_ready_required()
def add_card(request):
    # Check if shop has Stripe configured
    if request.shop.stripe is None:
        request.session.flash(("This shop doesn't accept credit cards yet.", "info"))
        return HTTPFound(get_referer_or_home(request))

    stripe_setup_intent = request.params.get("setup_intent")
    stripe_setup_intent_client_secret = request.params.get("setup_intent_client_secret")

    stripe_user_shop = request.shop.stripe_user_shop(request.user)

    if stripe_setup_intent:
        setup_intent = request.shop.stripe.SetupIntent.retrieve(
            stripe_setup_intent,
        )

        card_ids = stripe_user_shop.stripe_card_ids

        if len(card_ids) == 1:
            stripe_user_shop.active_card_id = card_ids[0]
            request.dbsession.add(stripe_user_shop)
            request.dbsession.flush()

        request.session.flash(("You saved a new card. {}", "success"))

    return HTTPFound("/billing")


@view_config(route_name="confirm-update-card", renderer="update-card.j2")
@user_required()
@shop_is_ready_required()
def confirm_update_card(request):
    card_id = request.matchdict.get("card_id")
    stripe_user_shop = request.shop.stripe_user_shop(request.user)
    card = stripe_user_shop.get_card_by_id(card_id)
    action = request.matchdict.get("action")
    action_human = action.replace("-", " ")
    return {
        "card": card,
        "card_id": card_id,
        "action": action,
        "action_human": action_human,
        "the_title": action_human.title(),
    }


@view_config(route_name="update-card")
@user_required()
@shop_is_ready_required()
def update_card(request):
    # Check if shop has Stripe configured
    if request.shop.stripe is None:
        request.session.flash(("This shop doesn't accept credit cards yet.", "info"))
        return HTTPFound(get_referer_or_home(request))

    action = request.params.get("action", None)
    card_id = request.params.get("card_id")
    stripe_user_shop = request.shop.stripe_user_shop(request.user)
    card = stripe_user_shop.get_card_by_id(card_id)

    if card_id == stripe_user_shop.active_card_id:
        request.session.flash(("Cannot update an active card.", "error"))
        return HTTPFound("/billing")

    if card_id not in stripe_user_shop.stripe_card_ids:
        request.session.flash(("Cannot update a card you do not own.", "error"))
        return HTTPFound("/billing")

    if action not in ["make-card-active", "delete-card"]:
        return HTTPBadRequest
    if "delete-card" == action:
        request.shop.stripe.PaymentMethod.detach(card_id)
        request.session.flash(("You deleted that card.", "success"))
    if "make-card-active" == action:
        stripe_user_shop.active_card_id = card_id
        request.dbsession.add(stripe_user_shop)
        request.dbsession.flush()
        request.session.flash(("You set the active card.", "success"))
    return HTTPFound("/billing")


@view_config(route_name="disconnect-paypal")
@user_required()
@shop_is_ready_required()
def disconnect_paypal(request):
    """Disconnect (remove) saved PayPal payment method."""
    # Check if shop has PayPal configured
    if not request.shop.is_paypal_ready:
        request.session.flash(("PayPal is not configured for this shop.", "error"))
        return HTTPFound("/billing")

    paypal_user_shop = request.shop.paypal_user_shop(request.user)

    if paypal_user_shop is None:
        request.session.flash(("No PayPal account connected.", "info"))
        return HTTPFound("/billing")

    # Clear saved payment token and payer ID
    paypal_user_shop.active_payment_token = None
    paypal_user_shop.payer_id = None
    paypal_user_shop.billing_agreement_id = None

    request.dbsession.add(paypal_user_shop)
    request.dbsession.flush()

    request.session.flash(("PayPal account disconnected successfully.", "success"))
    return HTTPFound("/billing")
