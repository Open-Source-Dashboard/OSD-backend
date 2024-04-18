from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Repo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('repo_name', models.CharField(max_length=255)),
                ('license', models.CharField(max_length=100)),
                ('avatar_url', models.URLField()),
                ('url', models.URLField()),
                ('commits_url', models.URLField()),
                ('topics', models.JSONField()),
                ('latest_commit_timestamp', models.DateTimeField(blank=True, null=True)),
                ('latest_committer', models.CharField(blank=True, max_length=255, null=True)),
            ],
        ),
    ]
