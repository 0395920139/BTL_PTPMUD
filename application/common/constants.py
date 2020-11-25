STATUS_CODE = {
    "OK": 200,
    "ERROR": 520,
    "AUTH": 523
}


status = {
    "active": "active",
    "deactive": "deactive",
    "delete": "delete",
    "show": "show",
    "hide": "hide"
}


promotion_status = {
    "active": "active",
    "deactive": "deactive",
    "notified": "notified",
    "used": "used",
    "canceled": "canceled",
    "locked": "locked",
    "log": "log",
    "scanning": "scanning"
}

promotion_combine = {
    "allow_limit": "allow-limit",
    "allow": "allow",
    "not_allow": "not-allow",
    "allow_auto": "allow-auto"
}

order_status = {
    "new": "new",
    "quoted": "quoted",
    "done": "done",
    "canceled": "canceled"
}

send_status = {
    "pending": "pending",
    "sending": "sending",
    "success": "success",
    "responsed": "responsed",
    "error": "error"
}

MSG_CODE = {
    "SUCCESS": "SUCCESS"
}

MSG = {
    "SUCCESS": "Success"
}


ERROR_CODE = {
    "EXCEPTION": "EXCEPTION",
    "SERVER_ERROR": "SERVER_ERROR",
    "AUTH_ERROR": "AUTH_ERROR",
    "TOKEN_ERROR": "NOT_PERMISSION",
    "NOT_FOUND": "NOT_FOUND",
    "EXIST_ERROR": "EXIST_ERROR",
    "NULL_ERROR": "NULL_ERROR",
    "ARGS_ERROR": "ARGS_ERROR",
    "DATA_FORMAT": "DATA_FORMAT",
    "INPUT_DATA_ERROR": "INPUT_DATA_ERROR"
}

ERROR_MSG = {
    "EXCEPTION": "Handle Exception",
    "SERVER_ERROR": "Server error",
    "AUTH_ERROR": "Authentication is failed",
    "TOKEN_ERROR": "Permission denied",
    "EXIST_ERROR": "Record already exists",
    "NOT_FOUND": "Not Found",
    "NULL_ERROR": "Some fields are not allow to be empty",
    "ARGS_ERROR": "Get arguments error",
    "DATA_FORMAT": "Data format is not correct",
    "INPUT_DATA_ERROR": "Input data is not enough to handle the business"
}

NEED_PASS_PROMOTION_CONDITIONS = ["contact_group", "contact_score_in_range", "day_of_week"]

