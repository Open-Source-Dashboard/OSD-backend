from django.urls import path
from .views import UserListView, UserDetailView, CheckUserView
from .auth import GitHubAuthCallback

urlpatterns = [
    # User-related endpoints
    path('users/', UserListView.as_view(), name='user-list'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='user-detail'),
    path('users/check-user/', CheckUserView.as_view(), name='check-user'),
    # path('users/<slug:user_name>/commits/', UserCommitsView.as_view(), name='user-commits'),
    
    # GitHub OAuth callback endpoint
    path('github/callback/', GitHubAuthCallback.as_view(), name='github-callback'),
    path('accounts/github/callback', GitHubAuthCallback.as_view(), name='github_callback_no_slash')
]
