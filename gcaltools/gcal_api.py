import os
import yaml
from gcaltools import gcal_tool
from datetime import datetime, timedelta
from gcaltools.config import SCOPES, COLORS
from pytz import timezone


def event_start(event):
    """Returns start time for full day length event or specific time event"""
    if 'date' in event['start'].keys():
        return event['start']['date']
    else:
        return event['start']['dateTime']


def _create_service(noauth_local_webserver: bool = False):
    """Initialize Google Calendar service"""
    args = ['']
    if noauth_local_webserver:
        args.append('--noauth_local_webserver')
    return gcal_tool.init(args, 'calendar', 'v3', __doc__, __file__, scope=SCOPES)


class GoogleCalendarManager:
    """Google Calendar Manager class
    Works as interface for google calendar API
    """
    defaults_file_path = os.path.join(os.path.expanduser('~'), '.gcaltools/.defaults')

    def __init__(self, use_api: bool = True, remote_auth: bool = False) -> None:
        if use_api:
            self._service, self._flags = _create_service(noauth_local_webserver=remote_auth)
            self._calendars = self.__get_calendars()['items']
        self.__load_user_preferences()

    def __load_user_preferences(self) -> None:
        """Loads user preferences and default settings from .yaml file"""
        if os.path.exists(self.defaults_file_path):
            with open(self.defaults_file_path) as file:
                self._preferences = yaml.load(file, Loader=yaml.FullLoader)
        else:
            self._preferences = {
                'default_calendar': None,
                'default_duration': 60,
                'default_timezone': self._calendars[0]['timeZone']
            }

    def reload(self) -> None:
        """Reload user preferences and default settings"""
        self.__load_user_preferences()

    def __save_user_preferences(self) -> None:
        """Write user preferences and defaulty settings to .yaml file"""
        with open(self.defaults_file_path, 'w') as file:
            yaml.dump(self._preferences, file)

    def __set_user_preference(self, setting: str, value) -> None:
        """Set user preference or default setting"""
        self._preferences[setting] = value
        self.__save_user_preferences()

    def reset_user_preferences(self) -> None:
        """Resets all user preferences and default settings"""
        if os.path.exists(self.defaults_file_path):
            os.remove(self.defaults_file_path)
            self.reload()
        else:
            print('WARNING: defaults not found, nothing to delete!')

    @property
    def default_calendar(self) -> str:
        return self._preferences['default_calendar']

    @default_calendar.setter
    def default_calendar(self, calendar_name: str) -> None:
        self.__set_user_preference('default_calendar', calendar_name)

    @property
    def default_event_duration(self) -> int:
        return self._preferences['default_duration']

    @default_event_duration.setter
    def default_event_duration(self, duration: int) -> None:
        self.__set_user_preference('default_duration', duration)

    @property
    def attendees_catalog(self) -> str:
        return self._preferences['attendees_catalog']

    @attendees_catalog.setter
    def attendees_catalog(self, attendees_catalog: str) -> None:
        self.__set_user_preference('attendees_catalog', attendees_catalog)

    @property
    def default_timezone(self) -> str:
        return self._preferences['default_timezone']

    @default_timezone.setter
    def default_timezone(self, time_zone: str) -> None:
        self.__set_user_preference('default_timezone', time_zone)

    def get_user_preferences(self) -> dict:
        """Returns user preferences and default settings"""
        return self._preferences

    def __get_calendar_id(self, calendar_name: str) -> str or None:
        for cal in self._calendars:
            if cal['summary'] == calendar_name:
                return cal['id']
        else:
            return None

    def __get_calendars(self):
        return self._service.calendarList().list().execute()

    def calendar_exists(self, calendar_name: str) -> bool:
        """Return True if given calendar exists, or False if not."""
        return True if self.__get_calendar_id(calendar_name) is not None else False

    def get_events(self, calendar_name: str, order_by=None, time_min=None, time_max=None, max_results=None):
        """Return list of events
        calendar_name:  Google Calendar Name        ->  str
        order_by:       Sort events by...           ->  str
        time_min:       first date                  -> datetime()
        time_max:       last date                   -> datetime()
        max_results:    maximum number of events    -> int
        """
        if time_max is not None:
            time_max = timezone(self.default_timezone).localize(time_max).isoformat()

        if time_min is not None:
            time_min = timezone(self.default_timezone).localize(time_min).isoformat()

        event_list = self._service.events().list(calendarId=self.__get_calendar_id(calendar_name), orderBy=order_by, timeMin=time_min, timeMax=time_max, maxResults=max_results).execute()['items']
        return sorted(event_list, key=lambda e: event_start(e))

    def get_calendars(self, sort_by_summary: bool = True):
        """Return list of available calendars"""
        if sort_by_summary:
            return sorted(self._calendars, key=lambda c: c['summary'])
        else:
            return self._calendars

    def insert_event(self, calendar_name: str, title: str, start_date: datetime, start_time: datetime, duration: int = None, attendees=None, color_name=None):
        """Inserts new event in calendar"""
        calendar_id = self.__get_calendar_id(calendar_name)
        if duration is None:
            duration = self.default_event_duration
        body_start_time = timezone(self.default_timezone).localize(start_date + timedelta(hours=start_time.hour, minutes=start_time.minute))
        body_end_time = body_start_time + timedelta(minutes=duration)

        body = {
            'summary': title,
            'start': {'dateTime': body_start_time.isoformat(), 'timZone': self.default_timezone},
            'end': {'dateTime': body_end_time.isoformat()},
        }

        if attendees is not None:
            body['attendees'] = [{'email': attendee} for attendee in attendees]

        if color_name is not None:
            body['colorId'] = COLORS[color_name]

        self._service.events().insert(calendarId=calendar_id, body=body).execute()


if __name__ == "__main__":
    pass
