from pathlib import Path

from django.db import models


def get_upload_lecture_path(instance, filename):
    return Path(instance.event.title) / instance.title / filename


def get_upload_event_path(instance, filename):
    return Path(instance.title) / filename


def get_upload_resume_path(instance, filename):
    return Path(instance.first_name) / filename


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
        verbose_name = "Мероприятие"
        verbose_name_plural = "Мероприятия"

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
        ordering = ["end"]
        verbose_name = "Блок"
        verbose_name_plural = "Блоки"

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
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=30,
        blank=True
    )
    job_title = models.CharField(
        verbose_name='Должность',
        max_length=50,
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

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return f'Пользователь {self.id} - {self.first_name if self.first_name else self.tg_id}'


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
        blank=True
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
    resume = models.FileField(
        verbose_name='Резюме',
        blank=True,
        null=True,
        upload_to=get_upload_resume_path
    )

    class Meta:
        verbose_name = "Анкета"
        verbose_name_plural = "Анкеты"

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

    class Meta:
        verbose_name = "Вопрос спикеру"
        verbose_name_plural = "Вопросы спикеру"

    def __str__(self):
        return f'Вопрос для tg_id={self.question_to.tg_id} от tg_id={self.question_from.tg_id}'


class Lecture(models.Model):
    """Лекция"""
    title = models.CharField(
        verbose_name='Заголовок',
        max_length=300,
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
    speakers = models.ManyToManyField(
        Client,
        verbose_name='Спикеры',
        related_name='lectures',
        blank=True,
    )
    start = models.DateTimeField(verbose_name='Начало доклада')
    end = models.DateTimeField(verbose_name='Конец доклада')

    class Meta:
        ordering = ["end"]
        verbose_name = "Лекция"
        verbose_name_plural = "Лекции"

    def __str__(self):
        return f'{"Лекция" if not self.is_timeout else ""} {self.title}'

    def get_speakers(self):
        return ", ".join(
            [speaker.first_name for speaker in self.speakers.all()])


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

    class Meta:
        verbose_name = "Донат"
        verbose_name_plural = "Донаты"

    def __str__(self):
        return f'Донат от tg_id={self.client.tg_id}'


class Notification(models.Model):
    """Отправить уведомление"""
    title = models.CharField(
        verbose_name='Заголовок',
        max_length=300,
        blank=True,
    )
    message = models.TextField(verbose_name='Описание')

    class Meta:
        verbose_name = "Уведомление"
        verbose_name_plural = "Уведомления"

    def __str__(self):
        return f'Уведомление {self.id} - {self.title if self.title else ""}'


class ProposedLecture(models.Model):
    user = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='proposed_lectures'
    )
    lecture_title = models.TextField(
        verbose_name='Описание лекции',
        blank=True)
    questionnaire = models.ForeignKey(
        Questionnaire,
        verbose_name='Анкета',
        on_delete=models.CASCADE,
        related_name='proposed_lectures',
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = "Предложенная лекция"
        verbose_name_plural = "Предложенные лекции"

    def __str__(self):
        return f'Предложенная лекция от {self.questionnaire.first_name}'

    def get_speaker_name(self):
        return self.user.first_name

    def get_speaker_title_job(self):
        return self.user.job_title
