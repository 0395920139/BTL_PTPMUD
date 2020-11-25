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
# MODELS
from .model import Item, ItemCategory, ItemCategoryRelation, PriceList, ItemPriceList, ItemVariants, ItemCombo


# POST PROCESS ON GETTING ITEMS
async def post_process_get_item(request, instance_id=None, result=None, **kw):
    current_tenant = get_current_tenant(request)
    if current_tenant is None or 'error_code' in current_tenant:
        return json({
            'error_code': 'TENANT_UNKNOWN',
            'error_message': 'Thông tin request không xác định'
        }, status=523)
    tenant_id = current_tenant.get('id')
    now_time = now_timestamp()
    # GET SINGLE
    if result is not None and result.get('id') is not None:
        # PRICE LIST
        active_price_list = PriceList.query.filter(and_(PriceList.tenant_id == tenant_id,\
                                                        or_(and_(PriceList.start_time <= now_time,\
                                                                PriceList.end_time >= now_time),\
                                                            PriceList.is_default == True),\
                                                        PriceList.deleted == False)).order_by(PriceList.is_default.desc()).first()

        if active_price_list is not None:
            # QUERY ITEM PRICE LIST
            item_price_list = ItemPriceList.query.filter(and_(ItemPriceList.tenant_id == tenant_id,\
                                                               ItemPriceList.price_list_id == active_price_list.id,\
                                                               ItemPriceList.item_id == result.get('id'))).first()
            if item_price_list is not None:
                dict_item_price = to_dict(item_price_list)
                dict_item_price['id'] = str(dict_item_price['id'])
                result['price_list'] = dict_item_price

        # COMBO
        combos = []
        item_combos = db.session.query(ItemCombo).filter(and_(ItemCombo.parent_id == result.get('id'),\
                                                                  ItemCombo.tenant_id == tenant_id)).all()
        if item_combos is not None:
            for _ in item_combos:
                combo_dict = to_dict(_)
                combo_dict['id'] = str(combo_dict['id'])
                combos.append(combo_dict)
        result['combos'] = combos
        # VARIANTS
        variants = []
        item_variants = db.session.query(ItemVariants).filter(and_(ItemVariants.item_id == result.get('id'),\
                                                                  ItemVariants.tenant_id == tenant_id)).all()
        if item_variants is not None:
            for _ in item_variants:
                variant_dict = to_dict(_)
                variant_dict['id'] = str(variant_dict['id'])
                variants.append(variant_dict)
        result['variants'] = variants

        if isinstance(result.get('price_lists'), list) and result.get('price_lists') is not None:
            new_price_lists = []
            for price_list in result.get('price_lists'):
                item_price_list = ItemPriceList.query.filter(and_(ItemPriceList.tenant_id == tenant_id,\
                                                                    ItemPriceList.price_list_id == price_list.get('id'),\
                                                                    ItemPriceList.item_id == result.get('id'))).first()
                item_price_list = to_dict(item_price_list)
                del item_price_list['id']
                price_list = {**price_list, **item_price_list}
                new_price_lists.append(price_list)
            result['price_lists'] = new_price_lists

        # result['categories'] = [] 
        # categories = db.session.query(ItemCategory).join(ItemCategoryRelation, \
        # ItemCategory.id == ItemCategoryRelation.category_id).filter(           \
        #     ItemCategory.category_type == result.get('item_type'),
        #     ItemCategory.tenant_id == tenant_id,
        #     ItemCategory.deleted == False).all()
        # for cate in categories:
        #     result['categories'].append(to_dict(cate))
        if result.get('item_type') == 'default' or result.get('item_type') == 'combo':
            result['topping'] = []

            topping = []
            categories = db.session.query(ItemCategory, ItemCategoryRelation).join(ItemCategoryRelation).filter(
                ItemCategoryRelation.item_id == result.get('id'),
                ItemCategory.category_type == 'topping',
                ItemCategory.deleted == False,
                ItemCategory.tenant_id == tenant_id
            ).all()
            active_price_list = PriceList.query.filter(and_(PriceList.tenant_id == tenant_id,\
                or_(and_(PriceList.start_time <= now_time,\
                        PriceList.end_time >= now_time),\
                    PriceList.is_default == True),\
                PriceList.deleted == False)).order_by(PriceList.is_default.desc()).first()

            for category, item_category_relation in categories:
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
                item_category_relation = to_dict(item_category_relation)    
                # del item_category_relation['id']
                del category_dict['id']
                del item_category_relation['item_id']
                category_dict = {**category_dict, **item_category_relation}
                topping.append(to_dict(category_dict))
                result['topping'] = topping

    elif result is not None:
        active_price_list = PriceList.query.filter(and_(PriceList.tenant_id == tenant_id,\
                                                        or_(and_(PriceList.start_time <= now_time,\
                                                                PriceList.end_time >= now_time),\
                                                            PriceList.is_default == True),\
                                                        PriceList.deleted == False)).order_by(PriceList.is_default.desc()).first()
        if isinstance(result.get('objects'), list):
            for index, _ in enumerate(result['objects']):
                # JOIN PRICE LIST
                item_price_list = ItemPriceList.query.filter(and_(ItemPriceList.tenant_id == tenant_id,\
                                                                ItemPriceList.price_list_id == active_price_list.id,\
                                                                ItemPriceList.item_id == _.get('id'))).first()
                if item_price_list is not None:
                    dict_item_price = to_dict(item_price_list)
                    dict_item_price['id'] = str(dict_item_price['id'])
                    result['objects'][index]['price_list'] = dict_item_price
                # VARIANTS
                # item_variants = ItemVariants.query.filter(and_(ItemVariants.tenant_id == tenant_id,\
                #                                                ItemVariants.item_id == _.get('id'))).all()
                # variants = []
                # if item_variants is not None:
                #     for variant in item_variants:
                #         variant_dict = to_dict(variant)
                #         variant_dict['id'] = str(variant_dict['id'])
                #         variants.append(variant_dict)
                # result['objects'][index]['variants'] = variants
    
# PRE PROCESS ON SAVE ITEM
async def pre_process_save_item(request, data=None, **kw):
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
            new_item = Item()
            for key, value in data.items():
                if key in ['id', 'variants', 'categories', 'tenant_id', 'price_lists', 'extra_attributes']:
                    continue
                if hasattr(new_item, key) and not isinstance(data.get(key), (dict)):
                    setattr(new_item, key, value)
            # print(new_item.__dict__.keys())
            new_item.tenant_id = tenant_id
            db.session.add(new_item)
            db.session.commit()
            data['id'] = str(new_item.id)
        elif request.method == 'PUT':
            current_item = db.session.query(Item).filter(and_(Item.tenant_id == tenant_id,\
                                                              Item.id == data.get('id')))
            is_exist = db.session.query(literal(True)).filter(current_item.exists()).scalar()
            if is_exist == True:
                tmp_item = Item()
                update_item = {}
                for key in data:
                    if key in ['id', 'variants', 'categories', 'tenant_id', 'price_lists', 'extra_attributes']:
                        continue
                    if hasattr(tmp_item, key) == True:
                        update_item[key] = data.get(key)

                current_item.update(update_item)
                db.session.commit()

        # CHECK CATEGORY
        if data.get('categories') is not None and isinstance(data['categories'], list):
            item_category_ids = []
            for index, _ in enumerate(data['categories']):
                # print("id ==================  ", _)
                item_category_ids.append(_.get('id'))
                # if _.get('category_type') == 'default':
                #     item_category_ids.append(_.get('id'))
                # CHECK EXIST
                # category_info = db.session.query(ItemCategory).filter(ItemCategory.id == _.get('id')).first()
                # if category_info is not None and category_info.category_type == 'default':
                #     item_category_ids.append(_.get('id'))

                exist_item_category_relation = ItemCategoryRelation.query.filter(and_(ItemCategoryRelation.tenant_id == tenant_id,\
                                                                                      ItemCategoryRelation.category_id == _.get('id'),\
                                                                                      ItemCategoryRelation.item_id == data.get('id'))).first()
                if exist_item_category_relation is None:
                    new_item_category_relation = ItemCategoryRelation()
                    new_item_category_relation.category_id = _.get('id')
                    new_item_category_relation.item_id = data.get('id')
                    new_item_category_relation.tenant_id = tenant_id
                    # new_item_category_relation.extra_data = _.get('extra_data')
                    db.session.add(new_item_category_relation)
                
            db.session.commit()
            # DELETE ALL UNUSE RELATIONS
            db.session.query(ItemCategoryRelation).filter(and_(ItemCategoryRelation.tenant_id == tenant_id,\
                                                               ItemCategoryRelation.item_id == data.get('id'),\
                                                               ~ItemCategoryRelation.category_id.in_(item_category_ids))).delete(synchronize_session=False)
        # PRICE LIST
        active_price_list = None
        if data.get('price_list') is not None and data['price_list'].get('price_list_id') is not None:
            active_price_list = db.session.query(PriceList).filter(and_(PriceList.tenant_id == tenant_id,\
                                                                        PriceList.id == data['price_list'].get('price_list_id'))).first()
        else:
            active_price_list = db.session.query(PriceList).filter(and_(PriceList.tenant_id == tenant_id,\
                                                                        or_(and_(PriceList.start_time <= now_time,\
                                                                                PriceList.end_time >= now_time),\
                                                                            PriceList.is_default == True),\
                                                                        PriceList.deleted == False)).order_by(PriceList.is_default.desc()).first()

        # print ("active_price_list ", active_price_list)
        if active_price_list is not None:
            current_variant_price_list = db.session.query(ItemPriceList).filter(and_(ItemPriceList.tenant_id == tenant_id,\
                                                                                   ItemPriceList.price_list_id == active_price_list.id,\
                                                                                   ItemPriceList.item_id == data.get('id')))

            exist_variant_price_list = db.session.query(literal(True)).filter(current_variant_price_list.exists()).scalar()

            if data.get('price_list') is not None:
                variants = []
                if data['price_list'].get('variants') is not None:
                    variants = data['price_list'].get('variants')

                if isinstance(variants, list) and len(variants) > 0:
                    if exist_variant_price_list == True:
                        current_variant_price_list.update({
                            'variants': variants,
                            'list_price': 0,
                            'delivery_price': 0
                        })
                        db.session.commit()
                    else:
                        new_variant_price_list = ItemPriceList()
                        new_variant_price_list.tenant_id = tenant_id
                        new_variant_price_list.price_list_id = active_price_list.id
                        new_variant_price_list.item_id = data.get('id')
                        new_variant_price_list.variants = variants
                        new_variant_price_list.list_price = 0
                        new_variant_price_list.delivery_price = 0
                        db.session.add(new_variant_price_list)
                        db.session.commit()
                        
                else:
                    if exist_variant_price_list == True:
                        delivery_price = data['price_list'].get('delivery_price', 0)
                        list_price = data['price_list'].get('list_price')
                        current_variant_price_list.update({
                            'variants': None,
                            'list_price': float(list_price) if list_price is not None else 0,
                            'delivery_price': float(delivery_price) if delivery_price is not None else 0
                        })
                        db.session.commit()
                    else:
                        print ("<>><>><><><> CREATE ITEM PRICE LIST")
                        new_variant_price_list = ItemPriceList()
                        new_variant_price_list.tenant_id = tenant_id
                        new_variant_price_list.price_list_id = active_price_list.id
                        new_variant_price_list.item_id = data.get('id')
                        new_variant_price_list.list_price = float(data['price_list'].get('list_price'))
                        new_variant_price_list.delivery_price = float(data['price_list'].get('delivery_price', 0))
                        new_variant_price_list.variants = None
                        db.session.add(new_variant_price_list)
                        db.session.commit()
                        print ("<>><>><><><> DONE ITEM PRICE LIST")

        # VARIANTS
        variants_ids = []
        if data.get('variants') is not None and isinstance(data['variants'], list):
            for index, _ in enumerate(data['variants']):
                variants_ids.append(_.get('id'))
                item_variant = db.session.query(ItemVariants).filter(and_(ItemVariants.tenant_id == tenant_id,\
                                                                          ItemVariants.item_id == data.get('id')))
                is_item_variant_exist = db.session.query(literal(True)).filter(item_variant.exists()).scalar()
                if is_item_variant_exist == True:
                    # UPDATE
                    update_variant = {
                        'variant_name': _.get('variant_name'),
                        'variant_attr': _.get('variant_attr'),
                        'item_id': data.get('id'),
                        'sort_number': index + 1,
                        'variants_details': _.get('variants_details')
                    }
                    item_variant.update(update_variant)
                else:
                    # CREATE
                    new_item_variant = ItemVariants()
                    new_item_variant.variant_name = _.get('variant_name')
                    new_item_variant.variant_attr = _.get('variant_attr')
                    new_item_variant.item_id = data.get('id')
                    new_item_variant.sort_number = index + 1
                    new_item_variant.variants_details = _.get('variants_details')
                    db.session.add(new_item_variant)
                    db.session.flush()

            db.session.commit()
        # DELETE ALL VARIANTS NOT IN LIST
        unuse_variants = db.session.query(ItemVariants).filter(and_(ItemVariants.tenant_id == tenant_id,\
                                                                    ItemVariants.item_id == data.get('id'),\
                                                                    ~ItemVariants.id.in_(variants_ids))).delete(synchronize_session=False)

        if data.get("price_lists") is not None and isinstance(data.get("price_lists"), list):
            for _ in data.get("price_lists"):
                if _.get('item_id') is None:
                    _['item_id'] = data.get('id')
                item_price_list = db.session.query(ItemPriceList).filter(
                    ItemPriceList.item_id == _.get('item_id'),
                    ItemPriceList.price_list_id == _.get('price_list_id')
                )
                item_price_list_exist = db.session.query(literal(True)).filter(item_price_list.exists()).scalar()
                print('--item_price_list_exist---', item_price_list_exist)
                if not item_price_list_exist:
                    new_item_price_list = ItemPriceList()
                    for key, value in _.items():
                        if key in ['id']:
                            continue
                        if hasattr(new_item_price_list, key) and not isinstance(value, (dict, list)):
                            setattr(new_item_price_list, key, value)
                        # if key == 'item_id':
                        #     setattr(new_item_price_list, key, data.get('id'))
                            
                    # print('asdgasgdag', to_dict(new_item_price_list))
                    new_item_price_list.tenant_id = tenant_id
                    db.session.add(new_item_price_list)
                else:
                    item_price_list.update({
                        "list_price": _.get('list_price'),
                        "delivery_price": _.get('delivery_price'),
                        "image": _.get('image'),
                        "variants": _.get('variants'),
                        "note": _.get('note'),
                        "extra_data": _.get('extra_data')
                    })
                db.session.commit()
        return json(data)

@app.route('/v1/item/get/categories', methods=['GET'])
async def create_default_price_list(request):
    item_id = request.args.get('item_id')
    if item_id is not None:
        current_tenant = get_current_tenant(request)
        result = []
        categories = db.session.query(ItemCategory).join(ItemCategoryRelation).filter(
            ItemCategoryRelation.category_id == ItemCategory.id,
            ItemCategoryRelation.item_id == item_id).all()
        for category in categories:
            result.append(to_dict(category))
        print('category categories', result)  
        return json({'categories': result}, status = 200)
    else:
        return json({'categories':[]})

@app.route('/v1/item/get/topping', methods=['GET'])
async def get_topping(request):
    current_tenant = get_current_tenant(request)
    if current_tenant is None or 'error_code' in current_tenant:
        return json({
            'error_code': 'TENANT_UNKNOWN',
            'error_message': 'Thông tin request không xác định'
        }, status=523)

    tenant_id = current_tenant.get('id')
    now_time = now_timestamp()

    item_id = request.args.get('item_id')

    topping = []
    active_price_list = PriceList.query.filter(and_(PriceList.tenant_id == tenant_id,\
        or_(and_(PriceList.start_time <= now_time,\
                PriceList.end_time >= now_time),\
            PriceList.is_default == True),\
        PriceList.deleted == False)).order_by(PriceList.is_default.desc()).first()

    categories_ids = db.session.query(ItemCategoryRelation.category_id).filter(
        ItemCategoryRelation.item_id == item_id, 
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
            ItemCategoryRelation.item_id == item_id,
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
    
    return json({"categories": topping}, status = 200)

apimanager.create_api(Item,
    methods=['GET', 'POST', 'DELETE', 'PUT'],
    url_prefix='/v1',
    preprocess=dict(GET_SINGLE=[verify_access, pre_filter_by_tenant],
                    GET_MANY=[verify_access, pre_filter_by_tenant],
                    POST=[verify_access, pre_post_set_tenant_id, pre_process_save_item],
                    PUT_SINGLE=[verify_access, pre_process_save_item]),
    # postprocess=dict(GET_SINGLE=[post_process_get_item],
    #                  GET_MANY=[post_process_get_item],
    #                  PUT_SINGLE=[],
    #                  DELETE_SINGLE=[]),
    postprocess=dict(
        GET_SINGLE=[post_process_get_item],
        GET_MANY=[post_process_get_item]
    ),
    collection_name='item')

apimanager.create_api(ItemCategory,
    methods=['GET', 'POST', 'DELETE', 'PUT'],
    url_prefix='/v1',
    preprocess=dict(GET_SINGLE=[verify_access, pre_filter_by_tenant],
                    GET_MANY=[verify_access, pre_filter_by_tenant],
                    POST=[verify_access, pre_post_set_tenant_id],
                    PUT_SINGLE=[verify_access]),
    collection_name='item_category')

apimanager.create_api(ItemCategoryRelation,
    methods=['GET', 'POST', 'DELETE', 'PUT'],
    url_prefix='/v1',
    preprocess=dict(GET_SINGLE=[verify_access, pre_filter_by_tenant],
                    GET_MANY=[verify_access, pre_filter_by_tenant],
                    POST=[verify_access, pre_post_set_tenant_id],
                    PUT_SINGLE=[verify_access]),
    collection_name='items_categories')


apimanager.create_api(ItemVariants,
    methods=['GET', 'POST', 'DELETE', 'PUT'],
    url_prefix='/v1',
    preprocess=dict(GET_SINGLE=[verify_access, pre_filter_by_tenant],
                    GET_MANY=[verify_access, pre_filter_by_tenant],
                    POST=[verify_access, pre_post_set_tenant_id],
                    PUT_SINGLE=[verify_access]),
    collection_name='item_variants')

apimanager.create_api(ItemCombo,
    methods=['GET', 'POST', 'DELETE', 'PUT'],
    url_prefix='/v1',
    preprocess=dict(GET_SINGLE=[verify_access, pre_filter_by_tenant],
                    GET_MANY=[verify_access, pre_filter_by_tenant],
                    POST=[verify_access, pre_post_set_tenant_id],
                    PUT_SINGLE=[verify_access]),
    collection_name='item_combo')

apimanager.create_api(PriceList,
    methods=['GET', 'POST', 'DELETE', 'PUT'],
    url_prefix='/v1',
    preprocess=dict(GET_SINGLE=[verify_access, pre_filter_by_tenant],
                    GET_MANY=[verify_access, pre_filter_by_tenant],
                    POST=[verify_access, pre_post_set_tenant_id],
                    PUT_SINGLE=[verify_access]),
    collection_name='price_list')


apimanager.create_api(ItemPriceList,
    methods=['GET', 'POST', 'DELETE', 'PUT'],
    url_prefix='/v1',
    preprocess=dict(GET_SINGLE=[verify_access, pre_filter_by_tenant],
                    GET_MANY=[verify_access, pre_filter_by_tenant],
                    POST=[verify_access, pre_post_set_tenant_id],
                    PUT_SINGLE=[verify_access]),
    collection_name='item_price_list')


