from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('twobeats_account', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='playlist',
            name='category',
            field=models.CharField(choices=[('music', '음악'), ('video', '영상')], db_column='playlist_category', default='music', max_length=10, verbose_name='분류'),
        ),
    ]
