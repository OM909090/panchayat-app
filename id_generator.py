
from datetime import datetime as dt
import random
import string

def get_random_chars(n):
    r_char = ''
    for i in range(n):        
        r_char += random.choice(string.ascii_uppercase)
    return r_char

def get_random_digits(n):
    r_num = ''
    for i in range(n):
        r_num += str(random.randint(0,9))        
    return r_num

def create_userId():
    r_char = get_random_chars(3)
    r_num = random.randint(1000, 9999)        
    user_id = r_char + str(r_num)
    return user_id

def complaint_token():
    t_date = dt.now().strftime("%y%m%d")
    r_num = random.randrange(10000, 100000)
    chars = get_random_chars(3)
    token = chars +'-'+ str(t_date)+'-' + str(r_num) 
    return token

def create_panchayat_id(b, p):
    r_num = get_random_digits(5)
    emp_id = b.upper() + p.upper() + str(r_num)
    return emp_id

def generate_otp():
    otp = ''
    for i in range(4):
        otp += str(random.randint(0,9))
    return otp

def generate_work_id(f_area):
    r_num = ''
    r_char = ''
    for i in range(5):
        if i<2:
            r_char += random.choice(string.ascii_uppercase)
        r_num += str(random.randint(0,9))
    id = f_area + r_num + r_char
    return id
    