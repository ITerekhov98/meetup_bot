# Generated by Django 4.0.6 on 2022-07-28 18:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('meetup_bot', '0006_remove_lecture_speaker_lecture_speaker'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lecture',
            name='speaker',
            field=models.ManyToManyField(blank=True, related_name='lectures', to='meetup_bot.client', verbose_name='Спикеры'),
        ),
    ]
