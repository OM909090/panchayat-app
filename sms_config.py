from flask import flash
from twilio.rest import Client

import configparser as cp

config = cp.RawConfigParser()
config.read('config.ini', encoding="utf8")

# ---------------------------------------------Twilio configuration
account_sid = config['twilio']['twilio_account_sid'].strip()
auth_token = config['twilio']['twilio_auth_token'].strip()
twilio_number = config['twilio']['twilio_number'].strip()

client = Client(account_sid, auth_token)

# ------------------------------------------ Send confirm message to customer
def send_message(uname, num, uid, utype):    
    to_number = num
    message_body = f"Dear {uname}, Thank You for joining PRANK as {utype} !! your user ID is {uid}. Kindly keep your user ID safe, "
    
    try:
        message = client.messages.create(
            body=message_body,
            from_=twilio_number,
            to=to_number
        )   
        msg = {'msg':'User Id sent to your registered number', 'status':'success'}
        return msg
    except Exception as e:
        msg = {'msg': type(e).__name__, 'status':'error'}
        return msg