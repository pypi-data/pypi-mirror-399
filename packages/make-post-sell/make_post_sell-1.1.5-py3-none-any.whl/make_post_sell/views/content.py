from pyramid.view import view_config

from . import get_referer_or_home

from pyramid.httpexceptions import HTTPFound


@view_config(route_name="content", renderer="content.j2")
@view_config(route_name="content_slug", renderer="content.j2")
def content(request):
    product = request.product

    if not request.is_saas_domain and request.domain != request.shop.domain_name:
        # The content uuid in the URI matchdict is mismatched with request shop.
        request.session.flash(("Refusing to display another shop's content.", "error"))
        return HTTPFound(get_referer_or_home(request))

    if product.is_private:
        if request.user is None or request.user.can_not_edit_product(product):
            request.session.flash(("That content is private.", "error"))
            return HTTPFound(get_referer_or_home(request))

    if product.is_sellable:
        return HTTPFound(f"/p/{product.id}/{product.slug}")

    if "slug" not in request.matchdict:
        return HTTPFound(f"/c/{product.id}/{product.slug}")

    signed_get_object_url = None

    bucket_name = request.app["bucket.secure_uploads"]

    # Params: Bucket, IfMatch, IfModifiedSince, IfNoneMatch, IfUnmodifiedSince,
    # Key, Range, ResponseCacheControl, ResponseContentDisposition, ResponseProductEncoding,
    # ResponseContentLanguage, ResponseContentType, ResponseExpires, VersionId,
    # SSECustomerAlgorithm, SSECustomerKey, SSECustomerKeyMD5, RequestPayer, PartNumber

    params = {
        "Bucket": bucket_name,
        "Key": product.s3_key,
    }

    # The content disposition string determines whether this is:
    # * an inline image (thumbnails)
    # * an attachment (file download)
    content_disposition = product.get_content_disposition("content")

    # The content type string determines whether this is a pdf, zip, etc.
    content_type = product.get_content_type("content")

    if content_disposition:
        params["ResponseContentDisposition"] = content_disposition

    if content_type:
        params["ResponseContentType"] = content_type

    signed_get_object_url = request.secure_uploads_client.generate_presigned_url(
        ClientMethod="get_object",
        Params=params,
        # 15 minutes.
        ExpiresIn=900,
    )

    product_size = ""
    if product.has_product_file:
        product_size = product.human_product_file_bytes

    # Load comments for the content
    from ..models.comment import get_comments_for_product

    comments = get_comments_for_product(
        request.dbsession, product.id, shop=product.shop, user=request.user
    )

    return {
        "product": product,
        "product_size": product_size,
        "signed_get_object_url": signed_get_object_url,
        "comments": comments,
        "shop": product.shop,
    }
