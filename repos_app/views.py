from django.views import View
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .models import GithubRepo
from .serializers import GithubRepoSerializer

class GitHubRepositoriesView(View):
    """A class-based view for retrieving GitHub repositories."""

    def get(self, request):
        repositories = GithubRepo.objects.fetch_repos()
        if not repositories:
            return JsonResponse({'error': 'Failed to fetch GitHub repositories'}, status=500)   
        print('Printing repos: ', repositories)

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

        print(repo_data)
        return JsonResponse(repo_data, safe=True, status=200)

    def github_repositories(request):
        repositories = GithubRepo.objects.all()
        serializer = GithubRepoSerializer(repositories, many=True)
        return JsonResponse(serializer.data, safe=False)