from django.contrib import admin
from .models import WorldCupGame, WorldCupResult

# 게임 상세 페이지(WorldCupGame) 들어가면 결과(WorldCupResult)를 바로 볼 수 있게 설정
class WorldCupResultInline(admin.TabularInline):
    model = WorldCupResult
    extra = 0
    ordering = ('wc_final_rank',) # 1등부터 순서대로 정렬

@admin.register(WorldCupGame)
class WorldCupGameAdmin(admin.ModelAdmin):
    list_display = ['wc_game_serial_key', 'wc_user', 'wc_total_rounds', 'wc_created_at']
    list_filter = ['wc_created_at', 'wc_total_rounds']
    search_fields = ['wc_user__username'] # 사용자 이름으로 검색
    inlines = [WorldCupResultInline] # 게임 안에 결과 리스트 포함

@admin.register(WorldCupResult)
class WorldCupResultAdmin(admin.ModelAdmin):
    list_display = ['wc_game', 'wc_music', 'wc_final_rank', 'wc_score']
    list_filter = ['wc_final_rank']
    search_fields = ['wc_music__music_title', 'wc_game__wc_user__username']