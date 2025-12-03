from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('twobeats_account', '0006_remove_legacy_playlists'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='HistoryList',
            new_name='MusicHistory',
        ),
        migrations.RenameModel(
            old_name='HistoryVideo',
            new_name='VideoHistory',
        ),
        migrations.AlterModelTable(
            name='musichistory',
            table='music_history',
        ),
        migrations.AlterModelTable(
            name='videohistory',
            table='video_history',
        ),
        migrations.AlterModelOptions(
            name='musichistory',
            options={'ordering': ['-played_at'], 'verbose_name': '음악 재생 기록', 'verbose_name_plural': '음악 재생 기록'},
        ),
        migrations.AlterModelOptions(
            name='videohistory',
            options={'ordering': ['-played_at'], 'verbose_name': '영상 재생 기록', 'verbose_name_plural': '영상 재생 기록'},
        ),
    ]
