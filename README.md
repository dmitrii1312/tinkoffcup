# О проекте
Данный проект - это планировщик работ в датацентрах. Позволяет планировать различные работы в нескольких зонах доступности
# Требования
Для работы приложения требуется наличие CalDAV сервера. Можно использовать Radical (https://github.com/tomsquest/docker-radicale). 
# Установка
Установка состоит из следующих этапов:
- склонировать репозиторий в отдельную папку
```
# git clone https://github.com/dmitrii1312/tinkoffcup.git
```
- собрать контейнер
```
# docker build . -t tinkoffcup:1.0
```
- подготовить конфигурационный файл (config.json) - описание ниже
- запустить контейнер
```
# docker run -d -v ./config.json:/app/config.json -p 8080:8080 tinkoffcup:1.0
```
- зайти в web-интерфейс, опубликованный на порту 8080
# Настройка
Конфигурационный файл config.json поддерживает следующие параметры:
- параметры доступа к CalDAV серверу: Url, логин, пароль
```
    "caldav_server": "http://tsquared.keenetic.pro:5232",
    "username": "admin",
    "password": "admin",
```
- Url web-клиента CalDAV (agenDAV)
- параметры доступа к календарям, для каждой зоны указывается название самой зоны и название календаря:
```
    "calForZones": {
        "zone1_name": "calendar1_name",
	"zone2_name": "calendar2_name",
	"zone3_name": "calendar3_name",
	"zone4_name": "calendar4_name"
    },
```
- Белый список - указываются интервалы в виде (час начала)-(час окончания), в которые можно планировать работы. Для каждой зоны указывается свой список интервалов:
```
    "white": {
        "zone1_name": ["1-4", "5-8"],
        "zone2_name": ["2-5", "6-9"],
        "zone3_name": ["2-5"],
        "zone4_name": ["2-7", "8-9"]
    },
```
- Чёрный список - список зон, в которых запрещено проводить работы:
```
    "black": ["zone3_name", "zone4_name"],
```
- Минимальное количество зон, на который не запланированы работы:
```
    "zoneAvailable": "2",
```

# Запуск
- запустить контейнер
```
# docker run -d -v ./config.json:/app/config.json -p 8080:8080 tinkoffcup:1.0
```
- зайти в web-интерфейс, опубликованный на порту 8080

# Install

````
python -m venv venv
source venv/bin/activate
pip -r requirements.txt
````
