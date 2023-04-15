from datetime import datetime
from interval import interval
from calendar_zone import CalendarZone
from icalendar import Event

import json
import os.path as path

## Ищем и проверяем существование конфига в корне проекта
#config_path = path.abspath(path.join(__file__ ,"../../config.json"))
#if not path.exists(config_path):
#    print("Config file doesn't exists")

# Метод валидации статического конфиг-файла на наличие календарей и зон
#def checkCalendarsForZones() -> dict:
#    with open(config_path) as json_file:
#        data=json.load(json_file)    
#    return data['black']

# возвращаем свободно ли в требуемой зоне и в скольки зонах есть места
def checkBlacklistzone(calendar,zonelist):
    for i in zonelist:
        if calendar.name==i:
            return True
    return False

# @params:
# interval, data = json_full_config
def checkInterval(ievent: interval, data:list) -> tuple:    

    zones = list(data['calForZones'].keys())
    blackList = data['black']

    im = []
    for zone in zones:
        im.append(get_event(zone, ievent.start, ievent.end))

    isFreeInZone = True        
    countFreeZone = 0 

    for izone in im:
        iFreeInZone = True
        for i in izone:
            if (ievent.start.timestamp()>=i.start.timestamp() and
                ievent.start.timestamp()<i.end.timestamp()) or (ievent.end.timestamp()>i.start.timestamp() and
                ievent.end.timestamp()<=i.end.timestamp()) or blackList.count(i.zone) > 0:
                iFreeInZone = False
                if i.zone == ievent.zone:
                    isFreeInZone = iFreeInZone
                break
        if iFreeInZone:
            countFreeZone +=1
    return (isFreeInZone, countFreeZone)

def get_event(calendar, startdate, enddate):
    tasks = calendar.get_task(startdate, enddate)
    itasks=[]
    for task in tasks:
        start = task.icalendar_component.get("DTSTART").dt
        end = task.icalendar_component.get("DTEND").dt
        itasks.append(interval(start,end,calendar))
    return  itasks

if __name__ == '__main__':
    testevent = interval(datetime(2023,4,15,14,00,00),datetime(2023,4,15,14,30,00),"zone1")
    print(checkInterval(testevent))
