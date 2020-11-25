import time
from sqlalchemy import and_, or_, literal
from gatco.response import json, text, html
from gatco_restapi.helpers import to_dict
from application.extensions import apimanager
from application.extensions import auth
from application.database import db
from application.server import app
from application.common.constants import STATUS_CODE, ERROR_CODE, ERROR_MSG
from application.components.base import verify_access, get_current_tenant, pre_filter_by_tenant, pre_post_set_tenant_id
from application.common.helpers import generate_salt, convert_phone_number
# Models
from application.components import User,Role,Permission

exclude_attrs = ['created_at', 'created_by', 'created_by_name', 'updated_at', 'updated_by', 'updated_by_name',\
    'deleted', 'deleted_at', 'deleted_by', 'deleted_by_name']

@auth.user_loader
def user_loader(token):
    if token is not None:
        if 'exprire' in token:
            if token['exprire'] < time.time():
                return None
            del(token["exprire"])
        return token
    return None


@auth.serializer
def serializer(user_info):
    auth_user = {
        'uid': user_info.get('id'),
        'exprire': time.time() + auth.expire
    }
    return auth_user


def preprocess_hash_password(data=None, **kw):
    if data is not None:

        if data.get('id', None) is None:
            data['id'] = str(uuid.uuid4())

        data['secret_key'] = generate_unique_key(128, True)
        data['salt'] = generate_salt()
        data['password'] = auth.encrypt_password(
            data['password'], data['salt'])


# ERROR CODE:
#  - E524: ERROR
#  - E504: DATA INPUT ERROR
#  - E523: AUTH ERROR
@app.route('/login', methods=['POST'])
async def login(request):
    data = request.json
    if data is None or data.get('username', None) is None or data.get('password', None) is None:
        return json({
            'error_code': 'AUTH_FAILED',
            'error_message': 'Username, password are required'
        }, status=523)

    username = data.get('username', None)
    password = data.get('password', None)

    login_user = db.session.query(User).filter(or_(User.phone == convert_phone_number(username),\
                                                    User.email == str(username).lower())).first()

    if login_user is None:
        return json({
            'error_code': 'E523',
            'error_message': 'Tài khoản không tồn tại.'
        }, status=523)
    
    if auth.verify_password(password, login_user.password, login_user.salt) == False:
        return json({
            'error_code': 'E523',
            'error_message': 'Mật khẩu không chính xác.'
        }, status=523)

    tenant_dict = to_dict(login_user.tenant)
    for key in exclude_attrs:
        if key in tenant_dict:
            del tenant_dict[key]

    login_user = to_dict(login_user)
    for key in exclude_attrs:
        if key in login_user:
            del login_user[key]

    request['session']['current_tenant_id'] = tenant_dict.get('id')
    login_user['tenant'] = tenant_dict
    auth.login_user(request, login_user)

    return json({
        'id': str(login_user.get('id')),
        'display_name': login_user.get('display_name'),
        'phone': login_user.get('phone'),
        'email': login_user.get('email'),
        'gender': login_user.get('gender'),
        'avatar': login_user.get('avatar'),
        'tenant': login_user.get('tenant'),
        'current_tenant_id': tenant_dict.get('id')
    })


@app.route('/logout')
async def logout(request):
    try:
        auth.logout_user(request)
    except:
        pass
    return json({})


@app.route('/current_user', methods=['GET'])
async def current_user(request):
    current_user = auth.current_user(request)
    if current_user is None:
        auth.logout_user(request)
        return json({
            "error_code": "E523",
            "error_message": "Phiên làm việc hết hạn!"
        }, status=520)

    uid = current_user['uid']
    if uid is None:
        auth.logout_user(request)
        return json({
            "error_code": "E523",
            "error_message": "Phiên làm việc hết hạn!"
        }, status=520)

    current_user = db.session.query(User).filter(and_(User.id == uid)).first()

    if current_user is None:
        return json({
            'error_code': 'NOT_EXIST',
            'error_message': 'User does not exist'
        }, status=520)
    
    if current_user.tenant is None:
        return json({
            'error_code': 'TENANT_UNKNOWN',
            'error_message': 'Request Unknown'
        }, status=523)

    tenant_dict = to_dict(current_user.tenant)
    for key in exclude_attrs:
        if key in tenant_dict:
            del tenant_dict[key]

    current_user = to_dict(current_user)
    for key in exclude_attrs:
        if key in current_user:
            del current_user[key]

    request['session']['current_tenant_id'] = tenant_dict.get('id')
    current_user['tenant'] = tenant_dict

    return json({
        'id': str(current_user.get('id')),
        'display_name': current_user.get('display_name'),
        'phone': current_user.get('phone'),
        'email': current_user.get('email'),
        'gender': current_user.get('gender'),
        'avatar': current_user.get('avatar'),
        'tenant': current_user.get('tenant'),
        'current_tenant_id': tenant_dict.get('id')
    })

    auth.logout_user(request)
    return json({
        "error_code": "SESSION_EXPIRED",
        "error_message": "Phiên làm việc hết hạn!"
    }, status=520)


@app.route('/change_password', methods=['POST'])
async def change_password(request):
    verify_access(request)

    current_tenant = get_current_tenant(request)
    if current_tenant is None or 'error_code' in current_tenant:
        return json({
            'error_code': 'TENANT_UNKNOW',
            'error_message': 'Request Unknown'
        }, status=523)

    current_user = auth.current_user(request)
    if current_user is None:
        auth.logout_user(request)
        return json({
            'error_code': 'E523',
            'error_message': 'Phiên làm việc hết hạn, đăng nhập lại.'
        }, status=523)

    current_tenant_id = current_tenant.get('id')
    current_user_id = current_user['uid']
    if current_user_id is None:
        auth.logout_user(request)
        return json({
            'error_code': 'E523',
            'error_message': 'Phiên làm việc hết hạn, đăng nhập lại.'
        }, status=523)

    user_info = db.session.query(User).filter(and_(User.tenant_id == current_tenant_id,\
                                                   User.id == current_user_id)).first()
    if user_info is None:
        return json({
            'error_code': 'E523',
            'error_message': 'Tài khoản không tồn tại.'
        }, status=520)

    body_data = request.json
    current_password = body_data.get('current_password', None)
    new_password = body_data.get('new_password', None)

    # CHECK CURRENT PASSWORD CORRECT OR NOT
    if auth.verify_password(current_password, user_info.password, user_info.salt) == False:
        return json({
            'error_code': 'E523',
            'error_message': 'Tên tài khoản hoặc mật khẩu không đúng'
        }, status=523)

    user_info.password = auth.encrypt_password(new_password, user_info['salt'])
    user_info.updated_at = now_timestamp()
    db.session.commit()
    return json({
        'code': 'S200',
        'message': 'Thành công'
    }, status=200)


@app.route("/api/v1/user/attrs", methods=["PUT"])
async def update_properties(request):
    verify_access(request)

    try:
        data = request.json
        if data is None or 'id' not in data or data['id'] is None:
            return json({"error_code": ERROR_CODE['DATA_FORMAT'], "error_message": ERROR_MSG['DATA_FORMAT']}, status=STATUS_CODE['ERROR'])

        contact = User.query.get(data['id'])
        if contact is not None:
            for name, value in data.items():
                if name != 'id':
                    setattr(contact, name, value)

            db.session.add(contact)
            db.session.commit()

            return json({"message": "success"})
    except:
        return json({"error_code": ERROR_CODE['EXCEPTION'], "error_message": ERROR_MSG['EXCEPTION']}, status=STATUS_CODE['ERROR'])


async def set_current_user(request, data, **kw):
    current_user = auth.current_user(request)
    if current_user is None:
        return json({
            'error_code': 'E523',
            'error_message': 'Phiên làm việc hết hạn, đăng nhập lại.'
        }, status=523)

    uid = current_user['uid']
    if uid is None or uid.find(".") <= 0:
        auth.logout_user(request)
        return json({
            'error_code': 'E523',
            'error_message': 'Phiên làm việc hết hạn, đăng nhập lại.'
        }, status=523)

    current_tenant_id = uid.split('.')[0]
    current_user_id = uid.split('.')[1]

    user_info = await motordb.db['user'].find_one({'tenant_id': current_tenant_id, 'id': str(current_user_id)})
    if user_info is not None:
        data["owner_id"] = str(user_info['_id'])


async def pre_process_create_user(request, data=None, **kw):
    if data is not None:
        tenant_id = None
        if data.get('tenant_id') is None:
            current_tenant = get_current_tenant(request)

            if current_tenant is None or 'error_code' in current_tenant:
                return json(current_tenant, status=523)
            tenant_id = current_tenant.get('id')
        else:
            tenant_id = data.get('tenant_id')

        if data.get('password') is not None:
            salt = generate_salt()
            data['salt'] = salt
            data['password'] = auth.encrypt_password(data.get('password'), salt)

        if 'confirm_password' in data:
            del data['confirm_password']

        if request.method == 'POST':
            data['tenant_id'] = tenant_id


        elif request.method == 'PUT':
            exclude_attrs = ['tenant_id']
            for key in exclude_attrs:
                if key in data:
                    del data[key]
            
            if 'password' in data and data.get('password') == None:
                del data['password']


apimanager.create_api(User,
                      methods=['GET', 'POST', 'DELETE', 'PUT'],
                      url_prefix='/v1',
                      preprocess=dict(GET_SINGLE=[verify_access],
                                      GET_MANY=[verify_access],
                                      POST=[verify_access, pre_process_create_user],
                                      PUT_SINGLE=[verify_access, pre_process_create_user]),
                      exclude_columns=['password', 'salt', 'created_at', 'created_by', 'created_by_name', 'updated_at',
                      'updated_by', 'updated_by_name', 'deleted_at', 'deleted_by', 'deleted_by_name'],
                      collection_name='user')


apimanager.create_api(Role,
                      methods=['GET', 'POST', 'DELETE', 'PUT'],
                      url_prefix='/v1',
                      preprocess=dict(GET_SINGLE=[verify_access, pre_filter_by_tenant],
                                      GET_MANY=[verify_access, pre_filter_by_tenant],
                                      POST=[verify_access, pre_post_set_tenant_id],
                                      PUT_SINGLE=[verify_access]),
                      collection_name='role')

apimanager.create_api(Permission,
                      methods=['GET', 'POST', 'DELETE', 'PUT'],
                      url_prefix='/v1',
                      preprocess=dict(GET_SINGLE=[verify_access, pre_filter_by_tenant],
                                      GET_MANY=[verify_access, pre_filter_by_tenant],
                                      POST=[verify_access, pre_post_set_tenant_id],
                                      PUT_SINGLE=[verify_access]),
                      collection_name='permission')
