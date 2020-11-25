from sqlalchemy import (
    Column, String, Integer, BigInteger,
    DateTime, Date, Boolean, FLOAT, Text,
    ForeignKey, UniqueConstraint
)
from sqlalchemy.orm import *
from sqlalchemy.dialects.postgresql import UUID, JSONB
from application.database import db
from application.database.model import CommonModel


# class BookingSpaItem(CommonModel):
#     __tablename__ = 'booking_spa_item'
#     contact_id = db.Column(UUID(as_uuid=True), ForeignKey("contact.id", onupdate="RESTRICT", ondelete="RESTRICT"), nullable=False)
#     provider_id = db.Column(UUID(as_uuid=True), ForeignKey("provider.id", onupdate="RESTRICT", ondelete="RESTRICT"), nullable=True)
#     service_id = db.Column(UUID(as_uuid=True), ForeignKey("service.id", onupdate="RESTRICT", ondelete="RESTRICT"), nullable=False)
#     book_time = db.Column(BigInteger)
#     timeserver = db.Column(String(50))
#     people_number = db.Column(Integer)
#     note = db.Column(Text())
#     device_id = db.Column(String(), nullable=False)
#     contact = db.relationship("Contact")
#     provider = db.relationship("Provider")
#     spa_items = db.relationship("Item", secondary = 'booking_spa_item_relations')
#     tenant_id = db.Column(String(), ForeignKey("tenant.id", onupdate="RESTRICT", ondelete="RESTRICT"), nullable=False)
    
# class BookingSpaItemRelations(CommonModel):
#     __tablename__ = 'booking_spa_item_relations'
#     spa_booking_id = db.Column(UUID(as_uuid=True), ForeignKey('booking_spa_item.id', ondelete='cascade'), primary_key=True)
#     item_id = db.Column(UUID(as_uuid=True), ForeignKey('item.id', ondelete='cascade'), primary_key=True)
#     current_price = db.Column(FLOAT(25,8), default=0)
#     tenant_id = db.Column(String(), ForeignKey("tenant.id", onupdate="RESTRICT", ondelete="RESTRICT"), nullable=False)
    