import caldav
from datetime import datetime


class CalendarZone:

    def __init__(self, sUrl, sUsername, sPassword, calendarName=None):

        self.sUrl, self.sUsername, self.sPassword = sUrl, sUsername, sPassword
        client = caldav.DAVClient(sUrl, username=sUsername, password=sPassword)
        self.principal = client.principal()
        self.calendar = self.principal.calendar(name=calendarName)    

        if calendarName is not None:
            # Check that calendar already exists
            calendars = self.principal.calendars()
            calendarName = next((calendar for calendar in calendars if calendar.name == calendarName), None)
            if calendarName is None:
                raise Exception("Calendar doesn't exists")

    def get_existing_cals(self):
        return self.principal.calendars()

    def add_calendar(self, name):
        calendars = self.get_existing_cals()
        if name not in calendars:
            caldav.CalendarSet.make_calendar(
                name=name
            )

    def add_task(self, start=datetime, end=datetime,
                 summary="", repeat="once", priority="2",
                 tasttype="auto"):

        event = {}

        if repeat != "once":
            event = self.calendar.save_event(
                dtstart=start,
                dtend=end,
                summary=summary,
                rrule={'FREQ': repeat})
        else:
            event = self.calendar.save_event(
                    dtstart=start,
                    dtend=end,
                    summary=summary)

    def get_task(self, start, end):
        tasks = self.calendar.search(
            start=start,
            end=end,
            event=True,
        )
        return tasks

    def del_task(self, events: caldav.Event):
        for event in events:
            event.delete()

    def modify_task(self, event, summary, start, end):
        if summary:
            event.icalendar_component["summary"] = summary
        if start:
            event.icalendar_component["dtstart"].dt = start
        if end:
            event.icalendar_component["dtend"].dt = end
        event.save()
