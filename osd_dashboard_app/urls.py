from django.urls import path
from osd_dashboard_app.views import GitHubRepositoriesView
from .auth import GitHubAuthCallback 


urlpatterns = [
  path('repos/', GitHubRepositoriesView.as_view()),
  path('github/callback/', GitHubAuthCallback.as_view(), name='github_callback'),
  path('api/github/repositories/', GitHubRepositoriesView.as_view(), name='github_repositories')
]
