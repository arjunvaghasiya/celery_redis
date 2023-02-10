from celery import shared_task
from . models import *
import json
from django.db import transaction
from celery import current_task
from django.core.mail import EmailMessage
from django_celery_results.models import TaskResult
from django.contrib.auth.models import User
import os
from datetime import datetime
import pytz
import time
import pipes
import smtplib, ssl
from os.path import basename
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from .logger_file import Logger_Class

def send_email_user(reciver_eml='arjunvaghasiya361@gmail.com',of_file_path=None,date_of = None):
    from_addr = 'arjunvaghasiya361@gmail.com'
    to_addr = reciver_eml
    subject = 'DAILY BACKUP'
    body = "Have Gratest Day!!"
    content = f'This database backup is taken on {date_of},You can use .sql file with the download option'

    msg = MIMEMultipart()
    msg['From']=from_addr
    msg['To']=to_addr
    msg['Subject']=subject
    body = MIMEText(content,'plain')
    msg.attach(body)

    filename = of_file_path
    with open(filename, 'r') as f:
        part = MIMEApplication(f.read(), Name=basename(filename))
        part['Content-Disposition'] = 'attachment; filename="{}"'.format(basename(filename))
    msg.attach(part)
    context=ssl.create_default_context()

    with smtplib.SMTP("smtp.gmail.com", port=587) as smtp:
        smtp.starttls(context=context)
        smtp.login(from_addr, "jupxfdgokubxbpgm")
        try:
            smtp.send_message(msg)
            print('Email Sent successfully')
        except:
            print('error please check')


def date_fun():
    current_time = datetime.now()
    c_date = current_time.strftime("%d/%m/%Y")  
    return c_date


def time_fun():
    current_time = datetime.now()
    c_time = current_time.strftime("%H:%M:%S")  
    return c_time

count = 0
def cpu_string_formatter(cp):
    dict1 = {}
    abc = cp
    abc = abc.replace('%Cpu(s):','').split(',')
    dict1['us'] = float(abc[0].replace(' us',''))
    dict1['sy'] = float(abc[1].replace(' sy',''))
    dict1['ni'] = float(abc[2].replace(' ni',''))
    dict1['id'] = float(abc[3].replace(' id',''))
    dict1['wa'] = float(abc[4].replace(' wa',''))
    dict1['hi'] = float(abc[5].replace(' hi',''))
    dict1['si'] = float(abc[6].replace(' si',''))
    dict1['st'] = float(abc[7].replace(' st',''))
    return dict1

def mib_mem_formattor(mib):
    dict1 = {}
    abc = mib
    abc = abc.replace('MiB Mem :   ','').split(',')
    dict1['total'] = float(abc[0].replace(' total', ''))
    dict1['free'] = float(abc[1].replace(' free', ''))
    dict1['used'] = float(abc[2].replace(' used', ''))
    dict1['buff/cache'] = float(abc[3].replace(' buff/cache', ''))
    return dict1


def mib_swap_formatter(swap):
    dict1 = {}
    abc = swap
    abc = abc.replace('MiB Swap:   ', '').split(',')
    dict1['total'] = float(abc[0].replace(' total', ''))
    dict1['free'] = float(abc[1].replace(' free', ''))
    dict1['used'] = float(((abc[2].split('d.')[0].replace(' use', ',''')).replace(' ','')).replace(',',''))
    dict1['availMem'] = float((abc[2].split('d.')[1].replace(' avail Mem','')).replace(' ',''))
    return dict1


@shared_task(bind=True)
@transaction.atomic
def test_func(self,f_id =''):

    file_json = Store_File.objects.get(file_id = int(f_id))
    print(type(current_task.request.id))
    for line in file_json.file_s.readlines():
        obj1 = News_Data(
            link_n=json.loads(line)['link'], 
            headline=json.loads(line)['headline'],
            category=json.loads(line)['category'],
            authors =json.loads(line)['authors'],
            short_description=json.loads(line)['short_description'],
            date_d= json.loads(line)['date'])
        obj1.save()
    # import pdb;pdb.set_trace()
    return current_task.request.id

@shared_task(bind=True)   
def email_func(self,id_task='',user_email=''):
    print(id_task)
    task_obj = TaskResult.objects.get(task_id=str(id_task)).status
    print(task_obj)
    if task_obj == 'SUCCESS':  
        email = EmailMessage(
        subject='Task Status',
        body=f"Dear user your given task: {str(id_task)} is successfully performed",
        to=[user_email]
    )
        email.send()
    elif task_obj == 'FAILURE':  
        email = EmailMessage(
        subject='Task Status',
        body=f"Dear user your given task: {str(id_task)} is Failed due to Un-desired data-content ",
        to=[user_email]
    )
        email.send()
    return print('celery work done')

@shared_task(bind=True)
def send_email_everyuser(self):
    users  = User.objects.all()
    for user in users:
        if user.is_active  == True:
            email = EmailMessage(
            subject='Daily Updates ',
            body=f"Hi dear user '{user.username}' this email is for daily updates",
            to=[user.email]
        )
            email.send()
            
@shared_task(bind=True)
def top_update(self):
    dt_utcnow  = datetime.now(tz=pytz.UTC)
    dt_ind = dt_utcnow.astimezone(pytz.timezone('Asia/Kolkata'))
    final_store = {}
    count = 0
    for line in os.popen("top -b -n 1 | head -n 5").readlines():
        if count == 2:
            final_store['cpu'] = cpu_string_formatter(line)
        if count == 3:
            final_store['mem'] = mib_mem_formattor(line)
        if count == 4:
            final_store['swap'] = mib_swap_formatter(line)
        count+=1
    top_obj = Top_Status(
                cpu_optimiztion = final_store['cpu'],
                mem_bytes = final_store['mem'],
                swap_file_bytes = final_store['swap'],

            )
    Logger_Class.logger.info(final_store['cpu'])
    top_obj.save()
    return current_task.request.id

@shared_task(bind=True)
def db_backup(self):
    DB_HOST = 'localhost' 
    DB_USER = 'root'
    DB_USER_PASSWORD = 'zymr@123'
    DB_NAME = 'new_second'
    BACKUP_PATH = '/tmp'
    DATETIME = time.strftime('%d_%m_%Y TIME_%H-%M')
    TODAYBACKUPPATH = BACKUP_PATH + '/' + DATETIME

    try:
        os.stat(TODAYBACKUPPATH)
    except:
        os.mkdir(TODAYBACKUPPATH)

    print ("checking for databases names file.")
    if os.path.exists(DB_NAME):
        file1 = open(DB_NAME)
        multi = 1
        print ("Databases file found...")
        print ("Starting backup of all dbs listed in file " + DB_NAME)
    else:
        print ("Databases file not found...")
        print ("Starting backup of database " + DB_NAME)
        multi = 0
    if multi:
       in_file = open(DB_NAME,"r")
       flength = len(in_file.readlines())
       in_file.close()
       p = 1
       dbfile = open(DB_NAME,"r")

       while p <= flength:
           db = dbfile.readline()   # reading database name from file
           db = db[:-1]         # deletes extra line
           dumpcmd = "mysqldump -h " + DB_HOST + " -u " + DB_USER + " -p" + DB_USER_PASSWORD + " " + db + " > " + pipes.quote(TODAYBACKUPPATH) + "/" + db + ".sql"
           os.system(dumpcmd)
           p = p + 1
       dbfile.close()
    else:
       db = DB_NAME
       dumpcmd = "mysqldump -h " + DB_HOST + " -u " + DB_USER + " -p" + DB_USER_PASSWORD + " " + db + " > " + pipes.quote(TODAYBACKUPPATH) + "/" + db + ".sql"
       print(os.system(dumpcmd))

    path_for = dumpcmd.split("'")
    path_for = f"{path_for[1]}{path_for[2]}"
    send_email_user(reciver_eml='frattahozoibe-4110@yopmail.com',of_file_path=path_for,date_of = DATETIME)
    return current_task.request.id
# /home/arjun.v@ah.zymrinc.com/Downloads/new_second.sql