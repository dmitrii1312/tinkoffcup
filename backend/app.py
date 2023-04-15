from flask import Flask, render_template, request
from datetime import datetime
import os.path as path
import time

# Our api
from calendar_zone import CalendarZone
from parse_config import *

# Check interval imports only
from check import checkInterval
from interval import interval


# Start app
app = Flask(__name__, template_folder='../templates')

### READ CONFIG JSON ###
# Ищем и проверяем существование конфига в корне проекта
config_path = path.abspath(path.join(__file__ ,"../../config.json"))
if not path.exists(config_path):
    print("Config file doesn't exists")

# Получаем весь конфиг
json_config_data = get_all_config(config_path)

remote_server = json_config_data['caldav_server']
username = json_config_data['username']
password = json_config_data['password']
zones = json_config_data['calForZones']

calendar_zones_objs = {}
for i in zones:
    calendar_zones_objs[i] = \
        CalendarZone(remote_server, username, password, zones[i])

### READ CONFIG JSON ###

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Получаем дату старта и время
        start_dateTime = datetime.strptime(
            str(request.form['startTime']),
            "%Y-%m-%dT%H:%M"
        )

        # Получаем длительность работ
        end_time = datetime.strptime(
            str(request.form['durationTime']),
            "%H:%M"
        )

        # Если со временем всё ок, создаем объект интервала
        interval_obj = interval(
            start_dateTime,
            end_time,
            str(request.form['zones']),)

        # И делаем чек для этого интервала
        checkInterval(interval_obj, json_config_data)

        print(start_dateTime, end_time, str(request.form['zones']))
        return "OK"

    else:
        data = {
            'zones': list(calendar_zones_objs.keys())
        }
        return render_template('index.html', data=data)

if __name__ == '__main__':
    app.run(debug=True)