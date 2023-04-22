import caldav
from datetime import datetime
from typeOfWork import typeOfWork
from icalendar import Calendar, vDatetime


class CalendarZone:

    def __init__(self, url, username, password, calendar_name=None):
        self.url, self.username, self.password = url, username, password
        client = caldav.DAVClient(url, username=username, password=password)
        self.principal = client.principal()
        self.calendar = self.principal.calendar(name=calendar_name)
        self.map_priority = {
            "normal": 1,
            "critical": 2
        }

        if calendar_name is not None:
            # Check that calendar already exists
            calendars = self.principal.calendars()
            calendar_name = next((calendar for calendar in calendars if calendar.name == calendar_name), None)
            if calendar_name is None:
                raise Exception("Calendar doesn't exists")

    def add_calendar(self, name):
        calendars = self.get_existing_cals()
        if name not in calendars:
            caldav.CalendarSet.make_calendar(name=name)

    def add_task(self, start: datetime, end: datetime, deadline: datetime, work_id: str, priority: str, summary="", repeat="once",
                 tasktype="auto"):

        if repeat != "once":
            event = self.calendar.save_event(
                dtstart=start,
                dtend=end,
                summary=summary,
                priority=self.map_priority[priority],
                tasktype=tasktype,
                deadline=vDatetime(deadline),
                workid=work_id,
                rrule={'FREQ': repeat}
            )
        else:
            event = self.calendar.save_event(
                dtstart=start,
                dtend=end,
                summary=summary,
                priority=self.map_priority[priority],
                tasktype=tasktype,
                deadline=vDatetime(deadline),
                workid=work_id,
            )

    def add_task_ex(self, type_of_work: typeOfWork):
        cross_events = self.get_task(start=type_of_work.start_time, end=type_of_work.end_time)
        list_of_work = []
        if cross_events:
            for event in cross_events:
                list_of_work.append(self.conv_task_to_work(event))
            return False, list_of_work
        else:
            self.add_task(start=type_of_work.start_time,
                          end=type_of_work.end_time,
                          summary=type_of_work.summary,
                          priority=type_of_work.priority,
                          tasktype=type_of_work.work_type,
                          deadline=type_of_work.deadline_time,
                          work_id=type_of_work.work_id)
        return True, type_of_work

    def conv_task_to_work(self, event: caldav.objects.CalendarObjectResource):
        res = typeOfWork(work_type=event.icalendar_component["tasktype"], work_id=event.icalendar_component["workid"])
        res.start_time = event.icalendar_component["dtstart"].dt
        res.end_time = event.icalendar_component["dtend"].dt
        res.duration_time = res.set_duration(res.calculate_duration())
        res.deadline_time = event.icalendar_component["deadline"].dt
        res.priority = [key for key, value in self.map_priority.items() if value == event.icalendar_component["priority"]]
        res.zone_name = event.calendar.name
        return res

    def get_task(self, start, end):
        return self.calendar.search(start=start, end=end, event=True)

    def get_task_ex(self, start, end):
        result = []
        tasks = self.calendar.search(start=start, end=end, event=True)
        if len(tasks) == 0:
            return None
        else:
            for i in tasks:
                result.append(self.conv_task_to_work(i))
        return result

    def get_work_id(self, event: caldav.Event):
        cal = Calendar.from_ical(event.data)
        event_component = cal.walk('VEVENT')[0]
        return event_component.get('WORKID')

    def get_existing_cals(self):
        return self.principal.calendars()

    def get_task_by_work_id(self, work_id: str):
        events = self.calendar.events()
        list_of_event = []
        for event in events:
            if self.get_work_id(event) == work_id:
                list_of_event.append(event)
        return list_of_event

    @staticmethod
    def del_task(events: caldav.Event):
        for event in events:
            event.delete()

    def modify_task(self, type_of_work: typeOfWork):
        event = self.get_task_by_work_id(type_of_work.work_id)[0]
        event.icalendar_component["summary"] = type_of_work.summary
        event.icalendar_component["dtstart"].dt = type_of_work.start_time
        event.icalendar_component["dtend"].dt = type_of_work.end_time
        event.icalendar_component["priority"] = [value for key, value in self.map_priority.items() if key == type_of_work.priority]
        event.icalendar_component["deadline"] = vDatetime(type_of_work.deadline_time)
        event.icalendar_component["tasktype"] = type_of_work.work_type
        event.save()
