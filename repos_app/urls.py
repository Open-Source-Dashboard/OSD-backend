from django.urls import path
from repos_app.views import GitHubRepositoriesView
from .auth import GitHubAuthCallback 


urlpatterns = [
  path('', GitHubRepositoriesView.as_view()),
  path('github/callback/', GitHubAuthCallback.as_view(), name='github_callback'),
  path('api/github/repositories/', GitHubRepositoriesView.as_view(), name='github_repositories')
  path('check_user_commits/', GitHubRepositoriesView.as_view({'get': 'check_user_commits'}), name='check_user_commits')
]
