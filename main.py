import caldav
from datetime import datetime, timedelta
from icalendar import Event

# summary описание
def add_event(calendar, start=datetime, end=datetime, summary=""):
    event = calendar.save_event(
        dtstart=start,
        dtend=end,
        summary=summary,
    )

def get_event(calendar):
    return

def del_event(calendar):
    return



url = "http://tsquared.keenetic.pro:5232/"
username = "admin"
password = "admin"
client = caldav.DAVClient(url, username=username, password=password)
principal = client.principal()

# Получение списка календарей
# calendar = principal.calendar(name="tinkoffcup")
# add_event(calendar, start=datetime(2023, 5, 13, 5), end=datetime(2023, 5, 13, 9), summary="Test event")

