from sqlalchemy import (
    Column, String, Integer, BigInteger, Date, Boolean, FLOAT, Text, ForeignKey, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import UUID, JSON, JSONB
#from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm import *
from application.database import db
from application.database.model import CommonModel


class ItemCategoryRelation(CommonModel):
    __tablename__ = 'items_categories'
    item_id = db.Column(UUID(as_uuid=True), ForeignKey('item.id', ondelete='cascade'), primary_key=True, index = True)
    category_id = db.Column(UUID(as_uuid=True), ForeignKey('item_category.id', ondelete='cascade'), primary_key=True, index = True)
    # category_label = db.Column(String(255))
    # min_quantity = db.Column(Integer(), default=0)
    # max_quantity = db.Column(Integer(), default=999)
    # is_required = db.Column(Boolean(), default=False)
    # is_default = db.Column(Boolean(), default=False)
    # sort_number = db.Column(Integer(), default = 0)
    extra_data = db.Column(JSONB())# {"min_quantity":1,"max_quantity":2,"is_required":true,"is_default":true,"category_label":"", "sort_number":1}
    tenant_id = db.Column(String(), ForeignKey("tenant.id", onupdate="RESTRICT", ondelete="RESTRICT"), nullable=False)

# hạng mục sp
class ItemCategory(CommonModel):
    __tablename__ = 'item_category'
    category_exid = db.Column(String(100), nullable=True, index=True) #
    category_no = db.Column(String(100), nullable=True)
    category_name = db.Column(String(150), nullable=False)
    category_type = db.Column(String(20), default="default", index=True) #default/topping
    thumbnail = db.Column(Text())
    is_show = db.Column(Boolean(), default=True)
    # sort_number = db.Column(Integer(), default=0) #
    status = db.Column(String(20), default="active")
    items = db.relationship("Item", secondary='items_categories', lazy='dynamic')
    tenant_id = db.Column(String(), ForeignKey("tenant.id", onupdate="RESTRICT", ondelete="RESTRICT"), nullable=False)
    def __repr__(self):
        return '<ItemCategory: {}>'.format(self.category_name)

# loại sản phẩm
class ItemVariants(CommonModel):#
    __tablename__ = 'item_variants'
    variant_name = db.Column(String(100), nullable=False)
    variant_attr = db.Column(String(100), index=True)#
    item_id = db.Column(UUID(as_uuid=True), ForeignKey("item.id", ondelete="CASCADE"), nullable=False)
    sort_number = db.Column(Integer(), default=0)
    variants_details = db.Column(JSONB())
    tenant_id = db.Column(String(), ForeignKey("tenant.id", onupdate="RESTRICT", ondelete="RESTRICT"), nullable=False)


# class ItemVariantsDetails(CommonModel):
#     __tablename__ = 'item_variants_details'
#     variant_id = db.Column(UUID(as_uuid=True), ForeignKey("item_variants.id", ondelete="CASCADE"))
#     variant_value = db.Column(String(100))
#     sort_number = db.Column(Integer(), default=0)
#     tenant_id = db.Column(String(), ForeignKey("tenant.id", onupdate="RESTRICT", ondelete="RESTRICT"), nullable=False)


class Item(CommonModel):
    __tablename__ = 'item'
    item_no = db.Column(String(40), index=True, nullable=False) # mã
    item_name = db.Column(String(150), nullable=False) # tên view 1
    item_ascii_name = db.Column(String(150))
    item_type = db.Column(String(20), default="default", index=True) # loại sản phẩm default/topping/combo
    item_class = db.Column(String(100)) # nhóm sản phẩm
    thumbnail = db.Column(Text()) # ảnh view 1
    images = db.Column(JSONB()) # ảnh detail
    brief_desc = db.Column(Text()) # mô tả ngắn gọn view 1
    description = db.Column(Text()) # mô tả detail

    manufacturer = db.Column(String(200), nullable=True) # nhà sản xuất
    unit_quantity = db.Column(FLOAT(11,2), nullable=True) # số lượng đơn vị
    weight = db.Column(FLOAT(11,2), nullable=True) # cân nặng
    pack_size = db.Column(Integer(), nullable=True)
    website = db.Column(String(100)) # sản phẩm liên kết đến đâu
    is_product = db.Column(Boolean(), default=True)
    is_raw_material = db.Column(Boolean(), default=False)
    is_material = db.Column(Boolean(), default=False)
    is_service = db.Column(Boolean(), default=False)
    is_combo = db.Column(Boolean(), default=False)
    is_trending = db.Column(Boolean(), default=False)
    allow_delivery = db.Column(Boolean(), default=False)

    active = db.Column(Boolean(), default=True) # sản phẩm còn hoạt động hay ko
    extra_attributes = db.Column(JSONB()) # dữ liệu thêm
    # currency_id = db.Column(UUID(as_uuid=True), ForeignKey('currency.id'), nullable=True)

    price_lists = db.relationship("PriceList", secondary='item_price_list')
    # variants = db.relationship("ItemCombo")
    # combos = db.relationship("ItemVariants")
    categories = db.relationship("ItemCategory", secondary='items_categories')
    service_id = db.Column(UUID(as_uuid=True), ForeignKey("service.id"), nullable=True)
    tenant_id = db.Column(String(), ForeignKey("tenant.id", onupdate="RESTRICT", ondelete="RESTRICT"), nullable=False)


# class ItemTopping(CommonModel):
#     __tablename__ = 'item_topping'
#     item_id = db.Column(UUID(as_uuid=True), ForeignKey('item.id', ondelete='cascade'), primary_key=True)
#     item_tooping_id = db.Column(UUID(as_uuid=True), ForeignKey('item.id', ondelete='cascade'), primary_key=True)
#     tenant_id = db.Column(String(), ForeignKey("tenant.id", onupdate="RESTRICT", ondelete="RESTRICT"), nullable=False)

class PriceList(CommonModel):
    __tablename__ = 'price_list'
    price_list_name = db.Column(String())
    is_default = db.Column(Boolean(), default=False)
    start_time = db.Column(BigInteger)
    end_time = db.Column(BigInteger)
    extra_data = db.Column(JSONB())
    items = db.relationship("Item", secondary="item_price_list")
    # workstation_id = db.Column(UUID(as_uuid=True), ForeignKey("workstation.id", ondelete="SET NULL"))
    # workstation = db.relationship("Workstation") #
    tenant_id = db.Column(String(), ForeignKey("tenant.id", onupdate="RESTRICT", ondelete="RESTRICT"), nullable=False)


class ItemPriceList(CommonModel):
    __tablename__ = 'item_price_list'
    price_list_id = db.Column(UUID(as_uuid=True), ForeignKey("price_list.id", ondelete="CASCADE"), index=True)
    item_id = db.Column(UUID(as_uuid=True), ForeignKey("item.id", ondelete="CASCADE"), index=True)
    list_price = db.Column(FLOAT(25,8), default=0)
    delivery_price = db.Column(FLOAT(25,8), default=0)
    image = db.Column(Text())
    variants = db.Column(JSONB())
    note = db.Column(Text())
    extra_data = db.Column(JSONB())
    tenant_id = db.Column(String(), ForeignKey("tenant.id", onupdate="RESTRICT", ondelete="RESTRICT"), nullable=False)


class ItemCombo(CommonModel):
    __tablename__ = 'item_combo'
    item_id = db.Column(UUID(as_uuid=True), ForeignKey("item.id", ondelete="CASCADE"))
    org_price = db.Column(FLOAT(25,8), default=0)
    list_price = db.Column(FLOAT(25,8), default=0)
    quantity = db.Column(FLOAT(10,2), default=0)
    description = db.Column(Text())
    parent_id = db.Column(UUID(as_uuid=True), ForeignKey("item.id", ondelete="CASCADE"))
    tenant_id = db.Column(String(), ForeignKey("tenant.id", onupdate="RESTRICT", ondelete="RESTRICT"), nullable=False)


# class ItemToppingGroup(db.Model):
#     __tablename__ = 'item_topping_group'
#     id = db.Column(UUID(as_uuid=True), primary_key=True)
#     name = db.Column(String())
#     min_quantity = db.Column(Integer())
#     max_quantity = db.Column(Integer())
#     sort_number = db.Column(Integer(), default=0)


# class ItemTopping(db.Model):
#     __tablename__ = 'item_topping'
#     id = db.Column(UUID(as_uuid=True), primary_key=True)
#     item_id = db.Column(UUID(as_uuid=True), ForeignKey("item.id", ondelete="CASCADE"))
