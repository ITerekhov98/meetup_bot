from pathlib import Path

from django.db import models


def get_upload_lecture_path(instance, filename):
    return Path(instance.event.title) / instance.title / filename


def get_upload_event_path(instance, filename):
    return Path(instance.title) / filename


class Event(models.Model):
    """Мероприятие"""
    title = models.CharField(
        verbose_name='Заголовок',
        max_length=300,
        unique=True
    )
    image = models.ImageField(
        verbose_name='Фотография',
        upload_to=get_upload_event_path,
        blank=True,
        null=True
    )
    description = models.TextField(verbose_name='Описание', blank=True)
    start = models.DateField(verbose_name='Начало мероприятия')
    end = models.DateField(verbose_name='Конец мероприятия')

    class Meta:
        ordering = ["-end"]

    def __str__(self):
        return f'Мероприятие {self.title}'


class Block(models.Model):
    """Блок"""
    title = models.CharField(
        verbose_name='Заголовок',
        max_length=300,
        unique=True
    )
    start = models.DateTimeField(verbose_name='Начало мероприятия')
    end = models.DateTimeField(verbose_name='Конец мероприятия')
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        verbose_name='Мероприятие',
        related_name='blocks'
    )

    class Meta:
        ordering = ["-end"]

    def __str__(self):
        return f'Блок {self.title}'


class Client(models.Model):
    """Пользователь"""
    tg_id = models.PositiveIntegerField(
        verbose_name='Telegram id',
        unique=True
    )
    is_speaker = models.BooleanField(
        default=False,
        verbose_name='Является спикером?',
        blank=True
    )
    event = models.ForeignKey(
        Event,
        on_delete=models.SET_NULL,
        verbose_name='Мероприятие',
        related_name='clients',
        null=True
    )
    current_state = models.CharField(
        'Состояние диалога',
        max_length=20
    )

    def __str__(self):
        return f'Пользователь tg_id={self.tg_id}'


class Questionnaire(models.Model):
    """Анкета"""
    client = models.OneToOneField(
        Client,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        primary_key=True
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=30,
        blank=True
    )
    email = models.EmailField(
        verbose_name='Почта',
        max_length=70,
        blank=True,
        unique=True
    )
    job_title = models.CharField(
        verbose_name='Должность',
        max_length=50,
        blank=True
    )
    company = models.CharField(
        verbose_name='Компания',
        max_length=50,
        blank=True
    )

    def __str__(self):
        return f'Анкета клиента с tg_id={self.client.tg_id}'


class Question(models.Model):
    """Вопрос спикеру"""
    question = models.TextField(verbose_name='Вопрос')
    from_user = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        verbose_name='От кого вопрос',
        related_name='outcoming_questions',
    )
    to_user = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        verbose_name='Кому вопрос',
        related_name='incoming_questions',
    )

    def __str__(self):
        return f'Вопрос для tg_id={self.question_to.tg_id} от tg_id={self.question_from.tg_id}'


class Lecture(models.Model):
    """Доклад"""
    title = models.CharField(
        verbose_name='Заголовок',
        max_length=300,
        unique=True
    )
    description = models.TextField(verbose_name='Описание', blank=True)
    image = models.ImageField(
        verbose_name='Фотография',
        upload_to=get_upload_lecture_path,
        blank=True,
        null=True
    )
    is_timeout = models.BooleanField(
        verbose_name='Перерыв?',
        default=False,
        blank=True
    )
    block = models.ForeignKey(
        Block,
        on_delete=models.CASCADE,
        verbose_name='Блок',
        related_name='lectures'
    )
    speaker = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        verbose_name='Спикер',
        related_name='lectures',
        blank=True,
        null=True
    )
    start = models.DateTimeField(verbose_name='Начало доклада')
    end = models.DateTimeField(verbose_name='Конец доклада')

    def save(self, *args, **kwargs):
        if self.speaker:
            user = self.speaker
            user.is_speaker = True
            user.save()
        return super(Lecture, self).save(*args, **kwargs)

    class Meta:
        ordering = ["end"]

    def __str__(self):
        return f'{"Доклад" if not self.is_timeout else ""} {self.title}'


class Donate(models.Model):
    """Донаты"""
    amount = models.PositiveIntegerField(verbose_name='Количество денег')
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='donates'
    )
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        verbose_name='Мероприятие',
        related_name='donates'
    )

    def __str__(self):
        return f'Донат от tg_id={self.client.tg_id}'
