from flask import Flask, render_template, request, jsonify
from datetime import datetime, timedelta
import os.path as path
import json

# Our api
from calendar_zone import CalendarZone
from parse_config import *
from time_functions import parse_timedelta

# Check interval imports only
from check import checkInterval
from interval import interval

from autoWork import autoWork
from manualWork import manualWork 
from typeOfWork import typeOfWork

# Start app
app = Flask(__name__,
            template_folder='../templates',
            static_folder='../static')


# app.add_url_rule('/static/ajax.js',
#                  endpoint='static',
#                  view_func=app.send_static_file)

# READ CONFIG JSON
# Ищем и проверяем существование конфига в корне проекта
config_path = path.abspath(path.join(__file__, "../../config.json"))
if not path.exists(config_path):
    print("Config file doesn't exists")
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
min_time = json_config_data['min_long']
max_time = json_config_data['max_long']

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

data = {
    'zones': list(calendar_zones_objs.keys()),
    'calLink': json_config_data['webcal_server']
}


# READ CONFIG JSON
@app.route('/', methods=['GET', 'POST'])
def index():

    if request.method == 'POST':

        # Дата и время начала работ
        start_dateTime = datetime.strptime(str(request.form['startTime']),
                                           "%Y-%m-%dT%H:%M")

        # Длительность работ
        end_time = datetime.strptime(str(request.form['durationTime']),
                                     "%Y-%m-%dT%H:%M")

        # Дедлайн
        deadline = datetime.strptime(str(request.form['deadline']),
                                     "%Y-%m-%dT%H:%M")

        duration = timedelta(hours=end_time.hour, minutes=end_time.minute)
        new_dateTime = start_dateTime + duration

        # Минимальная длительность работ
        # 10:00 - 09:00 = 1ч
        minMax_duration = end_time - start_dateTime
        # Максимальная длительность работ
        # 
        # Получаем тип работ (ручные, автоматические)
        worktype = str(request.form['typeofWork'])
        workPriority = str(request.form['workPriority'])

        """
            Минимальная длительность работ: 5 минут для автоматических
            и 30 минут для ручных

            Максимальная длительность работ - 6 часов, для обычных работ
            любого типа и без ограничений для критических.
        """
        if worktype == 'auto':
            # Для минимальных работ
            if minMax_duration < parse_timedelta(min_time[worktype]):
                print(f"Error auto work can't be less"
                      f"than {min_time[worktype]}")
        elif worktype == 'manual':
            if minMax_duration < parse_timedelta(min_time[worktype]):
                print(f"Error handmade work can't be less"
                      f"than {min_time[worktype]}")

        # Провека для ОБЫЧНЫХ максимальных работ
        if workPriority == 'normal':
            if (minMax_duration >
               parse_timedelta(max_time[worktype][workPriority])):
                print(f"Error maximal duration can't be greather"
                      f"than {max_time[worktype][workPriority]}")

        # Если со временем всё ок, создаем объект интервала
        entered_zone = str(request.form['zones'])
        interval_obj = interval(
            start_dateTime,
            new_dateTime,
            entered_zone)

        # И делаем чек для этого интервала
        # if checkBlacklist(entered_zone, blacklist):
        #     return "Zone in blacklist"
        # if deadline<new_dateTime:
        #     return "Deadline too early"

        # Creating Object
        current_task = typeOfWork(worktype)
        res, text = current_task.set_start_time(start_dateTime)
        if not res:
            return text
        res, text = current_task.set_duration(duration, min_time[worktype], max_time[worktype][priority])
        if not res:
            return text
        res, text = current_task.set_end_time(current_task.calculate_end_time())
        if not res:
            return text
        res, text = current_task.set_deadline(deadline)
        if not res:
            return text
        res, text = current_task.set_priority(priority)
        if not res:
            return text
        res, text = current_task.set_zone_name(entered_zone)
        if not res:
            return text
        # triing to save task object
        res, listOftasks = calendar_zones_objs[entered_zone].add_task_ex(current_task)
        if res:
            return render_template('data_added.html', data=data)
        else:
            res2, new_task = find_time_for_task(calendar_zones_objs[entered_zone],current_task)
            return "task conflict"
    else:
        # config_app = jsonify(json_config_data).data.decode('utf-8')
        return render_template('index.html', data=data)
    # return render_template('index.html', data=data)


def find_time_for_task(calendar: CalendarZone, whitelist, task: typeOfWork):
    newtask = task
    tasks = calendar.get_tasks(task)
    for itask in tasks:
        newtask.set_start_time(itask.get_end_time())
        newtask.set_end_time(newtask.calculate_end_time())
        n = calendar.get_tasks(newtask)
        if len(n) == 0:
            if checkWhitelist(whitelist, newtask.get_start_time(), newtask.get_duration_time()):
                return newtask





if __name__ == '__main__':
    app.run(debug=True)
