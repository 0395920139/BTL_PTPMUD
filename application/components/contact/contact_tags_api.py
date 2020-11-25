import copy
import sqlalchemy
from sqlalchemy import or_, func, and_
from sqlalchemy.sql.expression import cast
from gatco.response import json, text, html
from gatco_restapi.helpers import to_dict
from application.extensions import apimanager, auth, jinja
from application.server import app
from application.database import db
from application.common.constants import ERROR_CODE, ERROR_MSG, STATUS_CODE
from application.components.base import verify_access, get_current_tenant
from application.common.helpers import now_timestamp
# MODELS
from application.components import Contact, ContactTags, ContactTagsDetails
#from gatco.exceptions import ServerError


@app.route('/api/v1/contact_tags/get_contact_by_tags', methods=['POST'])
async def get_contact_by_tags(request):
    verify_access(request)
    current_tenant = get_current_tenant(request)
    if current_tenant is None or 'error_code' in current_tenant:
        return json({
            'error_code': 'TENANT_UNKNOWN',
            'error_message': 'Thông tin request không xác định'
        }, status=523)

    tenant_id = current_tenant.get('id')
    body_data = request.json
    if body_data is None or isinstance(body_data, list) == False or len(body_data) == 0:
        return json({
            'error_code': 'BODY_DATA_ERROR',
            'error_message': 'Dữ liệu không đúng định dạng'
        }, status=520)

    tags_ids = [_.get('id') for _ in body_data]

    contact_tags_details = db.session.query(ContactTagsDetails.contact_id,\
        func.count(ContactTagsDetails.id)).filter(and_(ContactTagsDetails.tenant_id == tenant_id,\
                                                       ContactTagsDetails.contact_tags_id.in_(tags_ids))).group_by(ContactTagsDetails.contact_id).all()

    results = []
    if contact_tags_details is not None and isinstance(contact_tags_details, list):
        for tag_detail in contact_tags_details:
            if tag_detail[1] == len(tags_ids):
                results.append(str(tag_detail[0]))

    return json(results)
