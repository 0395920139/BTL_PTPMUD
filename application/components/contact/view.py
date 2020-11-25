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
from application.components import Contact, ContactNoSeq, ContactNote, ContactTags, ContactRoomSession, Device
import requests
import json as ujson
characters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'K',
              "L", 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'Y']


def get_next_contact_no(request):
    current_tenant = get_current_tenant(request)
    print ("<><><> current_tenant ", current_tenant)
    contact_no_seq = db.session.query(ContactNoSeq).filter(ContactNoSeq.id == current_tenant.get('id')).with_for_update().first()
    print ("<><> contact_no_seq <><> ", contact_no_seq)
    if contact_no_seq is None:
        contact_no_seq = ContactNoSeq()
        contact_no_seq.id = current_tenant.get('id')
        contact_no_seq.current_no = 1
    else:
        contact_no_seq.current_no += 1
    db.session.add(contact_no_seq)
    db.session.commit()
    print (">>>>>>>>>>>>>>>>>> " + str(contact_no_seq.current_no) + " <<<<<<<<<<<<<<<<<<")
    return contact_no_seq.current_no



# MAX VALUE: 528.999 for 5 characters of code length (AB123)
# MAX VALUE: 5.289.999 for 6 characters of code length (AB1234)
# MAX VALUE: 52.899.990 for 7 characters of code length (AB12345)
def convert_code(value):
    contact_code_prefix = get_contact_code_prefix() if get_contact_code_prefix() is not None else ""

    contact_code_length = int(get_contact_code_length()) if get_contact_code_length() is not None else 6

    value = str(value)
    if len(value) <= (contact_code_length - 1):
        value = generate_zerostring(contact_code_length - len(value)) + value
#     count = 0
#     result = None
#     for c in characters:
#         for c1 in characters:
#             head_str = c + c1
#             if count == int(str(value)[:-(contact_code_length - 2)]):
#                 result = head_str + str(value)[-(contact_code_length - 2):]
#             count += 1
    return str(value)


def convert_gender(value):
    gender = None
    if value is not None and value != "":
        if value.lower() == 'male' or value.lower() == 'anh' or value.lower() == 'nam'\
                or value.lower() == 'ông' or value.lower() == 'ngài' or value == 1:
            gender = 'male'
        else:
            gender = 'female'

    return gender

#
# generate number of '0' basing on contact_no
# to map length of contact_code
#


def generate_zerostring(num=8):
    zeroStr = ''.join(random.choice("0") for _ in range(num))
    return zeroStr


def separate_birthday_date(data=None, **kw):
    if data is not None:
        if data['birthday'] is not None and data['birthday'] != "":
            dob = None
            try:
                # 1994-07-12
                dob = convert_datetime_format(data['birthday'], "%Y-%m-%d")
                if dob is not None:
                    d = datetime.strptime(dob, "%Y-%m-%d")
                    data['bdate'] = d.day
                    data['bmonth'] = d.month
                    data['byear'] = d.year
                    data['birthday'] = dob
                else:
                    data['birthday'] = None
            except:
                data['birthday'] = None


def separate_birthday_object(data=None, **kw):
    if data is not None:
        if data.birthday is not None and data.birthday != "":
            dob = None
            try:
                # 1994-07-12
                dob = convert_datetime_format(data.birthday, "%Y-%m-%d")
                if dob is not None:
                    d = datetime.strptime(dob, "%Y-%m-%d")
                    data.bdate = d.day
                    data.bmonth = d.month
                    data.byear = d.year
                    data.birthday = dob
                else:
                    data.birthday = None
            except:
                data.birthday = None

async def get_code_image(request=None, instance_id=None, result=None, **kw):
    if result is not None:
        barcode_path = app.config.get('BARCODE_STORAGE_PATH')
        contact_prefix = get_contact_code_prefix()
        if contact_prefix is None:
            contact_prefix = ''
        contact_no = result.get('contact_no')
        if contact_no is not None:
            contact_code = str(contact_prefix).upper() + convert_code(contact_no)
            img_path = barcode_path + contact_code

            headers = {
                'content-type': 'application/json'
            }
            params = {
                'code': contact_code,
                'path': img_path
            }
            response = await HTTPClient.get(app.config.get('UPSTART_COMMON_SERVICES') + '/api/barcode/get', params, headers)
            if response is not None and response.get('path', None) is not None:
                result['contact_barcode'] = contact_code + '.png'


async def create_code_image(data=None, **kw):
    if data is not None:
        barcode_path = app.config.get('BARCODE_STORAGE_PATH')
        contact_prefix = get_contact_code_prefix()
        if contact_prefix is None:
            contact_prefix = ''
        contact_no = data.get('contact_no')
        if contact_no is not None:
            contact_code = str(contact_prefix).upper() + convert_code(contact_no)

            headers = {
                'content-type': 'application/json'
            }
            data = {
                'file_type': 'png',
                'code': contact_code,
                'path': barcode_path + contact_code
            }
            result = await HTTPClient.post(app.config.get('UPSTART_COMMON_SERVICES') + '/api/barcode/create', data, headers)

            if result is not None and result.get('path', None) is not None:
                data['contact_barcode'] = contact_code + '.png'

#
# 0.4 update some attr
#
@app.route("/api/v1/contact/attrs", methods=["POST", "PUT", "OPTIONS"])
async def update_properties(request):
    verify_access(request)
    if request.method == "OPTIONS":
        return json(None)
    try:
        data = request.json
        if data is None:
            return json({"error_code": "", "error_message": ""}, status=520)

        contact_dict = dynamic_save_contact(data)

        return json(contact_dict)

    except:
        return json({
            "error_code": ERROR_CODE['EXCEPTION'],
            "error_message": ERROR_MSG['EXCEPTION']
        }, status=STATUS_CODE['ERROR'])


async def dynamic_save_contact(request, data):
    contact_dict = None
    try:
        if 'id' in data and data['id'] is not None:
            contact = Contact.query.get(data['id'])
            if contact is not None:
                for name, value in data.items():
                    if name != 'id':
                        setattr(contact, name, value)

                        if name == "birthday":
                            try:
                                separate_birthday_object(contact)
                            except:
                                pass
        # create
        elif 'id' not in data or data['id'] is None or contact is None:
            contact = Contact()
            for name, value in data.items():
                if name != 'id':
                    setattr(contact, name, value)

                    if name == "birthday":
                        try:
                            separate_birthday_object(contact)
                        except:
                            pass

            generate_contact_no_obj(request, contact)
        db.session.add(contact)
        db.session.commit()
        contact_dict = to_dict(contact)
        create_code_image(contact_dict)
    except:
        pass
    return contact_dict

async def send_notify_to_device(request, instance_id=None, result=None, **kw):
    room_id = result.get('room_id')
    list_device_ids = []
    devices = db.session.query(Device).filter(Device.room_id == room_id).all()
    for device in devices:
        list_device_ids.append(str(device.device_id))

    url_notify = "https://furama.upgo.vn/api/v1/notification/send_multiple"
    data = ujson.dumps({ "data": {"type":"has_user_checkin"}, "app": "upgo_furama", "device_ids": list_device_ids})
    headers = {
                'content-type': 'application/json',
                'UPSTART-FIREBASE-KEY': '07jZNydE4C9OXqC4IjNcMyBk7hCpivz9qIW37ZvZsuBdK35gdIhN4IY1NqfTJCSZ'
            }
    requests.post(url_notify, data = data, headers=headers)

apimanager.create_api(
    Contact,
    methods=['GET', 'POST', 'DELETE', 'PUT'],
    url_prefix='/v1',
    preprocess=dict(
        GET_SINGLE=[verify_access, pre_filter_by_tenant],
        GET_MANY=[verify_access, pre_filter_by_tenant],
        POST=[verify_access, pre_post_set_tenant_id],
        PUT_SINGLE=[verify_access]),
    postprocess=dict(
        GET_SINGLE=[],
        GET_MANY=[],
        POST=[],
        PUT=[]
    ),
    collection_name='contact'
)

apimanager.create_api(
    ContactRoomSession,
    methods=['GET', 'POST', 'DELETE', 'PUT'],
    url_prefix='/v1',
    preprocess=dict(
        GET_SINGLE=[verify_access, pre_filter_by_tenant],
        GET_MANY=[verify_access, pre_filter_by_tenant],
        POST=[verify_access, pre_post_set_tenant_id],
        PUT_SINGLE=[verify_access]),
    postprocess=dict(
        GET_SINGLE=[],
        GET_MANY=[],
        POST=[send_notify_to_device],
        PUT=[]
    ),
    collection_name='contact_room_session'
)


apimanager.create_api(
    ContactNote,
    methods=['GET', 'POST', 'DELETE', 'PUT'],
    url_prefix='/api/v1',
    preprocess=dict(
        GET_SINGLE=[verify_access, pre_filter_by_tenant],
        GET_MANY=[verify_access, pre_filter_by_tenant],
        POST=[verify_access],
        PUT_SINGLE=[verify_access]),
    postprocess=dict(
        GET_SINGLE=[],
        POST=[],
    ),
    collection_name='contactnote'
)

apimanager.create_api(
    ContactTags,
    methods=['GET', 'POST', 'DELETE', 'PUT'],
    url_prefix='/api/v1',
    preprocess=dict(
        GET_SINGLE=[verify_access, pre_filter_by_tenant],
        GET_MANY=[verify_access, pre_filter_by_tenant],
        POST=[verify_access],
        PUT_SINGLE=[verify_access]),
    postprocess=dict(
        GET_SINGLE=[],
        POST=[],
    ),
    collection_name='contact_tags'
)
