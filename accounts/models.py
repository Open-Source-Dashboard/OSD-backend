from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils.translation import gettext_lazy as _
from datetime import datetime
import requests, environ

env = environ.Env()
environ.Env.read_env()
class GitHubUserManager(models.manager):
    """Fetch and process the users push events"""

    def fetch_user_push_events(self, max_pages=5):
        headers = {{"Authorization": f"Bearer {env('GITHUB_ORG_ACCESS_TOKEN')}"}}
        
        user_push_events = []
        for page in range(1, max_pages + 1):
            try:
                response = requests.get(f'https://api.github.com/users/{user}/events', headers=headers)
                response.raise_for_status()
                user_events = response.json()
                for event in user_events:
                    if event['type'] == 'PushEvent':
                        user_events.append(user_push_events)
            except requests.exceptions.RequestException as e:
                print(f"Error fetching repositories: {str(e)}")
                return []
        return user_push_events
    
    def commits_after_registration(registration_date, user_push_events):
        
            

class GitHubUser(AbstractUser):
    user_name = models.CharField(max_length=255, blank=True, null=True)
    registration_date = models.DateTimeField(auto_now_add=True)
    last_login_date = models.DateTimeField(auto_now=True)
    # repos = models.URLField()
    # commits_url = models.URLField()
    last_commit_repo = models.CharField(max_length=255)
    opensource_commit_count = models.IntegerField(default=0)

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

    # def check_and_increment_donut(self):
    #     authenticated_user = self.user_name
    #     user_register_date = self.registration_date.strptime("%Y-%m-%dT%H:%M:%SZ")

    #     repositories = GithubRepo.objects.fetch_repos()
    #     if not repositories:
    #         print('No repos fetched')
    #         return 
    #     has_committed = GithubRepo.objects.check_user_commits(repositories, authenticated_user, user_register_date)
    #     if has_committed:
    #         self.opensource_commit_count += 1
    #         self.save
    #         print(f"{authenticated_user} has contributed after their first login date. Open-source commit count incremented.")
    #     else:
    #         print(f'{authenticated_user} has not contributed to an opensource project')
    objects = GitHubUserManager()
    
    def __str__(self):
        return self.user_name
