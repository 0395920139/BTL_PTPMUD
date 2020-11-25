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
from application.components import Post

# @app.route('/v1/update_thumbnail', methods=['GET'])
# async def update(request):
#     current_tenant = get_current_tenant(request)
#     if current_tenant is None or 'error_code' in current_tenant:
#         return json({
#             'error_code': 'TENANT_UNKNOWN',
#             'error_message': 'Thông tin request không xác định'
#         }, status=523)

#     tenant_id = current_tenant.get('id')
#     posts = db.session.query(Post).filter(Post.tenant_id == tenant_id).all()
#     for post in posts:
#         if post.thumbnail == "https://s3-alpha-sig.figma.com/img/00a2/767a/c209c3bef75a57f4fcaa03551dd31bcb?Expires=1605484800&Signature=REC4tR0yrtdUOwMSO5lXGPcY~ijrCvuhBN4Jl~I1oFrzHNtyxKA00Y5M4zkDc2tVSeRCqM835Qzk5EiXrZHiCc8hWCEPrXEYYXh2ebenlMDIiemlDJbiu8gGssnZO~cqkZI3A8c-YjFZm5sGhf4FsPjfV7ji7yfAPoZtXyN6oB6EMMt3vwQTepalDEN-MWnz3OmeF~NLqFE694d-q7sLjYEKah~LNPwQnXobm9cLhKbf3Wny8~oeHRJJ97w412f9hzr9sKmXNwN3BG6LPtztDTuxY8p0wbn45T249Z9AH~y1Mux2hEocstgk27JJ1mVA5DGRIiUqLLPz7pbFIHfbNg__&Key-Pair-Id=APKAINTVSUGEWH5XD5UA":
#             post.thumbnail = "https://upstart.vn/static/upload/upinstantpage/830526101231606202260215.jpg"
#             db.session.add(post)
#     db.session.commit()
#     return json({"ok": True})
apimanager.create_api(
    Post,
    methods=['GET', 'POST', 'DELETE', 'PUT'],
    url_prefix='/v1',
    preprocess=dict(GET_SINGLE=[verify_access, pre_filter_by_tenant],
                    GET_MANY=[verify_access, pre_filter_by_tenant],
                    POST=[verify_access, pre_post_set_tenant_id],
                    PUT_SINGLE=[verify_access]),
    postprocess=dict(
        GET_SINGLE=[],
        GET_MANY=[],
        POST=[],
        PUT=[]
    ),
    collection_name='post'
)