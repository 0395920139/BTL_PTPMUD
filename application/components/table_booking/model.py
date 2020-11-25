from sqlalchemy import (
    Column, String, Integer, BigInteger,
    DateTime, Date, Boolean, FLOAT, Text,
    ForeignKey, UniqueConstraint
)
from sqlalchemy.orm import *
from sqlalchemy.dialects.postgresql import UUID, JSONB
from application.database import db
from application.database.model import CommonModel


# class TableBooking(CommonModel):
#     __tablename__ = 'table_booking'
#     contact_id = db.Column(UUID(as_uuid=True), ForeignKey("contact.id", onupdate="RESTRICT", ondelete="RESTRICT"), nullable=False)
#     provider_id = db.Column(UUID(as_uuid=True), ForeignKey("provider.id", onupdate="RESTRICT", ondelete="RESTRICT"), nullable=False)
#     service_id = db.Column(UUID(as_uuid=True), ForeignKey("service.id", onupdate="RESTRICT", ondelete="RESTRICT"), nullable=False)
#     device_id = db.Column(String(), nullable=False)
#     people_number = db.Column(Integer)
#     book_time = db.Column(BigInteger)
#     note = db.Column(Text())
#     contact = db.relationship("Contact")
#     provider = db.relationship("Provider")
#     tenant_id = db.Column(String(), ForeignKey("tenant.id", onupdate="RESTRICT", ondelete="RESTRICT"), nullable=False)

