from pyramid.httpexceptions import HTTPFound


def get_referer_or_home(request):
    """return referer or or '/'"""
    return request.referer if request.referer is not None else "/"


# view decorator.
def user_required(
    flash_msg="You must log in to access that area.",
    flash_level="error",
    redirect_to_route_name="",
    max_redirects=3,  # Limit the number of redirects
):
    """This view requires that the request has a user."""

    def wrapped(fn):
        def inner(request):
            if request.user and request.user.authenticated:
                # Reset redirect count on successful authentication
                request.session.pop("redirect_count", None)
                return fn(request)
            # Track redirection attempts
            redirect_count = request.session.get("redirect_count", 0)
            if redirect_count >= max_redirects:
                # Redirect to a safe default page if max redirects reached
                request.session.flash(
                    ("Too many redirects, please try again later.", "error")
                )
                return HTTPFound(request.route_url("home"))
            # Increment redirect count
            request.session["redirect_count"] = redirect_count + 1
            # Flash message
            request.session.flash((flash_msg, flash_level))
            # Redirect to the login route
            if redirect_to_route_name:
                return HTTPFound(request.route_url(redirect_to_route_name))
            return HTTPFound(get_referer_or_home(request))

        return inner

    return wrapped


# view decorator.
def shop_is_ready_required(
    flash_msg="Sorry, this shop is not ready to make sales yet. Please try again later.",
    flash_level="error",
):
    """This view requires that the request has a shop and that shop is_ready_for_payment."""

    def wrapped(fn):
        def inner(request):
            if request.shop and request.shop.is_ready_for_payment(request):
                return fn(request)
            request.session.flash((flash_msg, flash_level))
            return HTTPFound(get_referer_or_home(request))

        return inner

    return wrapped


# view decorator.
def shop_owner_required(
    flash_msg="You must have a shop owner role to access that.",
    flash_level="error",
):
    """This view requires that the user of the request has a shop owner role.
    for protecting shop settings & shop user pages."""

    def wrapped(fn):
        def inner(request):
            if (
                request.user is not None
                and request.user.authenticated
                and request.shop is not None
                and request.user in request.shop.owners
            ):
                return fn(request)

            request.session.flash((flash_msg, flash_level))
            return HTTPFound(get_referer_or_home(request))

        return inner

    return wrapped


# view decorator.
def shop_editor_required(
    flash_msg="You must have a shop editor role to access that.",
    flash_level="error",
):
    """This view requires that the user of the request has a shop editor role.
    for protecting product & content edit pages."""

    def wrapped(fn):
        def inner(request):
            if (
                request.user is not None
                and request.user.authenticated
                and request.shop is not None
                and request.user in request.shop.editors
            ):
                return fn(request)

            request.session.flash((flash_msg, flash_level))
            return HTTPFound(get_referer_or_home(request))

        return inner

    return wrapped
