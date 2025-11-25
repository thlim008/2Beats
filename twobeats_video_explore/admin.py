from django.contrib import admin
from .models import VideoLike, VideoComment

@admin.register(VideoLike)
class VideoLikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'video', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'video__video_title']

@admin.register(VideoComment)
class VideoCommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'video', 'content', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'video__video_title', 'content']