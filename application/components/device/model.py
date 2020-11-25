from sqlalchemy import (
    Column, String, Integer, BigInteger,
    DateTime, Date, Boolean, FLOAT, Text,
    ForeignKey, UniqueConstraint
)
from sqlalchemy.orm import *
from sqlalchemy.dialects.postgresql import UUID, JSONB

from application.database import db
from application.database.model import CommonModel

from application.common.helpers import now_timestamp
from application.components.base import get_current_tenant

class Device(CommonModel):
    __tablename__ = 'device'
    device_id = db.Column(String(), index=True, unique=True) #id tich hop tu he thong khac
    device_name = db.Column(String(225))
    device_type = db.Column(String(50), index=True)
    price = db.Column(Integer())
    image = db.Column(Text(), nullable=True)
    status = db.Column(Boolean(), nullable=True)
    note = db.Column(Text(), nullable=True)
    room = db.relationship("Room")
    room_id = db.Column(UUID(as_uuid=True), ForeignKey("room.id", onupdate="CASCADE", ondelete="RESTRICT"))
    tenant_id = db.Column(String(), ForeignKey("tenant.id", onupdate="CASCADE", ondelete="RESTRICT"), nullable=False)
