from sqlalchemy import (
    Column, String, Integer, Date, Boolean, Text, ForeignKey, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from application.database import db
from application.database.model import CommonModel


class Workstation(CommonModel):
    __tablename__ = 'workstation'
    workstation_exid = db.Column(String(100), index=True) #id tich hop tu he thong khac
    workstation_no = db.Column(String(100))
    workstation_name = db.Column(String(255), nullable=False)
    phone = db.Column(String(50), nullable=True)
    address_street = db.Column(String(150), nullable=True)
    address_district = db.Column(String(100), nullable=True)
    address_city = db.Column(String(100), nullable=True)
    address_state = db.Column(String(100), nullable=True)
    address_country = db.Column(String(25), nullable=True)
    address_postalcode = db.Column(String(10), nullable=True)
    description = db.Column(String(255), nullable=True)
    extra_data = db.Column(JSONB())
    tax_code = db.Column(String(30), nullable=True)
    is_global = db.Column(Boolean(), default=False)
    active = db.Column(Boolean(), default=True)
    pos_list = db.relationship("PointOfSale")
    tenant_id = db.Column(String(), ForeignKey("tenant.id", onupdate="RESTRICT", ondelete="RESTRICT"), nullable=False)


class PointOfSale(CommonModel):
    __tablename__ = 'pointofsale'
    pointofsale_exid = db.Column(String(100), index=True) #id tich hop tu he thong khac
    pointofsale_no = db.Column(String(100))
    pointofsale_name = db.Column(String(255), nullable=False)
    extra_data = db.Column(JSONB())
    active = db.Column(Boolean(), default=True)
    workstation_id = db.Column(UUID(as_uuid=True), ForeignKey("workstation.id", onupdate="CASCADE"))
    workstation = db.relationship("Workstation")
    tenant_id = db.Column(String(), ForeignKey("tenant.id", onupdate="RESTRICT", ondelete="RESTRICT"), nullable=False)
