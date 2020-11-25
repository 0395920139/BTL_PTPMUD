import os
import requests
import ujson
from datetime import datetime
from sqlalchemy import literal
from sqlalchemy import and_, or_
from gatco.response import json
from gatco import Blueprint
from gatco.response import json, text, html
from gatco_restapi.helpers import to_dict
from application.extensions import apimanager
from application.extensions import auth
from application.database import db
from application.server import app
from application.common.constants import ERROR_CODE, ERROR_MSG, STATUS_CODE
#

ACCESS_TOKEN = "DSRD1FYGJXfO4PRvr3vPKSQ8xHXnScamSPNJiCdPnjrhW6Ad0VQyBwuX1gaIg8UY"


def get_current_tenant(request):
    if app.config.get('ENVIRONMENT') == 'development':
        return {
            'id': 'furama',
            'tenant_name': 'Furama',
            'active': True
        }
    from application.components.tenant.model import Tenant
    current_tenant_id = request['session'].get('current_tenant_id', None)
    if current_tenant_id is None:
        if request.headers.get('tenant_id') is not None:
            current_tenant_id = request.headers.get('tenant_id')
        else:
            return {
                'error_code': 'NONE_CURRENT_TENANT',
                'error_message': 'Current tenant not found'
            }

    current_tenant = Tenant.query.get(current_tenant_id)
    
    if current_tenant is None:
        return None

    return to_dict(current_tenant)



def auth_func(request=None, **kw):
    try:
        access_token = request.headers.get('access_token')
        if access_token is not None and access_token == ACCESS_TOKEN:
            return {
                "valid": True
            }
        else:
            return {
                "valid": False,
                "error": {
                    "error_code": ERROR_CODE['AUTH_ERROR'],
                    "error_message": ERROR_MSG['AUTH_ERROR']
                },
                "status": 523
            }
    except:
        return {
            "valid": False,
            "error": {
                "error_code": ERROR_CODE['AUTH_ERROR'],
                "error_message": ERROR_MSG['AUTH_ERROR']
            },
            "status": 523
        }


def verify_access(request, **kw):
    if app.config.get('ENVIRONMENT') == 'development':
        pass
    else:
        access_token = request.headers.get('access_token')
        current_user = auth.current_user(request)
        if access_token == ACCESS_TOKEN:
            pass

        elif current_user is not None:
            pass

        else:
            return json({
                'error_code': 'AUTH_ERROR',
                'error_message': 'Authentication failed'
            }, status=520)


async def pre_post_set_tenant_id(request, data=None, **kw):
    if data is not None:
        current_tenant = get_current_tenant(request)
        if current_tenant is None or 'error_code' in current_tenant:
            if data.get('tenant_id', None) is None:
                return json(current_tenant, status=523)
        else:
            data['tenant_id'] = current_tenant.get('id')



async def pre_filter_by_tenant(search_params=None, request=None, **kw):

    current_tenant = get_current_tenant(request)
    if current_tenant is None or 'error_code' in current_tenant:
        
        return json(current_tenant, status=523)

    if search_params is None:
        search_params = {
            "filters": {}
        }
    if 'filters' not in search_params:
        search_params['filters'] = {}
    search_params['filters']['tenant_id'] = {
        "$eq": current_tenant.get('id')
    }

    # print ("search_params ", search_params)

