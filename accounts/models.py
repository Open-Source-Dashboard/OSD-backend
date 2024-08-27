from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import datetime
import requests
import environ

# Load environment variables
env = environ.Env()
environ.Env.read_env()

class GitHubUserManager(models.Manager):
    """Manager to fetch and process GitHub user push events."""
    
    def fetch_user_push_events(self, user_name, max_pages=5):
        """Fetch push events for a GitHub user."""
        headers = {"Authorization": f"Bearer {env('GITHUB_ORG_ACCESS_TOKEN')}"}
        url = f"https://api.github.com/users/{user_name}/events"
        user_push_events = []

        for page in range(1, max_pages + 1):
            try:
                response = requests.get(url, headers=headers)
                response.raise_for_status()
                user_events = response.json()
                
                for event in user_events:
                    if event['type'] == 'PushEvent':
                        user_push_events.append(event)
            except requests.exceptions.RequestException as e:
                print(f"Error fetching user events: {str(e)}")
                return []

        return user_push_events

    def events_after_registration(self, user_push_events, registration_date=datetime(2023, 1, 1)):
        """Filter push events to only include those after a specific registration date."""
        after_registration_pushes = []

        for event in user_push_events:
            push_date = datetime.strptime(event["created_at"], "%Y-%m-%dT%H:%M:%SZ")
            if push_date >= registration_date:
                after_registration_pushes.append(event)

        return after_registration_pushes

    def get_commits_from_push(self, after_registration_pushes):
        """Extract commits from push events."""
        user_commits = []

        for push in after_registration_pushes:
            for commit in push['payload']['commits']:
                user_commits.append({
                    'sha': commit['sha'],
                    'message': commit['message'],
                    'url': commit['url'],
                    'author': commit['author']['name'],    
                })

        return user_commits

class GitHubUser(AbstractUser):
    github_username = models.CharField(max_length=255, blank=True, null=True)
    registration_date = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(default=timezone.now)
    last_commit_repo = models.CharField(max_length=255, blank=True, null=True)
    opensource_commit_count = models.IntegerField(default=1)

    # Override default groups and permissions to use related names specific to GitHubUser
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

    def save(self, *args, **kwargs):
        if not self.username:
            # Ensure username is populated or derived from github_username
            self.username = self.github_username or "default_username"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.github_username or self.username

class GithubRepoManager(models.Manager):
    """Manager to handle GitHub repository-related operations."""

    def fetch_latest_commit(self, repo_name):
        """Fetch the latest commit for a given repository."""
        headers = {"Authorization": f"Bearer {env('GITHUB_ORG_ACCESS_TOKEN')}"}
        url = f"https://api.github.com/repos/{repo_name}/commits"
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            commits = response.json()
            if commits:
                latest_commit = commits[0]
                return {
                    'sha': latest_commit['sha'],
                    'message': latest_commit['commit']['message'],
                    'url': latest_commit['html_url'],
                    'author': latest_commit['commit']['author']['name'],
                    'timestamp': latest_commit['commit']['author']['date'],
                }
            return None
        except requests.exceptions.RequestException as e:
            print(f"Error fetching latest commit: {str(e)}")
            return None

class GithubRepo(models.Model):
    name = models.CharField(max_length=255)
    license = models.CharField(max_length=100)
    topics = models.JSONField()
    url = models.URLField()
    commits_url = models.URLField()
    stargazers_count = models.IntegerField()
    description = models.TextField(max_length=1000)
    latest_commit_timestamp = models.DateTimeField(
        default=timezone.now, null=True, blank=True
    )
    latest_committer = models.CharField(max_length=255, null=True, blank=True)

    objects = GithubRepoManager()

    def __str__(self):
        return self.name
