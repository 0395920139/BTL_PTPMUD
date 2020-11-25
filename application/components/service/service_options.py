OPTIONS = {
    "table_booking":
        {
            "max_people": 20,
            "hours": [
                {"keyword": "6h", "name": "6h"},
                {"keyword": "6h30p", "name": "6h30p"},
                {"keyword": "7h", "name": "7h"},
                {"keyword": "7h30p", "name": "7h30p"},
                {"keyword": "8h", "name": "8h"},
                {"keyword": "8h30p", "name": "3h30p"},
                {"keyword": "11h", "name": "11h"},
                {"keyword": "11h30p", "name": "11h30p"},
                {"keyword": "12h", "name": "12h"},
                {"keyword": "12h30p", "name":"12h30p"},
                {"keyword": "13h", "name": "13h"},
                {"keyword": "18h30", "name": "18h30p"},
                {"keyword": "19h", "name": "19h"},
                {"keyword": "19h30p", "name": "19h30p"},
                {"keyword": "20h", "name": "20h"}
            ]
        },
    "cleaning_room_booking":{
        "max_people": None,
        "hours":[
            {"keyword": "7h", "name": "7h"},
            {"keyword": "8h", "name": "8h"},
            {"keyword": "9h", "name": "9h"},
            {"keyword": "10h", "name": "10h"},
            {"keyword": "11h", "name": "11h"},
            {"keyword": "12h", "name": "12h"},
            {"keyword": "13h", "name": "13h"},
            {"keyword": "14h", "name": "14h"},
            {"keyword": "15h", "name": "15h"},
            {"keyword": "16h", "name": "16h"},
            {"keyword": "17h", "name": "17h"},
            {"keyword": "18h", "name": "18h"},
            {"keyword": "19h", "name": "19h"},
            {"keyword": "20h", "name": "20h"},
            {"keyword": "21h", "name": "21h"},
            {"keyword": "22h", "name": "22h"},
        ]
    },
    "spa":{
        "max_people": 5,
        "hours":[
            {"keyword": "7h", "name": "7h"},
            {"keyword": "8h", "name": "8h"},
            {"keyword": "9h", "name": "9h"},
            {"keyword": "10h", "name": "10h"},
            {"keyword": "11h", "name": "11h"},
            {"keyword": "12h", "name": "12h"},
            {"keyword": "13h", "name": "13h"},
            {"keyword": "14h", "name": "14h"},
            {"keyword": "15h", "name": "15h"},
            {"keyword": "16h", "name": "16h"},
            {"keyword": "17h", "name": "17h"},
            {"keyword": "18h", "name": "18h"},
            {"keyword": "19h", "name": "19h"},
            {"keyword": "20h", "name": "20h"},
            {"keyword": "21h", "name": "21h"},
            {"keyword": "22h", "name": "22h"},
            {"keyword": "23h", "name": "23h"},
            {"keyword": "24h", "name": "24h"},
        ],
        "time_performs":[
            {"keyword": "1h", "name": "1 tiếng"},
            {"keyword": "2h", "name": "2 tiếng"},
            {"keyword": "3h", "name": "3 tiếng"},

        ]
    }
    
}
def get_option_service(service_no):
    return OPTIONS.get(service_no, {})