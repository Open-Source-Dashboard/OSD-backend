from django.urls import path
from repos_app.views import GitHubRepositoriesView

urlpatterns = [
    path("", GitHubRepositoriesView.as_view()),
    path("api/github/repositories/", GitHubRepositoriesView.as_view(),name="github_repositories"),
]
