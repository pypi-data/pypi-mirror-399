from pyramid.view import view_config
from ..models.invoice import Invoice
from . import shop_editor_required
from sqlalchemy import desc


@view_config(route_name="shop_sales", renderer="sales.j2")
@shop_editor_required()
def shop_sales(request):
    shop = request.shop
    invoices = shop.invoices.order_by(desc(Invoice.created_timestamp)).all()
    return {"invoices": invoices, "shop": shop}
