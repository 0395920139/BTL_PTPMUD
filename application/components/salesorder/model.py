from sqlalchemy import (
    Column, String, Integer, BigInteger, Date, Boolean,\
    FLOAT, Text, SmallInteger, ForeignKey, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import UUID, JSONB

from application.database import db
from application.database.model import CommonModel


class Salesorder(CommonModel):
    __tablename__ = 'salesorder'
    salesorder_exid = db.Column(String(100), index=True, unique=True) #id tich hop tu he thong khac
    salesorder_no = db.Column(String(100))
    title = db.Column(String(255))

    book_time = db.Column(BigInteger)
    book_day = db.Column(SmallInteger())
    book_month = db.Column(SmallInteger())
    book_year = db.Column(SmallInteger())
    book_hour = db.Column(SmallInteger())
    book_minute = db.Column(SmallInteger())
    book_day_of_week = db.Column(SmallInteger())

    time_perform = db.Column(String(50))

    contact_id = db.Column(UUID(as_uuid=True), ForeignKey('contact.id'), nullable=True)
    contact = db.relationship("Contact")
    room_id = db.Column(UUID(as_uuid=True), ForeignKey("room.id", onupdate="CASCADE", ondelete="RESTRICT"), nullable=False)
    room = db.relationship("Room")
    device_id = db.Column(String(), nullable = False)
    # contact_name = db.Column(String(255))
    # contact_phone = db.Column(String(50))
    # contact_email = db.Column(String(100))
    # contact_address = db.Column(Text())
    
    # workstation_id = db.Column(UUID(as_uuid=True), ForeignKey('workstation.id'), nullable=True)
    # workstation_name = db.Column(String(255))
    people_number = db.Column(Integer)
    hour_schedule = db.Column(String())
    unwant_order = db.Column(Boolean(), default = False)

    price_adjustment = db.Column(FLOAT(15,8), default=0)  #https://en.wikipedia.org/wiki/Price_adjustment_(retail)
    salescommission = db.Column(FLOAT(15,8), default=0) # hoa hong cho nhan vien ban hang
    exciseduty = db.Column(FLOAT(15,8), default=0) # thu tieu thu dac biet, danh cho hang hoa xa xi.
    
    taxtype = db.Column(String(25), default="group") #group: thue tren toan bill - individual: thue tren tung item
    tax_percent = db.Column(FLOAT(7,3), default=0)
    tax_amount = db.Column(FLOAT(15,8), default=0)
    
    net_amount = db.Column(FLOAT(15,8), default=0)
    amount = db.Column(FLOAT(15,8), default=0)
    discount_amount = db.Column(FLOAT(15,8), default=0) # tiền giảm tự túc tại cửa hàng hoặc chỉnh sửa
    discount_percent = db.Column(FLOAT(7,3), default=0)
    voucher_discount_amount = db.Column(FLOAT(15,8), default=0) # tiền giảm theo chương trình KM

    card_swipe_fee_amount = db.Column(FLOAT(15,8), default=0) # Phí quẹt thẻ
    card_swipe_fee_percent = db.Column(FLOAT(7,3), default=0)
    
    other_fee_percent = db.Column(FLOAT(7,3), default=0) # Phí khác
    other_fee_amount = db.Column(FLOAT(15,8), default=0)
    
    ship_fee_amount = db.Column(FLOAT(15,8), default=0)
    ship_partner = db.Column(String(200))
    
    terms_conditions = db.Column(Text())
    purchaseorder = db.Column(String(200))
    sostatus = db.Column(String(200), default = "wait_confirm") # wait_confirm, confirmed, transporting, processing, finished # saleorder_status
    
    currency_id = db.Column(UUID(as_uuid=True), ForeignKey('currency.id'), nullable=True)
    currency_code = db.Column(String(11), nullable=True)
    currency = db.relationship("Currency")
    conversion_rate = db.Column(FLOAT(10,3)) # ty gia currency
    
    payment_method = db.Column(String(50))
    payment_status = db.Column(String(20))
    note = db.Column(Text())
    is_delivery = db.Column(Boolean(), default=False)
    delivery_address = db.Column(String(255))

    provider_id = db.Column(UUID(as_uuid=True), ForeignKey("provider.id", onupdate="RESTRICT", ondelete="RESTRICT"), nullable=True)
    provider = db.relationship("Provider")

    service_id = db.Column(UUID(as_uuid=True), ForeignKey("service.id", onupdate="RESTRICT", ondelete="RESTRICT"), nullable=False)
    service = db.relationship("Service")

    salesorder_items = db.relationship("SalesorderItems", order_by="SalesorderItems.created_at", cascade="all, delete-orphan", lazy='dynamic')
    tenant_id = db.Column(String(), ForeignKey("tenant.id", onupdate="RESTRICT", ondelete="RESTRICT"), nullable=False)


class SalesorderItems(CommonModel):
    __tablename__ = 'salesorder_items'
    salesorder_id = db.Column(UUID(as_uuid=True), ForeignKey('salesorder.id'), nullable=False)
    item_id = db.Column(UUID(as_uuid=True), ForeignKey('item.id', ondelete="CASCADE"), nullable=False, index =True)
    item = db.relationship("Item", foreign_keys=[item_id])
    item_type = db.Column(String(40), default="default")
    item_no = db.Column(String(40))
    item_name = db.Column(String(150))
    parent_item_id = db.Column(UUID(as_uuid=True), ForeignKey('item.id', ondelete="CASCADE"), nullable=True, index =True)
    parent_item = db.relationship("Item", foreign_keys=[parent_item_id])
    quantity = db.Column(FLOAT(15,3), default=1)
    current_price = db.Column(FLOAT(27,8), default=0)  #selling price, unit price, don gia
    discount_percent = db.Column(FLOAT(7,3), default=0)
    discount_amount = db.Column(FLOAT(27,8), default=0)
    voucher_discount_amount = db.Column(FLOAT(27,8), default=0)
    amount = db.Column(FLOAT(27,8), default=0)  # thanh tien sau khi tru discount
    net_amount = db.Column(FLOAT(27,8), default=0)  #thanh tien truoc khi tru discount
    description = db.Column(Text())
    tax_percent = db.Column(FLOAT(7,3), default=0)
    tax_amount = db.Column(FLOAT(15,8), default=0)
    purchase_cost = db.Column(FLOAT(27,8), default=0) # giá mua giả phẩm từ đại lý
    tenant_id = db.Column(String(), ForeignKey("tenant.id", onupdate="RESTRICT", ondelete="RESTRICT"), nullable=False)

class SalesorderLog(CommonModel):
    __tablename__ = 'saleorder_log'
    salesorder_id = db.Column(UUID(as_uuid=True), ForeignKey('salesorder.id', ondelete="CASCADE"), nullable=False)
    status = db.Column(String(20), default = "done")
    sostatus = db.Column(String(200)) # wait_confirm, confirmed, transporting, processing, finished # saleorder_status
    tenant_id = db.Column(String(), ForeignKey("tenant.id", onupdate="RESTRICT", ondelete="RESTRICT"), nullable=False)
    