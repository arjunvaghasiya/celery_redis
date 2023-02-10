from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from django.utils import timezone
import pytz
# Create your models here.
# https://youtu.be/EfWa6KH8nVI
# https://www.javatpoint.com/celery-tutorial-using-python

class News_Data(models.Model):
    news_id = models.AutoField(primary_key=True)
    link_n = models.CharField(max_length=400, blank=False)
    headline = models.CharField(max_length=400, blank=False)
    category = models.CharField(max_length=100, blank=False)
    date_d = models.DateField(null=True, blank=False)
    authors = models.CharField(max_length=100, blank=False)
    short_description = models.CharField(max_length=400, blank=False)

    def __str__(self):
        return str(self.news_id)
    
class Store_File(models.Model):
    user_id_fk = models.ForeignKey(User, on_delete=models.CASCADE)
    file_id = models.IntegerField(primary_key=True,blank=False)
    file_s = models.FileField(upload_to='uploded_files/') 
    
class Top_Status(models.Model):
    dt_utcnow  = datetime.now(tz=pytz.UTC)
    dt_ind = dt_utcnow.astimezone(pytz.timezone('Asia/Kolkata'))
    task_id = models.AutoField(primary_key=True)
    cpu_optimiztion = models.CharField(max_length=400, blank=False)
    mem_bytes= models.CharField(max_length=400, blank=False)
    swap_file_bytes= models.CharField(max_length=400, blank=False)
    added_date = models.DateField(auto_now_add=True,blank=True)
    added_time = models.TimeField(auto_now_add=True,blank=True)
    