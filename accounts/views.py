from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework import generics
from .models import GitHubUser
from .serializers import GitHubUserSerializer
import requests


class UserListView(generics.ListAPIView):
    """
    API endpoint that returns a JSON response with a list of all users.
    """
    queryset = User.objects.all()
    serializer_class = GitHubUserSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return JsonResponse({'users': serializer.data})


class UserDetailView(generics.RetrieveAPIView):
    """
    API endpoint that retrieves detailed information about a GitHub user,
    including their commits after registration.
    """
    queryset = GitHubUser.objects.all()
    serializer_class = GitHubUserSerializer
    lookup_field = 'user_name'

    def retrieve(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(user)

        try:
            user_events = GitHubUser.objects.fetch_user_push_events(user.user_name)
            after_registration_events = GitHubUser.objects.events_after_registration(user_events)
            user_commits = GitHubUser.objects.get_commits_from_push(after_registration_events)

            commit_data = {
                'user': serializer.data,
                'user_commits': user_commits,
            }
            return JsonResponse(commit_data)

        except requests.RequestException as e:
            return JsonResponse({'error': str(e)}, status=500)


class CheckUserView(LoginRequiredMixin, View):
    """
    View that checks if a user exists based on user_id.
    """
    def get(self, request, *args, **kwargs):
        user_id = request.GET.get('user_id')
        is_new_user = not User.objects.filter(id=user_id).exists()
        return JsonResponse({'isNewUser': is_new_user})
