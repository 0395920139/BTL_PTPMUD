from datetime import datetime
import sqlalchemy
from sqlalchemy import or_, func, and_
from sqlalchemy.sql.expression import cast
from gatco.response import json, text, html
from gatco_restapi.helpers import to_dict
from application.extensions import apimanager, auth, jinja
from application.server import app
from application.database import db, notify_redisdb
from application.common.constants import ERROR_CODE, ERROR_MSG, STATUS_CODE
from application.components.base import verify_access, pre_post_set_tenant_id, get_current_tenant,\
    pre_filter_by_tenant
from application.common.helpers import now_timestamp
from application.common.httpclient import HTTPClient
from application.components.tenant.view import get_tenant_info
from application.config import Config
import firebase_admin 
from firebase_admin import credentials, messaging
import json as ujson

cred = credentials.Certificate("application/components/notify/serviceAccountKey.json") 
firebase_admin.initialize_app( cred )
# def sendPush(title, msg, registration_token, dataObject=None):
#     # See documentation on defining a message payload.
#     message = messaging.MulticastMessage(
#         notification=messaging.Notification(
#             title=title,
#             body=msg
#         ),
#         data=dataObject,
#         tokens=registration_token,
#     )

#     # Send a message to the device corresponding to the provided
#     # registration token.
#     response = messaging.send_multicast(message)
#     # Response is a message ID string.
#     print('Successfully sent message:', response)
# # @app.route('/v1/test_notify', methods=['GET'])
# # async def test_notify(request):
# #     tokens = ["evnxSBbdSHWPk-ZtjhjWpX:APA91bE-v-oiIoYktNWas-V2eJoCgyTGKM2fs8AtKAiMGsrHqU8kbrOnfekyxl2uts_SS84bY8MBbngEnQYKeDtChJeh7G74s3W_I8KPgrPZHwSzco4tvfafuKwAoNYLEoach1m9RbBj"]
# #             #evnxSBbdSHWPk-ZtjhjWpX:APA91bE-v-oiIoYktNWas-V2eJoCgyTGKM2fs8AtKAiMGsrHqU8kbrOnfekyxl2uts_SS84bY8MBbngEnQYKeDtChJeh7G74s3W_I8KPgrPZHwSzco4tvfafuKwAoNYLEoach1m9RbBj
# #     sendPush("Hi", "This is my next msg", tokens)

@app.route('/v1/notification/save_token', methods=['POST'])
async def set_notify_token(request):
    data = request.json
    if data is None:
        return json({
            'error_code': 'PARAMS_ERROR',
            'error_message': 'PARAMS_ERROR'
        }, status=520)
    firebase_access_token = request.headers.get('UPSTART-FIREBASE-KEY', None)
    # CHECK REQUEST ACCESS PERMISSION
    if firebase_access_token != Config.UPSTART_FIREBASE_KEY:
        return json({
            'error_code': 'AUTH_ERROR',
            'error_message': 'Authentication Error'
        }, status=523)
    app = data.get("app", None)
    device_id = data.get("device_id", None)
    token = data.get("token", None)
    if app is None or app not in Config.ALLOWED_APPS:
        return json({
            'error_code': 'APP PERMISSION DENIED',
            'error_message': 'Authentication App Error'
        }, status=520)
    notify_redisdb.set(app + "_" + str(device_id), token)
    return json({
        'ok': True
    }, status=200)

@app.route('/v1/notification/send_single', methods=['POST'])
async def send_single_notify(request):
    data_request = request.json
    if data_request is None:
        return json({
            'error_code': 'PARAMS_ERROR',
            'error_message': 'PARAMS_ERROR'
        }, status=520)
    firebase_access_token = request.headers.get('UPSTART-FIREBASE-KEY', None)
    # CHECK REQUEST ACCESS PERMISSION
    if firebase_access_token != Config.UPSTART_FIREBASE_KEY:
        return json({
            'error_code': 'AUTH_ERROR',
            'error_message': 'Authentication Error'
        }, status=523)

    app = data_request.get("app", None)
    device_id = data_request.get("device_id", None)
    data = data_request.get("data", None)
    # data = data.replace("\'", "\"")
    
    if app is None or app not in Config.ALLOWED_APPS:
        return json({
            'error_code': 'APP PERMISSION DENIED',
            'error_message': 'Authentication App Error'
        }, status=520)

    token = notify_redisdb.get(app + "_" + str(device_id))
    token = token.decode('utf8')
    # See documentation on defining a message payload.
    message = messaging.Message(
        data = data,
        token = token
    )
    response = messaging.send(message)
    # Response is a message ID string.
    return json({"ok": True}, status = 200)

@app.route('/v1/notification/send_multiple', methods=['POST'])
async def send_single_notify(request):
    data_request = request.json
    if data_request is None:
        return json({
            'error_code': 'PARAMS_ERROR',
            'error_message': 'PARAMS_ERROR'
        }, status=520)
    firebase_access_token = request.headers.get('UPSTART-FIREBASE-KEY', None)
    # CHECK REQUEST ACCESS PERMISSION
    if firebase_access_token != Config.UPSTART_FIREBASE_KEY:
        return json({
            'error_code': 'AUTH_ERROR',
            'error_message': 'Authentication Error'
        }, status=523)
    app = data_request.get("app", None)
    device_ids = data_request.get("device_ids", None)
    data = data_request.get("data", None)
    # print("---device_ids---",device_ids)
    # data = data.replace("\'", "\"")

    if app is None or app not in Config.ALLOWED_APPS:
        return json({
            'error_code': 'APP PERMISSION DENIED',
            'error_message': 'Authentication App Error'
        }, status=520)

    tokens = []
    for device_id in device_ids:
        token  = notify_redisdb.get(app + "_" + str(device_id))
        if token is not None:
            token = token.decode('utf8')
            tokens.append(token)
    
    message = messaging.MulticastMessage(
        data = data,
        tokens = tokens,
    )
    response = messaging.send_multicast(message)
    # Response is a message ID string.
    return json({"ok": True}, status = 200)

@app.route('/v1/notification/send_topic', methods=['POST'])
async def send_topic(request):
    data_request = request.json
    if data_request is None:
        return json({
            'error_code': 'PARAMS_ERROR',
            'error_message': 'PARAMS_ERROR'
        }, status=520)
    firebase_access_token = request.headers.get('UPSTART-FIREBASE-KEY', None)
    # CHECK REQUEST ACCESS PERMISSION
    if firebase_access_token != Config.UPSTART_FIREBASE_KEY:
        return json({
            'error_code': 'AUTH_ERROR',
            'error_message': 'Authentication Error'
        }, status=523)

    app = data_request.get("app", None)
    topic = data_request.get("topic", None)
    data = data_request.get("data", None)
    data = data.replace("\'", "\"")

    if app is None or app not in Config.ALLOWED_APPS:
        return json({
            'error_code': 'APP PERMISSION DENIED',
            'error_message': 'Authentication App Error'
        }, status=520)

    # See documentation on defining a message payload.
    message = messaging.Message(
        data = ujson.loads(data),
        topic = 'topic'
    )

    # Send a message to the devices subscribed to the provided topic.
    response = messaging.send(message)
    # Response is a message ID string.
    print('Successfully sent message:', response)
    return json({"ok": True}, status = 200)

@app.route('/v1/notification/test', methods=['POST'])
async def test(request):
    condition = "'stock-GOOG' in topics || 'industry-tech' in topics"
    message = messaging.Message(
        notification=messaging.Notification(
            title='$GOOG up 1.43% on the day',
            body='$GOOG gained 11.80 points to close at 835.67, up 1.43% on the day.',
        ),
        condition=condition,
    )

    # Send a message to devices subscribed to the combination of topics
    # specified by the provided condition.
    response = messaging.send(message)