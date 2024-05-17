from django.contrib.auth.models import User 
from django.shortcuts import render, get_object_or_404
from rest_framework import generics
from .serializers import GitHubUserSerializer
import requests
from django.http import JsonResponse
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import GitHubUser


class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = GitHubUserSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return render(request, 'users_list.html', {'users': serializer.data})

class UserDetailView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = GitHubUserSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return render(request, 'user_detail.html', {'user': serializer.data})

    def github_repositories(request, username):
        url = f'https://api.github.com/users/{username}/repos'
        response = requests.get(url)

        if response.status_code == 200:
            repositories = response.json()
            return render(request, 'github_repositories.html', {'repositories': repositories})
        else:
            error_message = 'Failed to fetch repositories.'
            return render(request, 'github_repositories_error.html', {'error': error_message})


class CheckUserView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        user_id = request.GET.get('user_id')
        is_new_user = not User.objects.filter(id=user_id).exists()
        return JsonResponse({'isNewUser': is_new_user})

class CheckAndAddDonutsView(LoginRequiredMixin, View):
    def get(self, request, user_name, *args, **kwargs):
        user = get_object_or_404(GitHubUser, user_name=user_name)
        user.check_and_increment_donut()
        return JsonResponse(
            {
                "status": "success",
                "message": "Check completed.",
                "user": user.user_name,
                "opensource_commit_count": user.opensource_commit_count,
            }
        )
