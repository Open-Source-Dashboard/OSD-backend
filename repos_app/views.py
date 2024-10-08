from django.views import View
from django.shortcuts import render
from django.http import JsonResponse
from .models import GithubRepo
from accounts.models import GitHubUser
from .serializers import GithubRepoSerializer
import requests
from datetime import datetime
from django.utils import timezone
from django.db.models import F


class GitHubRepositoriesView(View):
    """A class-based view for retrieving GitHub repositories."""

    def get(self, request):        
        repositories = GithubRepo.objects.fetch_repos()
        if not repositories:
            return JsonResponse(
                {"error": "Failed to fetch GitHub repositories"}, status=500
            )

        repositories = GithubRepo.objects.prioritize_hacktoberfest_repos(repositories)
        popular_repo_result = GithubRepo.objects.get_popular_repos(repositories)
        featured_repo_result = GithubRepo.objects.get_featured_repo(popular_repo_result)
        latest_contributors_result = GithubRepo.objects.get_latest_contributors(repositories)

        repo_data = {
            "popular_repos_result": popular_repo_result,
            "featured_repo_result": featured_repo_result,
            "latest_contributors_result": latest_contributors_result,
        }

        return JsonResponse(repo_data, safe=True, status=200)

class GitHubUserContributionView(View):
    """A class-based view for retrieving user contributions."""
    
    def get_github_username(self, user_access_token):
        url = 'https://api.github.com/user'
        headers = {
            'Authorization': f'Bearer {user_access_token}'
        }

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            response_json = response.json()
            return response_json['login']
        except requests.exceptions.RequestException as e:
            print(f'Failed to fetch GitHub user: {e}')
            return None

    def get_user_events(self, username, user_access_token):
        url = f'https://api.github.com/users/{username}/events/public'
        headers = {
            'Authorization': f'Bearer {user_access_token}'
        }

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f'Failed to fetch user events: {e}')
            return None

    def get_repository_commits(self, owner, repo, user_access_token):
        url = f'https://api.github.com/repos/{owner}/{repo}/commits'
        headers = {
            'Authorization': f'Bearer {user_access_token}'
        }

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f'Failed to fetch commits for {owner}/{repo}: {e}')
            return None

    def get(self, request):
        user_access_token = request.headers.get('Authorization')

        if not user_access_token:
            return JsonResponse({'error': 'Access token not provided'}, status=400)

        if user_access_token.startswith('Bearer '):
            user_access_token = user_access_token.split(' ')[1]

        github_username = self.get_github_username(user_access_token)

        if not github_username:
            return JsonResponse({'error': 'Failed to retrieve GitHub username'}, status=500)

        events = self.get_user_events(github_username, user_access_token)

        if not events:
            return JsonResponse({'error': 'Failed to retrieve user events'}, status=500)

        # Initialize commit count
        new_commit_count = 0

        # Fetch the user's last login time
        try:
            github_user = GitHubUser.objects.get(github_username=github_username)
            last_login_time = github_user.last_login.replace(tzinfo=None)
        except GitHubUser.DoesNotExist:
            return JsonResponse({'error': 'GitHub user not found'}, status=404)

        user_contribution_data = []

        # TODO: Revise user contribution so that only user-entered commit messages are accepted as new commits. Do not increment for a merge or unmerge event. 
        for event in events:
            if event['type'] == 'PushEvent':
                for commit in event['payload']['commits']:
                    commit_date = datetime.strptime(event['created_at'], "%Y-%m-%dT%H:%M:%SZ")

                    if commit_date > last_login_time:
                        new_commit_count += 1

                    user_contribution_data.append({
                        "commit_date": event['created_at'],
                        "commit_message": commit['message'],
                        "repository": {
                            "repo_id": event['repo']['id'],
                            "repo_name": event['repo']['name'],
                            "repo_full_name": event['repo']['name'],
                            "repo_avatar_url": None,  # This data is not available from events API
                            "repo_html_url": f"https://github.com/{event['repo']['name']}",
                            "repo_labels_url": None,  # This data is not available from events API
                        }
                    })

        user_contribution_data.sort(key=lambda x: x["commit_date"], reverse=True)

        # Update the user's opensource_commit_count
        if new_commit_count > 0:
            GitHubUser.objects.filter(github_username=github_username).update(
                opensource_commit_count=F('opensource_commit_count') + new_commit_count
            )
            github_user = GitHubUser.objects.get(github_username=github_username)

        github_user.last_login = timezone.now()
        github_user.save()

        return JsonResponse(user_contribution_data, safe=False, status=200)

    def check_user_commits(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'User not authenticated'}, status=401)
        github_user = request.user
        if not github_user.user_name:
            return JsonResponse({'error': 'GitHub username not set'}, status=400)

        repo_manager = GithubRepo.objects
        has_user_commits, commit_count = repo_manager.check_user_commits(github_user.user_name, github_user.registration_date)

        if has_user_commits:
            github_user.opensource_commit_count = commit_count
            github_user.save()
            return JsonResponse({"message": "User has commits in the repositories"}, status=200)
        else:
            return JsonResponse({"message": "User has no commits in the repositories"}, status=200)
