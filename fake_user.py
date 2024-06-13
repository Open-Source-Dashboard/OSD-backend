# File for testing
import os
import django
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'osd_backend.settings')
django.setup()

from accounts.models import GitHubUser

fake_user = GitHubUser.objects.create(
    user_name="ariley215",
    registration_date=datetime.now() - timedelta(days=30),
    last_login=datetime.now(),
    last_commit_repo="fake/repo",
    opensource_commit_count=5,
)
print(f'Fake user created: {fake_user.user_name}')