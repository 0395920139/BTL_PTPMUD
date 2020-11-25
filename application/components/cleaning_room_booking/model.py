from sqlalchemy import (
    Column, String, Integer, BigInteger,
    DateTime, Date, Boolean, FLOAT, Text,
    ForeignKey, UniqueConstraint
)
from sqlalchemy.orm import *
from sqlalchemy.dialects.postgresql import UUID, JSONB
from application.database import db
from application.database.model import CommonModel


# class CleaningRoomBooking(CommonModel):
#     __tablename__ = 'cleaning_room_booking'
#     contact_id = db.Column(UUID(as_uuid=True), ForeignKey("contact.id", onupdate="RESTRICT", ondelete="RESTRICT"), nullable=False)
#     provider_id = db.Column(UUID(as_uuid=True), ForeignKey("provider.id", onupdate="RESTRICT", ondelete="RESTRICT"), nullable=True)
#     service_id = db.Column(UUID(as_uuid=True), ForeignKey("service.id", onupdate="RESTRICT", ondelete="RESTRICT"), nullable=False)
#     book_time = db.Column(BigInteger)
#     note = db.Column(Text())
#     device_id = db.Column(String(), nullable=False)
#     contact = db.relationship("Contact")
#     provider = db.relationship("Provider")
#     tenant_id = db.Column(String(), ForeignKey("tenant.id", onupdate="RESTRICT", ondelete="RESTRICT"), nullable=False)

