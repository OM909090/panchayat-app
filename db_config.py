from flask import session, flash
from pymongo import MongoClient
from datetime import datetime

global con
global db
global db_developement
global col_management
global col_people
global col_complain
global col_development_work


def connect_db():
    global con
    global db
    global db_developement
    global col_management
    global col_people
    global col_complain
    global col_development_work
    
    con = MongoClient('mongodb+srv://PanchayatApp:panchayat1234@cluster0.2l72r.mongodb.net/')
    db = con.Pachayat_DB
    db_developement = con.Development_work_DB
    col_management = db.management_staff
    col_people = db.citizen
    col_complain = db.complain_box
    col_development_work = db_developement.Development_works
    
    
def check_admin_existance():
    global col_management
    connect_db()
    
    c = col_management.count_documents({'user_type': 'Admin'})
    return c

def create_admin(user_data):
    global col_management
    connect_db()
    
    col_management.insert_one(user_data)
    return

def create_panchayat(user_data):
    global col_management
    connect_db()
    
    col_management.insert_one(user_data)
    return

def create_user(user_data):
    global col_people
    connect_db()
    
    col_people.insert_one(user_data)
    return

def check_user_existance(email_id, user_type):
    global col_people
    global col_management
    connect_db()
    
    if user_type == 'Admin':
        c = col_management.find({'user_type': user_type}, {'_id':0})
    elif user_type == 'Management':
        c = col_management.find({'user_type': user_type, 'email': email_id}, {'_id':0})
    else:
        c = col_people.find({'user_type': user_type, 'email': email_id}, {'_id':0})
    return c
    
def get_other_panchayat_of_block(block):
    global col_management
    connect_db()
    
    c = col_management.find({'block': block}, {'_id':0, 'panchayat':1})
    return c

def check_panchayat_existance(p):
    global col_management
    connect_db()
    
    p = col_management.find({'panchayat': str(p)}, {'_id':0})
    return p

def register_complain(complain_data):
    global col_complain
    connect_db()
    
    col_complain.insert_one(complain_data)
    return

def get_all_raised_issues():
    global col_complain
    connect_db()
    
    issues = col_complain.find({}, {'_id':0})
    return issues

def count_complaints():
    global col_complain
    connect_db()
    counts = {}
    
    if session['user_type'] == 'Management':
        raised_issues_count = col_complain.count_documents({'panchayat': session['panchayat']})
        pending_issues_count = col_complain.count_documents({'panchayat': session['panchayat'], 'complain_status': 'Pending' })
        closed_issues_count = col_complain.count_documents({'panchayat': session['panchayat'], 'complain_status': 'Closed' })
    elif session['user_type'] == 'Admin':
        raised_issues_count = col_complain.count_documents({})
        pending_issues_count = col_complain.count_documents({'complain_status': 'Pending' })
        closed_issues_count = col_complain.count_documents({'complain_status': 'Closed' })
    counts['raised_issues_count'] = raised_issues_count
    counts['pending_issues_count'] = pending_issues_count
    counts['closed_issues_count'] = closed_issues_count  
    
    
    return counts

# def count_complaints2(p):
#     global col_complain
#     connect_db()
    
#     count = col_complain.aggregate([
#         {'$facet':{
#             'raised_issues' :[      
#                 {"$match" : {"panchayat":p}},     
#                 {"$count": 'raised_issues'}
#             ],
#             'pending_issues':[
#                 {"$match" : {"panchayat":p, "complain_status":'Pending'}},
#                 {"$count": 'pending_issues'}
#             ],
#              'closed_issues':[
#                 {"$match" : {"panchayat":p, "complain_status":'Closed'}},
#                 {"$count": 'closed_issues'}
#             ]
#         }},
#          { "$project": {
#             "raised_issues": { "$arrayElemAt": ["$raised_issues.raised_issues", 0] },
#             "pending_issues": { "$arrayElemAt": ["$pending_issues.pending_issues", 0] },
#             "closed_issues": { "$arrayElemAt": ["$closed_issues.closed_issues", 0] }
#         }}
#     ])
    
#     return count

def get_visitors_count():
    global col_people
    connect_db()
    
    c = col_people.count_documents({})
    return c

def get_visitors_count_by_panchayat(p):
    global col_people
    connect_db()
    
    c = col_people.count_documents({'panchayat':p})
    return c

def registered_panchayat_count():
    global col_management
    connect_db()
    
    p_count = col_management.count_documents({})
    return p_count

def get_all_panchayat():
    global col_management
    connect_db()
    
    cluster = col_management.find({'user_type':'Management'}, {'_id':0})
    return cluster

def update_password(update_data):
    global col_people
    global col_management
    connect_db()
    
    filter = {'email': update_data['email_id']}
    update_operation = {'$set':{
        'password': update_data['password'],
        'e_password' : update_data['e_password']
    }}
    
    if update_data['u_type'] == 'Management':
        col_management.update_one(filter, update_operation)
    else:
        col_people.update_one(filter, update_operation)
    return

def get_profile():    
    global col_people
    global col_management
    connect_db()
    
    if session['user_type'] == 'Management':
        p_cluster = col_management.find({'panchayat_id': session['panchayat_id']}, {'_id':0})
    elif session['user_type'] == 'Admin':
        p_cluster = col_management.find({'user_id': session['user_id']}, {'_id':0})
    else:
        p_cluster = col_people.find({'user_id': session['user_id']}, {'_id':0})
    return p_cluster

def update_profile(data):
    global col_management
    connect_db()
    
    filter = {'user_id' : data['user_id']}
    update_operation = {'$set':{
        'contact_person': data['contact_person'],
        'gender' : data['gender'],
        'date_of_birth' : data['date_of_birth']
    }}
    
    col_management.update_one(filter, update_operation)
    return

def get_raised_issues_by_user(u_id):
    global col_complain
    connect_db()
    
    issues = col_complain.find({'user_id': u_id}, {'_id':0})
    return issues

def get_raised_issues_by_panchayat(panchayat):    
    global col_complain
    connect_db()
    
    issues = col_complain.find({'panchayat': panchayat}, {'_id':0})
    return issues

def check_complaint_status(t):
    global col_complain
    connect_db()
    
    c = col_complain.find({'token': t}, {'_id':0})
    return c

def approve_issue(token):
    global col_complain
    connect_db()
    complain = {}
    user = ''
    
    if session['user_type'] == 'Admin':
        user = session['user_id']
    elif session['user_type'] == 'Management':
        user = session['panchayat_id']
        
    c = col_complain.find({'token': token}, {'_id':0})
    for i in c:
        complain = i
    
    if complain:
        filter = {'token' : token}
        update_operation = {'$set':{
            'complain_status': 'Proccessed',
            'complain_approval_date' : datetime.now(),
            'complain_approved_by' :user
        }}
    
        col_complain.update_one(filter, update_operation)
    return

def resolve_issue(token):
    global col_complain
    connect_db()
    
    c = col_complain.find({'token': token}, {'_id':0})
    for i in c:
        complain = i
        
    if complain:
        filter = {'token' : token}
        update_operation = {'$set':{
            'complain_status': 'Closed'
        }}    
        col_complain.update_one(filter, update_operation)
    return



def add_c_caption():
    global col_complain
    connect_db()
    
    filter = {}
    operation = {'$set':{'complaint_caption': ''}}
    
    col_complain.update_many({}, operation)
    return

def store_develoment_work(d_work):
    global col_development_work
    connect_db()
    
    col_development_work.insert_one(d_work)
    return

def fetch_all_development_works():
    global col_development_work
    connect_db()
    
    c = col_development_work.find({}, {'_id':0})    
    return c

def fetch_development_works_by_panchayat(p):
    global col_development_work
    connect_db()
    
    c = col_development_work.find({'panchayat': p}, {'_id':0})    
    return c
def dev_work_by_id(w_id):
    global col_development_work
    connect_db()
    
    c = col_development_work.find({'work_id': w_id}, {'_id':0})
    return c

def update_complain(data):
    global col_complain
    connect_db()
    
    filter = {'token' : data['token']}
    operation = {
        '$set' : {
            'complain_status': data['complain_status'],
            'reason_of_reject' : data['reason_of_reject'],
            'rejected_by' : data['rejected_by'],
            'rejected_date' : datetime.now()
        }
    }
    col_complain.update_one(filter, operation)
    return


def get_panchayat_by_id(pid):
    global col_management
    connect_db()
    
    p = col_management.find({'panchayat_id': pid}, {'_id':0})
    return p

def delete_issue(token):
    global col_complain
    connect_db()
    
    col_complain.delete_one({'token': token})
    return

def delete_panchayat(pid):
    global col_management
    connect_db()
    
    col_management.delete_one({'panchayat_id': pid})
    flash('Panchayat Deleted Successfully !!', 'success')
    return

# def update_field():
#     global col_management
#     connect_db()
    
#     operation = {'$set':{'panchayat_status': 'Active'}}
    
#     col_management.update_many({}, operation)
#     return