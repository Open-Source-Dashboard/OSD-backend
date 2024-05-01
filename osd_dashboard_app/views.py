from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views import View
from .serializers import GithubRepoSerializer
from .models import GithubRepo

import random
import environ
import requests
from datetime import datetime, timedelta

env = environ.Env(DEBUG=(bool, False))
environ.Env.read_env(raise_error_if_not_found=True)

class GitHubRepositoriesView(View):

  