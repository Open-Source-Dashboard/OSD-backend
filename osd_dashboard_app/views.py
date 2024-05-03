from django.views.generic import TemplateView
from .models import GithubRepo
import environ


env = environ.Env(DEBUG=(bool, False))
environ.Env.read_env(raise_error_if_not_found=True)

class GitHubRepositoriesView(TemplateView):
    template_name = 'repositories.html'
  
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        all_repos = GithubRepo.objects.fetch_repos()
        context['popular_repos'] = GithubRepo.objects.get_popular_repos(all_repos)
        context['featured_repo'] = GithubRepo.objects.get_featured_repo(all_repos)
        context['hacktoberfest_repos'] = GithubRepo.objects.prioritize_hacktoberfest_repos(all_repos)
        
        return context