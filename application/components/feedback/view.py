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
from application.components import FeeadBack, Device

async def pre_set_room_by_device_id(request, data=None, **kw):
    current_tenant = get_current_tenant(request)
    if current_tenant is None or 'error_code' in current_tenant:
        return json({
            'error_code': 'TENANT_UNKNOWN',
            'error_message': 'Thông tin request không xác định'
        }, status=523)
    tenant_id = current_tenant.get('id')
    if data.get('device_id') is None:
        return json({
            'error_code': 'PARAM_MISSING',
            'error_message': 'Thiếu device id'
        }, status=523)
    if data.get('contact_id') is None:
        return json({
            'error_code': 'PARAM_MISSING',
            'error_message': 'Thiếu contact id'
        }, status=523)
    
    device_info = db.session.query(Device).filter(Device.device_id == data.get('device_id')).first()
    data['room_id'] = str(device_info.room_id)



apimanager.create_api(
    FeeadBack,
    methods=['GET', 'POST', 'DELETE', 'PUT'],
    url_prefix='/v1',
    preprocess=dict(GET_SINGLE=[verify_access, pre_filter_by_tenant],
                    GET_MANY=[verify_access, pre_filter_by_tenant],
                    POST=[verify_access, pre_post_set_tenant_id, pre_set_room_by_device_id],
                    PUT_SINGLE=[verify_access]),
    postprocess=dict(
        GET_SINGLE=[],
        GET_MANY=[],
        POST=[],
        PUT=[]
    ),
    collection_name='feedback'
)