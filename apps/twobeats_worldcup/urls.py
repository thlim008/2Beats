from django.urls import path
from . import views

app_name = 'twobeats_worldcup'

urlpatterns = [
    path('candidates/', views.get_candidates, name='candidates'),
    path('save/', views.save_game_result, name='save_result'),
    path('play/', views.game_page, name='play'),
    path('ranking/', views.ranking_page, name='ranking'),
    path('chart/', views.wc_popular, name='chart'),
    path('result/<int:game_id>/', views.result_page, name='result'),
    path('save_playlist/<int:game_id>/', views.save_result_to_playlist, name='save_playlist'),
    path('create/', views.custom_worldcup_page, name='create_page'),
    path('api/create/', views.create_custom_worldcup, name='create_api'),
    path('custom/<uuid:access_code>/', views.custom_game_page, name='play_custom'),
]