from django.shortcuts import render
from django.http import HttpResponse

from django.views import View
import requests
from datetime import datetime, timedelta

# Create your views here.

class GitHubRepositoriesView(View):
    # Sample  for testing: https://api.github.com/search/repositories?q=topic:opensource%20pushed:%3E2024-04-14
    def get(self, request):
        print("get function was automatically invoked")
        def get_repositories():
            url = "https://api.github.com/search/repositories"
            yesterday = datetime.now() - timedelta(days=1)
            yesterday_str = yesterday.strftime("%Y-%m-%dT%H:%M:%SZ")
            params = {
                "q": f"topic:opensource pushed:>{yesterday_str}",
                "sort": "stars",
                "order": "desc"
            }
            response = requests.get(url, params=params)

            # response = requests.get('https://api.github.com/search/repositories?q=topic:opensource%20pushed:%3E2024-04-14')

            if response.status_code == 200:
                return response.json()["items"]
            else:
                print("Error:", response.status_code)
                return None

        def get_commit_info(commits_url):
            response = requests.get(commits_url)
            if response.status_code == 200:
                commits = response.json()
                if commits:
                    latest_commit = commits[0]
                    return latest_commit["commit"]["committer"]["date"], latest_commit["commit"]["committer"]["name"]
            return None, None

        def prioritize_hacktoberfest_repos(repositories):
            hacktoberfest_repos = []
            other_repos = []
            for repo in repositories:
                # Include filter for hacktoberfest within the last year
                if "hacktoberfest" in repo["topics"]:
                    hacktoberfest_repos.append(repo)
                else:
                    other_repos.append(repo)
            return hacktoberfest_repos + other_repos

        repositories = get_repositories()
        if repositories:
            repositories = prioritize_hacktoberfest_repos(repositories)
            for repo in repositories:
                # user these variables later: license, avatar_url, and url. Maybe topics.
                license = repo.get("license", {}).get("name", "N/A")
                avatar_url = repo["owner"]["avatar_url"]
                url = repo["html_url"]
                commits_url = repo["commits_url"].replace("{/sha}", "")
                topics = repo["topics"]
                latest_commit_timestamp, latest_committer = get_commit_info(commits_url)

                # investigate this structure: repo['latest_commit_timestamp'] = latest_commit_timestamp
                repo['latest_commit_timestamp'] = latest_commit_timestamp
                repo['latest_committer'] = latest_committer

            return render(request, 'repositories.html', {'repositories': repositories})
        else:
            return render(request, 'error.html', {'message': 'Failed to fetch repositories'})
