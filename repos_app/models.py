from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils import timezone
from datetime import datetime, timedelta
import requests, random, environ

env = environ.Env()
environ.Env.read_env()


class GithubRepoManager(models.Manager):
    """Fetch and process repositories from GitHub."""

    def fetch_repos(self):
        last_month = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%SZ")
        url = 'https://api.github.com/search/repositories'
        headers = {"Authorization": f"Bearer {env('GITHUB_ORG_ACCESS_TOKEN')}"}

        params = {
            "q": f"topic:opensource hacktoberfest pushed:>{last_month}",
            "order": "desc",
            "sort": "updated",
            "per_page": 20
        }

        try:
            response = requests.get(url,headers=headers, params=params)
            response.raise_for_status()
            repositories = response.json()['items']
            return repositories
        except requests.exceptions.RequestException as e:
            print(f'Error fetching repositories: {str(e)}')
            return []

    def get_popular_repos(self, repositories):
        """Sort repositories by stargazers_count in descending order."""
        
        return random.sample(repositories, min(len(repositories), 15))
    
    def get_featured_repo(self, repositories):
        """Select a single random repository from a list to feature."""
        
        featured_repo = random.choice(repositories) if repositories else None
        return [featured_repo]
    
    def prioritize_hacktoberfest_repos(self, repositories):
        hacktoberfest_repos = [repo for repo in repositories if 'hacktoberfest' in repo['topics']]
        other_repos = [repo for repo in repositories if 'hacktoberfest' not in repo['topics']]
        return hacktoberfest_repos + other_repos


    def get_latest_contributors(self, repositories):
        """Get a list of latest contributors."""
        
        calc_12_hours = (datetime.now() - timedelta(hours=12)).strftime("%Y-%m-%dT%H:%M:%SZ")
        repos_last_12_hours = [repo for repo in repositories if repo['updated_at'] < calc_12_hours
        ]
        latest_commits_url_each_repo = [repo['commits_url'].split('{')[0] for repo in repos_last_12_hours]

        latest_commit_authors = []
        latest_repo_names = []
        
        for url in latest_commits_url_each_repo:
            commits_response = requests.get(url)
            commits_response_json = commits_response.json()
            
            try:
                if commits_response_json:
                    latest_commit_author = commits_response_json[0].get('author', {}).get('login')
                    if latest_commit_author:
                        latest_commit_authors.append(latest_commit_author)
            except KeyError:
                print('empty url', commits_response_json)
                continue
            repo_name = url.split('/')[-2]
            latest_repo_names.append(repo_name)

        return [{"author": author, "repo_name": repo_name} for author, repo_name in zip(latest_commit_authors, latest_repo_names)]


# If performance becomes an issue, consider alternative methods to achieve randomness, such as selecting a random index in Python and retrieving the specific entry by ID.


class GithubRepo(models.Model):
    name = models.CharField(max_length=255)
    license = models.CharField(max_length=100)
    topics = models.JSONField()
    url = models.URLField()
    # avatar_url = models.URLField()
    commits_url = models.URLField()
    stargazers_count = models.IntegerField()
    latest_commit_timestamp = models.DateTimeField(default=timezone.now, null=True, blank=True)
    latest_committer = models.CharField(max_length=255, null=True, blank=True)

    objects = GithubRepoManager()

    def __str__(self):
        return self.name

class RepoContributor(models.Model):
    name = models.CharField(max_length=255)
    repo = models.ForeignKey(GithubRepo, on_delete=models.CASCADE)
    commit_url = models.URLField()
    last_commit_repo_name = models.CharField(max_length=255)