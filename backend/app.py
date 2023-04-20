from flask import Flask, render_template, request, jsonify
from datetime import datetime, timedelta
import os.path as path
import json

# Our api
from calendar_zone import CalendarZone
from parse_config import *

# Check interval imports only
from check import checkInterval
from interval import interval


# Start app
app = Flask(__name__,
            template_folder='../templates',
            static_folder='../static')


# app.add_url_rule('/static/ajax.js',
#                  endpoint='static',
#                  view_func=app.send_static_file)

# READ CONFIG JSON
# Ищем и проверяем существование конфига в корне проекта
print("Opening config file")
config_path = path.abspath(path.join(__file__, "../../config.json"))
if not path.exists(config_path):
    print("Config file doesn't exists")
print("Reading config")
# Получаем весь конфиг
try:
    with open(config_path, 'r') as json_config:
        json_config_data = json.load(json_config)
except ValueError:
    raise Exception("Errors in config file") from None

remote_server = json_config_data['caldav_server']
username = json_config_data['username']
password = json_config_data['password']
zones = json_config_data['calForZones']
nFreeZones = int(json_config_data['zoneAvailable'])
whitelist = json_config_data['white']
blacklist = json_config_data['black']
pause = json_config_data['pause']

calendar_zones_objs = {}
for i in zones:
    calendar_zones_objs[i] = \
        CalendarZone(remote_server, username, password, zones[i])


for i in zones.keys():
    try:
        whitelist[i]
    except KeyError:
        raise Exception("White list not for all zones")


i = len(zones)-len(blacklist)
if i < nFreeZones:
    raise Exception("Incorrect number of available zones: no zones to schedule works")

# for i in zones.keys():
#     try:
#         pause[i]
#     except KeyError:
#         raise Exception("Pause time set not for all zones")


# READ CONFIG JSON
@app.route('/', methods=['GET', 'POST'])
def index():

    data = {
        'zones': list(calendar_zones_objs.keys()),
        'calLink': json_config_data['webcal_server']
    }

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

        duration = timedelta(hours=end_time.hour, minutes=end_time.minute)
        new_dateTime = start_dateTime + duration
        worktype = str(request.form['worktype'])
        deadline = datetime.strptime(str(request.form['deadline']), "%Y-%m-%dT")      
        # Если со временем всё ок, создаем объект интервала
        entered_zone = str(request.form['zones'])
        interval_obj = interval(
            start_dateTime,
            new_dateTime,
            entered_zone)

        # И делаем чек для этого интервала
        if checkBlacklist(entered_zone, blacklist):
            return "Zone in blacklist"
        if deadline<new_dateTime:
            return "Deadline too early"

        check_data = checkInterval(calendar_zones_objs,
                                   interval_obj,
                                   json_config_data)

        if check_data:
            calendar_zones_objs[entered_zone].add_task(
                interval_obj.start,
                interval_obj.end)
            return render_template('data_added.html', data=data)
        else:
            return "Add data failed"
    else:
        config_app = jsonify(json_config_data).data.decode('utf-8')
        return render_template('index.html',
                               data=data,
                               config_app=config_app)


if __name__ == '__main__':
    app.run(debug=True)
