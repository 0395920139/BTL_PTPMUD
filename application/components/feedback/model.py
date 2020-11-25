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

class FeeadBack(CommonModel):
    __tablename__ = 'feedback'
    contact_id = db.Column(UUID(as_uuid=True), ForeignKey('contact.id'), nullable=True)
    contact = db.relationship("Contact")
    room_id = db.Column(UUID(as_uuid=True), ForeignKey("room.id", onupdate="CASCADE", ondelete="RESTRICT"))
    room = db.relationship("Room")
    device_id = db.Column(String(), nullable = False)
    score = db.Column(FLOAT(15,8))
    description = db.Column(String)
    tenant_id = db.Column(String(), ForeignKey("tenant.id", onupdate="CASCADE", ondelete="RESTRICT"), nullable=False)