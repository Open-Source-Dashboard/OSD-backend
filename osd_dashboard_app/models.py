from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.conf import settings
from datetime import datetime, timedelta
import requests, random


class GithubRepoManager(models.Manager):
    """Fetch and process repositories from GitHub."""
    def fetch_repos(self, include_hacktoberfest=False):
        last_month = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%SZ")
        url = 'https://api.github.com/search/repositories'
        query = 'topic: opensource'
        if include_hacktoberfest:
            query += ' hacktoberfest'
        headers = {
            'Authorization': f'Bearer {settings.GITHUB_ORG_ACCESS_TOKEN}'}

        params = {
            "q": f"topic:{query} pushed:>{last_month}",
            "order": "desc",
            "sort": "updated",
            "limit": 20
        }
        response = requests.get(url,headers=headers, params=params)
        response.raise_for_status
        return self.response.json()['items']

    def get_popular_repos(self, repositories):
        """Sort repositories by stargazers_count in descending order."""
        return sorted(repositories, key=lamda x: x['stargazers_count'], reverse=True)

# double check randomizer    
    def get_featured_repo(self, repositories):
        """Select a single random repository from a list to feature."""
        return random.choice(repositories) if repositories else None
    
    def prioritze_hacktoberfest_repos(self, repositories):
        hacktoberfest_repos = [repo for repo in repositories if 'hacktoberfest' in repo.get('topics', [])]
        other_repos = [repo for repo in repositories if 'hacktoberfest' not in repo.get('topics', [])]
        return hacktoberfest_repos + other_repos


# If performance becomes an issue, consider alternative methods to achieve randomness, such as selecting a random index in Python and retrieving the specific entry by ID.

class GithubUser(models.Model):
    username = models.CharField(max_length=100)
    avatar_url = models.URLField()
    profile_url = models.URLField()

    def __str__(self):
        return self.username

class GithubRepo(models.Model):
    name = models.CharField(max_length=255)
    license = models.CharField(max_length=100)
    topics = models.JSONField()
    url = models.URLField()
    avatar_url = models.URLField()
    commits_url = models.URLField()
    stargazers_count = models.IntegerField()
    latest_commit_timestamp = models.DateTimeField(default=timezone.now, null=True, blank=True)
    latest_committer = models.CharField(max_length=255, null=True, blank=True)
    
    objects = GithubRepoManager()
    
    def __str__(self):
        return self.name
    
    def latest_contributors(self):
        headers = {'Authorization': f'Bearer {settings.GITHUB_ORG_ACCESS_TOKEN}'}
        response = requests.get(f'https://api.github.com/repos/{self.name}/commits', header=headers)
        response.raise_for_status()
        commits = response.json()
        if commits:
            self.latest_committer = commits[0]['commit']['commiter']['name']
            self.save()
   
# does views latest_contributors logic need to go here?
class RepoContributor(models.Model):
    name = models.CharField(max_length=255)
    repo = models.ForeignKey(GithubRepo, on_delete=models.CASCADE)
    commit_url = models.URLField()
    last_commit_repo_name = models.CharField(max_length=255)


class OSDUserProfile(AbstractUser):
    github_username = models.CharField(max_length=100, blank=True, null=True)
    donut_stampcard_count = models.IntegerField(default=0)
    donut_boxes = models.IntegerField(default=0)
    last_commit_date = models.DateTimeField(null=True, blank=True)
    last_commit_repo_name = models.CharField(max_length=255, null=True, blank=True)
