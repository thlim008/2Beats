from django.contrib import admin
from .models import User, Playlist, PlaylistMusic, PlaylistVideo, HistoryList

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'user_uid', 'phone_number']
    search_fields = ['username', 'email']

@admin.register(Playlist)
class PlaylistAdmin(admin.ModelAdmin):
    list_display = ['folder_name', 'user', 'created_at']
    list_filter = ['created_at']
    search_fields = ['folder_name', 'user__username']

@admin.register(PlaylistMusic)
class PlaylistMusicAdmin(admin.ModelAdmin):
    list_display = ['playlist', 'music', 'order', 'created_at']
    list_filter = ['created_at']
    search_fields = ['playlist__folder_name', 'music__music_title']

# 25.11.25/Lim : 하실거면 하시고~ 말면 말고~ 일단 만들어놓았습니다.
@admin.register(PlaylistVideo)
class PlaylistVideoAdmin(admin.ModelAdmin):
    list_display = ['playlist', 'video', 'order', 'created_at']
    list_filter = ['created_at']
    search_fields = ['playlist__folder_name', 'video__video_title']

@admin.register(HistoryList)
class HistoryListAdmin(admin.ModelAdmin):
    list_display = ['user', 'music', 'played_at']
    list_filter = ['played_at']
    search_fields = ['user__username', 'music__music_title']