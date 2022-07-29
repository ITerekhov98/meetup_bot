# Generated by Django 4.0.6 on 2022-07-29 18:20

from django.db import migrations, models
import django.db.models.deletion
import meetup_bot.models


class Migration(migrations.Migration):

    dependencies = [
        ('meetup_bot', '0009_alter_block_options_alter_client_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='questionnaire',
            name='resume',
            field=models.FileField(blank=True, null=True, upload_to=meetup_bot.models.get_upload_resume_path, verbose_name='Резюме'),
        ),
        migrations.CreateModel(
            name='ProposedLecture',
            fields=[
                ('lecture_title', models.TextField(blank=True, verbose_name='Описание лекции')),
                ('questionnaire', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='meetup_bot.questionnaire', verbose_name='Анкета')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='proposed_lectures', to='meetup_bot.client', verbose_name='Пользователь')),
            ],
        ),
    ]
