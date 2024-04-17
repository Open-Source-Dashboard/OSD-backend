from django.shortcuts import render
from django.http import HttpResponse

from django.views import View
import requests
from datetime import datetime, timedelta



class GitHubRepositoriesView(View):
     # Sample  for testing:  # Sample  for testing: https://api.github.com/search/repositories?q=topic:opensource%20pushed:%3E2024-04-14
    def get(self, request):
        """A class-based view for retrieving GitHub repositories.

        This class extends the Django `View` class and provides a `get` method to handle HTTP GET requests. It retrieves the top open-source repositories on GitHub that were pushed within the last 24 hours and sorts them by the number of stars in descending order.
        """
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
        url = "https://api.github.com/search/repositories"
        params = {
            "q": f"topic:opensource pushed:>{yesterday}",
            "sort": "stars",
            "order": "desc"
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            repositories = response.json()['items']
        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch GitHub repositories: {e}")
            return HttpResponse("Failed to fetch GitHub repositories", status=500)
        # user these variables later: license, avatar_url, and url. Maybe topics.
        repositories = prioritize_hacktoberfest_repos(repositories)
        for repo in repositories:
            licence = repo.get('license', {}).get('name', 'N/A')
            avatar_url = repo['owner']['avatar_url']
            url = repo['html_url']
            commits_url = repo['commits_url'].replace("{/sha}", "")
            topics = repo['topics']
            latest_commit_timestamp, latest_committer = get_commit_info(commits_url)
            repo.update({
                'licence': licence,
                'avatar_url': avatar_url,
                'url': url,
                'topics': topics,
                'latest_commit_timestamp': latest_commit_timestamp,
                'latest_committer': latest_committer
            }) 
            return HttpResponse("GitHub repositories fetched successfully", status=200)
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

def get_commit_info(commits_url):
    """Get information about the latest commit.

    This function takes a GitHub repository's commits URL and returns the timestamp and committer name of the latest commit.

    Args:
        commits_url (str): The URL to fetch commits for a GitHub repository.

    Returns:
        tuple: A tuple containing the timestamp and committer name of the latest commit.
    """
    try:
        response = requests.get(commits_url)
        response.raise_for_status()
        commits = response.json()
        if commits:
            latest_commit = commits[0]
            return latest_commit['commit']['committer']['date'], latest_commit['commit']['committer']['name']
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch repository commit information: {e}")
        return None, None





     # response = requests.get('https://api.github.com/search/repositories?q=topic:opensource%20pushed:%3E2024-04-14')




# elif 'hacktoberfest' in repo['topics'] and repo['pushed_at'] >= (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%dT%H:%M:%SZ"):
        # hacktoberfest_repos.append(repo)