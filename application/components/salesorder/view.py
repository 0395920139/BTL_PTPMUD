from datetime import datetime
from sqlalchemy import or_, and_, literal
from sqlalchemy.sql import func
from application.extensions import apimanager
from gatco.response import json
from application.server import app
from application.database import db
from gatco_restapi.helpers import to_dict
from application.common.helpers import now_timestamp

from application.components.base import verify_access, get_current_tenant,\
    pre_filter_by_tenant, pre_post_set_tenant_id
from application.common.constants import ERROR_CODE, ERROR_MSG
# MODELS
from application.components import Salesorder, SalesorderItems, SalesorderLog, Item, ItemCategory, ItemCategoryRelation,\
PriceList, ItemPriceList, ItemVariants, Service, Device

from application.components.salesorder.saleorder_status import get_service_status
import copy
import json as ujson
import requests
async def pre_process_save_sale_order(request, data=None, **kw):
    if data is not None:
        current_tenant = get_current_tenant(request)
        if current_tenant is None or 'error_code' in current_tenant:
            return json({
                'error_code': 'TENANT_UNKNOWN',
                'error_message': 'Thông tin request không xác định'
            }, status=523)

        tenant_id = current_tenant.get('id')
        now_time = now_timestamp()

        device_info = db.session.query(Device).filter(Device.device_id == data.get('device_id')).first()
        room_id = str(device_info.room_id)

        if request.method == 'POST':
            # CREATE ITEM FIRST
            new_sale_order = Salesorder()
            for key, value in data.items():
                if key in ['id','salesorder_items','forward_status']:
                    continue
                if hasattr(new_sale_order, key) and not isinstance(data.get(key), (dict,list)):
                    setattr(new_sale_order, key, value)
            # print(new_item.__dict__.keys())
            new_sale_order.tenant_id = tenant_id

            book_time_obj = datetime.fromtimestamp(data.get("book_time")//1000)
            new_sale_order.book_day = book_time_obj.day
            new_sale_order.book_month = book_time_obj.month
            new_sale_order.book_year = book_time_obj.year
            new_sale_order.book_hour = book_time_obj.hour
            new_sale_order.book_minute = book_time_obj.minute
            new_sale_order.book_day_of_week = book_time_obj.weekday()
            new_sale_order.room_id = room_id

            db.session.add(new_sale_order)
            db.session.commit()
            data['id'] = str(new_sale_order.id)
            await push_socket_to_cms(tenant_id, data)
        elif request.method == 'PUT':
            current_sale_order = db.session.query(Salesorder).filter(and_(Salesorder.tenant_id == tenant_id,\
                                                              Salesorder.id == data.get('id')))
            is_exist = db.session.query(literal(True)).filter(current_sale_order.exists()).scalar()
            if is_exist == True:
                tmp_sale_order = Salesorder()
                update_sale_order = {}
                for key in data:
                    if key in ['salesorder_items','forward_status', 'room', 'service', 'contact', 'provider', 'currency']:
                        continue
                    if hasattr(tmp_sale_order, key) == True:
                        update_sale_order[key] = data.get(key)
                        # setattr(update_sale_order, key, data.get(key))
                book_time_obj = datetime.fromtimestamp(data.get("book_time")//1000)
                update_sale_order["book_day"] = book_time_obj.day
                update_sale_order["book_month"] = book_time_obj.month
                update_sale_order["book_year"] = book_time_obj.year
                update_sale_order["book_hour"] = book_time_obj.hour
                update_sale_order["book_minute"] = book_time_obj.minute
                update_sale_order["book_day_of_week"] = book_time_obj.weekday()
                update_sale_order["room_id"] = room_id
                print(update_sale_order)
                current_sale_order.update(update_sale_order)
                db.session.commit()

        # SAVE SALE ORDER ITEMS
        if data.get("salesorder_items") is not None and isinstance(data.get("salesorder_items"), list):
            await insert_saleorders_items(
                data = data.get("salesorder_items"), 
                tenant_id = tenant_id, 
                salesorder_id = data.get("id"),
                salesorder_discount_percent = data.get("salesorder_discount_percent", 0), 
                salesorder_discount_amount = data.get("salesorder_discount_amount",0)
            )
        new_sale_order_log = SalesorderLog()
        new_sale_order_log.salesorder_id = data.get("id")
        new_sale_order_log.sostatus = data.get('sostatus', 'wait_confirm')
        new_sale_order_log.status = "done"
        new_sale_order_log.tenant_id = tenant_id
        db.session.add(new_sale_order_log)
        db.session.commit()
        # result = db.session.query(Salesorder).filter(Salesorder.id == data.get('id')).first()
        # result = to_dict(result)
        
        return json(data)

async def insert_saleorders_items(data, tenant_id, salesorder_id, salesorder_discount_percent, salesorder_discount_amount):
    data_spread = []
    saleorder_item_ids = {}
    for item in data:
        item['item_id'] = item.get('id')
        saleorder_item_ids[item.get('item_id')] = []
        if len(item.get('toppings', [])) == 0:
            pass
        else:
            for topping in item.get('toppings'):
                topping['parent_item_id'] = item.get('item_id')
                topping['item_id'] = topping.get('id')
                data_spread.append(topping)
                saleorder_item_ids[topping.get('id')] = []
                saleorder_item_ids[item.get('item_id')].append(topping.get('id'))
            # del item['toppings']
        data_spread.append(copy.deepcopy(item))
    if data_spread is not None and isinstance(data_spread, list):
        salesorder_amount = 0 #biến lưu thành tiền hóa đơn sau khi trừ discount
        salesorder_net_amount = 0 #biến lưu thành tiền hóa đơn trước khi trừ discount
        
        for index, _ in enumerate(data_spread):

            # if _.get('item_type') == 'default':
            #     saleorder_item_ids.append(_.get('item_id'))
            # if _.get('item_type') == 'topping':
            #     saleorder_topping_ids.append(_.get('item_id'))
            # CHECK EXIST
            exists_saleorder_item_relation = db.session.query(SalesorderItems).filter(and_(SalesorderItems.tenant_id == tenant_id,\
                                                                                    SalesorderItems.salesorder_id == salesorder_id,\
                                                                                    SalesorderItems.item_id == _.get('item_id'),\
                                                                                    SalesorderItems.parent_item_id == _.get('parent_item_id'))).first()
            if exists_saleorder_item_relation is None:
                new_sale_order_item = SalesorderItems()
                del saleorder_item_ids[_.get('item_id')]
                for key in _:
                    if key in ['id']:
                        continue
                    if hasattr(new_sale_order_item, key) == True:
                        setattr(new_sale_order_item, key, _.get(key))                    
                new_sale_order_item.salesorder_id = salesorder_id
                # active_price_list = db.session.query(PriceList).filter(and_(PriceList.tenant_id == tenant_id,\
                #                                                     or_(and_(PriceList.start_time <= now_time,\
                #                                                             PriceList.end_time >= now_time),\
                #                                                         PriceList.is_default == True),\
                #                                                     PriceList.deleted == False)).order_by(PriceList.is_default.desc()).first()
                # current_price_list = db.session.query(ItemPriceList).filter(and_(ItemPriceList.tenant_id == tenant_id,\
                #                                                                ItemPriceList.price_list_id == active_price_list.id,\
                #                                                                ItemPriceList.item_id == item.get('id'))).first()

                # item['current_price'] = current_price_list.list_price
                net_amount = _.get('price_list', {}).get('list_price', 0)*_.get('quantity', 1)
                amount = max(max(net_amount - _.get('discount_amount', 0), 0) - net_amount *_.get('discount_percent', 0)/100, 0)
                new_sale_order_item.net_amount = net_amount
                new_sale_order_item.amount = amount
                new_sale_order_item.tenant_id = tenant_id
                # print("item_id===============",_.get('item_id'))
                item_info = db.session.query(Item).filter(Item.id == _.get('item_id'), Item.tenant_id == tenant_id).first()
                new_sale_order_item.item_no = item_info.item_no
                new_sale_order_item.item_name = item_info.item_name
                new_sale_order_item.parent_item_id = _.get('parent_item_id')
                db.session.add(new_sale_order_item)
                db.session.commit()
                salesorder_net_amount += net_amount
                salesorder_amount += amount
        salesorder_amount = max(max(salesorder_amount - salesorder_discount_amount, 0) - salesorder_amount *(salesorder_discount_percent/100), 0)
        
        update_sale_order = db.session.query(Salesorder).filter(Salesorder.id == salesorder_id, Salesorder.tenant_id == tenant_id).first()
        update_sale_order.net_amount = salesorder_net_amount
        update_sale_order.amount = salesorder_amount
        db.session.add(update_sale_order)
        db.session.commit()

        # DELETE ALL UNUSE RELATIONS
        for item_id, topping_ids in saleorder_item_ids.items():
            delete_state = db.session.query(SalesorderItems).filter(and_(SalesorderItems.tenant_id == tenant_id,\
                                                            SalesorderItems.salesorder_id == salesorder_id,\
                                                            SalesorderItems.item_id == item_id))
            if len(topping_ids) != 0:
                delete_state.filter(~SalesorderItems.parent_item_id.in_(topping_ids))
            delete_state.delete(synchronize_session=False)

async def pre_process_get_salesorder(search_params=None, request=None, **kw):
    current_tenant = get_current_tenant(request)
    if current_tenant is None or 'error_code' in current_tenant:
        return json({
            'error_code': 'TENANT_UNKNOWN',
            'error_message': 'Thông tin request không xác định'
        }, status=523)
    tenant_id = current_tenant.get('id')
    service_no = request.args.get("service_no")
    if service_no is not None:
        service_info = db.session.query(Service).filter(Service.service_no == service_no).first()

        if search_params is None:
                search_params = {
                    "filters": {}
                }
        if 'filters' not in search_params:
            search_params['filters'] = {}

        search_params['filters']['service_id'] = {
            "$eq": str(service_info.id)
        }
# async def post_process_get_saleorder(request, instance_id=None, result=None, **kw):
#     current_tenant = get_current_tenant(request)
#     if current_tenant is None or 'error_code' in current_tenant:
#         return json({
#             'error_code': 'TENANT_UNKNOWN',
#             'error_message': 'Thông tin request không xác định'
#         }, status=523)
#     tenant_id = current_tenant.get('id')
#     if result is not None and result.get('id') is not None:

# @app.route('/v1/salesorder/update', methods= ['GET'])
# async def update(request):
#     current_tenant = get_current_tenant(request)
#     if current_tenant is None or 'error_code' in current_tenant:
#         return json({
#             'error_code': 'TENANT_UNKNOWN',
#             'error_message': 'Thông tin request không xác định'
#         }, status=523)
#     tenant_id = current_tenant.get('id')
#     salesorders = db.session.query(Salesorder).filter(Salesorder.tenant_id == tenant_id).all()
#     for salesorder in salesorders:
#         if salesorder.room_id == None:
#             device_info = db.session.query(Device).filter(Device.device_id == salesorder.device_id).first()
#             if device_info is not None:
#                 salesorder.room_id = device_info.room_id
#                 db.session.add(salesorder)
#     db.session.commit()
#     return json({"ok": True})

@app.route('/v1/salesorder/get/service_status', methods=['GET'])
async def service_status(request):
    current_tenant = get_current_tenant(request)
    if current_tenant is None or 'error_code' in current_tenant:
        return json({
            'error_code': 'TENANT_UNKNOWN',
            'error_message': 'Thông tin request không xác định'
        }, status=523)

    tenant_id = current_tenant.get('id')
    service_no = request.args.get('service_no')
    results = get_service_status(service_no)
    return json({"results":results}, status= 200)

@app.route('/v1/salesorder/get/history', methods= ['GET'])
async def history(request):
    current_tenant = get_current_tenant(request)
    if current_tenant is None or 'error_code' in current_tenant:
        return json({
            'error_code': 'TENANT_UNKNOWN',
            'error_message': 'Thông tin request không xác định'
        }, status=523)

    tenant_id = current_tenant.get('id')
    contact_id = request.args.get('contact_id')
    device_id = request.args.get('device_id')

    query_state = [Salesorder.tenant_id == tenant_id]

    # salesorder_query_state = db.session.query(Salesorder).filter(Salesorder.tenant_id == tenant_id)
    if contact_id is not None:
        query_state.append(Salesorder.contact_id == contact_id)
        # salesorder_query_state.filter(Salesorder.contact_id == contact_id)
    if device_id is not None:
        query_state.append(Salesorder.device_id == device_id)
        # salesorder_query_state.filter(Salesorder.device_id == device_id)
    
    salesorders = db.session.query(Salesorder).filter(*query_state).order_by(Salesorder.updated_at.asc()).all()
    # salesorders = salesorder_query_state.all()

    results = []
    for salesorder in salesorders:
        salesorder_dict = to_dict(salesorder)
        salesorder_dict['service'] = to_dict(salesorder.service)
        salesorder_dict['room'] = to_dict(salesorder.room)
        salesorder_dict['provider'] = to_dict(salesorder.provider)
        salesorder_dict['salesorder_items'] = []
        for item in salesorder.salesorder_items.all():
            salesorder_dict['salesorder_items'].append(to_dict(item))
        
        salesorder_dict['list_status'] = get_service_status(salesorder.service.service_no)
        status_name = "done"
        for status in salesorder_dict['list_status']:
            if status.get("sostatus") == salesorder_dict.get("sostatus"):
                status['status'] = status_name
                status_name = "pending"
                continue
            status['status'] = status_name
        results.append(copy.deepcopy(salesorder_dict))
    return json({"results": results},status = 200)

async def push_socket_to_cms(tenant_id, result=None, **kw):
    url_notify = "https://furama.upgo.vn/api/v1/push_socket"
    data = ujson.dumps({
        "data": result, 
        "app": "upgo_furama", 
        "tenant_id": tenant_id})
    headers = {
                'content-type': 'application/json',
                'UPSTART-WEB-SOCKET-KEY': '07jZNydE4C9OXqC4IjNcMyBk7hCpivz9qIW37ZvZsuBdK35gdIhN4IY1NqfTJCSZ'
            }
    requests.post(url_notify, data = data, headers=headers)

async def send_notify_to_device(request, data=None, **kw):
    room_id = data.get('room_id')
    list_device_ids = []
    devices = db.session.query(Device).filter(Device.room_id == room_id).all()
    for device in devices:
        list_device_ids.append(str(device.device_id))

    url_notify = "https://furama.upgo.vn/api/v1/notification/send_multiple"
    data = ujson.dumps({ "data": {"type":"has_saleorder_change"}, "app": "upgo_furama", "device_ids": list_device_ids})
    headers = {
                'content-type': 'application/json',
                'UPSTART-FIREBASE-KEY': '07jZNydE4C9OXqC4IjNcMyBk7hCpivz9qIW37ZvZsuBdK35gdIhN4IY1NqfTJCSZ'
            }
    requests.post(url_notify, data = data, headers=headers)

apimanager.create_api(Salesorder,
    methods=['GET', 'POST', 'DELETE', 'PUT'],
    url_prefix='/v1',
    preprocess=dict(
        GET_SINGLE=[verify_access, pre_filter_by_tenant],
        GET_MANY=[verify_access, pre_filter_by_tenant, pre_process_get_salesorder],
        POST=[verify_access, pre_post_set_tenant_id, pre_process_save_sale_order],
        PUT_SINGLE=[verify_access, send_notify_to_device, pre_process_save_sale_order]
    ),
    collection_name='salesorder')

apimanager.create_api(SalesorderItems,
    methods=['GET', 'POST', 'DELETE', 'PUT'],
    url_prefix='/v1',
    preprocess=dict(
        GET_SINGLE=[verify_access, pre_filter_by_tenant],
        GET_MANY=[verify_access, pre_filter_by_tenant],
        POST=[verify_access, pre_post_set_tenant_id],
        PUT_SINGLE=[verify_access]
    ),
    collection_name='salesorder_items')

apimanager.create_api(SalesorderLog,
    methods=['GET', 'POST', 'DELETE', 'PUT'],
    url_prefix='/v1',
    preprocess=dict(
        GET_SINGLE=[verify_access, pre_filter_by_tenant],
        GET_MANY=[verify_access, pre_filter_by_tenant],
        POST=[verify_access, pre_post_set_tenant_id],
        PUT_SINGLE=[verify_access]
    ),
    collection_name='salesorder_log')