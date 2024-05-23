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
    queryset = GitHubUser.objects.all()
    serializer_class = GitHubUserSerializer

    def retrieve(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(user)
        user_data = serializer.data

        user_events = user.objects.fetch_user_push_events(user_data) 
        after_registration_events = user.objects.events_after_registration(user.registration_date, user_events)
        user_commits = user.objects.get_commits_from_push(after_registration_events)
        
        context = {
            'user': user_data, 
            'user commits': user_commits,
        }
        return render(request, 'user_detail.html', context)

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
