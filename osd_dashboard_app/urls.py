from django.urls import path
from . import views
from osd_dashboard_app.views import GitHubRepositoriesView
from .auth import GitHubAuthCallback 

urlpatterns = [
  path('repos/', GitHubRepositoriesView.as_view()),
  path('github/callback/', GitHubAuthCallback.as_view(), name='github_callback'),
]
