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

## Запуск
```
python manage.py start_bot
```
