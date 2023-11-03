# api_users.py

import os
import uuid
import random
import secrets
from fastapi import HTTPException, Header
from typing import Optional
from pydantic import BaseModel

# import dbconnect
import dbconnect_admin
import commonfuncs as cf
from questionbank_launch import app
from emailfuncs import sendEmail

root = os.path.dirname(__file__)

OTP_VALIDITY = int(os.environ.get('OTP_VALIDITY',10)) * 60


def authenticate(token):
    s1 = f"""select t1.user_id, t2.email
    from sessions as t1
    left  join users as t2
    on t1.user_id = t2.user_id
    where t1.token = '{token}'
    """
    # to do later: verfied check.. let it be ignored for now.
    
    user = dbconnect_admin.makeQuery(s1, output='oneJson', noprint=True)
    if not user:
        print("rejected")
        raise HTTPException(status_code=401, detail="Invalid login")
    
    return user['user_id'], user['email']



class emailOTP_payload(BaseModel):
    email: str
    
@app.post("/api/users/emailOTP", tags=["users"])
def emailOTP(r: emailOTP_payload, X_Forwarded_For: Optional[str] = Header(None)):
    print("emailOTP POST api call")
    email = r.email
    # to do: validation

    # check if its a new user or existing one
    s1 = f"""select user_id from users where email = '{email}'"""
    user_id = dbconnect_admin.makeQuery(s1, output='oneValue')

    if not user_id:
        raise HTTPException(status_code=400, detail="invalid admin user")

    txnid = str(uuid.uuid4())
    otp = random.randint(1000,9999)
    
    i2 = f"""insert into sessions (txnid, user_id, otp) values ('{txnid}', {user_id},{otp})"""
    i2Count = dbconnect_admin.execSQL(i2)

    content = f"""<h2>OTP: {otp}</h2>
    <p>For Sci-beacon login</p>
    
    <br><br>
    <p><small>Disclaimer: This is an auto-generated message</small></p>"""

    textContent = f"OTP: {otp} for login"
    subject = f"OTP: {otp} for login"
    status = sendEmail(content=textContent, subject=subject, recipients=email, cc=None, html=content)
    
    returnD = {'email_sent' : True, 'txnid':txnid }
    return returnD



class verifyOTP_payload(BaseModel):
    txnid: str
    otp: int
    
@app.post("/api/users/verifyOTP", tags=["users"])
def verifyOTP(r: verifyOTP_payload, X_Forwarded_For: Optional[str] = Header(None)):
    txnid = r.txnid 
    otp = r.otp

    s1 = f"""select t2.email, t1.user_id
    from sessions as t1
    left join users as t2
    on t1.user_id = t2.user_id
    where t1.txnid='{txnid}' 
    and t1.otp={otp}
    and t1.created_on >= datetime(CURRENT_TIMESTAMP, '-30 minutes')
    and t1.token IS NULL
    """
    profile = dbconnect_admin.makeQuery(s1, output="oneJson")

    if not profile:
        raise HTTPException(status_code=401, detail="Unauthorized")
        return

    if not X_Forwarded_For: X_Forwarded_For = 'local'
    token = secrets.token_urlsafe(50)

    u1 = f"""update sessions
    set token = '{token}', 
    ipadrr = '{X_Forwarded_For}'
    where txnid = '{txnid}' and otp = {otp}
    """
    u1Count = dbconnect_admin.execSQL(u1)
    if not u1Count:
        raise HTTPException(status_code=500, detail="unable to update in DB, please repeat login process")
        return

    returnD = {'logged_in':True, 'token': token, 'profile':profile }
    return returnD



@app.get("/api/users/loggedincheck", tags=["users"])
def loggedincheck(x_access_token: str = Header(...)):

    s1 = f"""select t2.email, t1.user_id
    from sessions as t1
    left join users as t2
    on t1.user_id = t2.user_id
    where token = '{x_access_token}'
    """
    profile = dbconnect_admin.makeQuery(s1, output="oneJson")

    if not profile:
        raise HTTPException(status_code=401, detail="Unauthorized")
        return
    
    returnD = {'logged_in':True, 'profile':profile }
    return returnD