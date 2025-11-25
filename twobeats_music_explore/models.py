# twobeats_music_explore/models.py

from django.db import models
from django.conf import settings
from twobeats_upload.models import Music

class MusicLike(models.Model):
    """음악 좋아요"""
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='사용자',
        db_column='ml_user_id'
    )
    music = models.ForeignKey(
        Music,
        on_delete=models.CASCADE,
        verbose_name='음악',
        db_column='ml_music_id'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='좋아요일',
        db_column='ml_created_at'
    )
    
    class Meta:
        db_table = 'music_like'
        unique_together = ('user', 'music')  # 중복 방지
        verbose_name = '음악 좋아요'
        verbose_name_plural = '음악 좋아요'
    
    def __str__(self):
        return f"{self.user.username} → {self.music.music_title}"


class MusicComment(models.Model):
    """음악 댓글"""
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='작성자',
        db_column='mc_user_id'
    )
    music = models.ForeignKey(
        Music,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='음악',
        db_column='mc_music_id'
    )
    content = models.TextField(
        verbose_name='내용',
        db_column='mc_content'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='작성일',
        db_column='mc_created_at'
    )
    
    class Meta:
        db_table = 'music_comment'
        ordering = ['-created_at']
        verbose_name = '음악 댓글'
        verbose_name_plural = '음악 댓글'
    
    def __str__(self):
        return f"{self.user.username}: {self.content[:20]}"