STATUS = {
    "food_and_drink":[
        {"sostatus": "wait_confirm", "status_name": "chờ xác nhận", "color":"red"},
        {"sostatus": "confirmed", "status_name": "đã xác nhận", "color":"blue"},
        {"sostatus": "transporting", "status_name": "đang vận chuyển", "color":"#ff66b3"},
        {"sostatus": "finished", "status_name": "hoàn thành", "color":"green"}
    ],
    "minibar":[
        {"sostatus": "wait_confirm", "status_name": "chờ xác nhận", "color":"red"},
        {"sostatus": "confirmed", "status_name": "đã xác nhận", "color":"blue"},
        {"sostatus": "transporting", "status_name": "đang vận chuyển", "color":"#ff66b3"},
        {"sostatus": "finished", "status_name": "hoàn thành", "color":"green"}
    ],
    "table_booking":[
        {"sostatus": "wait_confirm", "status_name": "Gửi yêu cầu đặt bàn thành công", "color":"red"},
        {"sostatus": "confirmed", "status_name": "Nhân viên đã xác nhận", "color":"blue"}
    ],
    "spa":[
        {"sostatus": "wait_confirm", "status_name": "Gửi yêu cầu thành công", "color":"red"},
        {"sostatus": "confirmed", "status_name": "Nhân viên đã xác nhận", "color":"blue"}
    ],
    "laundry":[
        {"sostatus": "wait_confirm", "status_name": "Gửi yêu cầu thành công", "color":"red"},
        {"sostatus": "confirmed", "status_name": "Nhân viên đã xác nhận", "color":"blue"},
        {"sostatus": "processing", "status_name": "Đang thực hiện", "color":"#ff66b3"},
        {"sostatus": "finished", "status_name": "hoàn thành", "color":"green"}
    ],
    "cleaning_room_booking":[
        {"sostatus": "wait_confirm", "status_name": "Gửi yêu cầu thành công", "color":"red"},
        {"sostatus": "confirmed", "status_name": "Nhân viên đã xác nhận", "color":"blue"},
        {"sostatus": "processing", "status_name": "Đang thực hiện", "color":"#ff66b3"},
        {"sostatus": "finished", "status_name": "hoàn thành", "color":"green"}
    ]
}
def get_service_status(service_no):
    return STATUS.get(service_no)
