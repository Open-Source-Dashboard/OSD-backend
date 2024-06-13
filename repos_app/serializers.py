from rest_framework import serializers
from .models import GithubRepo

class GithubRepoSerializer(serializers.ModelSerializer):
    class Meta:
        model = GithubRepo
        fields = ['id', 'name', 'license', 'topics', 'url', 'commits_url', 'stargazers_count', 'latest_commit_timestamp', 'latest_committer']