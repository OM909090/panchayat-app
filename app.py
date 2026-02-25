from flask import Flask, render_template, redirect, url_for, request, flash, session
from passlib.hash import sha256_crypt
from datetime import datetime
import configparser as cp
from flask_mail import Mail, Message # type: ignore
import time

import grab_form_data as gfd
import id_generator as id
import db_config as db
# ===================================================================================
config = cp.RawConfigParser()
config.read('config.ini', encoding="utf8")

app = Flask(__name__)
app.secret_key = str.encode(config['secret_key']['s_key'])
app.config.from_object(__name__) 


app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'sraj81791.sm@gmail.com'
app.config['MAIL_PASSWORD'] = 'sckm nfbd nxiv rmup'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_DEFAULT_SENDER'] = 'sraj81791.sm@gmail.com'
mail = Mail(app)

# ====================================================================================
#Password Encryption
def sha_encryption(un_encrypted_password):
	encrypted_password = sha256_crypt.encrypt(un_encrypted_password)
	return encrypted_password
# ====================================================================================

@app.route("/send_mail/<data>")
def send_email(data):
    msg = Message(
        subject = data['subject'], 
        sender = 'sraj81791.sm@gmail.com', 
        recipients=[data['mail_id']]
        )
    msg.html = data['message']
    mail.send(msg)
    return
     

# ===================================================================================
@app.route('/')
def index():
    # session['username'] = 'Guest'
    return render_template('index.html')

@app.route('/logout')
def logout():
    session.clear()    
    return redirect(url_for('login_page'))

@app.route('/login_attempt', methods=['POST'])
def login_attempt():
    user_type = request.form['user_type']
    email_id = request.form.get('email_id')
    pwd = request.form.get('password')
    
    user_data = {}
    cluster = db.check_user_existance(email_id, user_type)
    for i in cluster:
        user_data = i
    print('===================user_data')
    print(user_data)
    if user_data:
        if sha256_crypt.verify(pwd, user_data['e_password']):
            if user_data['user_type'] == 'Admin':
                session['user_id'] = user_data['user_id']
                session['username'] = user_data['contact_person']
                session['dist'] = user_data['dist']
                session['state'] = user_data['state']
            elif user_data['user_type'] == 'Management':
                print('management----------------------')
                session['panchayat_id'] = user_data['panchayat_id']
                session['panchayat'] = user_data['panchayat']
                session['username'] = user_data['contact_person']
                session['block'] = user_data['block']
            elif user_data['user_type'] == 'Citizen':
                session['user_id'] = user_data['user_id']
                session['first_name'] = user_data['first_name']
                session['last_name'] = user_data['last_name']
                session['username'] = user_data['first_name']+' '+user_data['last_name']
                session['panchayat'] = user_data['panchayat']
                session['block'] = user_data['block']
                
            session['user_type'] = user_data['user_type']            
            session['email'] = user_data['email']
            session['contact_num'] = user_data['contact_num']
            print('======================session')
            print(session)
            session['page'] = ''
            
                
            return redirect(url_for('dashboard'))
        else:
            flash('Incorrect Password', 'warning')
            session.clear()
            return redirect(url_for('login_page'))
    else:
        flash('Incorrect Credentials : Invalid User', 'warning')
        return redirect(url_for('login_page'))

@app.route('/profile')
def profile():    
    profile = {}
    profile_cluster = db.get_profile()
    for i in profile_cluster:
        profile = i
    session['page'] = 'profile'
    return render_template('profile.html', profile = profile)

@app.route('/update_profile', methods=['POST'])
def update_profile():
    data = {}
    f_name = request.form.get('f_name').strip()
    l_name = request.form.get('l_name').strip()
    gender = request.form.get('gender')
    dob = request.form.get('dob').strip()
    
    data['user_id'] = session['user_id']
    data['contact_person'] = f"{f_name} {l_name}"
    data['gender'] = gender
    data['date_of_birth'] = dob
    
    db.update_profile(data)
    session['username'] = data['contact_person']
    session['contact_num'] = data['contact_num']
    return redirect(url_for('profile'))

@app.route('/dashboard')
def dashboard():
    
    if session:
        if session['user_type'] == 'Admin':
            issues_list = []
            count_issues = {}
            panchayat_list = []
            visitors_count = 0
            all_d_work_list = []
            
            i_cluster = db.get_all_raised_issues()
            for i in i_cluster:
                issues_list.append(i)
                
            complaint_count = db.count_complaints()
                
            visitors_count = db.get_visitors_count()
            registered_panchayat_count = db.registered_panchayat_count()
            
            p_cluster = db.get_all_panchayat()
            for p in p_cluster:
                panchayat_list.append(p)
            
            c = db.fetch_all_development_works()
            for i in c:
                all_d_work_list.append(i)
             
            session['page'] = 'dashboard'
            return render_template('admin_dashboard.html', 
                                   issues_list = issues_list,
                                   count_issues = complaint_count,
                                   v_count = visitors_count,
                                   p_count = registered_panchayat_count,
                                   p_list = panchayat_list,
                                   dw_works = all_d_work_list)
        elif session['user_type'] == 'Management':
            issues = []
            d_work_list = []
            
            cluster = db.get_raised_issues_by_panchayat(session['panchayat'])
            for k in cluster:
                issues.append(k)
                
            c = db.fetch_development_works_by_panchayat(session['panchayat'])
            for i in c:
                d_work_list.append(i)
            
            complaint_count = db.count_complaints()             
                
            visitors_count = db.get_visitors_count_by_panchayat(session['panchayat'])
            
            session['page'] = 'dashboard'
            return render_template('management_dashboard.html', 
                                   i_list = issues,
                                   dw_list = d_work_list,                      
                                   count_issues = complaint_count,
                                   v_count = visitors_count) 
        elif session['user_type'] == 'Citizen':
            issues_list_for_self = []
            d_work_list = []
            c = db.get_raised_issues_by_user(session['user_id'])
            for i in c:
                issues_list_for_self.append(i)
                
            dw_c = db.fetch_development_works_by_panchayat(session['panchayat'])
            for i in dw_c:
                d_work_list.append(i)
                
            session['page'] = 'dashboard'  
            return render_template('citizen_dashboard.html', 
                                   i_list = issues_list_for_self,
                                   dw_list = d_work_list) 
        else:
            return redirect(url_for('login_page'))
    else:
        return redirect(url_for('login_page'))
    
@app.route('/manage_panchayat')
def manage_panchayat():
    p_list = []
    c = db.get_all_panchayat()
    for i in c:
        p_list.append(i)
    session['page'] = 'manage_panchayat'
    return render_template('manage_panchayat.html', p_list = p_list)

@app.route('/login_page')
def login_page():    
    return render_template('login.html')

@app.route('/account_creation_page')
def account_creation_page():   
    admin_count = 0
    admin_count = db.check_admin_existance()
    
    b_list = config['blocks_list']['BLOCKS'].split(', ')
    andapur_list = config['panchayat']['Anandapur'].split(', ')
    banspal_list = config['panchayat']['banspal'].split(', ')
    champua_list = config['panchayat']['Champua'].split(', ')
    Ghasipura_list = config['panchayat']['Ghasipura'].split(', ')
    Ghatagaon_list = config['panchayat']['Ghatagaon'].split(', ')
    Harichandanpur_list = config['panchayat']['Harichandanpur'].split(', ')
    Hatadihi_list = config['panchayat']['Hatadihi'].split(', ')
    Jhumpura_list = config['panchayat']['Jhumpura'].split(', ')
    Joda_list = config['panchayat']['Joda'].split(', ')
    Sadar_list = config['panchayat']['Sadar'].split(', ')
    Patana_list = config['panchayat']['Patana'].split(', ')
    Saharapada_list = config['panchayat']['Saharapada'].split(', ')
    Telkoi_list = config['panchayat']['Telkoi'].split(', ')
    return render_template('account_creation.html', b_list = b_list,
                                                    anandapur = andapur_list,
                                                    banspal = banspal_list,
                                                    champua = champua_list,
                                                    Ghasipura = Ghasipura_list,
                                                    Ghatagaon = Ghatagaon_list,
                                                    Harichandanpur = Harichandanpur_list,
                                                    Hatadihi = Hatadihi_list,
                                                    Jhumpura = Jhumpura_list,
                                                    Joda = Joda_list,
                                                    Sadar = Sadar_list,
                                                    Patana = Patana_list,
                                                    Saharapada = Saharapada_list,
                                                    Telkoi =Telkoi_list,
                                                    admin_count = admin_count                                                                           
                           )

@app.route('/forgot_password')
def forgot_password():
    return render_template('forgot_password.html')

@app.route('/change_password')
def change_password():
    return render_template('change_password.html')

@app.route('/update_new_password', methods=['POST'])
def update_new_password():
    update_data = {}
    pwd = request.form.get('new_password').strip()
    c_pwd = request.form.get('confirm_password').strip()
    if pwd == c_pwd:
        encrypted_password = sha_encryption(pwd)
        update_data['password'] = pwd
        update_data['e_password'] = encrypted_password
        update_data['email_id'] = session['otp_data']['email']
        update_data['u_type'] = session['otp_data']['u_type']
        
        db.update_password(update_data)
        session.pop('otp_data', None)
        
        return redirect(url_for('login_page'))
    else:
        return redirect(url_for('update_new_password'))
    

@app.route('/verify_otp', methods=['POST'])
def verify_otp():
    otp = request.form.get('otp').strip()
    if otp == session['otp_data']['otp']:        
        return redirect(url_for('change_password'))
    else:
        session.pop('otp_data', None)
        flash('OTP not matched', 'warning')
        return redirect(url_for('forgot_password'))

@app.route('/otp_verification')
def otp_verification():
    return render_template('otp_verification.html')

@app.route('/send_reset_link', methods=['POST'])
def send_reset_link():
    user_data = {}
    u_type = request.form.get('user_type')
    email = request.form.get('email_id').strip()
    
    cluster = db.check_user_existance(email, u_type)
    for i in cluster:
        user_data = i
        
    if user_data:
        otp = id.generate_otp()
        mail_data = {}
        mail_data['subject'] = 'Password Reset Link'
        mail_data['mail_id'] = email
        mail_data['message'] = f"We received your request of Password reset. <br>If you not initiated this request, Please ignore the mail.<br>Your OTP is <h4 style='font-size:25px'>{otp}</h4>"
        send_email(mail_data)
        session['otp_data'] = {'otp': otp, 'email': email, 'u_type':u_type} 
    return redirect(url_for('otp_verification'))

def generate_admin_mail_data(data):
    m_data = {}
    m_data['subject'] = 'Account Created'
    m_data['mail_id'] = data['email']
    m_data['message'] = f"""Dear <strong>{data['contact_person']}</strong>, <br>
    Congratulations for successfully registered with us.<br>
    Your are now the - <strong>{data['user_type']}</strong> of Panchayat Helpdesk.<br>
    Your user ID is : <strong>{data['user_id']}</strong><br><br><br>
    Best Regards<br><br>
    Panchayat Helpdesk<br>
    Keonjhar, Odisha
    """
    return m_data

def generate_mgmt_mail_data(data):
    m_data = {}
    m_data['subject'] = 'Panchayat Registered'
    m_data['mail_id'] = data['email']
    m_data['message'] = f"""Dear {data['contact_person']}, <br>
    Congratulations!! Registration of Panchayat ({data['panchayat']}) of {data['block']} block is successful.<br>
    Panchayat ID is : <span style="font-size:25px">{data['panchayat_id']}</span><br>
    Kindly keep the Panchayat Id safely.<br><br><br>
    
    Best Regards<br><br>
    Panchayat Helpdesk<br>
    Keonjhar, Odisha
    """
    return m_data

def generate_citizen_mail_data(data):
    m_data = {}
    m_data['subject'] = 'Account Created'
    m_data['mail_id'] = data['email']
    m_data['message'] = f"""Dear {data['first_name']} {data['last_name']}, <br>
    Congratulations!! Your Account created successfully.<br>
    Your User ID is : <span style="font-size:25px">{data['user_id']}</span><br>
    Kindly keep the User Id safely.<br><br><br>
    
    Best Regards<br><br>
    Panchayat Helpdesk<br>
    Keonjhar, Odisha
    """
    return m_data

def get_other_panchayat_of_block(block):
    p_list = []
    c = db.get_other_panchayat_of_block(block)
    for i in c:
        p_list.append(i)
    return p_list

@app.route('/create_account', methods=['POST'])
def create_account():
    panchayat_record = {}
    existing_user_info = []
    user_data = gfd.get_signup_form_data()
    
    encrypted_password = sha_encryption(user_data['password'])
    user_data['e_password'] = encrypted_password
    
    if user_data['user_type'] == 'Citizen':
        user_data['user_id'] = id.create_userId()
        user_data['creation_date'] = datetime.now() 
    elif user_data['user_type'] == 'Management':
        b = user_data['block']
        p = user_data['panchayat']
        user_data['panchayat_id'] = id.create_panchayat_id(b[:3:2], p[:3:2])
        user_data['panchayat_added_date'] = datetime.now() 
    else:        
        user_data['user_id'] = id.create_userId()
        user_data['admin_added_date'] = datetime.now()   
          
    def get_panchayat_details(panch):
        panchayat_record = {}
        cluster = db.check_panchayat_existance(panch)
        for i in cluster:
            panchayat_record = i
        return panchayat_record
        
            
        
    if user_data['user_type'] == 'Admin':
        admin_count = db.check_admin_existance()
        if admin_count:
            flash('Admin already exists', 'warning')
            return redirect(url_for('login_page'))
        else:
            db.create_admin(user_data)
            mail_data = generate_admin_mail_data(user_data)
            send_email(mail_data)
            return redirect(url_for('login_page'))
    elif user_data['user_type'] == 'Management':
        p_record = get_panchayat_details(user_data['panchayat'])
        if p_record:
            flash('Mentioned Panchayat already registered.', 'warning')  
            return redirect(url_for('login_page'))
        else:
            mail_data = generate_mgmt_mail_data(user_data)
            a = send_email(mail_data)
            print('===================~~~~~~')
            print(a)
            print('===================~~~~~~')
            
            db.create_panchayat(user_data)
            return redirect(url_for('login_page'))
    elif user_data['user_type'] == 'Citizen':
        p_record = get_panchayat_details(user_data['panchayat'])
        if p_record:
            c = db.check_user_existance(user_data['email'], user_data['user_type'])
            for i in c:
                existing_user_info.append(i)
            if existing_user_info:
                flash('User exists with this credential', 'warning')
            else:
                db.create_user(user_data)    
                mail_data = generate_citizen_mail_data(user_data)
                send_email(mail_data)    
            return redirect(url_for('login_page'))
        else:
            p_list = get_other_panchayat_of_block(user_data['block'])
            
            if p_list:
                print(p_list)
            
            flash(f"Panchayat Helpdesk not exist for Panchayat : {user_data['panchayat']}, Available Panchayat from your block {user_data['block']} are : {p_list}. You can register from any of the available Panchayat", 'warning')
            return redirect(url_for('account_creation_page'))
    else:
        flash('Something went wrong while creating account', 'danger')
        return redirect(url_for('account_creation_page'))


    
@app.route('/register_complaint', methods=['POST'])
def register_complaint():
    
    complain = gfd.get_complaint_form_data()
    db.register_complain(complain)
    return redirect(url_for('dashboard'))

@app.route('/all_raised_issues')
def all_raised_issues():
    raised_issues = []
    cluster = db.get_all_raised_issues()
    for i in cluster:
        raised_issues.append(i)
    session['page'] = 'complaint_status'
    return render_template('raised_issues_management.html', r_issues = raised_issues)

@app.route('/track_complaint_status')
def track_complaint_status():    
    issues_list = []
    panchayat_data = {}
    
    if session['user_type'] == 'Management':
        issues = db.get_raised_issues_by_panchayat(session['panchayat'])
    elif session['user_type'] == 'Citizen':
        issues = db.get_raised_issues_by_user(session['user_id'])
        
    
    for i in issues:
        issues_list.append(i)
    session['page'] = 'complaint_status'
    cluster = db.check_panchayat_existance(session['panchayat'])
    for i in cluster:
        panchayat_data = i
    return render_template('track_complaint_status.html', 
                           issues_list = issues_list,
                           p_data = panchayat_data)

@app.route('/detailed_issues/<t>')
def detailed_issues(t):
    issue = {}
    c = db.check_complaint_status(t)
    for i in c:
        issue = i
    session['page'] = 'complaint_status'
    
    return render_template('detailed_issue.html', issue = issue)

@app.route('/approve_issue/<token>')
def approve_issue(token):
    db.approve_issue(token)
    if session['user_type'] == 'Management':
        return redirect(url_for('track_complaint_status'))
    elif session['user_type'] == 'Admin':
        return redirect(url_for('all_raised_issues'))

@app.route('/resolve_issue/<token>')
def resolve_issue(token):
    db.resolve_issue(token)
    if session['user_type'] == 'Management':
        return redirect(url_for('track_complaint_status'))
    elif session['user_type'] == 'Admin':
        return redirect(url_for('all_raised_issues'))


@app.route('/reject_issue/<token>', methods=['POST'])
def reject_issue(token):
    rejection_data = {}
    reason = request.form.get('reject_reason').strip()
    u_name = session['username']
    u_type = session['user_type']
    rejected_by = f"{u_name}-{u_type}"
    rejection_data['reason_of_reject'] = reason
    rejection_data['rejected_by'] = rejected_by
    rejection_data['complain_status'] = 'Rejected'
    rejection_data['token'] = token
    
    db.update_complain(rejection_data)
    return redirect(url_for('dashboard'))


@app.route('/dev_works')
def dev_works():    
    session['page'] = 'dev_works'
    d_works = []
    if session['user_type'] == 'Admin' :
        c = db.fetch_all_development_works()
    elif session['user_type'] == 'Management' :
        c = db.fetch_development_works_by_panchayat(session['panchayat'])
    for i in c:
        d_works.append(i)
    return render_template('development_works.html', d_works = d_works)

@app.route('/development_work', methods=['POST'])
def development_work():
    d_work = gfd.fetch_dw_form_data()
    db.store_develoment_work(d_work)
    return redirect(url_for('dev_works'))
    

@app.route('/detailed_dev_works/<w_id>')
def detailed_dev_works(w_id):    
    work = {}
    c = db.dev_work_by_id(w_id)
    for i in c:
        work = i
    return render_template('detailed_dev_works.html', work = work)   
    
    
@app.route('/antyodaya')
def antyodaya():
    session['page'] = 'antyodaya'
    return render_template('antyodaya.html')

@app.route('/pmay_grameen')
def pmay_grameen():
    session['page'] = 'pmay_grameen'
    return render_template('pmay_grameen.html')

@app.route('/deactivate_panchayat/<pid>', methods=['POST'])
def deactivate_panchayat(pid):
    reason = request.form.get('deactivate_reason')
    panchayat = {}
    c = db.get_panchayat_by_id(pid)
    for i in c:
        panchayat = i   
    
    mail_data = {}
    mail_data['subject'] = 'Panchayat Deactivated'
    mail_data['mail_id'] = panchayat['email']
    mail_data['message'] = f"""Dear {panchayat['contact_person']},<br>
    The panchayat-{panchayat['panchayat']} of Block- {panchayat['block']}
    is deactivated due to below mentioned reason. i.e.  <br>
    <h3>{reason}</h3><br><br>
    
    Kindly contact Admin of panchayat Helpdesk for more information !
    <br><br>
    Best Regards,
    <br><br>
    
    <strong>Panchayat Helpdesk<br>
    Keonjhar</strong>
    """
    send_email(mail_data)
    db.delete_panchayat(pid)
    
    return redirect(url_for('manage_panchayat'))

@app.route('/delete_issue/<token>')
def delete_issue(token):
    db.delete_issue(token)
    flash(f'delete issue with token No. : {token}', 'success')
    return redirect(url_for('dashboard'))


# @app.route('/update_field')
# def update_field():
#     db.update_field()
#     return redirect(url_for('index'))


# ========================================================================

if __name__ == '__main__':
    app.run(debug=True)

