from gatco.response import json, text, html
from application.extensions import apimanager
from .model import Currency
from application.database import db
from application.server import app
from application.components.base import verify_access, pre_filter_by_tenant


apimanager.create_api(Currency,
                      methods=['GET', 'POST', 'DELETE', 'PUT'],
                      url_prefix='/api/v1',
                      preprocess=dict(GET_SINGLE=[verify_access, pre_filter_by_tenant],
                                      GET_MANY=[verify_access, pre_filter_by_tenant],
                                      POST=[verify_access],
                                      PUT_SINGLE=[verify_access]),
                      collection_name='currency')
