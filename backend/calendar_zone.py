import caldav
from datetime import datetime
from typeOfWork import typeOfWork


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

    def add_task(self, start: datetime, end: datetime, summary="", repeat="once", priority="2", tasktype="auto", deadline: datetime):
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

    def add_task_ex(self, type_of_work: typeOfWork):
        cross_task = self.get_task(start=type_of_work.start_time, end=type_of_work.end_time)

        if cross_task:
            return False, type_of_work
        else:
            self.add_task(start=type_of_work.start_time,
                          end=type_of_work.end_time,
                          summary=type_of_work.summary,
                          priority=type_of_work.priority,
                          tasktype=type_of_work.work_type,
                          deadline=type_of_work.deadline_time)
        return True,cross_task

    def get_task(self, start, end):
        tasks = self.calendar.search(start=start, end=end,event=True)
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
