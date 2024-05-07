from rest_framework import serializers
from .models import GitHubUser

class GitHubUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = GitHubUser
        fields = ['id', 'user_name', 'registration_date', 'last_login_date', 'donut_stampcard_count', 'donut_box_count']
