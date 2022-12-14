# Generated by Django 4.0.6 on 2022-07-27 17:29

from django.db import migrations, models
import django.db.models.deletion
import meetup_bot.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Block',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=300, unique=True, verbose_name='Заголовок')),
                ('start', models.DateTimeField(verbose_name='Начало мероприятия')),
                ('end', models.DateTimeField(verbose_name='Конец мероприятия')),
            ],
            options={
                'ordering': ['-end'],
            },
        ),
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tg_id', models.PositiveIntegerField(unique=True, verbose_name='Telegram id')),
                ('is_speaker', models.BooleanField(blank=True, default=False, verbose_name='Является спикером?')),
                ('current_state', models.CharField(max_length=20, verbose_name='Состояние диалога')),
            ],
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=300, unique=True, verbose_name='Заголовок')),
                ('image', models.ImageField(blank=True, null=True, upload_to=meetup_bot.models.get_upload_event_path, verbose_name='Фотография')),
                ('description', models.TextField(blank=True, verbose_name='Описание')),
                ('start', models.DateField(verbose_name='Начало мероприятия')),
                ('end', models.DateField(verbose_name='Конец мероприятия')),
            ],
            options={
                'ordering': ['-end'],
            },
        ),
        migrations.CreateModel(
            name='Questionnaire',
            fields=[
                ('client', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='meetup_bot.client', verbose_name='Пользователь')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='Имя')),
                ('email', models.EmailField(blank=True, max_length=70, unique=True, verbose_name='Почта')),
                ('job_title', models.CharField(blank=True, max_length=50, verbose_name='Должность')),
                ('company', models.CharField(blank=True, max_length=50, verbose_name='Компания')),
            ],
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.TextField(verbose_name='Вопрос')),
                ('from_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='outcoming_questions', to='meetup_bot.client', verbose_name='От кого вопрос')),
                ('to_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='incoming_questions', to='meetup_bot.client', verbose_name='Кому вопрос')),
            ],
        ),
        migrations.CreateModel(
            name='Lecture',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=300, unique=True, verbose_name='Заголовок')),
                ('description', models.TextField(blank=True, verbose_name='Описание')),
                ('image', models.ImageField(blank=True, null=True, upload_to=meetup_bot.models.get_upload_lecture_path, verbose_name='Фотография')),
                ('is_timeout', models.BooleanField(blank=True, default=False, verbose_name='Перерыв?')),
                ('start', models.DateTimeField(verbose_name='Начало доклада')),
                ('end', models.DateTimeField(verbose_name='Конец доклада')),
                ('block', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lectures', to='meetup_bot.block', verbose_name='Блок')),
                ('speaker', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='lectures', to='meetup_bot.client', verbose_name='Спикер')),
            ],
            options={
                'ordering': ['end'],
            },
        ),
        migrations.CreateModel(
            name='Donate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.PositiveIntegerField(verbose_name='Количество денег')),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='donates', to='meetup_bot.client', verbose_name='Пользователь')),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='donates', to='meetup_bot.event', verbose_name='Мероприятие')),
            ],
        ),
        migrations.AddField(
            model_name='client',
            name='event',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='clients', to='meetup_bot.event', verbose_name='Мероприятие'),
        ),
        migrations.AddField(
            model_name='block',
            name='event',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='blocks', to='meetup_bot.event', verbose_name='Мероприятие'),
        ),
    ]
