from sqlalchemy import (
    Column, String, Integer, BigInteger,
    DateTime, Date, Boolean, FLOAT, Text,
    ForeignKey, UniqueConstraint
)
from sqlalchemy.orm import *
from sqlalchemy.dialects.postgresql import UUID, JSONB
from application.database import db
from application.database.model import CommonModel


class Provider(CommonModel):
    __tablename__ = 'provider'
    provider_name = db.Column(String())
    provider_no = db.Column(String() , unique = True)
    images = db.Column(JSONB())
    thumbnail = db.Column(Text())
    description = db.Column(Text())
    phone = db.Column(String())
    email = db.Column(String())
    address = db.Column(String())
    services = db.relationship("Service", secondary="services_providers", lazy='dynamic')
    tenant_id = db.Column(String(), ForeignKey("tenant.id", onupdate="RESTRICT", ondelete="RESTRICT"), nullable=False)

