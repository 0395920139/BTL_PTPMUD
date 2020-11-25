from datetime import datetime
import sqlalchemy
from sqlalchemy import or_, func, and_
from sqlalchemy.sql.expression import cast
from gatco.response import json, text, html
from gatco_restapi.helpers import to_dict
from application.extensions import apimanager, auth, jinja
from application.server import app
from application.database import db
from application.common.constants import ERROR_CODE, ERROR_MSG, STATUS_CODE
from application.components.base import verify_access, pre_post_set_tenant_id, get_current_tenant,\
    pre_filter_by_tenant
from application.common.helpers import now_timestamp
from application.common.httpclient import HTTPClient
from application.components.tenant.view import get_tenant_info
# MODELS
from application.components import Room, ContactRoomSession, Device

@app.route('/v1/room/get/available', methods=['GET'])
async def get_room_available(request):
    current_tenant = get_current_tenant(request)
    if current_tenant is None or 'error_code' in current_tenant:
        return json({
            'error_code': 'TENANT_UNKNOWN',
            'error_message': 'Thông tin request không xác định'
        }, status=523)

    tenant_id = current_tenant.get('id')
    now_time = now_timestamp()
    list_room_busy_ids = db.session.query(ContactRoomSession.room_id).filter(
        ContactRoomSession.end_time >= now_time,
        ContactRoomSession.checkout == True,
        ContactRoomSession.tenant_id == tenant_id,
    ).distinct(ContactRoomSession.room_id).all()

    rooms_availabel = db.session.query(Room).filter(
        Room.active == True, 
        ~Room.id.in_(list_room_busy_ids)
    ).all()

    results = []
    for room in rooms_availabel:
        results.append(to_dict(room))
    return json({'results': results}, status = 200)

@app.route('/v1/filter_room', methods=['GET'])
async def filter_room(request):
    current_tenant = get_current_tenant(request)
    if current_tenant is None or 'error_code' in current_tenant:
        return json({
            'error_code': 'TENANT_UNKNOWN',
            'error_message': 'Thông tin request không xác định'
        }, status=523)
    tenant_id = current_tenant.get('id')
    device_id = request.args.get('device_id')
    room = db.session.query(Room).join(Device).filter(Device.device_id == device_id, Device.tenant_id == tenant_id).first()
    result = to_dict(room)
    return json(result, status=200)
    
apimanager.create_api(
    Room,
    methods=['GET', 'POST', 'DELETE', 'PUT'],
    url_prefix='/v1',
    preprocess=dict(GET_SINGLE=[verify_access, pre_filter_by_tenant],
                    GET_MANY=[verify_access, pre_filter_by_tenant],
                    POST=[verify_access, pre_post_set_tenant_id],
                    PUT_SINGLE=[verify_access]),
    postprocess=dict(
        GET_SINGLE=[],
        GET_MANY=[],
        POST=[],
        PUT=[]
    ),
    collection_name='room'
)