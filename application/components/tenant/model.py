from sqlalchemy import (
    Column, String, Text, BigInteger, Boolean
)
from sqlalchemy.dialects.postgresql import UUID, JSONB

from application.server import app
from application.database import db
from application.common.helpers import now_timestamp


class Tenant(db.Model):
    __tablename__ = 'tenant'
    id = db.Column(String(32), primary_key=True) # upstart
    tenant_name = db.Column(String(255))
    image = db.Column(Text())
    phone = db.Column(String(15))
    address = db.Column(Text())
    district = db.Column(String())
    city = db.Column(String())
    country = db.Column(String())
    description = db.Column(String(100))
    business_line = db.Column(String(50))
    status = db.Column(String(50), default='active')
    extra_data = db.Column(JSONB())
    created_at = db.Column(BigInteger, index=True, default=now_timestamp)
    created_by = db.Column(UUID(as_uuid=True))
    created_by_name = db.Column(String())
    updated_at = db.Column(BigInteger)
    updated_by = db.Column(UUID(as_uuid=True))
    updated_by_name = db.Column(String())
    deleted = db.Column(Boolean, default=False)
    deleted_at = db.Column(BigInteger)
    deleted_by = db.Column(UUID(as_uuid=True))
    deleted_by_name = db.Column(String())
    partners = db.relationship("Partner")
