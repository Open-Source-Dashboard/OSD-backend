from django.views import View
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .models import GithubRepo
from .serializers import GithubRepoSerializer



class GitHubRepositoriesView(View):
    """A class-based view for retrieving GitHub repositories."""

    def get(self, request):
        # if 'check_user_commits' in request.GET:
        #     return self.check_user_commits(request)
        repositories = GithubRepo.objects.fetch_repos()
        if not repositories:
            return JsonResponse(
                {"error": "Failed to fetch GitHub repositories"}, status=500
            )
        # print('Printing repos: ', repositories)

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

        # print(repo_data)
        return JsonResponse(repo_data, safe=True, status=200)

# class GitHubUserContributionView(View):
#     def get(self, username):
#         commits = GithubRepo.objects.get_commits_sorted_by_date(username)
#         for commit in commits:

#             print(commits["commit"]["author"]["date"], commit["commit"]["message"])
#             return JsonResponse(commits["commit"]["author"]["date"], commit["commit"]["message"])

        # TODO: send data to make the model

    # def check_user_commits(self, request):
    #     if not request.user.is_authenticated:
    #         return JsonResponse({'error: User not authenticated' }, status=401)
    #     github_user = request.user
    #     if not github_user.user_name:
    #         return JsonResponse({'error: GitHub username not set'}, status=400)

    #     repo_manager = GithubRepo.objects
    #     has_user_commits, commit_count = repo_manager.check_user_commits(github_user.user_name, github_user.registration_date)

    #     if has_user_commits:
    #         github_user.opensource_commit_count = commit_count
    #         github_user.save()
    #         return JsonResponse({"message": "User has commits in the repositories"}, status=200)
    #     else:
    #         return JsonResponse({"message": "User has no commits in the repositories"}, status=200)
