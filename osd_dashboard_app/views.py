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
    template_name = 'repositories.html'
  
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        all_repos = GithubRepo.objects.fetch_repos()
        context['popular_repos'] = GithubRepo.objects.get_popular_repos(all_repos)
        context['featured_repo'] = GithubRepo.objects.get_featured_repo(all_repos)
        context['hacktoberfest_repos'] = GithubRepo.objects.prioritize_hacktoberfest_repos(all_repos)
        
        return context