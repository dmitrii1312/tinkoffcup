from datetime import datetime
from interval import interval

import json
import os.path as path

# Ищем и проверяем существование конфига в корне проекта
config_path = path.abspath(path.join(__file__ ,"../../config.json"))
if not path.exists(config_path):
    print("Config file doesn't exists")

# Метод валидации статического конфиг-файла на наличие календарей и зон
def checkCalendarsForZones() -> dict:
    with open(config_path) as json_file:
        data=json.load(json_file)    
    return data['black']

def checkInterval(ievent):    
    im = [  [interval(datetime(2023,4,15,15,00,00),datetime(2023,4,15,15,30,00),"zone1"),interval(datetime(2023,4,15,17,00,00),datetime(2023,4,15,17,30,00),"zone1")],
            [interval(datetime(2023,4,15,10,00,00),datetime(2023,4,15,10,30,00),"zone2"),interval(datetime(2023,4,15,16,00,00),datetime(2023,4,15,17,30,00),"zone2")]]
    blackList = getBlackZone()
    isFreeInZone = True        
    countFreeZone = 0 

    for izone in im:
        iFreeInZone = True
        for i in izone:
            if (ievent.start>=i.start and ievent.start<i.end) or (ievent.end>i.start and ievent.end<=i.end) or blackList.count(i.zone)>0:
                iFreeInZone = False
                if i.zone == ievent.zone:
                    isFreeInZone = iFreeInZone
                break
        if iFreeInZone:
            countFreeZone +=1

    return (isFreeInZone,countFreeZone)

def getBlackZone() -> list:
    with open(config_path, 'r') as json_file:
        data=json.load(json_file)    
    return data['black']

if __name__ == '__main__':
    print(checkInterval(interval(datetime(2023,4,15,14,00,00),datetime(2023,4,15,14,30,00),"zone1")))
