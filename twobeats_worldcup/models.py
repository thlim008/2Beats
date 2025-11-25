# twobeats_worldcup/models.py

from django.db import models
from django.conf import settings
from twobeats_upload.models import Music

class WorldCupResult(models.Model):
    """월드컵 우승 결과"""
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='사용자',
        db_column='world_cup_id'
    )
    winner_music = models.ForeignKey(
        Music,
        on_delete=models.CASCADE,
        verbose_name='우승곡',
        db_column='world_cup_music'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='플레이일시',
        db_column='world_cup_created_at'
    )
    
    class Meta:
        db_table = 'world_cup'
        verbose_name = '월드컵 결과'
        verbose_name_plural = '월드컵 결과'
    
    def __str__(self):
        return f"{self.user.username} → {self.winner_music.music_title}"