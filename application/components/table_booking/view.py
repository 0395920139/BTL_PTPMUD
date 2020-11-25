import uuid, copy
from application.extensions import apimanager
from sqlalchemy import or_, and_, func, literal
from sqlalchemy.sql.expression import cast
from gatco_restapi.helpers import to_dict
from gatco.response import json, text, html
from application.server import app
from application.database import db
from application.common.helpers import now_timestamp
from application.components.base import verify_access, get_current_tenant,\
    pre_filter_by_tenant, pre_post_set_tenant_id
from application.components.item.model import Item, ItemCategory, ItemCategoryRelation, PriceList, ItemPriceList, ItemVariants


# MODELS
# from .model import TableBooking

# apimanager.create_api(TableBooking,
#     methods=['GET', 'POST', 'DELETE', 'PUT'],
#     url_prefix='/v1',
#     preprocess=dict(GET_SINGLE=[verify_access, pre_filter_by_tenant],
#                     GET_MANY=[verify_access, pre_filter_by_tenant],
#                     POST=[verify_access, pre_post_set_tenant_id],
#                     PUT_SINGLE=[verify_access]),
#     # postprocess=dict(GET_SINGLE=[post_process_get_item],
#     #                  GET_MANY=[post_process_get_item],
#     #                  PUT_SINGLE=[],
#     #                  DELETE_SINGLE=[]),
#     collection_name='table_booking')