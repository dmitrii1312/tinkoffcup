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
def conv_whitelist_to_interval(date: datetime, whitelist: str):
    startdate= datetime(year=date.year, month=date.month, day=date.day, hour=0, minute=0)
    sParts = whitelist.partition("-")
    nIntStart = startdate + timedelta(hours=(int(sParts[0])-1))
    nIntEnd = startdate + timedelta(hours=int(sParts[2]))
    result=interval(start=nIntStart, end=nIntEnd)
    return result

def checkBlacklist(zonename, blackzonelist):
    for i in blackzonelist:
        if zonename==i:
            return True
    return False

def checkWhitelist(whitelist, start, duration):

    nHstart=int(start.strftime("%H"))
    dtHend=start+duration
    nHend=int(dtHend.strftime("%H"))+1
    for i in whitelist:
        sParts=i.partition("-")
        nIntStart=int(sParts[0])
        nIntEnd=int(sParts[2])
        if nHstart>nIntStart and nHend<nIntEnd:
            return True
    return False

def countWorksInInterval(calendar, start, duration):
    end=start+duration
    return calendar.get_task(start, end)

def countAvailableZonesInInterval(calendars, start, duration):
    return 0
# @params:
# interval, data = json_full_config
def checkInterval(calendar_zones_objs, ievent: interval, data:list):

    zones = list(data['calForZones'].keys())
    blackList = data['black']

    im = []
    for zone in zones:
        im.append(get_event(calendar_zones_objs[zone], ievent.start, ievent.end))

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

    if isFreeInZone and countFreeZone > int(data['zoneAvailable']):
        return True
    else:
        return False

def get_event(calendar, startdate, enddate):
    tasks = calendar.get_task(startdate, enddate)
    itasks=[]
    for task in tasks:
        start = task.icalendar_component.get("DTSTART").dt
        end = task.icalendar_component.get("DTEND").dt
        itasks.append(interval(start,end,calendar))
    return  itasks
