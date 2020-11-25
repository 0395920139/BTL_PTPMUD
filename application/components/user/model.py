from sqlalchemy import (
    Column, String, Integer, BigInteger, DateTime, Date, Boolean, Text, ForeignKey, UniqueConstraint
)
#from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.dialects.postgresql import UUID, JSONB

from application.database import db
from application.database.model import CommonModel
from application.components.workstation.model import Workstation
from application.components.currency.model import Currency


def default_user_config():
    data = {}
    return data


roles_users = db.Table('roles_users',
                       db.Column('user_id', UUID(as_uuid=True), db.ForeignKey('user.id', ondelete='cascade'), primary_key=True),
                       db.Column('role_id', UUID(as_uuid=True), db.ForeignKey('role.id', onupdate='cascade'), primary_key=True))


class Role(CommonModel):
    __tablename__ = 'role'
    role_code = db.Column(Integer(), index=True, nullable=True)
    role_name = db.Column(String(100), index=True, nullable=False, unique=True)
    description = db.Column(String(255))
    permissions = db.relationship("Permission", cascade="all")
    tenant_id = db.Column(String(), ForeignKey("tenant.id", onupdate="RESTRICT", ondelete="RESTRICT"), nullable=False)


class Permission(CommonModel):
    __tablename__ = 'permission'
    role_id = db.Column(UUID(as_uuid=True), ForeignKey('role.id', ondelete="CASCADE", onupdate="CASCADE"))
    subject = db.Column(String, index=True)
    permission = db.Column(JSONB()) # read
    # value = db.Column(Boolean, default=False) # false
    tenant_id = db.Column(String(), ForeignKey("tenant.id", onupdate="RESTRICT", ondelete="RESTRICT"), nullable=False)
    __table_args__ = (UniqueConstraint('role_id', 'subject', 'permission', name='uq_permission_role_subject_permission'),)


class User(CommonModel):
    __tablename__ = 'user'
    display_name = db.Column(String(255), nullable=False)
    phone = db.Column(String(50), index=True, nullable=False)
    email = db.Column(String(100), index=True, nullable=True)
    birthday = db.Column(String())
    phone_other = db.Column(String(50), nullable=True)
    email_other = db.Column(String(100), nullable=True)
    gender = db.Column(db.String(20))
    avatar = db.Column(Text())

    password = db.Column(String(255), nullable=True)
    salt = db.Column(String(255), nullable=True)
    role_id = db.Column(UUID(as_uuid=True), ForeignKey("role.id", onupdate="SET NULL", ondelete="SET NULL"))
    role = db.relationship('Role')

    department = db.Column(String(50), nullable=True)
    signature = db.Column(Text(), nullable=True)
    address_street = db.Column(String(150), nullable=True)
    address_city = db.Column(String(100), nullable=True)
    address_state = db.Column(String(100), nullable=True)
    address_country = db.Column(String(25), nullable=True)
    address_postalcode = db.Column(String(10), nullable=True)
    tz = db.Column(String(30), nullable=True)
    theme = db.Column(String(100), nullable=True)
    language = db.Column(String(36), nullable=True)
    time_zone = db.Column(String(200), nullable=True)
    config_data = db.Column(JSONB(), default=default_user_config)
    tenant_id = db.Column(String(), ForeignKey("tenant.id", onupdate="RESTRICT", ondelete="RESTRICT"), nullable=False)
    tenant = db.relationship('Tenant')

    def __repr__(self):
        """ Show user object info. """
        return '<User: {}>'.format(self.id)

    def has_role(self, role):
        if isinstance(role, str):
            return role in (role.role_name for role in self.roles)
        else:
            return role in self.roles

    def add_role(self, role):
        pass

    def remove_role(self,role):
        pass

