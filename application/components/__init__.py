from application.extensions import jinja
from gatco.response import json, text, html


from application.components.schema.model import *
# from application.components.contact.model import *
# from application.components.currency.model import *
# from application.components.service.model import *
# from application.components.item.model import *
# from application.components.salesorder.model import *
# from application.components.tenant.model import *
# from application.components.user.model import *
# from application.components.workstation.model import *
# from application.components.integration.model import *
# from application.components.room.model import *
# from application.components.device.model import *
# from application.components.provider.model import *
# from application.components.post.model import *
# from application.components.feedback.model import *

# from application.components.table_booking.model import *
# from application.components.cleaning_room_booking.model import *
# from application.components.spa_booking.model import *

def init_components(app):
    import application.components.schema.view
    # import application.components.contact.view
    # import application.components.contact.api
    # import application.components.contact.contact_tags_api
    # import application.components.currency.view
    # import application.components.item.view
    # import application.components.item.api
    

    # import application.components.salesorder.view
    # import application.components.user.view
    # import application.components.workstation.view
    # import application.components.tenant.view
    # import application.components.integration.view

    # import application.components.room.view
    # import application.components.device.view
    # import application.components.service.view
    # import application.components.provider.view
    # import application.components.post.view
    # import application.components.feedback.view
    # # import application.components.table_booking.view
    # # import application.components.cleaning_room_booking.view
    # # import application.components.spa_booking.view

    # import application.components.notify.view
    # report
    # import application.components.report.salesorder_report
    # import application.components.report.contact_report
    # import application.components.report.item_report

    @app.route('/')
    def index(request):
        return jinja.render('layout.html', request)
