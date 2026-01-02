from collections import (
    OrderedDict,
    deque,
)

from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    Integer,
    Unicode,
    UnicodeText,
    or_,
    func,
)

from sqlalchemy.orm import relationship, backref

import uuid

from slugify import slugify

from make_post_sell.lib.time_funcs import (
    timestamp_to_datetime,
    timestamp_to_ago_string,
)

from make_post_sell.lib.render import markdown_to_html

from .meta import Base, RBase
from .meta import UUIDType
from .meta import now_timestamp, foreign_key, get_object_by_id

import logging

try:
    unicode("")
except:
    from six import u as unicode

log = logging.getLogger(__name__)


class Comment(RBase, Base):
    """
    Comment class acts like a linked list to support nested comments:

        Product -> Comments -> Replies -> Sub-replies

    The `parent_id` column is only used by child comments.

    The class allows 3 layer nesting like StackOverflow or unlimited
    nesting like reddit. The frontend code determines the particular
    nesting strategy.

    For more information checkout this section of the SQLAlchemy Docs:

    http://docs.sqlalchemy.org/en/latest/orm/relationships.html#adjacency-list-relationships
    """

    id = Column(UUIDType, primary_key=True, index=True)
    root_id = Column(UUIDType, index=True, default=None)
    parent_id = Column(UUIDType, foreign_key("Comment", "id"), default=None)
    product_id = Column(UUIDType, foreign_key("Product", "id"), default=None)
    user_id = Column(UUIDType, foreign_key("User", "id"), default=None)

    title = Column(Unicode(256), default=None)
    data = Column(UnicodeText, default=None)
    data_html = Column(UnicodeText, default=None)

    # the depth of this comment in the thread's graph / tree.
    graph_depth = Column(Integer, nullable=False, default=-1)

    created_timestamp = Column(BigInteger, nullable=False)
    updated_timestamp = Column(BigInteger, nullable=False)
    disabled_timestamp = Column(BigInteger)
    disabled = Column(Boolean, default=False)
    verified = Column(Boolean, default=False)

    # a locked thread (root comment) prevents new commenting.
    locked = Column(Boolean, default=False)
    # by default comments are approved. unless shop requires approval.
    approved = Column(Boolean, default=True)

    ip_address = Column(Unicode(45), default=None)

    # lazy='joined' performs a left join to reduce queries, it's magic.
    user = relationship(argument="User", lazy="joined")

    # lazy='joined' performs a left join to reduce queries, it's magic.
    product = relationship(argument="Product", lazy="joined")

    # lazy='dynamic' returns a query object instead of collection.
    # Reference: http://docs.sqlalchemy.org/en/latest/orm/collections.html
    children = relationship(
        argument="Comment",
        lazy="dynamic",
        order_by="Comment.created_timestamp",
        foreign_keys=[parent_id],
        backref=backref("parent", remote_side=[id]),
    )

    # lazy='dynamic' returns a query object instead of collection.
    # Reference: http://docs.sqlalchemy.org/en/latest/orm/collections.html
    children_desc = relationship(
        argument="Comment",
        lazy="dynamic",
        order_by="desc(Comment.created_timestamp)",
        foreign_keys=[parent_id],
        overlaps="children,parent",
    )

    def __init__(self):
        self.id = uuid.uuid1()
        self.created_timestamp = now_timestamp()
        self.updated_timestamp = self.created_timestamp

    def get_children(self, order_by="asc"):
        if order_by == "desc":
            return self.children_desc
        return self.children

    @property
    def verified_children(self):
        return self.children.filter(Comment.verified == True)

    @property
    def unverified_children(self):
        return self.children.filter(Comment.verified == False)

    @property
    def enabled_children(self):
        """Get all non-disabled child comments."""
        return self.children.filter(Comment.disabled == False)

    @property
    def path_to_root(self):
        """The path from this comment to the root comment."""
        # TODO: memoize this result? how / when to deal with cache busting?
        comment = self
        path_to_root = []
        path_to_root.append(comment)
        while comment.parent is not None:
            comment = comment.parent
            path_to_root.append(comment)
        return path_to_root

    @property
    def path_from_root(self):
        """The path from the root comment to this comment."""
        return list(reversed(self.path_to_root))

    @property
    def root(self):
        """The origin or top most parent comment without a parent."""
        if self.is_root:
            return self
        return self.dbsession.query(Comment).filter(Comment.id == self.root_id).one()

    @property
    def is_root(self):
        if not self.parent_id or not self.root_id or self.root_id == self.id:
            return True
        return False

    def recompute_depth(self):
        """recompute the depth of a comment in the thread."""
        self.graph_depth = len(self.path_to_root) - 1

    @property
    def depth(self):
        if self.graph_depth == -1:
            self.recompute_depth()
        return self.graph_depth

    @property
    def ago_string(self):
        return timestamp_to_ago_string(self.created_timestamp)

    @property
    def datetime(self):
        return timestamp_to_datetime(self.created_timestamp)

    @property
    def is_locked(self):
        """Check if this comment thread is locked (prevents new comments)."""
        if self.locked:
            return True
        if not self.is_root and self.root.locked:
            return True
        return False

    def set_data(self, data):
        """Set comment data and generate HTML."""
        self.data = data
        if data:
            # Pass shop context if available through product relationship
            shop = self.product.shop if self.product else None
            self.data_html = markdown_to_html(data, shop)
        else:
            self.data_html = None
        self.updated_timestamp = now_timestamp()

    def stamp_updated_timestamp(self):
        self.updated_timestamp = now_timestamp()

    def disable(self):
        """Disable comment (soft delete)."""
        self.disabled = True
        self.disabled_timestamp = now_timestamp()
        self.stamp_updated_timestamp()

    def enable(self):
        """Enable comment (undelete)."""
        self.disabled = False
        self.disabled_timestamp = None
        self.stamp_updated_timestamp()

    def has_user_purchased_product(self, user_id):
        """Check if user has purchased this product (for purchase-required commenting)."""
        if not self.product:
            return False

        # Check if user has purchased this product
        from .user_product import UserProduct

        user_product = (
            self.dbsession.query(UserProduct)
            .filter(
                UserProduct.user_id == user_id,
                UserProduct.product_id == self.product_id,
            )
            .first()
        )

        return user_product is not None

    def can_user_comment(self, user, shop):
        """Check if user can comment based on shop settings."""
        if not shop.comments_enabled:
            return False, "Comments are disabled for this shop"

        if self.is_locked:
            return False, "This comment thread is locked"

        if shop.comments_require_purchase and user:
            if not self.has_user_purchased_product(user.id):
                return False, "You must purchase this product to leave a comment"

        return True, None

    def can_user_comment(self, user, shop):
        """Check if user can reply to this comment based on shop settings."""
        if not shop.comments_enabled:
            return False, "Comments are disabled for this shop"

        if self.is_locked:
            return False, "This comment thread is locked"

        if shop.comments_require_purchase and user:
            if not self.has_user_purchased_product(user.id):
                return False, "You must purchase this product to leave a comment"

        return True, None

    def can_user_moderate(self, user, shop):
        """Check if user can moderate comments (approve, delete, etc)."""
        if not user:
            return False

        # Shop owners and editors can moderate
        return shop.is_owner(user) or shop.is_editor(user)


def get_comment_by_id(dbsession, comment_id):
    """Get a comment by its ID."""
    return get_object_by_id(dbsession, comment_id, Comment)


def get_comments_for_product(dbsession, product_id, shop=None, user=None):
    """Get all root comments for a product, filtered by approval settings."""
    query = dbsession.query(Comment).filter(
        Comment.product_id == product_id,
        Comment.parent_id == None,
        Comment.disabled == False,
    )

    # If shop requires approval, only show approved comments to regular users
    if shop and shop.comments_require_approval:
        # Shop owners/editors can see all comments
        if not (user and (shop.is_owner(user) or shop.is_editor(user))):
            query = query.filter(Comment.approved == True)

    return query.order_by(Comment.created_timestamp.desc()).all()


def get_recent_comments(dbsession, shop_id=None, limit=10):
    """Get recent comments, optionally filtered by shop."""
    query = dbsession.query(Comment).filter(Comment.approved == True)

    if shop_id:
        # Join with Product to filter by shop
        from .product import Product

        query = query.join(Product).filter(Product.shop_id == shop_id)

    return query.order_by(Comment.created_timestamp.desc()).limit(limit).all()


def get_total_comment_count_for_product(dbsession, product_id, shop=None, user=None):
    """Get total count of all approved, non-disabled comments (root + replies) for a product."""
    query = dbsession.query(Comment).filter(
        Comment.product_id == product_id,
        Comment.disabled == False,
        Comment.approved == True,
    )

    return query.count()
