from django.shortcuts import render
from django.http import HttpResponse
from django.views import View

import random
import environ
import requests
from datetime import datetime, timedelta

env = environ.Env(
    DEBUG=(bool, False)
)

environ.Env.read_env(raise_error_if_not_found=True)


class GitHubRepositoriesView(View):
    def get(self, request):
        """A class-based view for retrieving GitHub repositories.

        This class extends the Django `View` class and provides a `get` method to handle HTTP GET requests. It retrieves the top open-source repositories on GitHub that were pushed within the last 24 hours and sorts them by the number of stars in descending order.
        """
        last_month = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%SZ")
        url = "https://api.github.com/search/repositories"
        GITHUB_ORG_ACCESS_TOKEN = env.str('GITHUB_ORG_ACCESS_TOKEN')
        headers = {
            "Authorization": f"Bearer {GITHUB_ORG_ACCESS_TOKEN}"
        }
        params = {
            "q": f"topic:opensource hacktoberfest pushed:>{last_month}",
            "order": "desc",
            "limit": 20
        }

        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            repositories = response.json()['items']

        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch GitHub repositories: {e}")
            return HttpResponse("Failed to fetch GitHub repositories", status=500)
        
        repositories = prioritize_hacktoberfest_repos(repositories)

        for repo in repositories:
            if repo is None:
                print("Encountered a None value in the repositories list.")
            licence = repo.get("license", "no license")
            avatar_url = repo['owner']['avatar_url']
            url = repo['html_url']
            commits_url = repo['commits_url'].replace("{/sha}", "")
            topics = repo['topics']
            updated_at = repo['updated_at']
            repo.update({
                'licence': licence,
                'avatar_url': avatar_url,
                'url': url,
                'topics': topics,
                'updated_at': updated_at,
                'commits_url': commits_url
            }) 

        popular_repos_result = popular_repos(repositories)
        featured_repo_result = featured_repo(popular_repos_result)
        latest_contributors_result = latest_contributors(repositories)
        latest_contributors(repositories)

        context = {
            'popular_repos_result': popular_repos_result,
            'featured_repo_result': featured_repo_result,
            'latest_contributors_result': latest_contributors_result,
            'repositories': repositories
        }

        return render(request, 'repositories.html', context)

def prioritize_hacktoberfest_repos(repositories):
    """Prioritize Hacktoberfest repositories.

    This function takes a list of GitHub repositories and prioritizes repositories that have the 'hacktoberfest' topic. It returns a new list with Hacktoberfest repositories followed by other repositories.

    Args:
        repositories (list): A list of GitHub repositories.

    Returns:
        list: A list of GitHub repositories with Hacktoberfest repositories prioritized.
    """
    hacktoberfest_repos = []
    other_repos = []
    for repo in repositories:
        if 'hacktoberfest' in repo['topics']:
            hacktoberfest_repos.append(repo)
        
        else:
            other_repos.append(repo)
    return hacktoberfest_repos + other_repos

# def get_commit_info(commits_url):
#     """Get information about the latest commit.

#     This function takes a GitHub repository's commits URL and returns the timestamp and committer name of the latest commit.

#     Args:
#         commits_url (str): The URL to fetch commits for a GitHub repository.

#     Returns:
#         tuple: A tuple containing the timestamp and committer name of the latest commit.
#     """
#     try:
#         response = requests.get(commits_url)
#         response.raise_for_status()
#         commits = response.json()
#         if commits:
#             latest_commit = commits[0]
#             return latest_commit['commit']['committer']['date'], latest_commit['commit']['committer']['name']
#     except requests.exceptions.RequestException as e:
#         print(f"Failed to fetch repository commit information: {e}")
#         return None, None

# Get a list of latest projects you might like
def popular_repos(repos):
  popular_repos_randomized = []
 
  for repo in repos:
    if not repo['full_name'] in popular_repos_randomized:
        popular_repos_randomized.append(repo)
  
  return popular_repos_randomized


def featured_repo(repos):
    random_repo_index = random.randint(0, len(repos) - 1)
    random_featured_repo = repos[random_repo_index]
    
    return random_featured_repo 

# Get a list of latest contributors
# TO DO: Edit to only include contributors with an OSD account
def latest_contributors(repos):
  calc_12_hours = (datetime.now() - timedelta(hours=12)).strftime("%Y-%m-%dT%H:%M:%SZ")
  repos_last_12_hours = list(filter(lambda repo: repo['updated_at'] < calc_12_hours, repos))

  last_commits_url_from_each_repo = []
  latest_commit_authors = []
  latest_repo_names = []

  for repo in repos_last_12_hours:
    formatted_commits_url = repo['commits_url'].split('{')[0]
    last_commits_url_from_each_repo.append(formatted_commits_url)


  for url in last_commits_url_from_each_repo:
    commits_response = requests.get(url)
    commits_response_json = commits_response.json()

    if commits_response_json:
        latest_commit_author = commits_response_json[0].get('author', {}).get('login')
        if latest_commit_author:
            latest_commit_authors.append(latest_commit_author)

    for url in last_commits_url_from_each_repo:
        repo_name = url.split('/')[-2]
        latest_repo_names.append(repo_name)

    zipped_users_and_repos = zip(latest_commit_authors, latest_repo_names)

    zipped_list = list(zipped_users_and_repos)
    print('zipped_list', zipped_list)

    return zipped_list