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

class Post(CommonModel):
    __tablename__ = 'post'
    post_name = db.Column(String())
    post_type = db.Column(String())
    thumbnail = db.Column(String())
    images = db.Column(JSONB())
    title = db.Column(String())
    content = db.Column(String())
    position = db.Column(Integer())
    status = db.Column(String())
    active = db.Column(Boolean(), nullable=True, default=True)
    note = db.Column(Text(), nullable=True)
    tenant_id = db.Column(String(), ForeignKey("tenant.id", onupdate="CASCADE", ondelete="RESTRICT"), nullable=False)