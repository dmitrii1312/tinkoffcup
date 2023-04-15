import caldav
import datetime

class CalendarZone:

    def __init__(self, sUrl, sUsername, sPassword, calendarName ):
        self.sUrl = sUrl
        self.sUsername = sUsername
        self.sPassword = sPassword
        client = caldav.DAVClient(sUrl, username=sUsername, password=sPassword)
        self.calendar = client.principal().calendar(name=calendarName)



    def add_task(self, start=datetime, end=datetime, summary=""):
        event = self.calendar.save_event(
            dtstart=start,
            dtend=end,
            summary=summary,
        )

    def get_task(self, start=datetime, end=datetime):
        tasks = self.calendar.search(
            start=start,
            end=end,
            event=True,
        )
        return tasks


    def del_task(self, event:caldav.Event):
        event.delete
        return








