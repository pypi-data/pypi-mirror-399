import uuid

import json

import mimetypes

from sqlalchemy import Column, Integer, BigInteger, Boolean, Unicode, UnicodeText

from sqlalchemy.orm import relationship

from .meta import (
    Base,
    RBase,
    UUIDType,
    now_timestamp,
    foreign_key,
    get_object_by_id,
    get_objects_by_ids,
    VISIBILITY_INT_TO_HUMAN,
)

from sqlalchemy.ext.associationproxy import association_proxy

from .user_product import UserProduct
from .price import Price

from make_post_sell.lib.render import markdown_to_html
from make_post_sell.lib.time_funcs import timestamp_to_datetime, timestamp_to_ago_string

from slugify import slugify

from ..lib.currency import (
    dollars_to_cents,
    cents_to_dollars,
)

try:
    unicode("")
except:
    from six import u as unicode


DEFAULT_FILE_METADATA = unicode(
    """
{
  "originals":{},
  "extensions":{}
}
"""
)

DEFAULT_BUNDLE_METADATA = unicode(
    """
{
  "bundle-ids":[],
  "product-ids":[]
}
"""
)


def sizeof_fmt(num, suffix="B"):
    for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"


class Product(RBase, Base):
    """This class represents a product."""

    error_message = None

    id = Column(UUIDType, primary_key=True, index=True)
    shop_id = Column(UUIDType, foreign_key("Shop", "id"), nullable=False)
    title = Column(Unicode(256), nullable=False)

    # TODO: rename this column to description_raw.
    description = Column(UnicodeText, nullable=False)
    description_html = Column(UnicodeText, nullable=False)

    json_file_metadata = Column(UnicodeText, default=DEFAULT_FILE_METADATA)

    json_file_bytes = Column(UnicodeText, default="{}")

    total_file_bytes = Column(BigInteger, nullable=False, default=0)

    # a denormalized json field to relate products to bundles, and vice versa.
    json_bundle_metadata = Column(
        UnicodeText, default=DEFAULT_BUNDLE_METADATA, nullable=False
    )

    # 0=private, 1=public, 2=unlisted
    visibility = Column(Integer, nullable=False, default=1)

    price_in_cents = Column(BigInteger, nullable=False, default=0)

    created_timestamp = Column(BigInteger, nullable=False)
    updated_timestamp = Column(BigInteger, nullable=False)

    # this value should be treated as immutable after object creation.
    is_bundle = Column(Boolean, default=False, nullable=False)

    # this value should be treated as immutable after object creation.
    is_sellable = Column(Boolean, default=False, nullable=False)

    # this value should be treated as immutable after object creation.
    is_physical = Column(Boolean, default=False, nullable=False)

    # Add relationship to inventories
    inventories = relationship("Inventory", lazy="joined", back_populates="product")

    # lazy="joined" performs a left join to reduce queries, it's magic.
    # set uselist=False creates one-to-one relationship.
    shop = relationship(argument="Shop", uselist=False, lazy="joined")

    # lazy="joined" performs a left join to reduce queries, it's magic.
    price_history = relationship(
        argument="Price",
        lazy="dynamic",
        order_by="desc(Price.created_timestamp)",
        back_populates="product",
    )

    # lazy="dynamic" returns a query object for all comments
    comments = relationship(
        argument="Comment",
        lazy="dynamic",
        order_by="Comment.created_timestamp",
        back_populates="product",
    )

    # many to many uses association_proxy.
    users = association_proxy(
        "product_users", "user", creator=lambda u: UserProduct(user=u)
    )

    file_keys = [
        "product",
        "preview",
        "thumbnail1",
        "thumbnail2",
        "thumbnail3",
        "thumbnail4",
    ]

    file_public_keys = [
        "preview",
        "thumbnail1",
        "thumbnail2",
        "thumbnail3",
        "thumbnail4",
    ]

    file_thumbnail_keys = ["thumbnail1", "thumbnail2", "thumbnail3", "thumbnail4"]

    def __init__(self, title, description):
        self.id = uuid.uuid1()
        self.title = title
        self.set_description(description)
        self.created_timestamp = now_timestamp()
        self.updated_timestamp = now_timestamp()

    @property
    def human_updated_timestamp(self):
        return timestamp_to_ago_string(self.updated_timestamp)

    @property
    def human_created_timestamp(self):
        return timestamp_to_ago_string(self.created_timestamp)

    def get_userproduct_for_user(self, user):
        """Given a User object, return the UserProduct object or None."""
        for up in self.product_users:
            if up.user == user:
                return up

    def unlock_for_user(self, user):
        """
        Unlock this product for user so they may download.
        Adds User object to UserProduct.
        """
        up = self.get_userproduct_for_user(user)
        if up is None:
            up = UserProduct(user=user, product=self)
            self.product_users.append(up)
        return up

    def set_description(self, description):
        self.updated_timestamp = now_timestamp()
        # TODO: rename this column to description_raw.
        self.description = description
        self.description_html = markdown_to_html(description, self.shop)

    def set_price(self, price):
        self.updated_timestamp = now_timestamp()
        try:
            self.price_in_cents = dollars_to_cents(price)
        except ValueError:
            self.error_message = "Please use only numbers for price."
            return None
        # create and return a price history object.
        return Price(self, self.price_in_cents)

    @property
    def price(self):
        return cents_to_dollars(self.price_in_cents)

    @property
    def current_price(self):
        """return the most current Price object for this Product from history."""
        return self.price_history.limit(1).one()

    @property
    def has_product_file(self):
        """returns True if product has a product file, else False"""
        return True if self.extensions.get("product") else False

    @property
    def is_ready(self):
        """Internal safety checks prior to allowing the sale of this product."""
        if self.is_sellable:
            if self.is_bundle:
                return True if len(self.bundle_metadata["product-ids"]) >= 1 else False
            if self.is_physical:
                return "thumbnail1" in self.extensions
            return self.has_product_file

        # Content is always ready, for example a blog post only needs a title & description.
        return True

    @property
    def is_not_ready(self):
        return not self.is_ready

    @property
    def is_not_sellable(self):
        return not self.is_sellable

    @property
    def is_public(self):
        return True if self.visibility == 1 else False

    @property
    def is_unlisted(self):
        return True if self.visibility == 2 else False

    @property
    def is_private(self):
        return True if self.visibility == 0 else False

    @property
    def human_visibility(self):
        return VISIBILITY_INT_TO_HUMAN[self.visibility]

    @property
    def slug(self):
        """return slug from title"""
        return slugify(self.title)

    @property
    def total_inventory_quantity(self):
        if not self.is_physical:
            return None
        return sum(inventory.quantity for inventory in self.inventories)

    @property
    def s3_path(self):
        """return the S3 path shop.id/product.id"""
        return f"{self.shop.id}/{self.id}"

    @property
    def s3_key(self):
        """return the product S3 key"""
        return f"{self.s3_path}/product"

    @property
    def s3_key_preview(self):
        """return the product preview S3 key"""
        return f"{self.s3_path}/preview"

    def s3_key_thumbnail(self, file_key):
        """return the thumbail S3 key"""
        return f"{self.s3_path}/{file_key}"

    @property
    def s3_key_thumbnails(self):
        thumbnails = {}
        for thumbnail_key in self.file_thumbnail_keys:
            if thumbnail_key in self.extensions:
                thumbnails[thumbnail_key] = self.s3_key_thumbnail(thumbnail_key)
        return thumbnails

    @property
    def file_metadata(self):
        """memoized dictionary of file_metadata"""
        if self.json_file_metadata:
            if hasattr(self, "_file_metadata") == False:
                self._file_metadata = json.loads(self.json_file_metadata)
            return self._file_metadata
        return {}

    @property
    def file_bytes(self):
        return json.loads(self.json_file_bytes)

    @file_bytes.setter
    def file_bytes(self, new_dict):
        self.json_file_bytes = json.dumps(new_dict)
        self.total_file_bytes = sum(self.file_bytes.values())

    @property
    def human_total_file_bytes(self):
        return sizeof_fmt(self.total_file_bytes)

    @property
    def human_product_file_bytes(self):
        return sizeof_fmt(self.file_bytes.get("product", 0))

    def human_file_bytes(self, file_key):
        """Return human-readable file size for a specific file key."""
        return sizeof_fmt(self.file_bytes.get(file_key, 0))

    @property
    def extensions(self):
        return self.file_metadata.get("extensions", {})

    @property
    def originals(self):
        return self.file_metadata.get("originals", {})

    def set_file_metadata(self, file_key, extension, original_filename):
        tmp = self.file_metadata
        tmp["extensions"][file_key] = extension
        tmp["originals"][file_key] = original_filename
        self._file_metadata = tmp
        self.json_file_metadata = json.dumps(tmp)

    def store_file_metadata(self, s3_key):
        # example s3_key: "uuid/uuid/product.MyTaco.Beans.pdf"
        # example parts: ["product", "MyTaco", "Beans", "pdf"]
        parts = s3_key.split("/")[-1].split(".")
        # product
        file_key = parts[0]
        # pdf
        file_ext = parts[-1]
        # MyTaco.Beans.pdf
        original_filename = ".".join(parts[1:])
        self.set_file_metadata(file_key, file_ext, original_filename)
        return file_key

    def get_content_type(self, file_key):
        """return the content type string for the S3 object, or None."""
        extension = self.extensions.get(file_key)
        if extension:
            return mimetypes.types_map.get("." + extension)

    def get_content_disposition(self, file_key):
        """
        Return the content disposition string for the S3 object, or None.

        The content disposition string determines whether this is:

         * an inline image (thumbnails)
         * an attachment (file download)
        """
        file_prefix = "" if file_key == "product" else f"{file_key}-"
        extension = self.extensions.get(file_key, "")
        filename = f"{file_prefix}{self.slug}.{extension}"
        content_disposition = f"attachment; filename={filename}"

        if file_key in self.file_thumbnail_keys:
            content_disposition = f"inline; filename={filename}"
        elif self.is_not_sellable:
            content_disposition = f"inline; filename={filename}"

        return content_disposition

    @property
    def content_disposition(self):
        """return the content_disposition for the product."""
        return self.get_content_disposition("product")

    @property
    def preview_content_disposition(self):
        """return the content_disposition  for the preview."""
        return self.get_content_disposition("preview")

    def absolute_url(self, request, slug=True):
        """
        The absolute URI to the product page.

        For example:

          https://my.makepostsell.com/p/product-uuid
        """
        p_or_c = "p" if self.is_sellable else "c"
        if slug:
            return f"{request.host_url}/{p_or_c}/{self.id}/{self.slug}"
        return f"{request.host_url}/{p_or_c}/{self.id}"

    def absolute_edit_url(self, request, subject=""):
        """
        The absolute URI to the product edit page.

        For example:

          https://makepostsell.com/p/product-uuid/edit
        """
        if subject:
            return f"{self.absolute_url(request, slug=False)}/{subject}/edit"
        return f"{self.absolute_url(request, slug=False)}/edit"

    @property
    def shop_uuid_str(self):
        return self.id_to_uuid_str(self.shop_id)

    @property
    def bundle_metadata(self):
        """memoized dictionary of bundle_metadata"""
        if hasattr(self, "_bundle_metadata") == False:
            self._bundle_metadata = json.loads(self.json_bundle_metadata)
        return self._bundle_metadata

    def add_product_to_bundle(self, product):
        if self.is_bundle == False:
            self.error_message = "This product is not a bundle."
        elif self.shop_id != product.shop_id:
            self.error_message = "The product and bundle must share the same shop."
        elif product.is_physical or self.is_physical:
            self.error_message = (
                f"Refusing to bundle {product.title}, it is a physical item."
            )
        elif product in self.products_in_this_bundle:
            self.error_message = (
                f"Refusing to bundle {product.title}, it is already in the bundle."
            )

        if self.error_message:
            return False

        # denormalized bundle relationship metadata for bundle.
        self.bundle_metadata["product-ids"].append(str(product.id))
        self.json_bundle_metadata = json.dumps(self.bundle_metadata)

        # denormalized bundle relationship metadata for product in bundle.
        product.bundle_metadata["bundle-ids"].append(str(self.id))
        product.json_bundle_metadata = json.dumps(product.bundle_metadata)

        return True

    def remove_product_from_bundle(self, product):
        if self.is_bundle == False:
            self.error_message = "This product is not a bundle."
        if self.error_message:
            return False

        # denormalized bundle relationship metadata for bundle.
        self.bundle_metadata["product-ids"].remove(str(product.id))
        self.json_bundle_metadata = json.dumps(self.bundle_metadata)

        # denormalized bundle relationship metadata for product in bundle.
        product.bundle_metadata["bundle-ids"].remove(str(self.id))
        product.json_bundle_metadata = json.dumps(product.bundle_metadata)

        return True

    @property
    def products_in_this_bundle(self):
        """if this product is a bundle return a list of Product objects in this bundle."""
        if self.is_bundle == False:
            return []
        if hasattr(self, "_products_in_bundle") == False:
            self._products_in_this_bundle = (
                get_products_by_ids(self.dbsession, self.bundle_metadata["product-ids"])
                or []
            )
        return self._products_in_this_bundle

    @property
    def bundles_with_this_product(self):
        """
        Return a list of zero or many bundle Product objects.
        All the bundles out there which if purchased unlock this product.
        """
        if self.is_bundle:
            return []
        if hasattr(self, "_bundles_with_this_product") == False:
            self._bundles_with_this_product = (
                get_products_by_ids(self.dbsession, self.bundle_metadata["bundle-ids"])
                or []
            )
        return self._bundles_with_this_product

    def stamp_updated_timestamp(self):
        self.updated_timestamp = now_timestamp()

    def get_s3_acl_for_file_key(self, file_key):
        """Return appropriate S3 ACL based on product visibility and file type."""
        # Public files (thumbnails, previews) are always public-read for public/unlisted products
        if file_key in self.file_public_keys:
            if self.is_private:
                return "private"
            else:
                return "public-read"

        # Product files are always private regardless of visibility
        # Access is controlled via presigned URLs
        return "private"

    def update_s3_acls(self, s3_client, bucket_name):
        """Update S3 ACLs for all product files based on current visibility."""

        # Update ACLs for all file types
        for file_key in self.file_keys:
            if file_key in self.extensions:
                s3_key = getattr(self, f"s3_key_{file_key}", None)
                if s3_key is None and file_key == "product":
                    s3_key = self.s3_key
                elif s3_key is None and file_key == "preview":
                    s3_key = self.s3_key_preview
                elif s3_key is None and file_key.startswith("thumbnail"):
                    s3_key = self.s3_key_thumbnail(file_key)

                if s3_key:
                    try:
                        acl = self.get_s3_acl_for_file_key(file_key)
                        s3_client.put_object_acl(
                            Bucket=bucket_name, Key=s3_key, ACL=acl
                        )
                    except Exception as e:
                        # Log error but don't fail the visibility change
                        print(f"Failed to update S3 ACL for {s3_key}: {e}")

    def set_visibility(self, new_visibility, s3_client=None, bucket_name=None):
        """Set product visibility and update S3 ACLs accordingly."""
        old_visibility = self.visibility
        self.visibility = new_visibility

        # Update S3 ACLs if client provided and visibility changed
        if s3_client and bucket_name and old_visibility != new_visibility:
            self.update_s3_acls(s3_client, bucket_name)

    def has_user_purchased_product(self, user_id):
        """Check if user has purchased this product (for purchase-required commenting)."""
        # Check if user has purchased this product
        user_product = (
            self.dbsession.query(UserProduct)
            .filter(UserProduct.user_id == user_id, UserProduct.product_id == self.id)
            .first()
        )

        return user_product is not None

    def can_user_comment(self, user, shop):
        """Check if user can comment on this product based on shop settings."""
        if not shop.comments_enabled:
            return False, "Comments are disabled for this shop"

        if shop.comments_require_purchase and user:
            if not self.has_user_purchased_product(user.id):
                return False, "You must purchase this product to leave a comment"

        return True, None

    @property
    def public_comments(self):
        """Return only approved, non-disabled comments for public display."""
        from .comment import Comment

        return self.comments.filter(Comment.approved == True, Comment.disabled == False)

    @property
    def public_comment_count(self):
        """Return count of approved, non-disabled comments."""
        return self.public_comments.count()


def get_all_products(dbsession):
    """
    Return all Product objects descending order by created timestamp (newest first).
    """
    return dbsession.query(Product).order_by(Product.created_timestamp.desc())


def get_all_products_by_visibility(dbsession, visibility=1):
    """
    Return all Product objects with the given visibility integer in descending order by created timestamp (newest first).
    """
    # 0=private, 1=public, 2=unlisted
    return (
        dbsession.query(Product)
        .filter(Product.visibility == visibility)
        .order_by(Product.created_timestamp.desc())
    )


def get_product_by_id(dbsession, product_id):
    """Try to get Product object by id or return None."""
    return get_object_by_id(dbsession, product_id, Product)


def get_products_by_ids(dbsession, product_ids):
    """Try to get Product objects by ids or return None."""
    return get_objects_by_ids(dbsession, product_ids, Product)


def get_all_products_from_a_shop(shop):
    return shop.products.order_by(Product.updated_timestamp.desc())


def get_products_from_a_shop(shop, visibility=1):
    """
    given a Shop object, return all products,
    ordered by descending updated_timestamp.
    """
    return shop.products.filter(Product.visibility == visibility).order_by(
        Product.updated_timestamp.desc()
    )


def get_products_by_keywords(dbsession, keywords, shop=None):
    scores = {}
    hits = {}

    if shop:
        product_query = shop.products
    else:
        product_query = dbsession.query(Product)

    for keyword in keywords:
        keyword_filter = Product.title.ilike(f"%{keyword}%")
        # the product _must_ be public (1).
        products = (
            product_query.filter(keyword_filter).filter(Product.visibility == 1).all()
        )

        for product in products:
            if product.id not in scores:
                scores[product.id] = 0
            scores[product.id] += 1

            if product.id not in hits:
                hits[product.id] = product

    # sort the scores dictionary by value (score),
    # but get the key (object id),
    # reversed (highest score first)
    score_sorted_ids = sorted(scores, key=scores.get, reverse=True)

    # return a list of objects in sorted order by score.
    return [hits[_id] for _id in score_sorted_ids]
