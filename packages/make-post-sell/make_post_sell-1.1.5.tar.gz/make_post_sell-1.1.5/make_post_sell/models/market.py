from sqlalchemy import Column, Unicode

from .meta import Base, RBase, UUIDType


class Market(RBase, Base):
    """This class represents a Market place."""

    id = Column(UUIDType, primary_key=True, index=True)
    name = Column(Unicode(64), unique=True, nullable=False)
