from django.db import models
from django.conf import settings

class Tag(models.Model):
    """태그 (음악/영상 공통)"""
    
    name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='태그명',
        db_column='tag_name'
    )
    
    class Meta:
        db_table = 'tag_table'
        verbose_name = '태그'
        verbose_name_plural = '태그'
    
    def __str__(self):
        return self.name


class Music(models.Model):
    """음악"""
    
    music_title = models.CharField(
        max_length=200,
        verbose_name='제목'
    )
    music_singer = models.CharField(
        max_length=100,
        verbose_name='가수'
    )
    music_type = models.CharField(
        max_length=50,
        verbose_name='장르'
    )
    music_root = models.FileField(
        upload_to='music/',
        verbose_name='음원파일'
    )
    music_thumbnail = models.ImageField(
        upload_to='thumbnails/music/',
        blank=True,
        null=True,
        verbose_name='썸네일'
    )
    
    # 통계
    music_count = models.IntegerField(
        default=0,
        verbose_name='재생수'
    )
    music_like_count = models.IntegerField(
        default=0,
        verbose_name='좋아요수'
    )
    
    # 업로더
    uploader = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='uploaded_musics',
        verbose_name='업로더',
        db_column='music_user_id'
    )
    
    # 태그 (다대다)
    tags = models.ManyToManyField(
        Tag,
        blank=True,
        related_name='musics'
    )
    
    # 날짜
    music_created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='생성일'
    )
    music_updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='수정일'
    )
    
    class Meta:
        db_table = 'music'
        ordering = ['-music_created_at']
        verbose_name = '음악'
        verbose_name_plural = '음악'
    
    def __str__(self):
        return f"{self.music_title} - {self.music_singer}"


class Video(models.Model):
    """영상"""
    
    video_title = models.CharField(
        max_length=200,
        verbose_name='제목'
    )
    video_singer = models.CharField(
        max_length=100,
        verbose_name='아티스트'
    )
    video_type = models.CharField(
        max_length=50,
        verbose_name='장르'
    )
    video_root = models.FileField(
        upload_to='videos/',
        verbose_name='영상파일'
    )
    video_detail = models.TextField(
        blank=True,
        verbose_name='상세설명'
    )
    video_thumbnail = models.ImageField(
        upload_to='thumbnails/video/',
        blank=True,
        null=True,
        verbose_name='썸네일'
    )
    video_time = models.IntegerField(
        default=0,
        verbose_name='재생시간(초)'
    )
    
    # 통계
    video_views = models.IntegerField(
        default=0,
        verbose_name='조회수'
    )
    video_play_count = models.IntegerField(
        default=0,
        verbose_name='재생수'
    )
    
    # 업로더
    video_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='uploaded_videos',
        verbose_name='업로더',
        db_column='video_user_id'
    )
    
    # 태그
    tags = models.ManyToManyField(
        Tag,
        blank=True,
        related_name='videos'
    )
    
    # 날짜
    video_created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='생성일'
    )
    video_updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='수정일'
    )
    
    class Meta:
        db_table = 'video'
        ordering = ['-video_created_at']
        verbose_name = '영상'
        verbose_name_plural = '영상'
    
    def __str__(self):
        return self.video_title