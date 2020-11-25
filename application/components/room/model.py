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

class Room(CommonModel):
    __tablename__ = 'room'
    room_no = db.Column(String(20), index=True) #id tich hop tu he thong khac
    room_name = db.Column(String(225))
    room_type = db.Column(String(50), index=True)
    price = db.Column(Integer())
    image = db.Column(Text(), nullable=True)
    active = db.Column(Boolean(), nullable=True, default=True)
    note = db.Column(Text(), nullable=True)
    tenant_id = db.Column(String(), ForeignKey("tenant.id", onupdate="CASCADE", ondelete="RESTRICT"), nullable=False)
