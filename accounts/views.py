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
        return JsonResponse({'users': serializer.data})

class UserDetailView(generics.RetrieveAPIView):
    queryset = GitHubUser.objects.all()
    serializer_class = GitHubUserSerializer
    lookup_field = 'user_name'

    def retrieve(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(user)
        user_data = serializer.data
        print('user data:', user_data)
        try:
            user_events = GitHubUser.objects.fetch_user_push_events(user.user_name) 
            print('user events:', user_events)
        except requests.RequestException as e:
            return JsonResponse({'error': str(e)}, status=500)
        
        after_registration_events = GitHubUser.objects.events_after_registration(user_events)
        print('after registration events:', after_registration_events)
        
        user_commits = GitHubUser.objects.get_commits_from_push(after_registration_events)
        print('User commits:', user_commits)
        
        commit_data = {
            'user': user_data, 
            'user commits': user_commits,
        }
        return JsonResponse(commit_data)


class CheckUserView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        print('request from CheckUserView', request)
        user_id = request.GET.get('user_id')
        is_new_user = not User.objects.filter(id=user_id).exists()
        return JsonResponse({'isNewUser': is_new_user})
