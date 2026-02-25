from flask import request, session
from datetime import datetime as dt
import id_generator as id

def get_signup_form_data():
    u_type = request.form.get('user_type')
    f_name = request.form.get('f_name').strip().capitalize()
    m_name = request.form.get('m_name').strip().capitalize()
    l_name = request.form.get('l_name').strip().capitalize()
    gender = request.form.get('gender')
    dob = request.form.get('dob')
    c_num = request.form.get('c_num').strip()
    email = request.form.get('email_id').strip()
    pwd = request.form.get('password').strip()
    address = request.form.get('address').strip().capitalize()
    block = request.form.get('block_list')
    panchayat = request.form.get('panchayat')
    agreement = request.form.get('agree')
    
    
    if u_type == 'Citizen':
        record = {
            'user_id' : '',
            'user_type' : u_type,
            'first_name' : f_name,
            'middle_name' : m_name,
            'last_name' : l_name,
            'gender' : gender,
            'date_of_birth' : dob,
            'contact_num' : c_num,
            'email' : email,
            'password' : pwd,
            'e_password': '',
            'full_address' : address,
            'block' : block,
            'panchayat' : panchayat,
            'terms_conditions' : agreement,
            'creation_date' : ''
        }
    elif u_type == 'Management':
        record = {
            'panchayat_id' : '',
            'block' : block,
            'panchayat' : panchayat,
            'user_type' : u_type,
            'contact_person' : f"{f_name} {l_name}",
            'gender' : gender,
            'date_of_birth' : dob,
            'contact_num' : c_num,
            'email' : email,
            'password' : pwd,
            'e_password': '',
            'terms_conditions' : agreement,
            'panchayat_added_date' : ''
        }
    elif u_type == 'Admin':
        record = {
            'user_id' : '',
            'dist' : 'Keonjhar',
            'state' : 'Odisha',
            'user_type' : u_type,
            'contact_person' : f"{f_name} {l_name}",
            'gender' : gender,
            'date_of_birth' : dob,
            'contact_num' : c_num,
            'email' : email,
            'password' : pwd,
            'e_password': '',
            'terms_conditions' : agreement,
            'admin_added_date' : ''
        }
    
    return record


def get_complaint_form_data():
    category = request.form['complaint_category']
    sub_category = request.form.get('sub_category')
    complaint_caption = request.form.get('issue_short').strip()
    complaint = request.form.get('complaint')
    complaint_token = id.complaint_token()

    
    complaint_dict = {
        'token' : complaint_token,
        'category' : category,
        'sub_category' : sub_category,
        'complaint_caption': complaint_caption,
        'complaint' : complaint,
        'complain_raised_date' : dt.now().strftime("%d-%b-%Y, %H:%M:%S %p"),
        'complain_raised_by' : session['username'],
        'user_id' : session['user_id'],
        'block' : session['block'], 
        'panchayat' : session['panchayat'],
        'complain_status' : 'Pending',
        'complain_approval_date' : '',
        'complain_approved_by' : ''
    }
    return complaint_dict

def fetch_dw_form_data():
    d_work = {}
    w_name = request.form.get('w_name').strip().upper()
    activity = request.form.get('activity')
    w_type = request.form.get('w_type')
    scheme = request.form.get('scheme')
    d_start = request.form.get('d_start').strip()
    d_end = request.form.get('d_end').strip()
    expenditure = request.form.get('expenditure').strip()
    estimate = request.form.get('estimate').strip()
    focus_area = request.form.get('f_area')
    component = request.form.get('component')
    desc = request.form.get('desc').strip()
    
    d_work['work_id'] = id.generate_work_id(focus_area[0])
    d_work['work_added_date'] = dt.now().strftime("%d-%b-%Y, %H:%M:%S %p")
    d_work['block'] = session['block']
    d_work['panchayat'] = session['panchayat']
    d_work['w_name'] = w_name
    d_work['activity'] = activity
    d_work['w_type'] = w_type
    d_work['scheme'] = scheme
    d_work['d_start'] = d_start
    d_work['d_end'] = d_end
    d_work['expenditure'] = expenditure
    d_work['estimate'] = estimate
    d_work['focus_area'] = focus_area
    d_work['component'] = component
    d_work['desc'] = desc
    d_work['status'] = 'Ongoing'
    
    return d_work