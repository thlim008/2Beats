from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid


class User(AbstractUser):
    # 고유 UUID를 PK로 사용
    user_uid = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name='고유ID',
    )

    # 추가 필드
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='전화번호',
        db_column='user_pnum',
    )
    profile_image = models.ImageField(
        upload_to='profiles/',
        blank=True,
        null=True,
        verbose_name='프로필 이미지',
        db_column='user_image',
    )

    class Meta:
        db_table = 'user'
        verbose_name = '사용자'
        verbose_name_plural = '사용자'

    def __str__(self):
        return self.username


class MusicPlaylist(models.Model):
    """음악 전용 플레이리스트"""

    user = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        related_name='music_playlists',
        verbose_name='사용자',
        db_column='mplaylist_user_id',
    )
    folder_name = models.CharField(
        max_length=100,
        verbose_name='폴더명',
        db_column='mplaylist_folder_name',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='생성일',
        db_column='mplaylist_created_at',
    )

    class Meta:
        db_table = 'music_playlist'
        verbose_name = '음악 플레이리스트'
        verbose_name_plural = '음악 플레이리스트'

    def __str__(self):
        return f"{self.user.username} - {self.folder_name}"


class VideoPlaylist(models.Model):
    """영상 전용 플레이리스트"""

    user = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        related_name='video_playlists',
        verbose_name='사용자',
        db_column='vplaylist_user_id',
    )
    folder_name = models.CharField(
        max_length=100,
        verbose_name='폴더명',
        db_column='vplaylist_folder_name',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='생성일',
        db_column='vplaylist_created_at',
    )

    class Meta:
        db_table = 'video_playlist'
        verbose_name = '영상 플레이리스트'
        verbose_name_plural = '영상 플레이리스트'

    def __str__(self):
        return f"{self.user.username} - {self.folder_name}"


class PlaylistTrack(models.Model):
    """음악 플레이리스트의 트랙"""

    playlist = models.ForeignKey(
        MusicPlaylist,
        on_delete=models.CASCADE,
        related_name='tracks',
        verbose_name='플레이리스트',
        db_column='ptrack_playlist_id',
    )
    music = models.ForeignKey(
        'twobeats_upload.Music',
        on_delete=models.CASCADE,
        verbose_name='음악',
        db_column='ptrack_music_id',
    )
    order = models.IntegerField(
        default=0,
        verbose_name='순서',
        db_column='ptrack_order',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='추가일',
        db_column='ptrack_created_at',
    )

    class Meta:
        db_table = 'playlist_track'
        ordering = ['order']
        unique_together = ('playlist', 'music')
        verbose_name = '플레이리스트 트랙'
        verbose_name_plural = '플레이리스트 트랙'

    def __str__(self):
        return f"{self.playlist.folder_name} - {self.music.music_title}"


class PlaylistClip(models.Model):
    """영상 플레이리스트의 클립"""

    playlist = models.ForeignKey(
        VideoPlaylist,
        on_delete=models.CASCADE,
        related_name='clips',
        verbose_name='플레이리스트',
        db_column='pclip_playlist_id',
    )
    video = models.ForeignKey(
        'twobeats_upload.Video',
        on_delete=models.CASCADE,
        verbose_name='영상',
        db_column='pclip_video_id',
    )
    order = models.IntegerField(
        default=0,
        verbose_name='순서',
        db_column='pclip_order',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='추가일',
        db_column='pclip_created_at',
    )

    class Meta:
        db_table = 'playlist_clip'
        ordering = ['order']
        unique_together = ('playlist', 'video')
        verbose_name = '플레이리스트 영상'
        verbose_name_plural = '플레이리스트 영상'

    def __str__(self):
        return f"{self.playlist.folder_name} - {self.video.video_title}"


class MusicHistory(models.Model):
    """음악 재생 기록"""

    user = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        verbose_name='사용자',
        db_column='historylist_user_id',
    )
    music = models.ForeignKey(
        'twobeats_upload.Music',
        on_delete=models.CASCADE,
        verbose_name='음악',
        db_column='historylist_music_id',
    )
    played_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='재생일시',
        db_column='historylist_played_at',
    )

    class Meta:
        db_table = 'music_history'
        ordering = ['-played_at']
        verbose_name = '음악 재생 기록'
        verbose_name_plural = '음악 재생 기록'

    def __str__(self):
        return f"{self.user.username} - {self.music.music_title}"


class VideoHistory(models.Model):
    """영상 재생 기록"""

    user = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        verbose_name='사용자',
        db_column='historyvideo_user_id',
    )
    video = models.ForeignKey(
        'twobeats_upload.Video',
        on_delete=models.CASCADE,
        verbose_name='영상',
        db_column='historyvideo_video_id',
    )
    played_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='재생일시',
        db_column='historyvideo_played_at',
    )

    class Meta:
        db_table = 'video_history'
        ordering = ['-played_at']
        verbose_name = '영상 재생 기록'
        verbose_name_plural = '영상 재생 기록'

    def __str__(self):
        return f"{self.user.username} - {self.video.video_title}"
