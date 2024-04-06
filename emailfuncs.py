# emailFunctions.py

import os
import json
import asyncio
import httpx

import commonfuncs as cf

EMAIL_API_KEY = os.environ.get('EMAIL_API_KEY')
EMAIL_API_URL = os.environ.get('EMAIL_API_URL')
EMAIL_SENDER = os.environ.get('EMAIL_SENDER')
EMAIL_SENDER_NAME = os.environ.get('EMAIL_SENDER_NAME')

async def handle_request(url, headers=None, rtype="get", payload=None):
    attempts = 0

    while attempts <= 50:
        try:
            # using httpx lib for async api calls, ref: https://www.python-httpx.org/async/
            async with httpx.AsyncClient(verify=False, http2=True, timeout=None) as client:
                if rtype == "post":
                    r = await client.post(url, headers=headers, data=payload, follow_redirects=True)
                
                elif payload:
                    r = await client.get(f"{url}?{payload}", headers=headers, follow_redirects=True)
                    # r = requests.get(f"{url}?{payload}", headers=headers, verify=False)
                else:
                    r = await client.get(url, headers=headers, follow_redirects=True)
                    # r = requests.get(f"{url}", headers=headers, verify=False)


            if 200 <= r.status_code < 300:
                if len(r.text)==0:
                    print("Got empty success response")
                    return {}, r.elapsed.total_seconds()
                else:
                    return r.json(), r.elapsed.total_seconds()
            
            if r.status_code == 503:
                attempts += 1
                print(f"Got 503 service unavailable for {url}, attempting again after a minute")
                await asyncio.sleep(60)  # Non-blocking sleep
                continue
                
            elif r.status_code == 502:
                attempts += 1
                print(f"Got 502 proxy error for {url}, attempting again after a minute")
                await asyncio.sleep(60)
                continue
            
            else:
                r.raise_for_status()

 
        except json.JSONDecodeError as e:
            attempts += 1
            if attempts > 50:
                print(f"Hits to {url} giving non-JSON response, giving up after {attempts} attempts.")
                print(e)
                raise
            print(f"Hit to {url} got non-JSON response, retrying after 20sec cooloff: {e}")
            print(r.text)
            await asyncio.sleep(20)


        except Exception as e:
            print(f"Unknown exception when trying to hit {url}, pls investigate. Exiting program.")
            print(e)
            # print(r.status_code)
            # print(r.text)

            raise

    print(f"Quitting after {attempts} attempts")
    raise



async def sendEmail(html, subject, recipient):
    global EMAIL_API_KEY, EMAIL_API_URL, EMAIL_SENDER, EMAIL_SENDER_NAME
    body = {  
        "sender":{  
            "name": EMAIL_SENDER_NAME,
            "email": EMAIL_SENDER,
        },
        "to":[],
        "subject": subject,
        "htmlContent": html,
    }

    if isinstance(recipient, list):
        for r in recipient:
            body['to'].append({'email':r, 'name':r})
    else:
        body['to'].append({'email':recipient, 'name':recipient})
    
    headers = {
        'accept': 'application/json',
        'api-key': EMAIL_API_KEY,
        'content-type': 'application/json',
    }
    res, t = await handle_request(EMAIL_API_URL, headers=headers, rtype="post", payload=json.dumps(body))
    
    if res.get('messageId'):
        cf.logmessage(f"{res['messageId']=}")
        return True
    else:
        cf.logmessage(f"{res=}")
        return False



