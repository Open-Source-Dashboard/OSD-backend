import os
import requests
from django.http import JsonResponse
from django.views import View

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

        if 'access_token' in response_json:
            github_username = get_github_username(response_json['access_token'])
            access_token= response_json['access_token']
            return JsonResponse({'github_username': github_username, 'access_token': access_token}, status=200)
        else:
            return JsonResponse(
                {'error': 'Failed to get access token'}, status=400
            )
