from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('load-more/', views.load_more_tracks, name='load_more'),
    path('track/<str:track_id>/', views.track_detail, name='track_detail'),
    path('add-track/', views.add_track, name='add_track'),
    path('vote/<str:track_id>/', views.vote_track, name='vote_track'),
    path('track/<str:track_id>/cover/', views.track_cover, name='track_cover'),
]   
