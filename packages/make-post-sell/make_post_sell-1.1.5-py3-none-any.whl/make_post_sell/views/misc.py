from sqlalchemy import text

from pyramid.view import view_config

from ..models.product import get_all_products

# needed for favicon
import os
from pyramid.response import (
    FileResponse,
    Response,
)

from make_post_sell.lib.render import markdown_to_html


DEFAULT_ROBOTS_DOT_TXT = """
User-agent: *
Disallow:
"""


@view_config(route_name="favicon")
def favicon_view(request):
    here = os.path.dirname(__file__)
    icon = os.path.join(here, "..", "static", "favicon.ico")
    return FileResponse(icon, request=request)


@view_config(route_name="robots")
def robots_view(request):
    """Load and return either default robots.txt or version from .ini"""
    response = Response(
        body=request.app.get("robots_dot_txt", DEFAULT_ROBOTS_DOT_TXT).lstrip()
    )
    response.content_type = "text/plain"
    return response


@view_config(route_name="ask-for-on-demand-tls", require_csrf=False)
def ask_for_on_demand_tls(request):
    """
    This implements Caddy ask protocol defined here:

    * https://caddyserver.com/docs/caddyfile/options#on-demand-tls

    Caddy will make an HTTP request to the given URL with a query string of ?domain= containing
    the value of the domain name. If the endpoint returns a 2xx status code, Caddy will be authorized
    to obtain a certificate for that name. Any other status code will result in cancelling issuance
    of the certificate.
    """
    domain_name_requesting_tls = request.params.get("domain")
    if domain_name_requesting_tls:
        query = text(
            "SELECT EXISTS (SELECT 1 FROM mps_shop WHERE domain_name = :domain_name)"
        )
        result = request.dbsession.execute(
            query, {"domain_name": domain_name_requesting_tls}
        )
        exists = result.scalar()
        if exists:
            return Response(status=200)
    return Response(status=401)


# I set require_csfr to false because new browsers
# don't save 3rd party cookies anymore.
# This ajax endpoint should work whether a user is authenticated or not.
@view_config(
    route_name="markup-editor-preview", renderer="string", xhr=True, require_csrf=False
)
def markup_editor_preview(request):
    """AJAJ: Accept Markup data param, return HTML"""
    return markdown_to_html(request.params["data"], request.shop)
    # currently only supports markdown, but eventually we could support others.
    # try:
    #    return markdown_to_html(request.params["data"], request.shop)
    # except:
    #    return "we could not create markdown to html preview."
