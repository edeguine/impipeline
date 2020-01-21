from django.db import models
from django.contrib.auth.models import User

class TUser(models.Model):
    username = models.CharField(max_length=256, unique=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

class Image(models.Model):
    filename = models.CharField(max_length=200)
    user = models.ForeignKey(TUser, on_delete=models.SET_NULL, null=True) # We don't want to delete pictures when user is deleted

class Task(models.Model):
    taskType = models.CharField(max_length=50)
    status = models.CharField(max_length=50)
    params = models.CharField(max_length=100000)
    complete = models.CharField(max_length=50, default='0')
    user = models.ForeignKey(TUser, on_delete=models.SET_NULL, null=True)

# Create your models here.
