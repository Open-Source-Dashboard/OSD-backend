import os
import requests
from django.http import JsonResponse
from django.views import View
from .models import GitHubUser
from django.forms.models import model_to_dict

def get_github_username(user_access_token):
    url = 'https://api.github.com/user'
    headers = {
        'Authorization': f'Bearer {user_access_token}'
    }

    try:
        response = requests.get(url, headers=headers)
        response_json = response.json()
        print("username from frontend: ", response_json['login'])
        return response_json['login']
    except requests.exceptions.RequestException as e:
        print(f'Failed to fetch GitHub user: {e}')
        return None

class GitHubAuthCallback(View):
    def get(self, request):
        print('GitHubAuthCallback request: ', request)

        code = request.GET.get('code')

        client_id = os.getenv('GITHUB_CLIENT_ID')
        client_secret = os.getenv('GITHUB_CLIENT_SECRET')

        token_url = 'https://github.com/login/oauth/access_token'
        data = {
            'client_id': client_id,
            'client_secret': client_secret,
            'code': code,
        }
        print('data: ', data)

        headers = {
            'Accept': 'application/json',
        }

        response = requests.post(token_url, data=data, headers=headers)
        response_json = response.json()
        
        print('response_json request: ', response_json)

        if 'access_token' in response_json:
            print('response_json', response_json)
            github_username = get_github_username(response_json['access_token'])
            access_token = response_json['access_token']
            expires_in = response_json['expires_in']
            refresh_token = response_json['refresh_token']
            refresh_token_expires_in = response_json['refresh_token_expires_in']
            token_type = response_json['token_type']
            scope = response_json['scope']
            
            if github_username:
                user, created = GitHubUser.objects.get_or_create(username=github_username)
                if created:
                    user.user_name = github_username
                user.save()
                
                user_model_data = model_to_dict(user)
                
                return JsonResponse({'github_username': github_username, 'access_token': access_token, 'user_model_data': user_model_data}, status=200)
            else:
                return JsonResponse({'error': 'Failed to fetch GitHub username'}, status=400)
        else:
            return JsonResponse({'error': 'Failed to get access token'}, status=400)