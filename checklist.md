## Перед запуском

- прописать путь до файлов с графом и вики:
	- settings.WIKI\_ZIMFILE\_PATH
	- settings.GRAPH\_OFFSET\_PATH
	- settings.GRAPH\_EDGES\_PATH
- сделать миграции: `python manage.py makemigrations`
- мигрировать: `python manage.py migrate`

## Запуск

- `python manage.py runserver` (для теста)
