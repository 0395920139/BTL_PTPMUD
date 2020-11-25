from sqlalchemy import or_
from sqlalchemy.sql import func
from gatco.response import json, text, html
from gatco_restapi.helpers import to_dict
from application.extensions import apimanager
from application.server import app
from application.components.base import verify_access
from application.components import Tenant


def get_tenant_info(tenant_id):
    tenant = Tenant.query.get(tenant_id)
    if tenant is not None:
        return to_dict(tenant)
    return None


@app.route('/tenant/set_current_tenant', methods=['POST'])
async def set_current_tenant(request):
    verify_access(request)

    body_data = request.json

    tenant_id = body_data.get('tenant_id', None)
    if tenant_id is None:
        return json({
            'error_code': 'DATA_ERROR',
            'error_message': 'Dữ liệu không hợp lệ'
        }, status=520)

    request['session']['current_tenant_id'] = tenant_id

    return json({}, status=200)


apimanager.create_api(
    Tenant,
    methods=['GET', 'POST', 'DELETE', 'PUT'],
    url_prefix='/api/v1',
    preprocess=dict(
        GET_SINGLE=[],
        GET_MANY=[],
        POST=[],
        PUT_SINGLE=[]),
    collection_name='tenant'
)
