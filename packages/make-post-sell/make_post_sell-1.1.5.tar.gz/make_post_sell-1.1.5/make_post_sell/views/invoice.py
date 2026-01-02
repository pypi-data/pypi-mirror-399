from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from ..models.invoice import get_invoice_by_id

from . import user_required, get_referer_or_home


@view_config(route_name="view_invoice", renderer="invoice.j2")
@view_config(route_name="view_invoice2", renderer="invoice.j2")
@user_required()
def view_invoice(request):
    invoice_id = request.matchdict.get("invoice_id")
    invoice = get_invoice_by_id(request.dbsession, invoice_id)

    if invoice is None:
        request.session.flash(("Invoice not found.", "error"))
        return HTTPFound(get_referer_or_home(request))

    # check if the user is the owner of the invoice or a shop editor.
    if request.user != invoice.user and not request.user.can_edit_shop(invoice.shop):
        request.session.flash(
            ("You do not have permission to view this invoice.", "error")
        )
        return HTTPFound(get_referer_or_home(request))

    return {
        "invoice": invoice,
    }
