from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
# '''
# User model that includes

# # User name -  char
# # Donut stampcard - int
# # Donut boxes - int
# # Last commit date - from Github api
# # Last commit repo name - from Github api
# '''

# from django.contrib.auth.models import AbstractUser
# import requests

# class User(AbstractUser):
#     github_username = models.CharField(max_length=100, blank=True, null=True)
#     donut_stampcard_count = models.IntegerField(default=0)
#     donut_boxes = models.IntegerField(default=0)
#     last_commit_date = models.DateTimeField(null=True, blank=True)
#     last_commit_repo_name = models.CharField(max_length=255, null=True, blank=True)


'''
Repo model that includes
# name
# license
# avatar_url 
# url 
# commits_url 
# topics 
# latest_commit_timestamp 
# latest_committer 
'''

class Repo(models.Model):
    repo_name = models.CharField(max_length=255)
    license = models.CharField(max_length=100)
    avatar_url = models.URLField()
    url = models.URLField()
    commits_url = models.URLField()
    topics = models.JSONField()
    latest_commit_timestamp = models.DateTimeField(null=True, blank=True)
    latest_committer = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.name