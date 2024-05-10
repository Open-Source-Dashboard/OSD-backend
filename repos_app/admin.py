from django.contrib import admin
from .models import GithubRepo, GithubUser

admin.site.register(GithubUser)
admin.site.register(GithubRepo)
