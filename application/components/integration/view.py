from datetime import datetime
from sqlalchemy import or_, func, and_
from sqlalchemy.sql.expression import cast
from gatco.response import json, text, html
from gatco_restapi.helpers import to_dict
from application.extensions import apimanager, auth, jinja
from application.server import app
from application.database import db
from application.common.constants import ERROR_CODE, ERROR_MSG, STATUS_CODE
from application.components.base import verify_access
from application.common.helpers import now_timestamp
from application.common.httpclient import HTTPClient
# MODELS
from .model import Partner


apimanager.create_api(
    Partner,
    methods=['GET', 'POST', 'DELETE', 'PUT'],
    url_prefix='/api/v1',
    preprocess=dict(
        GET_SINGLE=[verify_access],
        GET_MANY=[verify_access],
        POST=[verify_access],
        PUT_SINGLE=[verify_access]),
    postprocess=dict(
        GET_SINGLE=[],
        GET_MANY=[],
        POST=[],
        PUT=[]
    ),
    collection_name='partner'
)
