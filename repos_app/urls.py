from django.urls import path
from repos_app.views import GitHubRepositoriesView, GitHubUserContributionView

urlpatterns = [
    path("", GitHubRepositoriesView.as_view()),
    path("api/github/repositories/", GitHubRepositoriesView.as_view(),name="github_repositories"),
    path("api/github/commit-history/", GitHubUserContributionView.as_view(),name="user_commit_history")
]