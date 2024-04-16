from django.urls import path
from . import views
from osd_dashboard_app.views import GitHubRepositoriesView

urlpatterns = [
  path('repositories/', GitHubRepositoriesView.as_view()),
]