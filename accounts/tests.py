from django.test import TestCase
from accounts.models import GitHubUser

class GitHubUserTestCase(TestCase):
    fixtures = ['github_users.json']

    def setUp(self):
        """Set up common test data."""
        self.github_user = GitHubUser.objects.first()
        self.github_user_count = GitHubUser.objects.count()

    def test_github_user_count(self):
        """Check if the number of GitHubUser objects in the database is correct."""
        self.assertEqual(self.github_user_count, 2)

    def test_github_user_data(self):
        """Check if the data of the first GitHubUser object matches the fixture."""
        self.assertEqual(self.github_user.user_name, 'User One')
        self.assertEqual(str(self.github_user.registration_date), '2024-05-01 00:00:00+00:00')
        self.assertEqual(str(self.github_user.last_login), '2024-05-04 08:30:00+00:00')
        self.assertEqual(self.github_user.repos, 'https://github.com/user1')
        self.assertEqual(self.github_user.commits_url, 'https://api.github.com/user1/commits')
        self.assertEqual(self.github_user.last_commit_repo, 'Project A')
        self.assertEqual(self.github_user.opensource_commit_count, 10)

    def test_github_user_str_method(self):
        """Check the __str__ method of GitHubUser model."""
        self.assertEqual(str(self.github_user), 'user1')
