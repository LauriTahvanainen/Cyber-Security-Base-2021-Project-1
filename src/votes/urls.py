from django.urls import path

from . import views

app_name = 'votes'
urlpatterns = [
    path('', views.home, name='home'),
    path('proposal', views.create_proposal, name='create_proposal')
]