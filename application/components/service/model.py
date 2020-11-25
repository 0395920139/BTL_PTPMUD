from sqlalchemy import (
    Column, String, Integer, BigInteger,
    DateTime, Date, Boolean, FLOAT, Text,
    ForeignKey, UniqueConstraint
)
from sqlalchemy.orm import *
from sqlalchemy.dialects.postgresql import UUID, JSONB
from application.database import db
from application.database.model import CommonModel


class Service(CommonModel):
    __tablename__ = 'service'
    service_name = db.Column(String())
    service_no = db.Column(String() , unique = True, index = True)
    thumbnail = db.Column(Text())
    description = db.Column(Text())
    providers = db.relationship("Provider", secondary="services_providers", lazy='dynamic')
    tenant_id = db.Column(String(), ForeignKey("tenant.id", onupdate="RESTRICT", ondelete="RESTRICT"), nullable=False)

class ServicesProviders(CommonModel):
    __tablename__ = 'services_providers'
    service_id = db.Column(UUID(as_uuid=True), ForeignKey('service.id', ondelete='cascade'), primary_key=True)
    provider_id = db.Column(UUID(as_uuid=True), ForeignKey('provider.id', ondelete='cascade'), primary_key=True)
    tenant_id = db.Column(String(), ForeignKey("tenant.id", onupdate="RESTRICT", ondelete="RESTRICT"), nullable=False)
