# api_users.py

import os
import uuid
from fastapi import HTTPException

# import dbconnect
import dbconnect_admin
import commmonfuncs as cf


root = os.path.dirname(__file__)

OTP_VALIDITY = int(os.environ.get('OTP_VALIDITY',10)) * 60


def authenticate(token):
    s1 = f"""select t1.user_id, t2.email
    from sessions as t1
    left  join users as t2
    on t1.user_id = t2.user_id
    where t1.token = '{token}'
    and NOT t1.expired 
    """
    # to do later: verfied check.. let it be ignored for now.
    
    user = dbconnect_admin.makeQuery(s1, output='oneJson', noprint=True)
    if not user:
        cf.logmessage(f"rejected")
        raise HTTPException(status_code=401, detail="Invalid login")
    
    return user['user_id'], user['email']

