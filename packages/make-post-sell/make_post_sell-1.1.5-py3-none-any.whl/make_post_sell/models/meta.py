from time import time
import base64

from sqlalchemy import ForeignKey

from sqlalchemy.orm import declarative_base, declared_attr

from sqlalchemy.schema import MetaData

from sqlalchemy.orm.session import object_session

import uuid
from sqlalchemy_utils import UUIDType as TempUUIDType


UUIDType = TempUUIDType(binary=False)


CLASS_TO_TABLE = {
    "Shop": "mps_shop",
    "ShopLocation": "mps_shop_location",
    "Inventory": "mps_inventory",
    "Product": "mps_product",
    "Coupon": "mps_coupon",
    "CouponRedemption": "mps_coupon_redemption",
    "User": "mps_user",
    "UserShop": "mps_user_shop",
    "UserProduct": "mps_user_product",
    "UserAddress": "mps_user_address",
    "Price": "mps_price",
    "License": "mps_license",
    "Cart": "mps_cart",
    "CartCoupon": "mps_cart_coupon",
    "Invoice": "mps_invoice",
    "InvoiceLineItem": "mps_invoice_line_item",
    "ShopSearchRequest": "mps_shop_search_request",
    "StripeUserShop": "mps_stripe_user_shop",
    "PayPalUserShop": "mps_paypal_user_shop",
    "Market": "mps_market",
    "Comment": "mps_comment",
    "CryptoPayment": "mps_crypto_payment",
    "CryptoProcessor": "mps_crypto_processor",
    "UserCryptoRefundAddress": "mps_user_crypto_refund_address",
}


# Recommended naming convention used by Alembic, as various different database
# providers will autogenerate vastly different names making migrations more
# difficult. See: http://alembic.zzzcomputing.com/en/latest/naming.html
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=NAMING_CONVENTION)
# Base = declarative_base(metadata=metadata)
Base = declarative_base()


COUPON_ACTION_TYPES = {
    "dollar-off",
    "percent-off",
}

VISIBILITY_INT_TO_HUMAN = {
    0: "Private",
    1: "Public",
    2: "Unlisted",
}


def short_id_to_bytes(short_id):
    """Accept a short_id (sanitized url safe base64 string) and return a byte string.

    >>> short_id_to_bytes('dbHeSEFLEeeuz5xONpxxWA')
    'u\xb1\xdeHAK\x11\xe7\xae\xcf\x9cN6\x9cqX'

    """
    return base64.b64decode((short_id + "==").replace("_", "/").replace("-", "+"))


def id_to_uuid(the_id):
    """
    Accept an id string, return a UUID object.

    >>> id_to_uuid('dbHeSEFLEeeuz5xONpxxWA')
    UUID('75b1de48-414b-11e7-aecf-9c4e369c7158')

    >>> id_to_uuid('75b1de48414b11e7aecf9c4e369c7158')
    UUID('75b1de48-414b-11e7-aecf-9c4e369c7158')

    >>> id_to_uuid('75b1de48-414b-11e7-aecf-9c4e369c7158')
    UUID('75b1de48-414b-11e7-aecf-9c4e369c7158')
    """
    if isinstance(the_id, uuid.UUID):
        # if the_id is already a UUID object, return it.
        return the_id

    try:
        # assume the_id is already a hex uuid string.
        return uuid.UUID(hex=the_id)

    except ValueError:
        try:
            # assume the_id is a base64 "short_id" string.
            return uuid.UUID(bytes=short_id_to_bytes(the_id))
        except ValueError:
            pass

    return None


def get_object_by_id(dbsession, object_id, cls):
    """Try to get object from database by id or return None"""
    object_uuid = id_to_uuid(object_id)
    if object_uuid:
        return dbsession.query(cls).filter(cls.id == object_uuid).one_or_none()


def get_objects_by_ids(dbsession, object_ids, cls):
    """Try to get a list of objects from database by ids or return None"""

    # TODO: if the list of object_ids is _very_ long consider chunking up
    #       the sequence and querying the database more than once before
    #       aggregating and returning the results.

    # make object_ids unique by converting to a set and the back to a list.
    object_ids = list(set(object_ids))

    # sort the object_ids list.
    object_ids.sort()

    # transform uuid with dashes to uuid without dashes.
    object_uuids = [id_to_uuid(object_id) for object_id in object_ids]

    if object_uuids:
        # reference: https://stackoverflow.com/q/444475
        return dbsession.query(cls).filter(cls.id.in_(object_uuids)).all()


def bucket_objects_by_id(objects):
    """
    Given a list of model Objects, return a dict where the key
    is a str representation of the id/uuid and the value is the Object.
    """
    bucket = {}
    if objects:
        for obj in objects:
            bucket[obj.uuid_str] = obj
    return bucket


def now_timestamp():
    return int(time() * 1000)


def foreign_key(class_name, column_name):
    return ForeignKey(f"{CLASS_TO_TABLE[class_name]}.{column_name}")


class RBase(object):
    """Mixin for models."""

    def __eq__(self, other):
        """Determine if equal by id."""
        if other:
            return self.id == other.id
        return False

    def __ne__(self, other):
        """Determine if not equal by user id."""
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.id)

    @declared_attr
    def __tablename__(cls):
        return CLASS_TO_TABLE[cls.__name__]

    @property
    def dbsession(self):
        return object_session(self)

    @property
    def uuid(self):
        return id_to_uuid(self.id)

    @property
    def uuid_str(self):
        return self.uuid.__str__()

    def id_to_uuid(self, _id):
        """Method for converting an id to UUID object."""
        return id_to_uuid(_id)

    def id_to_uuid_str(self, _id):
        """Method for converting an id to UUID str."""
        return self.id_to_uuid(_id).__str__()
