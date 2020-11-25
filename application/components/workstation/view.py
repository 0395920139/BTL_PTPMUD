from gatco.response import json, text, html
from gatco_restapi.helpers import to_dict
from application.extensions import apimanager
from application.database import db
from application.server import app
from application.components.base import verify_access, pre_filter_by_tenant, pre_post_set_tenant_id
from application.components.workstation.model import PointOfSale, Workstation


@app.route("/api/v1/workstation/get_all", methods=["GET"])
async def get_all_workstation(request):
    verify_access(request)

    workstations = Workstation.query.filter().all()

    results = []
    for ws in workstations:
        results.append(to_dict(ws))

    return json(results)


@app.route("/api/v1/workstation/get", methods=["GET"])
async def get_workstation_info(request):
    verify_access(request)

    exid = None
    try:
        exid = request.args.get("exid")
    except:
        pass

    if exid is not None:
        workstation = Workstation.query.filter(Workstation.workstation_exid == exid).first()
        return json(to_dict(workstation))

    return json(None)


apimanager.create_api(Workstation,
                      methods=['GET', 'POST', 'DELETE', 'PUT'],
                      url_prefix='/api/v1',
                      preprocess=dict(GET_SINGLE=[verify_access, pre_filter_by_tenant],
                                      GET_MANY=[verify_access, pre_filter_by_tenant],
                                      POST=[verify_access, pre_post_set_tenant_id],
                                      PUT_SINGLE=[verify_access]),
                      collection_name='workstation')


apimanager.create_api(PointOfSale,
                      methods=['GET', 'POST', 'DELETE', 'PUT'],
                      url_prefix='/api/v1',
                      preprocess=dict(GET_SINGLE=[verify_access, pre_filter_by_tenant],
                                      GET_MANY=[verify_access, pre_filter_by_tenant],
                                      POST=[verify_access, pre_post_set_tenant_id],
                                      PUT_SINGLE=[verify_access]),
                      collection_name='pointofsale')
