from pyramid.view import view_config

from pyramid.httpexceptions import HTTPFound

from . import (
    user_required,
    shop_editor_required,
    get_referer_or_home,
)

from ..models.product import Product
from ..models.shop_location import ShopLocation
from ..models.inventory import Inventory

from ..lib.currency import validate_float


def checkbox_to_bool(checkbox):
    return checkbox == "on"


@view_config(route_name="product", renderer="product.j2")
@view_config(route_name="product_slug", renderer="product.j2")
def product(request):
    product = request.product

    if not request.is_saas_domain and request.domain != request.shop.domain_name:
        # The product uuid in the URI matchdict is mismatched with request shop.
        request.session.flash(("Refusing to display another shop's product.", "error"))
        return HTTPFound(get_referer_or_home(request))

    if product.is_private:
        if request.user is None or request.user.can_not_edit_product(product):
            request.session.flash(("That product is private.", "error"))
            return HTTPFound(get_referer_or_home(request))

    if product.is_not_sellable:
        return HTTPFound(f"/c/{product.id}/{product.slug}")

    if "slug" not in request.matchdict:
        return HTTPFound(f"/p/{product.id}/{product.slug}")

    signed_get_object_url = None

    bucket_name = request.app["bucket.secure_uploads"]

    if (
        request.user
        and request.user.authenticated
        and request.user.can_download_product(product)
    ):
        # Params: Bucket, IfMatch, IfModifiedSince, IfNoneMatch, IfUnmodifiedSince,
        # Key, Range, ResponseCacheControl, ResponseContentDisposition, ResponseContentEncoding,
        # ResponseContentLanguage, ResponseContentType, ResponseExpires, VersionId,
        # SSECustomerAlgorithm, SSECustomerKey, SSECustomerKeyMD5, RequestPayer, PartNumber

        params = {
            "Bucket": bucket_name,
            "Key": product.s3_key,
        }

        # The content disposition string determines whether this is:
        # * an inline image (thumbnails)
        # * an attachment (file download)
        content_disposition = product.get_content_disposition("product")

        # The content type string determines whether this is a pdf, zip, etc.
        content_type = product.get_content_type("product")

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

    # Load comments for the product
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


@view_config(route_name="product_new", renderer="product_new.j2")
@view_config(route_name="content_new", renderer="content_new.j2")
@user_required()
@shop_editor_required()
def product_new(request):
    title = request.params.get("title", "").strip()
    description = request.params.get("description", "").strip()
    price = request.params.get("price", "").strip()

    is_bundle_checkbox = request.params.get("is_bundle", "off")
    is_bundle = checkbox_to_bool(is_bundle_checkbox)

    is_sellable_checkbox = request.params.get("is_sellable", "off")
    is_sellable = checkbox_to_bool(is_sellable_checkbox)

    is_physical = bool(request.params.get("is_physical", "false") == "true")

    if "submit" in request.params:
        # check for required fields.
        if not title or not description or (is_sellable and not price):
            msg = ("You must fill out all fields.", "error")
            request.session.flash(msg)
        else:
            # Validate price if the product is sellable
            price_error = False
            if is_sellable:
                try:
                    price = validate_float(price)
                except Exception as e:
                    price_error = True
                    msg = (f"Please enter a valid number for price. {e}", "error")
                    request.session.flash(msg)

            if not price_error:
                # prevent trying to create a bundle and also physical product.
                if is_bundle and is_physical:
                    msg = (
                        "The bundle feature only works with digital goods. Please uncheck the bundle option or mark the product as digital.",
                        "error",
                    )
                    request.session.flash(msg)
                else:
                    product = Product(title, description)
                    product.shop = request.shop
                    product.is_bundle = is_bundle
                    product.is_sellable = is_sellable
                    product.is_physical = is_physical

                    if product.error_message:
                        request.session.flash((product.error_message, "error"))
                    else:
                        if is_sellable and price:
                            product_price = product.set_price(price)
                            request.dbsession.add(product_price)

                        request.dbsession.add(product)
                        request.dbsession.flush()
                        msg = ("Great, next you may upload files.", "success")
                        request.session.flash(msg)
                        return HTTPFound(f"/p/{product.id}/edit")

    return {
        "title": title,
        "description": description,
        "price": price,
        "is_bundle": is_bundle,
        "is_physical": is_physical,
        "create_location_url": request.route_url(
            "shop_location_new", shop_id=request.shop.id
        ),
        "shop_has_locations": len(request.shop.shop_locations.all()) > 0,
    }


@view_config(route_name="product_description_edit", renderer="markup_editor.j2")
@view_config(route_name="content_description_edit", renderer="markup_editor.j2")
@shop_editor_required()
def product_edit_description(request):
    product = request.product

    raw_markup_data = request.params.get(
        "markup-editor-textarea",
        # TODO: rename this column to description_raw.
        product.description,
    ).strip()

    if raw_markup_data and raw_markup_data != product.description:
        product.set_description(raw_markup_data)
        msg = ("You set the Products's Description!", "success")
        request.session.flash(msg)
        request.dbsession.add(product)
        request.dbsession.flush()

    return {
        "markup_subject": f"Product Description for {product.title}",
        "markup_rendered": product.description_html,
        "markup_raw": product.description,
        "markup_form_path": f"{product.absolute_edit_url(request, subject='description')}",
    }


@view_config(route_name="product_edit", renderer="product_edit.j2")
@view_config(route_name="product_edit2", renderer="product_edit.j2")
@view_config(route_name="content_edit", renderer="product_edit.j2")
@view_config(route_name="content_edit2", renderer="product_edit.j2")
@shop_editor_required()
def product_edit(request):
    product_modified = False
    product = request.product

    title = request.params.get("title", product.title).strip()
    description = request.params.get("description", product.description).strip()
    price = request.params.get("price", product.price)
    visibility = int(request.params.get("visibility", product.visibility))
    uploaded_file_key = request.params.get("uploaded", "")

    if uploaded_file_key:
        request.session.flash(
            (
                f"You successfully uploaded a new {uploaded_file_key} file!",
                "success",
            )
        )

    try:
        price = validate_float(price)
    except Exception as e:
        request.session.flash((f"Invalid price. {e}", "error"))
        price = product.price

    s3_webhook_key = request.params.get("key")
    s3_webhook_bucket = request.params.get("bucket")
    s3_webhook_etag = request.params.get("etag")

    if title != product.title:
        product_modified = True
        product.title = title
        request.session.flash(("You updated the product's title.", "success"))

    if description != product.description:
        product_modified = True
        product.set_description(description)
        request.session.flash(("You updated the product's description.", "success"))

    if visibility != product.visibility:
        product_modified = True
        product.set_visibility(
            visibility,
            request.secure_uploads_client,
            request.app["bucket.secure_uploads"],
        )
        request.session.flash(("You updated the product's visibility.", "success"))

    if price != product.price:
        product_modified = True
        request.dbsession.add(product.set_price(price))
        request.session.flash(("You updated the product's price.", "success"))

    if s3_webhook_key and s3_webhook_bucket and s3_webhook_etag:
        # Check if the file exists and has a non-zero size
        try:
            response = request.secure_uploads_client.head_object(
                Bucket=s3_webhook_bucket,
                Key=s3_webhook_key,
            )
            file_size = response.get("ContentLength", 0)
            if file_size == 0:
                raise ValueError("File size is zero")
        except Exception:
            request.session.flash(
                ("File upload failed. Pick a file and try again.", "error")
            )
            return HTTPFound(request.route_url("product_edit", product_id=product.id))

        # Store the uploaded user's file_metadata in our database.
        file_key = product.store_file_metadata(s3_webhook_key)

        # This is how we protect our digital downloads while using the
        # same bucket for thumbnails and previews related to the product.
        # Use the new visibility-aware ACL method
        acl = product.get_s3_acl_for_file_key(file_key)
        if product.is_not_sellable:
            acl = "public-read"

        # don't allow proxies to cache and set the max age to 2 days.
        cache_control = "private, max-age=172800"

        # copy upload to our system defined s3 location.
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Client.copy_object
        request.secure_uploads_client.copy_object(
            ACL=acl,
            Bucket=request.app["bucket.secure_uploads"],
            CopySource={
                "Bucket": s3_webhook_bucket,
                "Key": s3_webhook_key,
            },
            ContentDisposition=product.get_content_disposition(file_key),
            ContentType=product.get_content_type(file_key),
            CacheControl=cache_control,
            Key=f"{product.s3_path}/{file_key}",
            MetadataDirective="REPLACE",
        )

        # delete original upload key.
        request.secure_uploads_client.delete_object(
            Bucket=s3_webhook_bucket,
            Key=s3_webhook_key,
        )

        # get file size & store in our database.
        response = request.secure_uploads_client.head_object(
            Bucket=request.app["bucket.secure_uploads"],
            Key=f"{product.s3_path}/{file_key}",
        )

        product_content_length = response["ContentLength"]

        tmp_file_bytes = product.file_bytes or {}
        tmp_file_bytes[file_key] = product_content_length
        product.file_bytes = tmp_file_bytes

        product.stamp_updated_timestamp()
        request.dbsession.add(product)
        request.dbsession.flush()

        # redirect back to this page to clear
        # the params posted by the s3 webhooks.
        return HTTPFound(f"{product.absolute_edit_url(request)}?uploaded={file_key}")

    if product_modified and product.error_message is None:
        request.dbsession.add(product)
        request.dbsession.flush()

    signed_posts = {}

    for file_key in product.file_keys:
        key_starts_with = f"{product.s3_path}/{file_key}."
        conditions = [
            {"success_action_redirect": product.absolute_edit_url(request)},
            ["starts-with", "$key", key_starts_with],
        ]

        signed_posts[file_key] = request.secure_uploads_client.generate_presigned_post(
            Bucket=request.app["bucket.secure_uploads"],
            Key=key_starts_with + "${filename}",
            ExpiresIn=900,
            Conditions=conditions,
        )

        # We must create a field key/value for each extra condition.
        # unfortunately `conditions` is a list of single key/value dicts
        # and/or 2/3 item lists so we flatten them into a single fields dict.
        # [{1:2}, [3,4]] -> {1:2, 3:4}
        for condition in conditions:
            if isinstance(condition, list):
                if len(condition) == 2:
                    # convert list into dict.
                    condition = {condition[0]: condition[1]}
                else:
                    continue
            signed_posts[file_key]["fields"].update(condition)

    # Fetch locations and inventory quantities for physical products
    locations = []
    if product.is_physical:
        locations = (
            request.dbsession.query(ShopLocation)
            .filter_by(shop_id=product.shop_id)
            .all()
        )
        inventories = {
            inv.shop_location.id: inv.quantity for inv in product.inventories
        }

    return {
        "product": product,
        "title": title,
        "description": description,
        "price": price,
        "visibility": visibility,
        "signed_posts": signed_posts,
        "locations": locations,
        "inventories": inventories if product.is_physical else {},
    }


@view_config(route_name="product_inventory_edit")
@shop_editor_required()
def product_inventory_edit(request):
    product = request.product

    if not product.is_physical:
        request.session.flash(("This product is not physical.", "error"))
        return HTTPFound(get_referer_or_home(request))

    # Get all shop locations for the product's shop
    shop_locations = request.shop.shop_locations

    updated = False

    for location in shop_locations:
        quantity = request.params.get(f"inventory_{location.id}", None)
        if quantity is not None:
            try:
                quantity = int(quantity)
                inventory = next(
                    (
                        inv
                        for inv in product.inventories
                        if inv.shop_location_id == location.id
                    ),
                    None,
                )
                if inventory:
                    if inventory.quantity != quantity:
                        inventory.update_quantity(quantity)
                        request.dbsession.add(inventory)
                        updated = True
                else:
                    inventory = Inventory(
                        shop_location=location, product=product, quantity=quantity
                    )
                    request.dbsession.add(inventory)
                    updated = True
            except ValueError:
                request.session.flash(
                    (f"Invalid quantity for location {location.name}.", "error")
                )

    if updated:
        request.dbsession.flush()
        request.session.flash(("Inventory updated successfully.", "success"))

    return HTTPFound(get_referer_or_home(request))


@view_config(route_name="product_bundle_edit")
@view_config(route_name="product_bundle_edit2")
@shop_editor_required()
def product_bundle_edit(request):
    from ..models.product import get_products_by_ids

    from ..lib.uuid_validation import UUID_ALL_PATTERN

    product = request.product

    if not product.is_bundle:
        request.session.flash(
            ("You may only add products to a Product bundle.", "error")
        )

    bundle_data = request.params.get("bundle-data", "").strip()

    if bundle_data:
        products = get_products_by_ids(
            request.dbsession, UUID_ALL_PATTERN.findall(bundle_data)
        )

        if products is None:
            request.session.flash(
                ("We didn't detect any product ids. Try again.", "error")
            )
            return HTTPFound(get_referer_or_home(request))

        for product_to_bundle in products:
            if not product.add_product_to_bundle(product_to_bundle):
                request.session.flash((product.error_message, "error"))
                product.error_message = None
                continue

            request.session.flash(
                (
                    f"You added product {product_to_bundle.title} to this bundle!",
                    "success",
                )
            )

    return HTTPFound(get_referer_or_home(request))


@view_config(route_name="product_remove_bundled_product")
@shop_editor_required()
def product_bundle_remove_product(request):
    from ..models.product import get_product_by_id

    product = request.product

    bundled_product_id = request.matchdict.get("bundled_product_id")
    bundled_product = get_product_by_id(request.dbsession, bundled_product_id)

    if not product.is_bundle:
        request.session.flash(
            ("You may only remove products from a Product bundle.", "error")
        )

    if not product.remove_product_from_bundle(bundled_product):
        request.session.flash((product.error_message, "error"))
    else:
        request.session.flash(("You removed a product from this bundle!", "success"))

    return HTTPFound(get_referer_or_home(request))
