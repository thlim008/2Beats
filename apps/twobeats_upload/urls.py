# apps/twobeats_upload/urls.py
from django.urls import path
from . import views

app_name = 'twobeats_upload'

urlpatterns = [
    # Music
    path('music/', views.music_list, name='music_list'),
    path('music/upload/', views.music_upload_start, name='music_upload_start'),
    path('music/create/', views.music_create, name='music_create'),
    path('music/<int:pk>/', views.music_detail, name='music_detail'),
    path('music/<int:pk>/update/', views.music_update, name='music_update'),
    path('music/<int:pk>/delete/', views.music_delete, name='music_delete'),
    # Video
    path('video/', views.video_list, name='video_list'),
    path('video/upload/', views.video_upload_start, name='video_upload_start'), 
    path('video/create/', views.video_create, name='video_create'),
    path('video/<int:pk>/', views.video_detail, name='video_detail'),
    path('video/<int:pk>/edit/', views.video_update, name='video_update'),
    path('video/<int:pk>/delete/', views.video_delete, name='video_delete'),
    path('video/<int:pk>/like/', views.video_like, name='video_like'),
]
