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
# from websocket import create_connection
import json as ujson
from application.database import socket_redisdb
from application.config import Config

# def generate_expirable_token(data, time_duration):
#     # token = binascii.hexlify(uuid.uuid4().bytes).decode()

#     # pipe = redisdb.pipeline()
#     # pipe.set("sessions:" + token, data)
#     # if (time_duration > 0):
#     #     pipe.expire("sessions:" + token, time_duration)
#     # pipe.execute()
#     return token
@app.route('/v1/push_socket', methods=['GET', 'POST'])
async def test(request):
    data = request.json
    if data is None:
        return json({
            'error_code': 'PARAMS_ERROR',
            'error_message': 'PARAMS_ERROR'
        }, status=520)
    web_socket_access_token = request.headers.get('UPSTART-WEB-SOCKET-KEY', None)
    # CHECK REQUEST ACCESS PERMISSION
    if web_socket_access_token != Config.UPSTART_WEB_SOCKET_KEY:
        return json({
            'error_code': 'AUTH_ERROR',
            'error_message': 'Authentication Error'
        }, status=523)
    if data.get('tenant_id') is None:
        return json({
            'error_code': 'BAD REQUEST',
            'error_message': 'require tenant_id in body'
        }, status=400)
    if data.get('data') is None:
        return json({
            'error_code': 'BAD REQUEST',
            'error_message': 'require data in body'
        }, status=400)
    socket_redisdb.set(data.get('tenant_id'), ujson.dumps(data.get('data')))
    return json({"ok": True})
