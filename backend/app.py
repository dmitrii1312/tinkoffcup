from flask import Flask, render_template, request, jsonify, Response
from datetime import datetime, timedelta
import os.path as path
import json
import time
from typing import *

import requests

# Our api
from calendar_zone import CalendarZone
# Our utils
from utils import load_config, parse_timedelta

# Check interval imports only
from check import *
from interval import interval

from autoWork import autoWork
from manualWork import manualWork 
from typeOfWork import typeOfWork
import uuid

# Start Flask application
app = Flask(__name__,
            template_folder='../templates',
            static_folder='../static')


# Ищем и проверяем существование конфига в корне проекта
config_path = path.abspath(path.join(__file__, "../../config.json"))
if not path.exists(config_path):
    Exception(f"Config {config_path} doesn't exists")
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
max_deadline = json_config_data['max_deadline']
# Кратность dict
multiplicity = json_config_data['multiplicity']

# Объекты типа календарь, сформированные на основе
# zone = spb -> zone[spb] = имя календаря
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
        res, error_message = add_work(request)


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


def add_work(request):
    current_tasks = []
    # Дата и время начала работ
    start_dateTime = datetime.strptime(str(request.form['startTime']),
                                       "%Y-%m-%dT%H:%M")

    print("START_DATETIME: ", start_dateTime)
    # Для проверки начала работ на кратность
    start_time_only = start_dateTime.hour * 60 + start_dateTime.minute

    # Длительность работ
    work_duration = datetime.strptime(str(request.form['durationTime']),
                                      "%H:%M")

    # Дедлайн
    deadline = datetime.strptime(str(request.form['deadline']),
                                 "%Y-%m-%dT%H:%M")

    # Длительность дедлайна
    deadline_duration = deadline - start_dateTime  # datetime
    duration = timedelta(hours=work_duration.hour,
                         minutes=work_duration.minute)
    new_dateTime = start_dateTime + duration  # datetime

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
        if duration < parse_timedelta(min_time[worktype]):
            error_message = (f"Ошибка, автоматические работы не могут "
                             f"быть меньше {min_time[worktype]}")
    elif worktype == 'manual':
        if duration < parse_timedelta(min_time[worktype]):
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
        if (duration >
           parse_timedelta(max_time[worktype][workPriority])):
            error_message = (f"Ошибка, максимальное время не может быть "
                             f"больше {max_time[worktype][workPriority]}")

    if deadline_duration > parse_timedelta(max_deadline):
        error_message = (f"Ошибка, дедлайн не может превышать "
                         f"{max_deadline}")
        
    

    # Если со временем всё ок, создаем объект интервала
    entered_zone = request.form.getlist('zones')
    print("VVEDENIY ZONE: ", entered_zone)
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
    work_id = uuid.uuid4()
    for i in entered_zone:
        res, text, current_task = request_to_task(request, str(work_id), i)
        if res:
            current_tasks.append(current_task)
        else:
            return res, text

    # triing to save task object
    task_to_reschedule = []
    task_with_ok = []

    for i in current_tasks:
        if calendar_zones_objs[i.zone_name].get_task_ex(i.get_start_time(),i.get_end_time()) != None:
            print("I_ZONE: ", i.zone_name)
            res, new_task = find_time_for_task(calendar_zones_objs[i.zone_name],
                                               whitelist[i.zone_name], i)
            if res:
                task_to_reschedule.append(new_task)
            else:
                return res, "can't schedule task, no free windows till deadline"
        else:
            task_with_ok.append(i)

    if len(task_to_reschedule) == 0:
        for i in task_with_ok:
            calendar_zones_objs[i.zone_name].add_task_ex(i)

    return True, "OK"

def cancel_task(request):
    work_id = request.form['work_id']
    for calendar in calendar_zones_objs:
        res, event = calendar.find_by_workid(work_id)
        if res:
            calendar.delete_task(event)


def reschedule_work(request):
    work_id = request.form['work_id']
    if validate_request(request):

        for i in request.form['zones']:
            res, task = calendar_zones_objs[i].get_task_by_work_id(work_id)
            if res:
                task = request_to_task(request, work_id, i)
                calendar_zones_objs[i].modify_task(task)


def find_time_for_task(calendar: CalendarZone, whitelist, task: typeOfWork):
    newtask = task
    tasks = calendar.get_task_ex(task.get_start_time(),task.get_deadline_time())
    freeintervals = find_intervals_by_duration (calendar, whitelist, newtask)
    if len(freeintervals) == 0:
        return None
    else:
        newtask.set_start_time(freeintervals[0].start)
        newtask.set_end_time(newtask.calculate_end_time())
        return newtask

def find_intervals_by_duration(calendar: CalendarZone, whitelist, task: typeOfWork ):
    planned_tasks=calendar.get_task_ex(task.get_start_time(),task.get_deadline_time())
    duration= task.get_deadline_time()-task.get_start_time()
    duration_minutes = duration.seconds//60
    freebusy = []
    whitelist_dt=[]
    retval=[]
    oneday=timedelta(days=1)
    k=0
    for i in range(0,duration_minutes):
        freebusy[i]=1

    for i in whitelist:
        while k*oneday<(duration+oneday) :
            whitelist_dt.append(conv_whitelist_to_interval(task.get_start_time()+k*oneday,i))
            k=k+1

    for i in whitelist_dt:
        if i.start > task.get_deadline_time():
            continue
        if i.start < task.get_start_time():
            free_start=0
        else:
            free_start = int((i.start-task.get_start_time())//60)
        if i.end < task.get_start_time():
            continue
        if i.end > task.get_deadline_time():
            free_end = duration_minutes
        else:
            free_end = i.end - task.get_start_time()
        freebusy= fillarray(freebusy, free_start, free_end, 0)

    for i in planned_tasks:
        if i.get_start_time()<task.get_start_time():
            busy_start=0
        else:
            if i.get_start_time() > task.get_start_time():
                continue
            else:
                busy_start = int((i.get_start_time()-task.get_start_time())//60)
        if i.get_end_time()>task.get_deadline_time():
            busy_end = duration_minutes
        else:
            if i.get_end_time()< task.get_start_time():
                continue
            busy_end = (i.get_end_time()-task.get_start_time())//60
        freebusy= fillarray(freebusy,busy_start, busy_end, 1)
    start_index=find_free_space_index(freebusy,int(task.get_duration_time()//60))
    if start_index != -1:
        starttime_delta=timedelta(minutes=start_index)
        retval.append(interval(start=task.get_start_time()+starttime_delta,end=task.get_start_time()+starttime_delta+task.duration))
        return retval
    return None


def fillarray(arr: List[int], start, end, num):
    for i in range(start,end):
        arr[i]=num
    return arr

def validate_request(request):
    return True

def find_free_space_index(arr: List[int], duration: int, good_value: int):
    k=0
    start=0
    for i in range(0,len(arr)):
        if arr[i] == good_value:
            k=k+1
            if k== duration:
                return i
        else:
            k=0
    return -1

def request_to_task(request, work_id: str, zone):
    start_dateTime = datetime.strptime(str(request.form['startTime']),
                                       "%Y-%m-%dT%H:%M")

    # Для проверки начала работ на кратность
    start_time_only = start_dateTime.hour * 60 + start_dateTime.minute

    # Длительность работ
    work_duration = datetime.strptime(str(request.form['durationTime']),
                                      "%H:%M")

    # Дедлайн
    deadline = datetime.strptime(str(request.form['deadline']),
                                 "%Y-%m-%dT%H:%M")

    deadline_duration = deadline - start_dateTime
    duration = timedelta(hours=work_duration.hour,
                         minutes=work_duration.minute)
    print("DURATION: ", duration)
    new_dateTime = start_dateTime + duration

    # Минимальная длительность работ
    # 10:00 - 09:00 = 1ч
    # Максимальная длительность работ
    #
    # Получаем тип работ (ручные, автоматические)
    worktype = str(request.form['typeofWork'])
    workPriority = str(request.form['workPriority'])
    summary = str(request.form['summary'])
    entered_zone = zone
    current_task = typeOfWork(worktype, work_id)
    res, text = current_task.set_start_time(start_dateTime)
    if not res:
        return res, text, None
    res, text = current_task.set_duration(duration, parse_timedelta(min_time[worktype]), parse_timedelta(max_time[worktype][workPriority]))
    if not res:
        return res, text, None
    res, text = current_task.set_end_time(current_task.calculate_end_time())
    if not res:
        return res, text, None
    res, text = current_task.set_deadline(deadline)
    if not res:
        return res, text, None
    res, text = current_task.set_priority(workPriority)
    if not res:
        return res, text, None
    res, text = current_task.set_zone_name(entered_zone)
    if not res:
        return res, text, None
    res, text = current_task.set_summary(summary)
    if not res:
        return res, text, None

    return True, "OK", current_task

if __name__ == '__main__':
    app.run(debug=True)
