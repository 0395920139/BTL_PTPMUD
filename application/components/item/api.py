import uuid
from application.extensions import apimanager
from sqlalchemy import literal
from sqlalchemy import or_, and_, func
from sqlalchemy.sql.expression import cast
from gatco_restapi.helpers import to_dict
from gatco.response import json, text, html
from application.server import app
from application.database import db
from application.common.helpers import now_timestamp
from application.components.base import verify_access, get_current_tenant,\
    pre_filter_by_tenant, pre_post_set_tenant_id
# MODELS
from .model import Item, ItemCategory, ItemCategoryRelation, PriceList, ItemPriceList, ItemVariants

exclude_attrs = ['category_exid', 'tenant_id', 'created_at', 'created_by', 'created_by_name', 'updated_at', 'updated_by', 'updated_by_name',\
    'deleted', 'deleted_at', 'deleted_by', 'deleted_by_name']


MOCK_ITEMS = [{
    'id': 'e06b22db-e2e0-450d-9b19-5b644949d73a',
    'item_no': 'GNO',
    'item_name': 'Gà nướng ớt',
    'item_ascii_name': 'ga-nuong-ot',
    'item_type': None,
    'brief_desc': 'Món gà nướng muối ớt thơm lừng có lớp da giòn, thịt mềm thấm vị mặn của muối, vị cay nồng của ớt chinh phục cả những người ăn khó tính và trở thành món ăn được rất nhiều người ưa chuộng.',
    'description': 'Món gà nướng muối ớt thơm lừng có lớp da giòn, thịt mềm thấm vị mặn của muối, vị cay nồng của ớt chinh phục cả những người ăn khó tính và trở thành món ăn được rất nhiều người ưa chuộng. Tạo nên thành công của món gà nướng không thể nào bỏ qua công đoạn tẩm ướp gia vị. Chính vì vậy, Hướng Nghiệp Á Âu gởi đến các bạn “tất tần tật” về quy trình chế biến tạo nên món gà nướng thơm ngon, hấp dẫn, đặc biệt là công đoạn ướp gà.',
    'thumbnail': 'https://upstart.vn/static/upload/upinstantpage/033486815881587575007762.jpeg',
    'images': ['https://upstart.vn/static/upload/upinstantpage/033486815881587575007762.jpeg', 'https://upstart.vn/static/upload/upinstantpage/033486815881587575007762.jpeg', 'https://upstart.vn/static/upload/upinstantpage/033486815881587575007762.jpeg'],
    'weight': None,
    'usage_unit': None,
    'points': None,
    'price_list': {
        'item_id': 'e06b22db-e2e0-450d-9b19-5b644949d73a',
        'price_list_id': 'd82b24fb-e2e0-450d-9b19-5b644949d145s',
        'list_price': 395000,
        'delivery_price': 0,
        'variants': [],
        'note': None,
        'extra_data': None
    },
    'is_product': True,
    'is_combo': False,
    'is_service': False,
    'is_trending': False,
    'allow_delivery': True,
    'currency_id': None,
    'extra_attributes': [],
    'active': True
},
{
    'id': 'e06b22db-e2e0-450d-9b19-5b644949d73a',
    'item_no': 'GNO',
    'item_name': 'Gà nướng ớt',
    'item_ascii_name': 'ga-nuong-ot',
    'item_type': None,
    'brief_desc': 'Món gà nướng muối ớt thơm lừng có lớp da giòn, thịt mềm thấm vị mặn của muối, vị cay nồng của ớt chinh phục cả những người ăn khó tính và trở thành món ăn được rất nhiều người ưa chuộng.',
    'description': 'Món gà nướng muối ớt thơm lừng có lớp da giòn, thịt mềm thấm vị mặn của muối, vị cay nồng của ớt chinh phục cả những người ăn khó tính và trở thành món ăn được rất nhiều người ưa chuộng. Tạo nên thành công của món gà nướng không thể nào bỏ qua công đoạn tẩm ướp gia vị. Chính vì vậy, Hướng Nghiệp Á Âu gởi đến các bạn “tất tần tật” về quy trình chế biến tạo nên món gà nướng thơm ngon, hấp dẫn, đặc biệt là công đoạn ướp gà.',
    'thumbnail': 'https://upstart.vn/static/upload/upinstantpage/033486815881587575007762.jpeg',
    'images': ['https://upstart.vn/static/upload/upinstantpage/033486815881587575007762.jpeg', 'https://upstart.vn/static/upload/upinstantpage/033486815881587575007762.jpeg', 'https://upstart.vn/static/upload/upinstantpage/033486815881587575007762.jpeg'],
    'weight': None,
    'usage_unit': None,
    'points': None,
    'price_list': {
        'item_id': 'e06b22db-e2e0-450d-9b19-5b644949d73a',
        'price_list_id': 'd82b24fb-e2e0-450d-9b19-5b644949d145s',
        'list_price': 395000,
        'delivery_price': 0,
        'variants': [],
        'note': None,
        'extra_data': None
    },
    'is_product': True,
    'is_combo': False,
    'is_service': False,
    'is_trending': False,
    'allow_delivery': True,
    'currency_id': None,
    'extra_attributes': [],
    'active': True
}]


@app.route('/api/v1/item/list', methods=['GET'])
async def get_list_item(request):
    verify_access(request)
    tenant_id = request.headers.get('tenant_id')

    categories = db.session.query(ItemCategory).filter(and_(ItemCategory.tenant_id == tenant_id,\
                                                            ItemCategory.status == 'active',\
                                                            ItemCategory.deleted == False,\
                                                            ItemCategory.is_show == True)).all()                         
    result_categories = []
    result_items = MOCK_ITEMS
    for category in categories:
        category_dict = to_dict(category)
        for key in exclude_attrs:
            if key in category_dict:
                del category_dict[key]

        category_dict['items'] = MOCK_ITEMS

        items_of_category = db.session.query(Item).filter(and_(Item.id == ItemCategoryRelation.item_id,\
                                                               ItemCategory.id == ItemCategoryRelation.category_id,\
                                                               ItemCategory.id == category.id,\
                                                               Item.tenant_id == tenant_id,\
                                                               Item.deleted == False,\
                                                               Item.active == True)).all()
        for item in items_of_category:
            item_dict = {
                'id': str(item.id),
                'item_no': item.item_no,
                'item_name': item.item_name,
                'type': item.item_type,
                'thumbnail': item.thumbnail,
                'items': item.images,
                'brief_desc': item.brief_desc,
                'description': item.description,
                'price_list': {},
                'is_trending': item.is_trending,
                'is_product': True,
                'is_service': False,
                'is_combo': False,
                'combo_items': [],
                'toppings': []
            }
            category_dict['items'].append(item_dict)

        result_categories.append(category_dict)


    return json({
        'time': now_timestamp(),
        'categories': result_categories,
        'items': result_items
    })
