from django.test import TestCase
from django.contrib.auth import get_user_model

class GitHubUserTestCase(TestCase):
    fixtures = ['github_users.json']

    def test_github_user_count(self):
        # Check if the number of GitHubUser objects in the database is correct
        from accounts.models import GitHubUser
        github_user_count = GitHubUser.objects.count()
        self.assertEqual(github_user_count, 2)

    def test_github_user_data(self):
        # Check if the data of the first GitHubUser object matches the fixture
        from accounts.models import GitHubUser

        # Get the first GitHubUser object from the database
        github_user = GitHubUser.objects.first()

        # Check if the fields match the fixture data
        self.assertEqual(github_user.user_name, 'User One')
        self.assertEqual(str(github_user.registration_date), '2024-05-01 00:00:00+00:00')
        self.assertEqual(str(github_user.last_login_date), '2024-05-04 08:30:00+00:00')
        self.assertEqual(github_user.repos, 'https://github.com/user1')
        self.assertEqual(github_user.commits_url, 'https://api.github.com/user1/commits')
        self.assertEqual(github_user.last_commit_repo, 'Project A')
        self.assertEqual(github_user.donut_stampcard_count, 5)
        self.assertEqual(github_user.donut_box_count, 3)

    def test_github_user_str_method(self):
        # Check the __str__ method of GitHubUser model
        from accounts.models import GitHubUser

        # Get a GitHubUser object
        github_user = GitHubUser.objects.first()

        # Check if __str__ method returns the expected string
        self.assertEqual(str(github_user), 'user1')
