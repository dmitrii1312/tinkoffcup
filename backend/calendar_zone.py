import caldav
import datetime

class CalendarZone:

    def __init__(self, sUrl, sUsername, sPassword, calendarName=None ):

        self.sUrl, self.sUsername, self.sPassword = sUrl, sUsername, sPassword
        client = caldav.DAVClient(sUrl, username=sUsername, password=sPassword)
        self.principal = client.principal()

        if calendarName is not None:
            # Check that calendar already exists
            calendars = self.principal.calendars()
            calendarName = next((calendar for calendar in calendars if calendar.name == calendarName), None)
            if calendarName is None:
                raise Exception("Calendar doesn't exists")
            # no need replaced by add_calendar() self.calendar = self.principal.calendar(name=calendarName)


    def get_existing_cals(self):
        return self.principal.calendars()

    def add_calendar(self, name):
        calendars = self.get_existing_cals()
        if name not in calendars:
            caldav.CalendarSet.make_calendar(
                name=name
            )

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

    def modify_task(self, event, summary, start, end):
        if summary:
            event.icalendar_component["summary"] = summary

        if start:
            event.icalendar_component["dtstart"].dt = start
        
        if end:
            event.icalendar_component["dtend"].dt = end

        event.save()

obj = CalendarZone("http://tsquared.keenetic.pro:5232/", 'admin', 'admin')
print(obj.get_existing_cals())
