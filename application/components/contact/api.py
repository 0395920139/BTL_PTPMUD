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
from application.common.helpers import convert_datetime_format,\
    convert_phone_number, phone_detector, now_timestamp, get_datetime_timezone
from application.common.barcode_generator import get_barcode_png
from application.common.httpclient import HTTPClient
from application.components.tenant.view import get_tenant_info
# MODELS
from application.components import Contact, ContactNoSeq, ContactCategory, ContactNote,\
    Salesorder, ContactTags, ContactTagsDetails, ContactRoomSession, Room, Device


def get_next_contact_no(request):
    current_tenant = get_current_tenant(request)
    contact_no_seq = db.session.query(ContactNoSeq).filter(ContactNoSeq.id == current_tenant.get('id')).with_for_update().first()
    if contact_no_seq is None:
        contact_no_seq = ContactNoSeq()
        contact_no_seq.id = current_tenant.get('id')
        contact_no_seq.current_no = 1
    else:
        contact_no_seq.current_no += 1
    db.session.add(contact_no_seq)
    db.session.commit()
    # db.session.rollback()
    return contact_no_seq.current_no


def make_stable_data(request, data=None, **kw):
    if data is not None:
        if 'phone' in data or data.get('phone') is not None:
            data['phone'] = convert_phone_number(data.get('phone'), '0')

        if 'gender' in data and data['gender'] is not None and data['gender'] != "":
            if data['gender'].lower() == 'male' or data['gender'].lower() == 'anh' or data['gender'].lower() == 'nam'\
                    or data['gender'].lower() == 'ông' or data['gender'].lower() == 'ngài':
                data['gender'] = 'male'
            else:
                data['gender'] = 'female'

        if data.get('birthday', None) is not None and data.get('birthday', "") != "":
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
    else:
        return json({
            "error_code": ERROR_MSG['DATA_FORMAT'],
            "error_message": ERROR_MSG['DATA_FORMAT']
        }, status=STATUS_CODE['ERROR'])


# CRETAE NEW CONTACT
@app.route('/api/v1/contact/create', methods=['POST'])
async def create_contact(request):
    current_tenant = get_current_tenant(request)
    tenant_id = current_tenant.get('id')
    data = request.json
    if data is None:
        return json({
            'error_code': '',
            'error_message': ''
        }, status=520)

    make_stable_data(request, data)
    # CHECK CONTACT EXIST
    exist_contact = Contact.query.filter(and_(Contact.tenant_id == tenant_id,\
                                              Contact.phone == data.get('phone'))).first()
    if exist_contact is not None:
        return json({
            'error_code': 'RECORD_EXIST',
            'error_message': 'Bản ghi đã tồn tại'
        }, status=520)

    contact = Contact()
    for key in data:
        if hasattr(contact, key) == True:
            setattr(contact, key, data[key])
        else:
            print (">>>>>> ", key, data[key])

    # GENERATE CONTACT NO
    contact_no_seq = db.session.query(ContactNoSeq).filter(ContactNoSeq.id == tenant_id).with_for_update().first()
    if contact_no_seq is None:
        contact_no_seq = ContactNoSeq()
        contact_no_seq.id = tenant_id
        contact_no_seq.current_no = 1
    else:
        contact_no_seq.current_no += 1

    contact.contact_no = contact_no_seq.current_no
    contact.tenant_id = tenant_id
    try:
        db.session.add(contact)
        db.session.commit()
        db.session.add(contact_no_seq)
        db.session.commit()
    except:
        db.session.rollback()

    # TAGS
    if data.get('tags') is not None and isinstance(data['tags'], list):
        for tag in data['tags']:
            # FIND EXIST
            exist_tag = ContactTags.query.filter(and_(ContactTags.tenant_id == tenant_id,\
                                                      ContactTags.id == tag.get('id'))).first()
            contact_tags_id = None
            if exist_tag is None:
                # CREATE NEW TAGS
                new_tag = ContactTags()
                new_tag.tag_label = tag.get('tag_label')
                new_tag.tag_ascii = tag.get('tag_ascii')
                new_tag.tenant_id = tenant_id
                db.session.add(new_tag)
                db.session.commit()
                contact_tags_id = new_tag.id
            else:
                contact_tags_id = exist_tag.id

            # CREATE CONTACT TAGS DETAILS
            new_contact_tags_details = ContactTagsDetails()
            new_contact_tags_details.contact_id = contact.id
            new_contact_tags_details.contact_tags_id = contact_tags_id
            new_contact_tags_details.timestamp = now_timestamp()
            new_contact_tags_details.tenant_id = tenant_id
            db.session.add(new_contact_tags_details)
            db.session.commit()
        

    return json({
        'id': str(contact.id)
    })


@app.route("/v1/contact/get/config", methods=["GET"])
async def get_config(request):
    current_tenant = get_current_tenant(request)
    if current_tenant is None or 'error_code' in current_tenant:
        return json({
            'error_code': 'TENANT_UNKNOWN',
            'error_message': 'Thông tin request không xác định'
        }, status=523)
    # room_id = request.args.get("room_id")
    device_id = request.args.get("device_id")
    # contact_id = request.args.get("contact_id")

    tenant_id = current_tenant.get('id')
    now_time = now_timestamp()
    filters = [
        ContactRoomSession.tenant_id == tenant_id,
        ContactRoomSession.end_time >= now_time,
        ContactRoomSession.start_time <= now_time
    ]

    if device_id is not None:
        device = db.session.query(Device).filter(Device.device_id == device_id).first()
        filters.append(ContactRoomSession.room_id == device.room_id)
        contact_room_session = db.session.query(ContactRoomSession).filter(*filters).first()
        if contact_room_session is not None:
            contact_room_session = to_dict(contact_room_session)
            contact = db.session.query(Contact).filter(Contact.id == contact_room_session.get('contact_id')).first()
            room = db.session.query(Room).filter(Room.id == contact_room_session.get('room_id')).first()
            contact_room_session['contact'] = to_dict(contact)
            contact_room_session['room'] = to_dict(room)
            contact_room_session['device'] = to_dict(device)
            return json(contact_room_session, status = 200)
        else:
            contact_room_session = ContactRoomSession()
            return json(to_dict(contact_room_session), status = 200)
    else:
        return json({"error_code": "MISSING PARAMETER",
                     "error_message": "Không tìm thấy param device_id"}, status = 422)