from django.urls import path
from . import views

urlpatterns = [
  path("/", views.say_hello, name="say_hello")
  # path('osd_dashboard_app/github', views.say_hello)
]