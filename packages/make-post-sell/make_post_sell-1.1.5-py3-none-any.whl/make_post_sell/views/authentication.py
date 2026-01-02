import re

from pyramid.view import view_config

from pyramid.httpexceptions import HTTPFound

from ..models.user import get_or_create_user_by_email

from ..lib.mail import send_verification_digits_to_email

from . import get_referer_or_home

from urllib.parse import urlencode

import logging

log = logging.getLogger(__name__)


@view_config(route_name="log-out")
def log_out(request):
    """log out the user, redirect to back to referer."""
    request.session["authenticated_user_id"] = None
    request.session["active_cart_id"] = None
    return HTTPFound("/")


@view_config(route_name="join-or-log-in", renderer="join-or-log-in.j2")
def join_or_log_in(request):
    """
    This view handles user registration, verification, and log in.
    It uses "password-less" authentication by sending 6 digit
    OTP (one-time-password) tokens to email addresses to verify both the email
    address & to authenticate the device displaying the challenge input field.
    """
    _email_regex = re.compile("^[^@]+@[^@]+\.[^.@]+$")
    raw_otp = request.params.get("raw-otp", "")
    email = request.params.get("email", "")

    if email and _email_regex.match(email) is None:
        email = ""
        request.session.flash(("That email address is invalid.", "error"))

    if request.spam:
        return request.spam

    if request.user and request.user.authenticated:
        request.session.flash(("You are already authenticated!", "info"))
        return HTTPFound(get_referer_or_home(request))

    elif email:
        user = get_or_create_user_by_email(request.dbsession, email)

        if user.throttle_password():
            msg = (
                f"Check email for a 6 digit verification code to log in. {user.email}",
                "info",
            )
        else:
            raw_otp = user.new_password()
            request.dbsession.add(user)
            request.dbsession.flush()
            send_verification_digits_to_email(request, user.email, raw_otp)
            msg = (
                f"Check email for a 6 digit verification code to log in. {user.email}",
                "info",
            )

        request.session.flash(msg)

        # Store 'unauthed_email' in session instead of passing via query param
        request.session["unauthed_email"] = email

        # Redirect to verification challenge without 'unauthed_email' in query
        return HTTPFound("/verification-challenge")

    return {
        "title": "Join or Log In",
    }


@view_config(route_name="verification-challenge", renderer="verification-challenge.j2")
def verification_challenge(request):
    # Retrieve 'unauthed_email' from the session
    unauthed_email = request.session.get("unauthed_email", "")

    if not unauthed_email:
        # If 'unauthed_email' is not in session, redirect to login/join
        request.session.flash(("Email is required for verification.", "error"))
        return HTTPFound("/join-or-log-in")

    user = get_or_create_user_by_email(request.dbsession, unauthed_email)

    if "submit" in request.params:
        raw_otp = request.params.get("raw-otp", "")
        if raw_otp and user.check_password(raw_otp):
            user.verified = True
            name = user.full_name or ""
            msg = (f"Welcome {name}", "success")
            _ = request.session.pop("unauthed_email", None)
            request.session["authenticated_user_id"] = str(user.id)
            request.session.flash(msg)

            # Merge carts
            request.active_cart.merge_in_cart(request.session_cart)
            request.dbsession.delete(request.session_cart)
            request.session["active_cart_id"] = str(request.active_cart.id)
            request.dbsession.add(user)
            request.dbsession.add(request.active_cart)
            request.dbsession.flush()

            return HTTPFound(
                "/cart" if request.active_cart.count > 0 else request.route_url("home")
            )

        else:
            msg = ("Invalid Verification Code", "error")
            request.session.flash(msg)

    return {
        "title": "Please Enter Verification Code",
        "raw_otp": request.params.get("raw-otp", ""),
    }
