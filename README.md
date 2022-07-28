# meetup_bot
Бот для конференций

## Установка 

Качаем репозиторий, в папке *meetup* создаём `.env` файл. Минимальный конфиг для запуска:
- DJANGO_SECRET_KEY
- TELEGRAM_ACCESS_TOKEN

Устанавливаем зависимости:
```
pip install -r requirements.txt
```

Формируем БД:
```
python manage.py migrate
```

Для запуска бота понадится хотя бы одно сохранённое в БД мероприятие. Для теста можно заполнить след образом:
```
python manage.py shell
```
Далее в консоли django:
```
from meetup_bot.models import Event
Event.objects.create(title='Мероприятие 1', start='2022-01-01', end='2023-01-01')
exit()
```



## Запуск
```
python manage.py start_bot
```

## Загрузка тестовых данных
После создания бд прописать в консоли команду:
```
python manage.py loaddata test_data.json
```
