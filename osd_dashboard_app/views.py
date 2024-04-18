from django.shortcuts import render
from django.http import HttpResponse

from django.views import View
import requests
from datetime import datetime, timedelta


class GitHubRepositoriesView(View):
    # All repo data filtered by opensource and hacktoberfest
    # Sample  for testing:  # Sample  for testing: https://api.github.com/search/repositories?q=topic:opensource%20pushed:%3E2024-04-14
    def get(self, request):
        """A class-based view for retrieving GitHub repositories.

        This class extends the Django `View` class and provides a `get` method to handle HTTP GET requests. It retrieves the top open-source repositories on GitHub that were pushed within the last 24 hours and sorts them by the number of stars in descending order.
        """
        last_month = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%SZ")
        url = "https://api.github.com/search/repositories"
        params = {
            "q": f"topic:opensource hacktoberfest pushed:>{last_month}",
            "order": "desc"
        }

        try:
            response = requests.get(url, params=params)
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
        popular_projects(repositories)
        latest_contributors(repositories)

        return render(request, 'repositories.html', {'repositories': repositories})

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
def popular_projects(repos):
  randomized_repos = []
 
  for repo in repos:
    if not repo['full_name']  in randomized_repos:
        randomized_repos.append(repo)
  
  return randomized_repos
        
# Get a list of latest contributors
def latest_contributors(repos):
  last_12_hours = (datetime.now() - timedelta(hours=12)).strftime("%Y-%m-%dT%H:%M:%SZ")
  repos_last_12_hours = list(filter(lambda repo: repo['updated_at'] < last_12_hours, repos))

  last_commits_url_from_each_repo = []

  for repo in repos:
    formatted_commits_url = repo['commits_url'].split('{')[0]
    last_commits_url_from_each_repo.append(formatted_commits_url)
  
  first_url = last_commits_url_from_each_repo[0]

  try:
    first_commit_url_response = requests.get(first_url).json()
    print('first_url_response:\n', first_commit_url_response)

  except requests.exceptions.RequestException as e:
      print(f"Failed to fetch repository commit information: {e}")
      return None, None


  # for commit in first_commit_url_response:
  #   author_github_name = commit['author']['login']
  #   # get repo name
  #   comitted_repo_url = commit['author']['url']
  #   comitted_repo_url_parts = comitted_repo_url.split('/')
  #   comitted_repo_name = comitted_repo_url_parts[-1]

  #   last_commits_url_from_each_repo.append({'author':author_github_name, 'repo_name': comitted_repo_name})
  #   print('last_commits_url_from_each_repo', last_commits_url_from_each_repo)
    
  #   break

  # print('last_commits_url_from_each_repo', last_commits_url_from_each_repo)
      




# elif 'hacktoberfest' in repo['topics'] and repo['pushed_at'] >= (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%dT%H:%M:%SZ"):
# hacktoberfest_repos.append(repo)
