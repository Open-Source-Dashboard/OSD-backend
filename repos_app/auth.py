import requests

def get_github_username(user_access_token):
    url = 'https://api.github.com/user'
    headers = {
        'Authorization': f'Bearer {user_access_token}'
    }

    try:
        response = requests.get(url, headers=headers)
        response_json = response.json()
        # print("*** username from frontend: ", response_json['login'])
        return response_json['login']
    except requests.exceptions.RequestException as e:
        print(f'Failed to fetch GitHub user: {e}')
        return None