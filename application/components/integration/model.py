from sqlalchemy import (
    Column, String, Integer, BigInteger,
    DateTime, Date, Boolean, FLOAT, Text,
    ForeignKey, UniqueConstraint
)
from sqlalchemy.orm import *
from sqlalchemy.dialects.postgresql import UUID, JSONB

from application.database import db
from application.database.model import CommonModel

def default_auth_data():
    return {}


class Partner(CommonModel):
    __tablename__ = 'partner'
    partner_id = db.Column(String(), index=True)
    partner_no = db.Column(String())
    partner_name = db.Column(String(), nullable=False)
    auth = db.Column(JSONB(), default=default_auth_data)
    description = db.Column(Text())
    extra_data = db.Column(JSONB())
    tenant_id = db.Column(String(), ForeignKey("tenant.id", onupdate="RESTRICT", ondelete="RESTRICT"), nullable=False)
