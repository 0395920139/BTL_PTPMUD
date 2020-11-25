from sqlalchemy import (
    Column, String, Integer, Date, Boolean, Text, ForeignKey, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import UUID

#from sqlalchemy.orm import relationship, backref

from application.database import db
from application.database.model import CommonModel

class Currency(CommonModel):
    __tablename__ = 'currency'
    currency_name = db.Column(String(50), unique=True, nullable=True) # viet nam
    currency_code = db.Column(String(11), unique=True, nullable=True) # vi-VN
    currency_symbol = db.Column(String(11), nullable=True) # 1.0-0
    tenant_id = db.Column(String(), ForeignKey("tenant.id", onupdate="RESTRICT", ondelete="RESTRICT"), nullable=False)