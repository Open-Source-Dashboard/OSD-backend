from django.urls import path
from .views import UserListView, UserDetailView, CheckUserView, CheckAndAddDonutsView

urlpatterns = [
    path('users/', UserListView.as_view(), name='user-list'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='user-detail'),
    path('users/check-user/', CheckUserView.as_view(), name='check-user'),
    path('user/check-commits/<str:user_name>', CheckAndAddDonutsView.as_view(), name='check-commits')
]