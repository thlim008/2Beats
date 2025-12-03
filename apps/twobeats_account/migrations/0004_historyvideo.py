from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('twobeats_upload', '0001_initial'),
        ('twobeats_account', '0003_playlist_category'),
    ]

    operations = [
        migrations.CreateModel(
            name='HistoryVideo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('played_at', models.DateTimeField(auto_now_add=True, db_column='historyvideo_played_at', verbose_name='재생일시')),
                ('user', models.ForeignKey(db_column='historyvideo_user_id', on_delete=django.db.models.deletion.CASCADE, to='twobeats_account.user', verbose_name='사용자')),
                ('video', models.ForeignKey(db_column='historyvideo_video_id', on_delete=django.db.models.deletion.CASCADE, to='twobeats_upload.video', verbose_name='영상')),
            ],
            options={
                'verbose_name': '재생 기록(영상)',
                'verbose_name_plural': '재생 기록(영상)',
                'db_table': 'historyvideo',
                'ordering': ['-played_at'],
            },
        ),
    ]
