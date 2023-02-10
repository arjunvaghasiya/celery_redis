from django.http import HttpResponse
from django.shortcuts import render
from .tasks import *
from rest_framework.response import Response
from rest_framework import status,viewsets,generics,parsers
from . serializer import *
import json
from django.core.mail import EmailMessage
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny 
import time
from datetime import datetime
from subprocess import Popen, PIPE 
import mysql.connector
from .logger_file import Logger_Class
from storages.backends.s3boto3 import S3Boto3Storage
import boto3
from botocore.exceptions import NoCredentialsError


def upload_to_aws(local_file, bucket, s3_file):
    ACCESS_KEY = 'AKIAX3RXG4RX7UXZK4OG'
    SECRET_KEY = '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'

    s3 = boto3.client('s3', aws_access_key_id=ACCESS_KEY,
                      aws_secret_access_key=SECRET_KEY)
    try:
     
        s3.upload_file(local_file, bucket, s3_file)
        print("Upload Successful")
        return True
    except FileNotFoundError:
        print("The file was not found")
        return False
    except NoCredentialsError:
        print("Credentials not available")
        return False

def download_from_aws(local_file, bucket, s3_file):
    ACCESS_KEY = 'AKIAX3RXG4RX7UXZK4OG'
    SECRET_KEY = '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'

    s3 = boto3.client('s3', aws_access_key_id=ACCESS_KEY,
                      aws_secret_access_key=SECRET_KEY)
    try:
     
        s3.download_file(Filename=local_file,Bucket=bucket,Key=s3_file,)
        print("download Successful")
        return True
    except FileNotFoundError:
        print("The file was not found")
        return False
    except NoCredentialsError:
        print("Credentials not available")
        return False    



def send_mail(user, token, pk):
    # import pdb;pdb.set_trace()
    email = EmailMessage(
        subject='verify email',
        body=f"Hi verify your account by click this LINK \n \n  http://127.0.0.1:8000/verify/{token}/{pk}",
        to=[user]
    )
    email.send()

def verify(request, token, pk):
    # import pdb;pdb.set_trace()
    user = User.objects.get(username=pk)
    user.is_active = True
    user.save()
    return HttpResponse('<h1>you have registerd succesfully </h1>')


class RegisterViewAPI(viewsets.ViewSet):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
    def create(self,request): 
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        pk = User.objects.get(email=serializer.data['email'])
        refresh = RefreshToken.for_user(pk)
        send_mail(serializer.data['email'], refresh.access_token, pk)
        context = {}
        context = dict(request.data)
        response_data = {
            'UserName':context['username'],
            "Email":context['email'],
            'Token Access' : str(refresh.access_token),
            "Token Refresh" : str(refresh)
        }
        return Response(data=response_data, status=status.HTTP_200_OK)

# Create your views here.
class News_Data(viewsets.ViewSet):
    serializer = File_Serializer
    def create(self,request,format = None):
        user = User.objects.get(username = request.user)
        file_data = {
            'user_id_fk':user.id,
            'file_id':request.data['file_id'],
            'file_s':request.data['file_s']
            
        } 
        serializer =File_Serializer(data=file_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        id = Store_File.objects.get(file_id = request.data['file_id'])
        taskid = test_func.delay(f_id =id.file_id)
        print(taskid)
        time.sleep(10)
        email_func.delay(id_task=str(taskid),user_email=user.email)
        return Response({'Stay with E-mail updates...!!':'After task completion, status will be shared to your registered E-mail account'},status=status.HTTP_201_CREATED)

class Cpu_optimization(viewsets.ViewSet):
    permission_classes = [AllowAny]
    def list(self,request):
        try:
            obj = Top_Status.objects.filter(added_date=request.data['enter_date'])
            serializer = Top_Serializer(obj,many = True)
        # breakpoint()
            sum_a = 0.0
            current = []
            dict_1 = {}
            len_a = len(serializer.data)
            for i in range(0,len_a):
                serial_val = float(serializer.data[i]['cpu_optimiztion'].split(',')[0].split(' ')[1])
                # print(serial_val)
                if len_a % 12 != 0:
                    # var_a = 28 - (len_a % 12)
                    sum_a += serial_val
                    if i % 12 == 0:
                        avg_rcrd = sum_a / 12
                        current.append(avg_rcrd)
                        dict_1[serializer.data[i]['added_time']] = avg_rcrd
                        sum_a = 0
                        avg_rcrd = 0
                    if i == len_a:
                        avg_rcrd = sum_a / (len_a%12)
                        dict_1[serializer.data[i]['added_time']]  = avg_rcrd
                if len_a % 12 == 0:
                    sum_a += serial_val
                    if i % 12 == 0:
                        avg_rcrd = sum_a / 12
                        current.append(avg_rcrd)
                        dict_1[serializer.data[i]['added_time']] = avg_rcrd
                        sum_a = 0
            print(dict_1)
            max_cup_time = max(zip(dict_1.values(), dict_1.keys()))[1]
            max_usage_at = max(current)
            min_cup_time = min(zip(dict_1.values(), dict_1.keys()))[1]
            min_usage_at = min(current)       
            response_data = {
                'Max_Cpu_Usage_At' : ((max_cup_time).split('.')[0][:-3]),
                'Max_Usage_at_time' : round(max_usage_at,2),
                'Min_Cpu_Usage_At' : ((min_cup_time).split('.')[0][:-3]),
                'Minimun_Cpu_Usage_At' : round(min_usage_at,2)
            }

            return Response(data=response_data,status=status.HTTP_202_ACCEPTED)

        except:
            return Response({'QuerySet_Error':'Data not found'},status=status.HTTP_404_NOT_FOUND)
        # breakpoint()
        
class Restore_Database(generics.GenericAPIView):
    permission_classes = [AllowAny]
    def post(self,request):
        username=request.data['username']
        password=request.data['password']
        database_name=request.data['database_name']
        file_path = request.data['file_path']
        Logger_Class.logger.debug(database_name)
        try:
            mydb = mysql.connector.connect(
                host = "localhost",
                user = username,
                password = password
            )
            reset = f"mysql -v -u {username} -p{password} {database_name} < {file_path}"
            os.system(reset)
    
            return Response({'Success':'Data is Restored'},status=status.HTTP_200_OK)
        except:
            return Response({'QuerySet_Error':'Data not found'},status=status.HTTP_404)
        
class MyStorage1(S3Boto3Storage):
    bucket_name = 'user-data'

   
class Add_S3(generics.GenericAPIView):
    permission_classes = [AllowAny]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]
    def post(self,request):
        if request.data['file_pth'] != '':
            # breakpoint()
            val_data = str((request.data['file_pth'].split('/'))[-1])
   
            uploaded = upload_to_aws(request.data['file_pth'], 'dj-bkt', f'celery_redis/user-data/{val_data}')
            if uploaded:
                return Response({'Success':'Data is Uploaded'},status=status.HTTP_200_OK)
            else:
                return Response({'Un-Success':'Data not Uploaded'},status=status.HTTP_403_FORBIDDEN)           
        else:
            return Response({'Un-Success':'Data not Uploaded'},status=status.HTTP_403_FORBIDDEN) 

    def get(self,request):

        if request.data['file_name'] and request.data['file_path'] != '':
            val_data = request.data['file_name']
            uploaded = download_from_aws(local_file=request.data['file_path'],bucket= 'dj-bkt',s3_file= f'celery_redis/user-data/{val_data}')
            if uploaded:
                return Response({'Success':'Data is Downloaded'},status=status.HTTP_200_OK)
            else:
                return Response({'Un-Success':'Data not Uploaded'},status=status.HTTP_403_FORBIDDEN)           
        else:
            return Response({'Un-Success':'Data not Uploaded'},status=status.HTTP_403_FORBIDDEN)             

