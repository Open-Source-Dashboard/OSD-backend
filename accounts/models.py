from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils.translation import gettext_lazy as _
from datetime import datetime
from django.utils import timezone

import requests, environ

env = environ.Env()
environ.Env.read_env()
class GitHubUserManager(models.Manager):
    """Fetch and process the users push events"""

    def fetch_user_push_events(self, user_name, max_pages=5):
        headers = {"Authorization": f"Bearer {env('GITHUB_ORG_ACCESS_TOKEN')}"}
        url = f"https://api.github.com/users/{user_name}/events"
        user_push_events = []
        for page in range(1, max_pages + 1):
            try:
                response = requests.get(url, headers=headers)
                print('*** Fetching user events url', response)
                response.raise_for_status()
                user_events = response.json()
                print('*** user_events', user_events)
                for event in user_events:
                    if event['type'] == 'PushEvent':
                        user_push_events.append(event)

            except requests.exceptions.RequestException as e:
                print(f"Error fetching repositories: {str(e)}")
                return []
        print('*** user_push_events', user_push_events)
        return user_push_events

    def events_after_registration(self, user_push_events):
        after_registration_pushes = []
        registration_date = datetime(2023, 1, 1)
        for event in user_push_events:
            push_date = datetime.strptime(event["created_at"], "%Y-%m-%dT%H:%M:%SZ")
            if push_date >= registration_date:
                after_registration_pushes.append(event)
        return after_registration_pushes

    def get_commits_from_push(self, after_registration_pushes):
        user_commits = []
        for push in after_registration_pushes:
            for commit in push['payload']['commits']:
                user_commits.append({
                    'sha': commit['sha'],
                    'message': commit['message'],
                    'url': commit['url'],
                    'author': commit['author']['name'],    
                })
        print('*** user_commits', user_commits)
        return user_commits

class GitHubUser(AbstractUser):
    github_username = models.CharField(max_length=255, blank=True, null=True)
    registration_date = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(default=timezone.now)
    last_commit_repo = models.CharField(max_length=255)
    opensource_commit_count = models.IntegerField(default=1)

    groups = models.ManyToManyField(
        Group,
        verbose_name=_('groups'),
        blank=True,
        related_name='githubuser_set',
        related_query_name='githubuser',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_('user permissions'),
        blank=True,
        related_name='githubuser_set',
        related_query_name='githubuser',
    )

    objects = GitHubUserManager()
    
    def __str__(self):
        return self.github_username
