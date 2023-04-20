import caldav
from datetime import datetime


class CalendarZone:

    def __init__(self, url, username, password, calendar_name=None):
        self.url, self.username, self.password = url, username, password
        client = caldav.DAVClient(url, username=username, password=password)
        self.principal = client.principal()
        self.calendar = self.principal.calendar(name=calendar_name)

        if calendar_name is not None:
            # Check that calendar already exists
            calendars = self.principal.calendars()
            calendar_name = next((calendar for calendar in calendars if calendar.name == calendar_name), None)
            if calendar_name is None:
                raise Exception("Calendar doesn't exists")

    def get_existing_cals(self):
        return self.principal.calendars()

    def add_calendar(self, name):
        calendars = self.get_existing_cals()
        if name not in calendars:
            caldav.CalendarSet.make_calendar(
                name=name
            )

    def add_task(self, start=datetime, end=datetime, summary="", repeat="once", priority="2", tasktype="auto", deadline=datetime):
        if repeat != "once":
            event = self.calendar.save_event(
                dtstart=start,
                dtend=end,
                summary=summary,
                priority=priority,
                tasktype=tasktype,
                deadline=deadline,
                rrule={'FREQ': repeat}
            )
        else:
            event = self.calendar.save_event(
                dtstart=start,
                dtend=end,
                summary=summary,
                priority=priority,
                tasktype=tasktype,
                deadline=deadline,
            )

    def get_task(self, start, end):
        tasks = self.calendar.search(
            start=start,
            end=end,
            event=True)
        return tasks

    @staticmethod
    def del_task(events: caldav.Event):
        for event in events:
            event.delete()

    @staticmethod
    def modify_task(event, summary, start, end):
        if summary:
            event.icalendar_component["summary"] = summary
        if start:
            event.icalendar_component["dtstart"].dt = start
        if end:
            event.icalendar_component["dtend"].dt = end
        event.save()
