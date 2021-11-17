from django.urls import path

from . import views

app_name = 'proposals'
urlpatterns = [
    path('', views.home, name='home'),
    path('proposal/new', views.create_proposal, name='create_proposal'),
    path('login', views.login, name='login'),
    path('register', views.register, name='register'),
    path('<int:proposal_id>/', views.proposal, name='proposal'),
    path('proposal/vote', views.vote, name='vote'),
    path('signout', views.signout, name='signout')
]