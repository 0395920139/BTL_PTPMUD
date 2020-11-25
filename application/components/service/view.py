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
from .model import Service, ServicesProviders
from application.components.service.service_options import get_option_service

@app.route('/v1/service/get/categories', methods=['GET'])
async def service_get_catagories(request):
    current_tenant = get_current_tenant(request)
    if current_tenant is None or 'error_code' in current_tenant:
        return json({
            'error_code': 'TENANT_UNKNOWN',
            'error_message': 'Thông tin request không xác định'
        }, status=523)

    tenant_id = current_tenant.get('id')
    now_time = now_timestamp()

    service_no = request.args.get('service_no')
    service_id = db.session.query(Service.id).filter(Service.service_no == service_no, Service.tenant_id == tenant_id).first()
    categories_ids = db.session.query(ItemCategoryRelation.category_id).join(Item).filter(
        Item.service_id == service_id, 
        ItemCategoryRelation.item_id == Item.id,
        Item.item_type == 'default'
    ).distinct(ItemCategoryRelation.category_id).all()

    # print('----categories_ids-----', categories_ids)
    categories = db.session.query(ItemCategory).filter(
        ItemCategory.deleted == False,
        ItemCategory.tenant_id == tenant_id,
        ItemCategory.category_type == 'default',
        ItemCategory.id.in_(categories_ids)
    ).all()

    results = []
    active_price_list = PriceList.query.filter(and_(PriceList.tenant_id == tenant_id,\
                                                        or_(and_(PriceList.start_time <= now_time,\
                                                                PriceList.end_time >= now_time),\
                                                            PriceList.is_default == True),\
                                                        PriceList.deleted == False)).order_by(PriceList.is_default.desc()).first()
    
    if len(categories) != 0:
        for category in categories:
            category_dict = to_dict(category)
            category_dict['items'] = []
            items = db.session.query(Item).join(ItemCategoryRelation).filter(
                ItemCategoryRelation.category_id == category_dict.get('id'),
                Item.item_type == 'default',
                Item.deleted == False, Item.tenant_id == tenant_id,
                Item.active == True).all()
            for item in items:
                item_dict = to_dict(item)

                if active_price_list is not None:
                    # QUERY ITEM PRICE LIST
                    item_price_list = ItemPriceList.query.filter(and_(ItemPriceList.tenant_id == tenant_id,\
                                                                    ItemPriceList.price_list_id == active_price_list.id,\
                                                                    ItemPriceList.item_id == item_dict.get('id'))).first()
                    if item_price_list is not None:
                        dict_item_price = to_dict(item_price_list)
                        dict_item_price['id'] = str(dict_item_price['id'])
                        item_dict['price_list'] = dict_item_price

                # item_dict['topping'] = get_topping(item_dict, tenant_id)
                category_dict['items'].append(item_dict)
            results.append(to_dict(category_dict))
    else:
        category = ItemCategory()
        category_dict = to_dict(category)
        category_dict['items'] = []
        items = db.session.query(Item).filter(
                Item.item_type == 'default',
                Item.service_id == service_id,
                Item.deleted == False, Item.tenant_id == tenant_id,
                Item.active == True).all()
        for item in items:
            item_dict = to_dict(item)
            if active_price_list is not None:
                    # QUERY ITEM PRICE LIST
                item_price_list = ItemPriceList.query.filter(and_(ItemPriceList.tenant_id == tenant_id,\
                                                                ItemPriceList.price_list_id == active_price_list.id,\
                                                                ItemPriceList.item_id == item_dict.get('id'))).first()
                if item_price_list is not None:
                    dict_item_price = to_dict(item_price_list)
                    dict_item_price['id'] = str(dict_item_price['id'])
                    item_dict['price_list'] = dict_item_price
            # item_dict['topping'] = get_topping(item_dict, tenant_id)
            category_dict['items'].append(item_dict)
        results.append(to_dict(category_dict))
    return json({'categories': results, "options": get_option_service(service_no)}, status = 200)
def get_topping(parent_item, tenant_id):
    topping = []
    now_time = now_timestamp()
    categories = db.session.query(ItemCategory).join(ItemCategoryRelation).filter(
        ItemCategoryRelation.item_id == parent_item.get('id'),
        ItemCategory.category_type == 'topping',
        ItemCategory.deleted == False,
        ItemCategory.tenant_id == tenant_id
    ).all()
    active_price_list = PriceList.query.filter(and_(PriceList.tenant_id == tenant_id,\
        or_(and_(PriceList.start_time <= now_time,\
                PriceList.end_time >= now_time),\
            PriceList.is_default == True),\
        PriceList.deleted == False)).order_by(PriceList.is_default.desc()).first()

    for category in categories:
        category_dict = to_dict(category)
        category_dict['items'] = []
        items = db.session.query(Item).join(ItemCategoryRelation).filter(
            ItemCategoryRelation.category_id == category_dict.get('id'),
            Item.item_type == 'topping',
            Item.deleted == False, Item.tenant_id == tenant_id,
            Item.active == True).all()
        for item in items:
            item_dict = to_dict(item)

            if active_price_list is not None:
                # QUERY ITEM PRICE LIST
                item_price_list = ItemPriceList.query.filter(and_(ItemPriceList.tenant_id == tenant_id,\
                                                                ItemPriceList.price_list_id == active_price_list.id,\
                                                                ItemPriceList.item_id == item_dict.get('id'))).first()
                if item_price_list is not None:
                    dict_item_price = to_dict(item_price_list)
                    dict_item_price['id'] = str(dict_item_price['id'])
                    item_dict['price_list'] = dict_item_price

            item_dict['topping'] = []
            category_dict['items'].append(item_dict)

        category_item_relations = db.session.query(ItemCategoryRelation).filter(
            ItemCategoryRelation.item_id == parent_item.get('id'),
            ItemCategoryRelation.category_id == category.id
            ).first()
        category_item_relations_dict = to_dict(category_item_relations)
        del category_item_relations_dict['id']
        del category_item_relations_dict['category_id']
        del category_item_relations_dict['item_id']
        topping.append({**category_dict, **category_item_relations_dict})
    return topping

def get_topping_test(parent_item, tenant_id, active_price_list):
    topping = []
    now_time = now_timestamp()
    # categories = db.session.query(ItemCategory).join(ItemCategoryRelation).filter(
    #     ItemCategoryRelation.item_id == parent_item.get('id'),
    #     ItemCategory.category_type == 'topping',
    #     ItemCategory.deleted == False,
    #     ItemCategory.tenant_id == tenant_id
    # ).all()
    categories_ids = db.session.query(ItemCategoryRelation.category_id).filter(
        ItemCategoryRelation.item_id == parent_item.get('id'), 
        ItemCategoryRelation.tenant_id == tenant_id
    ).distinct(ItemCategoryRelation.category_id).all()

    categories = db.session.query(ItemCategory).filter(
        ItemCategory.id.in_(categories_ids),
        ItemCategory.category_type == 'topping',
        ItemCategory.deleted == False,
        ItemCategory.tenant_id == tenant_id
    ).all()

    all_item = db.session.query(Item, ItemCategoryRelation).join(ItemCategoryRelation).filter(
            ItemCategoryRelation.category_id.in_(categories_ids),
            Item.item_type == 'topping',
            Item.deleted == False, Item.tenant_id == tenant_id,
            Item.active == True).all()
    # all_item = []
    all_item_category_relations = db.session.query(ItemCategoryRelation).filter(
            ItemCategoryRelation.item_id == parent_item.get('id'),
            ItemCategoryRelation.tenant_id == tenant_id
            ).all()
    all_item_category_relations_dict = {}
    for item_category in all_item_category_relations:
        all_item_category_relations_dict[item_category.category_id] = to_dict(item_category)
    
    all_item_price_list = ItemPriceList.query.filter(and_(ItemPriceList.tenant_id == tenant_id,\
                                                        ItemPriceList.price_list_id == active_price_list.id,\
                                                        )).all()
    all_item_price_list_dict = {}
    for item_price_list in all_item_price_list:
        all_item_price_list_dict[str(item_price_list.item_id)] = item_price_list

    for category in categories:
        category_dict = to_dict(category)
        category_dict['items'] = []
        
        items = []
        for item, item_relation in all_item:
            if str(item_relation.category_id) == category_dict.get('id'):
                items.append(item)
        # items = []
        for item in items:
            item_dict = to_dict(item)

            if active_price_list is not None:
                # QUERY ITEM PRICE LIST
                # item_price_list = ItemPriceList.query.filter(and_(ItemPriceList.tenant_id == tenant_id,\
                #                                                 ItemPriceList.price_list_id == active_price_list.id,\
                #                                                 ItemPriceList.item_id == item_dict.get('id'))).first()
                # item_price_list = ItemPriceList()
                item_price_list = all_item_price_list_dict.get(item_dict.get('id'))
                if item_price_list is not None:
                    dict_item_price = to_dict(item_price_list)
                    dict_item_price['id'] = str(dict_item_price['id'])
                    item_dict['price_list'] = dict_item_price

            item_dict['topping'] = []
            category_dict['items'].append(item_dict)

        # category_item_relations = db.session.query(ItemCategoryRelation).filter(
        #     ItemCategoryRelation.item_id == parent_item.get('id'),
        #     ItemCategoryRelation.category_id == category.id
        #     ).first()
        # category_item_relations_dict = to_dict(category_item_relations)
        category_item_relations_dict = all_item_category_relations_dict.get(category.id)
        
        del category_item_relations_dict['id']
        del category_item_relations_dict['category_id']
        del category_item_relations_dict['item_id']
        topping.append({**category_dict, **category_item_relations_dict})
    return topping
@app.route('/v1/service/get/providers', methods=['GET'])
async def service_get_catagories(request):
    current_tenant = get_current_tenant(request)
    if current_tenant is None or 'error_code' in current_tenant:
        return json({
            'error_code': 'TENANT_UNKNOWN',
            'error_message': 'Thông tin request không xác định'
        }, status=523)

    tenant_id = current_tenant.get('id')
    now_time = now_timestamp()

    service_no = request.args.get('service_no')
    service_info = db.session.query(Service).filter(Service.service_no == service_no, Service.tenant_id == tenant_id).first()
    providers = service_info.providers
    service_info = to_dict(service_info)
    service_info['providers'] = []
    for provider in providers:
        service_info['providers'].append(to_dict(provider))
    service_info['options'] = get_option_service(service_no)
    return json(service_info, status = 200)


async def pre_process_save_service(request, data=None, **kw):
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
            new_service = Service()
            for key, value in data.items():
                if key in ['id','providers']:
                    continue
                if hasattr(new_service, key) and not isinstance(data.get(key), (dict,list)):
                    setattr(new_service, key, value)
            # print(new_item.__dict__.keys())
            new_service.tenant_id = tenant_id
            db.session.add(new_service)
            db.session.flush()
            data['id'] = str(new_service.id)
        elif request.method == 'PUT':
            current_service = db.session.query(Service).filter(and_(Service.tenant_id == tenant_id,\
                                                              Service.id == data.get('id')))
            is_exist = db.session.query(literal(True)).filter(current_service.exists()).scalar()
            if is_exist == True:
                tmp_item = Service()
                update_item = {}
                for key in data:
                    if key in ['id', 'providers', 'service_no', 'tenant_id']:
                        continue
                    if hasattr(tmp_item, key) == True:
                        update_item[key] = data.get(key)

                current_service.update(update_item)
                db.session.commit()

        # CHECK PROVIDERS
        if data.get('providers') is not None and isinstance(data['providers'], list):
            services_providers_ids = []
            for index, _ in enumerate(data['providers']):
                # print("id ==================  ", _)
                services_providers_ids.append(_.get('id'))
                # CHECK EXIST
                exist_service_provider_relation = ServicesProviders.query.filter(and_(ServicesProviders.tenant_id == tenant_id,\
                                                                                      ServicesProviders.provider_id == _.get('id'),\
                                                                                      ServicesProviders.service_id == data.get('id'))).first()
                if exist_service_provider_relation is None:
                    new_service_provider_relation = ServicesProviders()
                    new_service_provider_relation.provider_id = _.get('id')
                    new_service_provider_relation.service_id = data.get('id')
                    new_service_provider_relation.tenant_id = tenant_id
                    db.session.add(new_service_provider_relation)
            db.session.commit()
            # DELETE ALL UNUSE RELATIONS
            db.session.query(ServicesProviders).filter(and_(ServicesProviders.tenant_id == tenant_id,\
                                                               ServicesProviders.service_id == data.get('id'),\
                                                               ~ServicesProviders.provider_id.in_(services_providers_ids))).delete(synchronize_session=False)
        db.session.commit()
        return json(data)

async def pre_get_many_service(search_params=None, request=None, **kw):
    # print(search_params)
    if search_params.get('order_by') is None:
        search_params['order_by'] = [{"field":"created_at","direction":"asc"}]
    else:
        search_params['order_by'].append({"field":"created_at","direction":"asc"})
        

apimanager.create_api(Service,
    methods=['GET', 'POST', 'DELETE', 'PUT'],
    url_prefix='/v1',
    preprocess=dict(GET_SINGLE=[verify_access, pre_filter_by_tenant],
                    GET_MANY=[verify_access, pre_filter_by_tenant, pre_get_many_service],
                    POST=[verify_access, pre_post_set_tenant_id, pre_process_save_service],
                    PUT_SINGLE=[verify_access, pre_process_save_service]),
    postprocess=dict(GET_SINGLE=[],
                     GET_MANY=[],
                     PUT_SINGLE=[],
                     DELETE_SINGLE=[]),
    collection_name='service')

apimanager.create_api(ServicesProviders,
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
    collection_name='services_providers')