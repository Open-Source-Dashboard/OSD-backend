import os
import requests
from django.http import JsonResponse
from django.views import View
from django.utils import timezone
from accounts.models import GitHubUser
from django.forms.models import model_to_dict
from django.db.models import F
from datetime import datetime

class GitHubAuthCallback(View):

    def get(self, request):
        code = request.GET.get('code')

        # Determine callback URL based on request headers
        callback_url = self.determine_callback_url(request)
        if not callback_url:
            return JsonResponse({'error': 'Invalid request'}, status=400)

        client_id = os.getenv('GITHUB_CLIENT_ID')
        client_secret = os.getenv('GITHUB_CLIENT_SECRET')

        token_url = 'https://github.com/login/oauth/access_token'
        data = {
            'client_id': client_id,
            'client_secret': client_secret,
            'code': code,
        }

        headers = {
            'Accept': 'application/json',
        }

        try:
            response = requests.post(token_url, data=data, headers=headers)
            response.raise_for_status()
            response_json = response.json()
        except requests.exceptions.RequestException as e:
            print(f'Failed to get access token: {e}')
            return JsonResponse({'error': 'Failed to get access token'}, status=400)

        if 'access_token' in response_json:
            github_username = self.get_github_username(response_json['access_token'])
            access_token = response_json['access_token']
            
            if github_username:
                user, created = GitHubUser.objects.get_or_create(github_username=github_username)
                
                if created:
                    user.user_name = github_username
                else:
                    user.last_login = timezone.now()
                    user.save()
                
                user_model_data = model_to_dict(user)

                if 'last_login' in user_model_data:
                    user_model_data['last_login'] = user_model_data['last_login'].isoformat()
                
                return JsonResponse({'github_username': github_username, 'access_token': access_token, 'user_model_data': user_model_data}, status=200)
            else:
                return JsonResponse({'error': 'Failed to fetch GitHub github_username'}, status=400)
        else:
            return JsonResponse({'error': 'Failed to get access token'}, status=400)

    def get_github_username(self, user_access_token):
        url = 'https://api.github.com/user'
        headers = {
            'Authorization': f'Bearer {user_access_token}'
        }

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            response_json = response.json()
            return response_json['login']
        except requests.exceptions.RequestException as e:
            print(f'Failed to fetch GitHub user: {e}')
            return None

    def determine_callback_url(self, request):
        # Modify this logic based on your requirements
        host = request.headers.get('Host')
        if host == 'localhost:8000':
            return 'http://localhost:8000/accounts/github/callback'
        elif host == 'donutdashboard.netlify.app':
            return 'https://donutdashboard.netlify.app/authentication'
        elif host == 'donutdashboard-td.netlify.app':
            return 'https://donutdashboard-td.netlify.app/authentication'
        else:
            return None
