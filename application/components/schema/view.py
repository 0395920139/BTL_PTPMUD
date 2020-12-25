from application.server import app
from application.database import db
from application.extensions import apimanager
from sqlalchemy import or_, and_, func, literal
from sqlalchemy.sql.expression import cast
from gatco_restapi.helpers import to_dict
from gatco.response import json, text, html
from sanic_session import Session
from application.common.helpers import now_timestamp
from application.components.schema.model import *
import requests
import webbrowser
# from bs4 import BeautifulSoup
#{"txtusername":"CT030237","txtpassword":"a5227f816cfe24c9e2e2e6aefa14ea2f"}
def LoginKMA(txtUserName,txtPassword):
    session = requests.Session()
    url = 'http://qldt.actvn.edu.vn/CMCSoft.IU.Web.info/Login.aspx'
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    datalogin = "__VIEWSTATE=mFlrOlcSZg1BDeEmUnJmDTDWk%2BGt8J6aKoSLvGCJsMrllHdjLvhaSsvQjFo4wGw3QPMpaNZlrkB8tRLzJTizzNMmMJN7N%2BDKr3jtG4Y%2F08r852W%2Be2uDUxMGMtwGXrkoaSEvsiwXHQXfA%2FV1Vc0vJ1OSz6Uva5PrZlEP2c7Z%2FzVR1Dvh%2BCFzAu9FPM74sIq59EBWQvFxK0bE%2B8Shc%2BbP6J3pSuyVyy%2BWeUEJKd8trV6akDlk4mR42G8SO8WhujPWwJusHWzJwdXke8EF07xPkvgV7n2ZPOnzk%2FWDLN2qve8WGy6G4Rh73H9ZSYJeZVDr%2FJgmxb%2FXXBuPHLUn6rHn9PcOH2wi4DpQxnjlOjf416gpSd9Yhx282J7OTCcM%2BII6wZQxi9ZLdGO8wC0kEzwyItDhcTr02%2FOBeLRT%2Bb19nQLitoTuPL8gRXx%2Bqs%2Bdkvh%2FKq1BI4bk3h%2FVX5cOnHgTAKg4mi%2FgY9Oo5rjSumkrjgYI0pbIk6FNW52PDPmwokr4xNa3K%2FyRaj5RSkrHIur33bwKLdtFRMZMJ6cK2Gs53IrCT1i%2BJP0v7nLyV2HPxEgASUp9knYLm1wrrRY%2FYJ8EmgC1pjb4TcbKdtRH13KrdllEGWAsPxc6PVf1D6XzYGsi61BdPQprvsvUWNfAgSWFw0PB8AsZvNCMDef6duJuGcJZu%2BhJv1cKU4FH9K%2BOGtMgQaUUB%2BRSTNUxRHMgIgsQtiHiqvqEsvVKR7DqvjLuNwmm7u3j%2B91EFh143mhycJWJAXkPaNl0NYfdvTUlL2vPCwXWW%2BwCSrO5Yn%2FnES5xWb9sU37UAMAZDBj0KxwxKrKTwgkF44KSb7P7wOu9Mzmuv0lwp8mh82sZeHUYi1cBT1xMbRtNPvQC%2BPfmkSXQKv%2FKGQhapYnBXq32eC775%2BEZTN9gr1cZCuKqxrFm%2B1GlWQK%2BEogMIln4ReiujDGwhVlbr2Lg1%2BQKdk8QaujACnWpfvwWlsuLPttsGSEWGm30kzzjJPU5pY%2BWs7NLKOkqZOXtEMpqpvVJbOIW1%2BsHkO7NEHe90zPigoAJezXBHgfwHU8WTinFEAtMI2GUetkdrd5SfT3EBSuxHKq9NqG0Bp5uMjLZb6s759KE3%2BO%2FeUaiG%2BPeX8pQn4aTZl1ivHaONujUjv5oSgn%2B6EYGxfr4veTnTYTwF8Jjzt3zgKVcNZ82KRgSswJjYySyvW61GY1F5opzuRufHU8mwScBZdVlK0IQaJXA3iixpg6q2zJMhQJN8MYaLB3UR92Xql79qLAP%2FR1bfGLMmwEdHh5zZ6nIwonOYO6zAMMBW3c%2BWS82HyKTYYvEKU4bo2qIj6Mhowz4u6Zv6oXqVvokQwBq599fkQCL4qwHWCZj%2FlgfYEYezKo%2F%2FngCFvLte8eLMnPOLNplG6T50RnywxDvP%2F0%2Fc2IrahmNR1kz73nvZbVVCyRPNxkw0hjPaiRX1buGh4aTCNfvYJbFB4YDKzKY2Boe3POF8S77DGgh7Lk0lJEUzToDoa%2B6Dwz8i2aRGdMIjMH16j3wT9IDa3Uxo6%2Fkyaxa%2BdXI0i41oNfV4DHzuLv%2F1vtxa0CqkulCbtAHew7sYY6HcYBAVlS6xnw7QOe%2FEEkUb2YfadFkCGWwbhHSDPRtOpdjDuEfs7EqHlZPCdimfL8k0J%2BAInwuVR%2B7r2zAjPjf1qOe5yLV2iaJXl7vbH9JEcc31W1I4FR%2Fi5KrHotzDTe7kfpviuaxApL2ov%2BfHpkceS3eD5D3arbAvWXf%2BBc6bAEpPMAoNrTbES11I%2BOQL6TsMEYvkI%2FTrXuqrPQeP3z3s8TWsVR%2FIjbmt3%2BhKzZ7nLRU3FXMqthVANQHU3hcJC98w4G9E%2BUK9MNo1UNa3c%2F2Mbe5joy70tGQQumA57JEMQrXcWJNrL8HiSsKoMp3DXl5NkgmOYBaifz5L4VvzO1b5KUvZYk8aQ%3D%3D&txtUserName="+txtUserName+"&txtPassword="+txtPassword+"&btnSubmit="
    r = session.post(url, datalogin, headers=headers)
    jar = session.cookies.get_dict()
    cookies = {'SignIn': jar.get("SignIn")}
    return cookies



@app.route("/login", methods=["POST"])
def login(request):
    data = request.json
    if data is None or data.get('txtusername', None) is None or data.get('txtpassword', None) is None:
        return json({
            'error_code': 'AUTH_FAILED',
            'error_message': 'Username, password are required'
        }, status=523)
    txtUserName = data.get('txtusername', None)
    txtPassword = data.get('txtpassword', None) 
    # cookies = LoginKMA(txtUserName,txtPassword)
    if LoginKMA(txtUserName,txtPassword)['SignIn'] is None:
        return json({
            'error_code': 'AUTH_FAILED',
            'error_message': 'Username, password false'},status=523)
    if LoginKMA(txtUserName,txtPassword) is not None:
        AddCookie = Cookie()
        AddCookie.student_code = txtUserName
        AddCookie.password = txtPassword
        AddCookie.cookie = LoginKMA(txtUserName,txtPassword).get("SignIn")
        #Luu vao db
        db.session.add(AddCookie)
        db.session.commit()
        return json(txtUserName)
@app.route("/v1/schedule", methods = ["GET","POST"])
def schedule(request):
    if request.methods == "GET":
        pass

    if request.methods == "POST":
        pass

