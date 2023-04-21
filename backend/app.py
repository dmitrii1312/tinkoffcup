from flask import Flask, render_template, request, jsonify, Response
from datetime import datetime, timedelta
import os.path as path
import json
import time

import requests

# Our api
from calendar_zone import CalendarZone
# Our utils
from utils import load_config, parse_timedelta

# Check interval imports only
from check import checkInterval
from interval import interval

from autoWork import autoWork
from manualWork import manualWork 
from typeOfWork import typeOfWork

# Start Flask application
app = Flask(__name__,
            template_folder='../templates',
            static_folder='../static')


# Ищем и проверяем существование конфига в корне проекта
config_path = path.abspath(path.join(__file__, "../../config.json"))
if not path.exists(config_path):
    Exception(f"Config {config_path} doesn't exists")
# Load configuration file for application
json_config_data = load_config(config_path)


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
max_deadline = json_config_data['max_deadline']
# Кратность dict
multiplicity = json_config_data['multiplicity']

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
@app.route('/planner', methods=['GET', 'POST'])
@app.route('/', methods=['GET', 'POST'])
def index():

    # Для обработки ошибок на фронте при рендеринге
    error_message = None

    if request.method == 'POST':

        # Дата и время начала работ
        start_dateTime = datetime.strptime(str(request.form['startTime']),
                                           "%Y-%m-%dT%H:%M")

        # Для проверки начала работ на кратность
        start_time_only = start_dateTime.hour * 60 + start_dateTime.minute

        # Длительность работ
        end_time = datetime.strptime(str(request.form['durationTime']),
                                     "%Y-%m-%dT%H:%M")

        # Дедлайн
        deadline = datetime.strptime(str(request.form['deadline']),
                                     "%Y-%m-%dT%H:%M")

        deadline_duration = deadline - start_dateTime
        print(deadline_duration)

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
                error_message = (f"Ошибка, автоматические работы не могут "
                                 f"быть меньше {min_time[worktype]}")
        elif worktype == 'manual':
            if minMax_duration < parse_timedelta(min_time[worktype]):
                error_message = (f"Ошибка, ручные работы не могут быть "
                                 f"меньше {min_time[worktype]}")
            # Проверка на кратность
            multiplicity_minutes = int(parse_timedelta(
                multiplicity[worktype]).total_seconds()/60)
            print("AAA", multiplicity_minutes)
            print("BBB: ", start_time_only)
            if start_time_only % multiplicity_minutes > 0:
                error_message = (f"Ошибка, ручные работы должны быть "
                                 f"кратны {multiplicity[worktype]}")

        # Провека для ОБЫЧНЫХ максимальных работ
        if workPriority == 'normal':
            if (minMax_duration >
               parse_timedelta(max_time[worktype][workPriority])):
                error_message = (f"Ошибка, максимальное время не может быть "
                                 f"больше {max_time[worktype][workPriority]}")

        if deadline_duration > parse_timedelta(max_deadline):
            error_message = (f"Ошибка, дедлайн не может превышать "
                             f"{max_deadline}")
            
        

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
        # current_task = typeOfWork(worktype)
        # res, text = current_task.set_start_time(start_dateTime)
        # if not res:
        #     return text
        # res, text = current_task.set_duration(duration, min_time[worktype], max_time[worktype][priority])
        # if not res:
        #     return text
        # res, text = current_task.set_end_time(current_task.calculate_end_time())
        # if not res:
        #     return text
        # res, text = current_task.set_deadline(deadline)
        # if not res:
        #     return text
        # res, text = current_task.set_priority(priority)
        # if not res:
        #     return text
        # res, text = current_task.set_zone_name(entered_zone)
        # if not res:
        #     return text
        # # triing to save task object
        # res, listOftasks = calendar_zones_objs[entered_zone].add_task_ex(current_task)
        # if res:
        #     return render_template('data_added.html',
        #                            data=data,
        #                            error_message=error_message)
        # else:
        #     error_message = "task conflict"

    return render_template('index.html',
                           data=data,
                           error_message=error_message)


@app.route('/agentdav/',
           methods=['GET', 'POST', 'PUT', 'DELETE', 'PROPFIND', 'MKCALENDAR'])
def agentdav_proxy():
    url = remote_server + request.full_path.replace('/agentdav', '')
    print(url)
    headers = {key: value for (key, value) in request.headers if key != 'Host'}
    headers['Content-Type'] = request.content_type or 'text/plain'

    response = requests.request(
        method=request.method,
        url=url,
        headers=headers,
        data=request.get_data(),
        auth=('admin', 'admin'),
        verify=False,
    )
    
    print(response.content, response.status_code, response.headers.items())
    return response.content, response.status_code, response.headers.items()


if __name__ == '__main__':
    app.run(debug=True)
