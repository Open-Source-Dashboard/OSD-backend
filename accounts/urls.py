from django.urls import path
from .views import UserListView, UserDetailView, CheckUserView

urlpatterns = [
    path('users/', UserListView.as_view(), name='user-list'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='user-detail'),
    path('users/check-user/', CheckUserView.as_view(), name='check-user'),
    path('users/<slug:user_name>/user-commits/', UserDetailView.as_view(), name='user-commits')
    
]
