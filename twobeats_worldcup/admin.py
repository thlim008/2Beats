from django.contrib import admin
from .models import WorldCupResult

@admin.register(WorldCupResult)
class WorldCupResultAdmin(admin.ModelAdmin):
    list_display = ['user', 'winner_music', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'winner_music__music_title']