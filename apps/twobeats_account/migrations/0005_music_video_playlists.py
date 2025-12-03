from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('twobeats_account', '0004_historyvideo'),
        ('twobeats_upload', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='MusicPlaylist',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('folder_name', models.CharField(db_column='mplaylist_folder_name', max_length=100, verbose_name='폴더명')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_column='mplaylist_created_at', verbose_name='생성일')),
                ('user', models.ForeignKey(db_column='mplaylist_user_id', on_delete=django.db.models.deletion.CASCADE, related_name='music_playlists', to='twobeats_account.user', verbose_name='사용자')),
            ],
            options={
                'verbose_name': '음악 플레이리스트',
                'verbose_name_plural': '음악 플레이리스트',
                'db_table': 'music_playlist',
            },
        ),
        migrations.CreateModel(
            name='VideoPlaylist',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('folder_name', models.CharField(db_column='vplaylist_folder_name', max_length=100, verbose_name='폴더명')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_column='vplaylist_created_at', verbose_name='생성일')),
                ('user', models.ForeignKey(db_column='vplaylist_user_id', on_delete=django.db.models.deletion.CASCADE, related_name='video_playlists', to='twobeats_account.user', verbose_name='사용자')),
            ],
            options={
                'verbose_name': '영상 플레이리스트',
                'verbose_name_plural': '영상 플레이리스트',
                'db_table': 'video_playlist',
            },
        ),
        migrations.CreateModel(
            name='PlaylistTrack',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.IntegerField(db_column='ptrack_order', default=0, verbose_name='순서')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_column='ptrack_created_at', verbose_name='추가일')),
                ('music', models.ForeignKey(db_column='ptrack_music_id', on_delete=django.db.models.deletion.CASCADE, to='twobeats_upload.music', verbose_name='음악')),
                ('playlist', models.ForeignKey(db_column='ptrack_playlist_id', on_delete=django.db.models.deletion.CASCADE, related_name='tracks', to='twobeats_account.musicplaylist', verbose_name='플레이리스트')),
            ],
            options={
                'verbose_name': '플레이리스트 트랙',
                'verbose_name_plural': '플레이리스트 트랙',
                'db_table': 'playlist_track',
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='PlaylistClip',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.IntegerField(db_column='pclip_order', default=0, verbose_name='순서')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_column='pclip_created_at', verbose_name='추가일')),
                ('playlist', models.ForeignKey(db_column='pclip_playlist_id', on_delete=django.db.models.deletion.CASCADE, related_name='clips', to='twobeats_account.videoplaylist', verbose_name='플레이리스트')),
                ('video', models.ForeignKey(db_column='pclip_video_id', on_delete=django.db.models.deletion.CASCADE, to='twobeats_upload.video', verbose_name='영상')),
            ],
            options={
                'verbose_name': '플레이리스트 영상',
                'verbose_name_plural': '플레이리스트 영상',
                'db_table': 'playlist_clip',
                'ordering': ['order'],
            },
        ),
        migrations.AlterUniqueTogether(
            name='playlisttrack',
            unique_together={('playlist', 'music')},
        ),
        migrations.AlterUniqueTogether(
            name='playlistclip',
            unique_together={('playlist', 'video')},
        ),
    ]
