from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid

class User(AbstractUser):
    
    # user_uid를 PK로 (UUID)
    user_uid = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name='고유ID'
    )
    
    # username은 AbstractUser에 이미 있음 (user_id로 사용)
    # password도 AbstractUser에 이미 있음 (user_pwd)
    
    # 추가 필드
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='전화번호',
        db_column='user_pnum'
    )
    profile_image = models.ImageField(
        upload_to='profiles/',
        blank=True,
        null=True,
        verbose_name='프로필 이미지',
        db_column='user_image'
    )
    
    class Meta:
        db_table = 'user'
        verbose_name = '사용자'
        verbose_name_plural = '사용자'
    
    def __str__(self):
        return self.username
    
class Playlist(models.Model):
    """플레이리스트 폴더"""
    
    user = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        related_name='playlists',
        verbose_name='사용자',
        db_column='playlist_user_id'
    )
    folder_name = models.CharField(
        max_length=100,
        verbose_name='폴더명',
        db_column='playlist_folder_name'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='생성일',
        db_column='playlist_created_at'
    )
    
    class Meta:
        db_table = 'playlist'
        verbose_name = '플레이리스트'
        verbose_name_plural = '플레이리스트'
    
    def __str__(self):
        return f"{self.user.username}의 {self.folder_name}"


class PlaylistMusic(models.Model):
    """플레이리스트 안의 곡들"""
    
    playlist = models.ForeignKey(
        Playlist,
        on_delete=models.CASCADE,
        related_name='playlist_musics',
        verbose_name='플레이리스트',
        db_column='pm_playlist_id'
    )
    music = models.ForeignKey(
        'twobeats_upload.Music',
        on_delete=models.CASCADE,
        verbose_name='음악',
        db_column='pm_music_id'
    )
    order = models.IntegerField(
        default=0,
        verbose_name='순서',
        db_column='pm_order'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='추가일',
        db_column='pm_created_at'
    )
    
    class Meta:
        db_table = 'playlist_music'
        ordering = ['order']
        unique_together = ('playlist', 'music')
        verbose_name = '플레이리스트 음악'
        verbose_name_plural = '플레이리스트 음악'
    
    def __str__(self):
        return f"{self.playlist.folder_name} - {self.music.music_title}"

# 25.11.25/Lim : 하실거면 하시고~ 말면 말고~ 일단 만들어놓았습니다.
class PlaylistVideo(models.Model):
    """플레이리스트 안의 영상들"""
    
    playlist = models.ForeignKey(
        Playlist,
        on_delete=models.CASCADE,
        related_name='playlist_videos',
        verbose_name='플레이리스트',
        db_column='pv_playlist_id'
    )
    video = models.ForeignKey(
        'twobeats_upload.Video',
        on_delete=models.CASCADE,
        verbose_name='영상',
        db_column='pv_video_id'
    )
    order = models.IntegerField(
        default=0,
        verbose_name='순서',
        db_column='pv_order'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='추가일',
        db_column='pv_created_at'
    )
    
    class Meta:
        db_table = 'playlist_video'
        ordering = ['order']
        unique_together = ('playlist', 'video')
        verbose_name = '플레이리스트 영상'
        verbose_name_plural = '플레이리스트 영상'
    
    def __str__(self):
        return f"{self.playlist.folder_name} - {self.video.video_title}"
    

class HistoryList(models.Model):
    """음악 재생 이력"""
    
    user = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        verbose_name='사용자',
        db_column='historylist_user_id'
    )
    music = models.ForeignKey(
        'twobeats_upload.Music',
        on_delete=models.CASCADE,
        verbose_name='음악',
        db_column='historylist_music_id'
    )
    played_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='재생일시',
        db_column='historylist_played_at'
    )
    
    class Meta:
        db_table = 'historylist'
        ordering = ['-played_at']
        verbose_name = '재생 이력'
        verbose_name_plural = '재생 이력'
    
    def __str__(self):
        return f"{self.user.username} → {self.music.music_title}"