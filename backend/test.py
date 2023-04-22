import caldav
from datetime import datetime
from typeOfWork import typeOfWork
from icalendar import Calendar, vDatetime
from calendar_zone import CalendarZone

calendar_zones_objs = CalendarZone("http://localhost:5232", "admin", "admin")
print(calendar_zones_objs)