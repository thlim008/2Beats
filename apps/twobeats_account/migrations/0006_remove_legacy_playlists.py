from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('twobeats_account', '0005_music_video_playlists'),
    ]

    operations = [
        migrations.DeleteModel(
            name='PlaylistMusic',
        ),
        migrations.DeleteModel(
            name='PlaylistVideo',
        ),
        migrations.DeleteModel(
            name='Playlist',
        ),
    ]
