from django.contrib import admin
from .models import (
    User,
    MusicHistory,
    VideoHistory,
    MusicPlaylist,
    VideoPlaylist,
    PlaylistTrack,
    PlaylistClip,
)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'user_uid', 'phone_number']
    search_fields = ['username', 'email']


@admin.register(MusicPlaylist)
class MusicPlaylistAdmin(admin.ModelAdmin):
    list_display = ['folder_name', 'user', 'created_at']
    list_filter = ['created_at']
    search_fields = ['folder_name', 'user__username']


@admin.register(VideoPlaylist)
class VideoPlaylistAdmin(admin.ModelAdmin):
    list_display = ['folder_name', 'user', 'created_at']
    list_filter = ['created_at']
    search_fields = ['folder_name', 'user__username']


@admin.register(PlaylistTrack)
class PlaylistTrackAdmin(admin.ModelAdmin):
    list_display = ['playlist', 'music', 'order', 'created_at']
    list_filter = ['created_at']
    search_fields = ['playlist__folder_name', 'music__music_title']


@admin.register(PlaylistClip)
class PlaylistClipAdmin(admin.ModelAdmin):
    list_display = ['playlist', 'video', 'order', 'created_at']
    list_filter = ['created_at']
    search_fields = ['playlist__folder_name', 'video__video_title']


@admin.register(MusicHistory)
class MusicHistoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'music', 'played_at']
    list_filter = ['played_at']
    search_fields = ['user__username', 'music__music_title']


@admin.register(VideoHistory)
class VideoHistoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'video', 'played_at']
    list_filter = ['played_at']
    search_fields = ['user__username', 'video__video_title']
