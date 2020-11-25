import uuid, copy
from application.extensions import apimanager
from sqlalchemy import or_, and_, func, literal
from sqlalchemy.sql.expression import cast
from gatco_restapi.helpers import to_dict
from gatco.response import json, text, html
from application.server import app
from application.database import db
from application.common.helpers import now_timestamp
from application.components.base import verify_access, get_current_tenant,\
    pre_filter_by_tenant, pre_post_set_tenant_id
from application.components.item.model import Item, ItemCategory, ItemCategoryRelation, PriceList, ItemPriceList, ItemVariants

# MODELS
from .model import BookingSpaItem, BookingSpaItemRelations

# PRE PROCESS ON SAVE ITEM
async def pre_process_save_booking_spa_item(request, data=None, **kw):
    if data is not None:
        current_tenant = get_current_tenant(request)
        if current_tenant is None or 'error_code' in current_tenant:
            return json({
                'error_code': 'TENANT_UNKNOWN',
                'error_message': 'Thông tin request không xác định'
            }, status=523)

        tenant_id = current_tenant.get('id')
        now_time = now_timestamp()
        if request.method == 'POST':
            # CREATE ITEM FIRST
            new_booking_spa_item = BookingSpaItem()
            for key, value in data.items():
                if key in ['id','spa_items']:
                    continue
                if hasattr(new_booking_spa_item, key) and not isinstance(data.get(key), (dict,list)):
                    setattr(new_booking_spa_item, key, value)
            new_booking_spa_item.tenant_id = tenant_id
            db.session.add(new_booking_spa_item)
            print('after add')
            db.session.commit()
            data['id'] = str(new_booking_spa_item.id)

        # elif request.method == 'PUT':
        if data.get('spa_items') is not None and isinstance(data['spa_items'], list):
            spa_item_ids = []
            for index, _ in enumerate(data['spa_items']):
                # print("id ==================  ", _)
                spa_item_ids.append(_.get('id'))
                # CHECK EXIST
                item = Item.query.filter(and_(Item.tenant_id == tenant_id,\
                Item.id == _.get('id'))).first()
                if item is not None:
                    print("1 : ", index)
                    booking_spa_item_relations = BookingSpaItemRelations()
                    booking_spa_item_relations.item_id = _.get('id')
                    booking_spa_item_relations.spa_booking_id = data.get('id')
                    booking_spa_item_relations.tenant_id = tenant_id
                    booking_spa_item_relations.current_price = _.get('current_price')
                    db.session.add(booking_spa_item_relations)
                    db.session.flush()
                    db.session.commit()
        return json(data)
# @app.route("/api/v1/fake_data_spa", methods=["GET", "POST"])
# async def fake(request):
apimanager.create_api(BookingSpaItem,
    methods=['GET', 'POST', 'DELETE', 'PUT'],
    url_prefix='/v1',
    preprocess=dict(GET_SINGLE=[verify_access, pre_filter_by_tenant],
                    GET_MANY=[verify_access, pre_filter_by_tenant],
                    POST=[verify_access, pre_post_set_tenant_id, pre_process_save_booking_spa_item],
                    PUT_SINGLE=[verify_access]),
    # postprocess=dict(GET_SINGLE=[post_process_get_item],
    #                  GET_MANY=[post_process_get_item],
    #                  PUT_SINGLE=[],
    #                  DELETE_SINGLE=[]),
    collection_name='booking_spa_item')

apimanager.create_api(BookingSpaItemRelations,
    methods=['GET', 'POST', 'DELETE', 'PUT'],
    url_prefix='/v1',
    preprocess=dict(GET_SINGLE=[verify_access, pre_filter_by_tenant],
                    GET_MANY=[verify_access, pre_filter_by_tenant],
                    POST=[verify_access, pre_post_set_tenant_id],
                    PUT_SINGLE=[verify_access]),
    # postprocess=dict(GET_SINGLE=[post_process_get_item],
    #                  GET_MANY=[post_process_get_item],
    #                  PUT_SINGLE=[],
    #                  DELETE_SINGLE=[]),
    collection_name='booking_spa_item_relations')