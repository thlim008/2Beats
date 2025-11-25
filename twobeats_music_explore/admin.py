from django.contrib import admin
from .models import MusicLike, MusicComment

@admin.register(MusicLike)
class MusicLikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'music', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'music__music_title']

@admin.register(MusicComment)
class MusicCommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'music', 'content', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'music__music_title', 'content']