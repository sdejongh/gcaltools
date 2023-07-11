import os.path

import yaml

from gcaltools.printer import calendar_list_printer, default_printer, events_printer, summary_printer, templates_printer
from gcaltools.reporter import xlsx_report
from datetime import datetime, timedelta
from calendar import monthrange
from gcaltools.config import COLORS, PERIODS
from os import path
from yaml import load, Loader


class CliCommand:
    def __init__(self, calendar_manager):
        self._calendar_manager = calendar_manager
        self._template_file = path.expanduser('~') + '/.gcaltools/templates.yaml'

    @property
    def calendar_manager(self):
        return self._calendar_manager

    def __load_template(self, template: str):
        if path.exists(self._template_file):
            try:
                with open(self._template_file) as f:
                    templates = load(f, Loader=Loader)
                    if template in templates.keys():
                        return templates[template]
                    else:
                        print('ERROR: Template {} not found in {}!'.format(template, self._template_file))
                        exit()
            except yaml.YAMLError:
                print("ERROR: Unable to parse {}".format(self._template_file))
                exit()
        else:
            print("ERROR: template file {} not found!".format(self._template_file))
            exit()

    # Execute CLI command
    def execute_cmd(self, cli_command: str, command_args):
        if cli_command == 'add':
            self.__command_add(command_args)
        elif cli_command == 'default':
            self.__command_default(command_args)
        elif cli_command == 'list':
            self.__command_list()
        elif cli_command == 'report':
            self.__command_report(command_args)
        elif cli_command == 'show':
            self.__command_show(command_args)
        elif cli_command == 'summary':
            self.__command_summary(command_args)
        elif cli_command == 'template':
            self.__command_template(command_args)
        else:
            pass

    # gcaltools ADD command
    def __command_add(self, command_args):

        if not command_args.title and not command_args.template:
            print('ERROR: No event title defined')
            exit()

        if command_args.calendar:
            if not self.calendar_manager.calendar_exists(command_args.calendar):
                print('ERROR: calendar {} does not exist.'.format(command_args.calendar))
                exit()
            active_calendar = command_args.calendar
        else:
            active_calendar = self.calendar_manager.default_calendar
            if active_calendar is None:
                print('ERROR: default calendar not set')
                exit()

        duration = self.calendar_manager.default_event_duration
        attendees = None
        color_name = None
        title = None

        if command_args.template:
            event = self.__load_template(command_args.template)
            title = event['title']
            duration = event['duration']
            color_name = event['color']
            attendees = event['attendees']

        if command_args.duration:
            duration = command_args.duration

        if command_args.attendees:
            attendees = command_args.attendees

        if command_args.override_color:
            color_name = command_args.override_color

        if command_args.title:
            title = command_args.title

        if command_args.start:
            self.calendar_manager.insert_event(active_calendar, title, command_args.start_date, command_args.start, duration, attendees, color_name)

        if command_args.full:
            for p in PERIODS:
                time = datetime.strptime(PERIODS[p], "%H:%M")
                self.calendar_manager.insert_event(active_calendar, title, command_args.start_date, time, duration, attendees, color_name)

    # gcaltools LIST command
    def __command_list(self):
        calendar_list_printer(self.calendar_manager.get_calendars())

    # gcaltools SHOW command
    def __command_show(self, command_args):
        min_time = command_args.startDate

        # Display only one day if no end date is given
        if command_args.endDate is None:
            max_time = min_time + timedelta(days=1)
        else:
            max_time = command_args.endDate


        # Displays events for the current week
        if command_args.w:
            min_time = (datetime.now() - timedelta(days=(datetime.now().weekday()))).replace(hour=0, minute=0, second=0)
            max_time = min_time + timedelta(days=6)

        # Displays events for the current month
        if command_args.m:
            min_time = datetime.now().replace(day=1, hour=0, minute=0, second=0)
            max_time = min_time.replace(day=monthrange(min_time.year, min_time.month)[1], hour=23, minute=59, second=59)

        if command_args.calendar:
            if not self.calendar_manager.calendar_exists(command_args.calendar):
                print('ERROR: calendar {} does not exist.'.format(command_args.calendar))
                exit()
            active_calendar = command_args.calendar
        else:
            active_calendar = self.calendar_manager.default_calendar
            if active_calendar is None:
                print('ERROR: default calendar not set')
                exit()

        events_printer(self.calendar_manager.get_events(active_calendar, time_min=min_time, time_max=max_time, max_results=1000))

    # gcaltools DEFAULT command
    def __command_default(self, command_args):
        if command_args.calendar:
            if self.calendar_manager.calendar_exists(command_args.calendar):
                self.calendar_manager.default_calendar = command_args.calendar
            else:
                print('ERROR: Calendar not found')
                exit()
        if command_args.duration:
            self.calendar_manager.default_event_duration = command_args.duration

        if command_args.timezone:
            self.calendar_manager.default_timezone = command_args.timezone

        if command_args.attendees_catalog:
            self.calendar_manager.attendees_catalog = command_args.attendees_catalog

        if command_args.reset:
            self.calendar_manager.reset_user_preferences()

        default_printer(self.calendar_manager.get_user_preferences())

    # gcaltools REPORT command
    def __command_report(self, command_args):
        if command_args.calendar:
            if not self.calendar_manager.calendar_exists(command_args.calendar):
                print('ERROR: calendar {} does not exist.'.format(command_args.calendar))
                exit()
            active_calendar = command_args.calendar
        else:
            active_calendar = self.calendar_manager.default_calendar
            if active_calendar is None:
                print('ERROR: default calendar not set')
                exit()

        if command_args.start_date and command_args.end_date:
            min_time = command_args.start_date
            max_time = command_args.end_date.replace(hour=23, minute=59, second=59)
            active_year = None
            active_month = None
        else:
            active_year = command_args.year if command_args.year is not None else datetime.now().year
            active_month = command_args.month if command_args.month is not None else datetime.now().month

            min_time = datetime(year=active_year, month=active_month, day=1)
            max_time = min_time.replace(day=monthrange(min_time.year, min_time.month)[1], hour=23, minute=59, second=59)

        attendees_catalog = command_args.attendees_catalog if command_args.attendees_catalog is not None else self.calendar_manager.attendees_catalog

        default_filename = "{}_{}_{}".format(active_calendar, min_time.strftime("%Y%m%d"), max_time.strftime("%Y%m%d"))
        print(default_filename)

        report_filename = command_args.filename if command_args.filename is not None else default_filename

        if command_args.outputformat == "md":
            # TO DO
            pass

        else:
            file_extension = ".xlsx"
            xlsx_report(self.calendar_manager.get_events(active_calendar, time_min=min_time, time_max=max_time, max_results=1000), report_filename + file_extension, active_year, active_month, min_time, max_time, attendees_catalog)

    # gcaltools SUMMARY command
    def __command_summary(self, command_args):
        if command_args.calendar:
            if not self.calendar_manager.calendar_exists(command_args.calendar):
                print('ERROR: calendar {} does not exist.'.format(command_args.calendar))
                exit()
            active_calendar = command_args.calendar
        else:
            active_calendar = self.calendar_manager.default_calendar
            if active_calendar is None:
                print('ERROR: default calendar not set')
                exit()

        if command_args.start_date and command_args.end_date:
            start = command_args.start_date
            end = command_args.end_date
        else:
            start = None
            end = None

        calendar_summary = {}

        events = self.calendar_manager.get_events(active_calendar, time_min=start, time_max=end, max_results=1000)

        calendar_summary['Training days with trainer'] = len([e for e in events if 'attendees' in e.keys()])/2
        calendar_summary['Training days without trainer'] = len([e for e in events if 'attendees' not in e.keys() and ('colorId' not in e.keys() or ('colorId' in e.keys() and int(e['colorId'])) != COLORS['graphite'])])/2
        calendar_summary['Total training days'] = len([e for e in events if 'colorId' not in e.keys() or int(e['colorId']) != COLORS['graphite']])/2

        summary_printer(active_calendar, calendar_summary, start, end)

    # gcaltools TEMPLATE command
    def __command_template(self, command_args):

        if not os.path.exists(self._template_file):
            try:
                with open(self._template_file, 'w') as f:
                    templates = {}
                    yaml.dump(templates, f, Dumper=yaml.Dumper)
            except OSError:
                print("ERROR: Unable to create template file {}".format(self._template_file))
                exit()

        else:
            try:
                with open(self._template_file) as f:
                    templates = yaml.load(f, Loader=yaml.Loader)
            except OSError:
                print("ERROR: Unable to create template file {}".format(self._template_file))
                exit()

        if command_args.subcommand == 'list':
            templates_printer(templates)

        if command_args.subcommand == 'add':
            if command_args.name not in templates:
                template = {
                    'title': command_args.title,
                    'duration': None,
                    'color': None,
                    'attendees': []
                }
                if command_args.duration:
                    template['duration'] = command_args.duration

                if command_args.override_color:
                    template['color'] = command_args.override_color

                if command_args.attendees:
                    template['attendees'] = command_args.attendees

                templates[command_args.name] = template

                try:
                    with open(self._template_file, 'w') as f:
                        yaml.dump(templates, f, Dumper=yaml.Dumper)
                    templates_printer(templates)
                except OSError:
                    print("ERROR: Unable to save templates to file {}".format(self._template_file))
            else:
                print("ERROR: Template {} already exists!".format(command_args.name))
                exit()

        if command_args.subcommand == 'del':
            if command_args.name not in templates:
                print("ERROR: Template {} does not exist!".format(command_args.name))
                exit()
            else:
                del(templates[command_args.name])
                try:
                    with open(self._template_file, 'w') as f:
                        yaml.dump(templates, f, Dumper=yaml.Dumper)
                    templates_printer(templates)
                except OSError:
                    print("ERROR: Unable to save templates to file {}".format(self._template_file))


