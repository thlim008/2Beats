from django.contrib import admin
from .models import Tag, Music, Video

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(Music)
class MusicAdmin(admin.ModelAdmin):
    list_display = [
        'music_title',
        'music_singer',
        'music_type',
        'music_count',
        'music_like_count',
        'uploader',
        'music_created_at'
    ]
    list_filter = ['music_type', 'music_created_at']
    search_fields = ['music_title', 'music_singer']
    filter_horizontal = ['tags']

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = [
        'video_title',
        'video_singer',
        'video_type',
        'video_views',
        'video_play_count',
        'video_user',
        'video_created_at'
    ]
    list_filter = ['video_type', 'video_created_at']
    search_fields = ['video_title', 'video_singer']
    filter_horizontal = ['tags']