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


class ContactNoSeq(db.Model):
    __tablename__ = 'contact_no_seq'
    id = db.Column(String(50), primary_key=True)
    current_no = db.Column(Integer)

class ContactRoomSession(CommonModel):
    __tablename__ = 'contact_room_session'
    start_time = db.Column(BigInteger)
    end_time = db.Column(BigInteger)
    do_not_distrub = db.Column(Boolean(), default=False)
    extra_data = db.Column(JSONB())
    people_number = db.Column(Integer())
    children_number = db.Column(Integer(), default = 0)
    note = db.Column(Text())
    checkout = db.Column(Boolean(), default=False)
    contacts = db.relationship("Contact")
    rooms = db.relationship("Room")
    contact_id = db.Column(UUID(as_uuid=True), ForeignKey("contact.id", onupdate="CASCADE", ondelete="RESTRICT"))
    room_id = db.Column(UUID(as_uuid=True), ForeignKey("room.id", onupdate="CASCADE", ondelete="RESTRICT"))
    tenant_id = db.Column(String(), ForeignKey("tenant.id", onupdate="CASCADE", ondelete="RESTRICT"), nullable=False)

class Contact(CommonModel):
    __tablename__ = 'contact'
    contact_exid = db.Column(String(100), index=True) #id tich hop tu he thong khac
    contact_no = db.Column(String(25), index=True)
    contact_name = db.Column(String(255), nullable=False)
    gender = db.Column(String(30), nullable=True)
    birthday = db.Column(BigInteger, index=True,)
    phone = db.Column(String(50), index=True, nullable=False)
    email = db.Column(String(100), index=True, nullable=True)
    image = db.Column(Text(), nullable=True)
    contacttype = db.Column(String(50), nullable=True)

    bdate = db.Column(Integer()) # date of birthday
    bmonth = db.Column(Integer()) # month of birthday
    byear = db.Column(Integer(), index=True) # year of birthday
    
    title = db.Column(String(50), nullable=True)
    department = db.Column(String(30), nullable=True)
    fax = db.Column(String(50), nullable=True)
    usertype = db.Column(String(50), nullable=True)

    score = db.Column(FLOAT(25,8), default=0) # Score to make RANK of membership
    used_times = db.Column(Integer(), default=0) # the number of time using service of shop
    last_order_date = db.Column(BigInteger) # the last time using service
    
    donotcall = db.Column(Boolean(), nullable=True)
    emailoptout = db.Column(String(3), nullable=True)
    
    reference = db.Column(String(3), nullable=True)
    reportsto = db.Column(String(30), nullable=True)
    notify_owner = db.Column(String(3), nullable=True)
    note = db.Column(Text())
    
    address_city = db.Column(String(30), nullable=True)
    address_code = db.Column(String(30), nullable=True)
    address_country = db.Column(String(30), nullable=True)
    address_state = db.Column(String(30), nullable=True)
    address_street = db.Column(String(250), nullable=True)
    address_pobox = db.Column(String(30), nullable=True)

    extra_attributes = db.Column(JSONB())
    extra_data = db.Column(JSONB())
    social_info = db.Column(JSONB()) # list of social
    # workstation_id = db.Column(UUID(as_uuid=True), ForeignKey("workstation.id", onupdate="CASCADE", ondelete="RESTRICT"))
    tenant_id = db.Column(String(), ForeignKey("tenant.id", onupdate="CASCADE", ondelete="RESTRICT"), nullable=False)

    __table_args__ = (UniqueConstraint('tenant_id', 'phone', name='uq_contact_tenant_id_phone'),)

    # Methods
    def __repr__(self):
        return '<Contact: {}>'.format(self.contact_name)


contacts_categories = db.Table('contacts_categories',
                      db.Column('contact_id', UUID(as_uuid=True), db.ForeignKey('contact.id', ondelete='cascade'), primary_key=True),
                      db.Column('category_id', UUID(as_uuid=True), db.ForeignKey('contactcategory.id', ondelete='cascade'), primary_key=True))

class ContactCategory(CommonModel):
    __tablename__ = 'contactcategory'
    category_exid = db.Column(String(100), nullable=True, index=True)
    category_no = db.Column(String(20), nullable=True)
    category_name = db.Column(String(150), nullable=False)
    is_default = db.Column(Boolean(), default=False)
    extra_data = db.Column(JSONB())
    contacts = db.relationship("Contact", secondary=contacts_categories, lazy='dynamic')
    workstation_id = db.Column(UUID(as_uuid=True), ForeignKey("workstation.id", ondelete="RESTRICT"))
    tenant_id = db.Column(String(), ForeignKey("tenant.id", onupdate="CASCADE", ondelete="RESTRICT"), nullable=False)
    def __repr__(self):
        return '<ContactCategory: {}>'.format(self.category_name)


class ContactTags(CommonModel):
    __tablename__ = 'contact_tags'
    tag_label = db.Column(String())
    tag_ascii = db.Column(String())
    description = db.Column(Text())
    tenant_id = db.Column(String(), ForeignKey("tenant.id", onupdate="CASCADE", ondelete="RESTRICT"), nullable=False)


class ContactTagsDetails(CommonModel):
    __tablename__ = 'contact_tags_details'
    contact_tags_id = db.Column(UUID(as_uuid=True), ForeignKey("contact_tags.id", onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    contact_id = db.Column(UUID(as_uuid=True), ForeignKey("contact.id", onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    timestamp = db.Column(BigInteger)
    description = db.Column(Text())
    tenant_id = db.Column(String(), ForeignKey("tenant.id", onupdate="CASCADE", ondelete="RESTRICT"), nullable=False)


class ContactNote(CommonModel):
    __tablename__ = 'contact_note'
    title = db.Column(String(255), nullable=False)
    note = db.Column(Text(), nullable=True)
    attachments = db.Column(JSONB(), nullable=True)
    rating = db.Column(Integer) # 1, 2, 3, 4, 5
    feedback = db.Column(Text(), nullable=True)
    contact_id = db.Column(UUID(as_uuid=True), ForeignKey("contact.id", ondelete="RESTRICT"))
    contact = db.relationship("Contact")
    workstation_id = db.Column(UUID(as_uuid=True), ForeignKey("workstation.id", ondelete="RESTRICT"), nullable=True)
    tenant_id = db.Column(String(), ForeignKey("tenant.id", onupdate="CASCADE", ondelete="RESTRICT"), nullable=False)
    def __repr__(self):
        return '<ContactNote: {}>'.format(self.title)


class ContactScoreLog(CommonModel):
    __tablename__ = 'contact_score_log'
    title = db.Column(String(255), nullable=False)
    note = db.Column(Text(), nullable=True)
    action = db.Column(String(20)) # plus, minus
    log_data = db.Column(JSONB())
    contact_id = db.Column(UUID(as_uuid=True), ForeignKey("contact.id", ondelete="CASCADE"))
    contact = db.relationship("Contact")
    workstation_id = db.Column(UUID(as_uuid=True), ForeignKey("workstation.id", ondelete="RESTRICT"), nullable=True)
    tenant_id = db.Column(String(), ForeignKey("tenant.id", onupdate="CASCADE", ondelete="RESTRICT"), nullable=False)
    def __repr__(self):
        return '<ContactNote: {}>'.format(self.title)