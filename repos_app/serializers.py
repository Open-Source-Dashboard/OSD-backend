from rest_framework import serializers
from .models import GithubUser, GithubRepo

class GithubUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = GithubUser
        fields = ['id', 'username', 'avatar_url', 'profile_url']

class GithubRepoSerializer(serializers.ModelSerializer):
    class Meta:
        model = GithubRepo
        # fields = ['id', 'name', 'license', 'topics', 'url', 'avatar_url', 'commits_url', 'stargazers_count', 'latest_commit_timestamp', 'latest_committer']
        fields = ['id', 'name', 'license', 'topics', 'url', 'commits_url', 'stargazers_count', 'latest_commit_timestamp', 'latest_committer']