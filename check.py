from datetime import datetime
import json
from interval import interval



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

def getBlackZone():
    with open("config.json") as json_file:
        data=json.load(json_file)    
    return data['black']

if __name__ == '__main__':
    print(checkInterval(interval(datetime(2023,4,15,14,00,00),datetime(2023,4,15,14,30,00),"zone1")))
