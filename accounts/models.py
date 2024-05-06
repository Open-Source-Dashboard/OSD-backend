from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils.translation import gettext_lazy as _

class GitHubUser(AbstractUser):
    user_name = models.CharField(max_length=255, blank=True, null=True)
    registration_date = models.DateTimeField(auto_now_add=True)
    last_login_date = models.DateTimeField(auto_now=True)
    repos = models.URLField()
    commits_url = models.URLField()
    last_commit_repo = models.CharField(max_length=255)
    donut_stampcard_count = models.IntegerField(default=0)
    donut_box_count = models.IntegerField(default=0)

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

    def __str__(self):
        return self.user_name
