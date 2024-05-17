from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils.translation import gettext_lazy as _
from .models import GitHubRepo
from datetime import datetime

class GitHubUser(AbstractUser):
    user_name = models.CharField(max_length=255, blank=True, null=True)
    registration_date = models.DateTimeField(auto_now_add=True)
    last_login_date = models.DateTimeField(auto_now=True)
    # repos = models.URLField()
    commits_url = models.URLField()
    last_commit_repo = models.CharField(max_length=255)
    opensource_commit_count = models.IntegerField(default=0)

    groups = models.ManyToManyField(
        Group,
        verbose_name=_('groups'),
        blank=True,
        related_name='githubuser_set',
        related_query_name='githubuser',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_('user permissions'),
        blank=True,
        related_name='githubuser_set',
        related_query_name='githubuser',
    )

    def check_and_increment_donut(self):
        authenticated_user = self.user_name
        user_register_date = self.registration_date.strptime("%Y-%m-%dT%H:%M:%SZ")

        repositories = GitHubRepo.objects.fetch_repos()
        if not repositories:
            print('No repos fetched')
            return 
        has_committed = GitHubRepo.objects.check_user_commits(repositories, authenticated_user, user_register_date)
        if has_committed:
            self.opensource_commit_count += 1
            self.save
            print(f"{authenticated_user} has contributed after their first login date. Open-source commit count incremented.")
        else:
            print(f'{authenticated_user} has not contributed to an opensource project')

    def __str__(self):
        return self.user_name
