from django.views import View
from django.shortcuts import render
from django.http import JsonResponse
from .models import GithubRepo
from .serializers import GithubRepoSerializer
import requests
# from .auth import get_github_username

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
        serialized_repos = GithubRepoSerializer(repositories, many=True).data

        repo_data = {
            "popular_repos_result": popular_repo_result,
            "featured_repo_result": featured_repo_result,
            "latest_contributors_result": latest_contributors_result,
            "repositories": serialized_repos,
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
            print("username from frontend: ", response_json['login'])
            return response_json['login']
        except requests.exceptions.RequestException as e:
            print(f'Failed to fetch GitHub user: {e}')
            return None

    def get(self, request):
        user_access_token = request.headers.get('Authorization')

        if not user_access_token:
            return JsonResponse({'error': 'Access token not provided'}, status=400)

        if user_access_token.startswith('Bearer '):
            user_access_token = user_access_token.split(' ')[1]

        username = self.get_github_username(user_access_token)
        if not username:
            return JsonResponse({'error': 'Failed to retrieve GitHub username'}, status=500)

        try:
            commits = GithubRepo.objects.get_user_commits(username)
            print('** all commits: ', commits[1])

            user_contribution_data = [
                {"date": commit["commit"]["author"]["date"], "message": commit["commit"]["message"]}
                for commit in commits
            ]
            # print('** user_contribution_data', user_contribution_data)

            # TODO: Sort the user_contribution_data before sending to the frontend
            return JsonResponse(user_contribution_data, safe=False)
        except Exception as e:
            print('** exception occurred for user_contribution_data')
            return JsonResponse({"error": str(e)}, status=400)

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