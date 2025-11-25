from django.db import models

# Create your models here.
# twobeats_video_explore/models.py

from django.db import models
from django.conf import settings
from twobeats_upload.models import Video

class VideoLike(models.Model):
    """영상 좋아요"""
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='사용자',
        db_column='vl_user_id'
    )
    video = models.ForeignKey(
        Video,
        on_delete=models.CASCADE,
        verbose_name='영상',
        db_column='vl_video_id'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='좋아요일',
        db_column='vl_created_at'
    )
    
    class Meta:
        db_table = 'video_like'
        unique_together = ('user', 'video')  # 중복 방지
        verbose_name = '영상 좋아요'
        verbose_name_plural = '영상 좋아요'
    
    def __str__(self):
        return f"{self.user.username} → {self.video.video_title}"


class VideoComment(models.Model):
    """영상 댓글"""
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='작성자',
        db_column='vc_user_id'
    )
    video = models.ForeignKey(
        Video,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='영상',
        db_column='vc_video_id'
    )
    content = models.TextField(
        verbose_name='내용',
        db_column='vc_content'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='작성일',
        db_column='vc_created_at'
    )
    
    class Meta:
        db_table = 'video_comment'
        ordering = ['-created_at']
        verbose_name = '영상 댓글'
        verbose_name_plural = '영상 댓글'
    
    def __str__(self):
        return f"{self.user.username}: {self.content[:20]}"