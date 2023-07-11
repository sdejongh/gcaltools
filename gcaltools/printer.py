from rich.table import Table
from rich.console import Console
from rich import box
from datetime import datetime


def calendar_list_printer(calendar_list):

    calendars_table = Table(title="Available calendars", box=box.SQUARE)
    calendars_table.add_column("Calendar Name", justify="left", style="magenta")
    calendars_table.add_column("Calendar ID", justify="right", style="green")

    for cal in calendar_list:
        calendars_table.add_row(cal['summary'], cal['id'])

    console = Console()
    console.print()
    console.print(calendars_table)
    console.print()


def events_printer(event_list):

    events_table = Table(title="Courses", box=box.SQUARE)
    events_table.add_column("Start Date", justify="center", style="cyan")
    events_table.add_column("End Date", justify="center", style="cyan")
    events_table.add_column("Title", justify="left", style="magenta")
    events_table.add_column("Attendees", justify="right", style="green")

    for e in event_list:
        if 'date' in e['start'].keys():
            start_date = datetime.fromisoformat(e['start']['date']).strftime('%a %d %b %Y (all day)')
            end_date = datetime.fromisoformat(e['end']['date']).strftime('%a %d %b %Y (all day)')
        else:
            start_date = datetime.fromisoformat(e['start']['dateTime']).strftime('%a %d %b %Y --- %H:%M')
            end_date = datetime.fromisoformat(e['end']['dateTime']).strftime('%a %d %b %Y --- %H:%M')

        if "attendees" in e.keys():
            attendees_string = ", ".join([att['email'] for att in e['attendees']])
        else:
            attendees_string = "n/a"

        events_table.add_row(start_date, end_date, e['summary'], attendees_string)

    console = Console()
    console.print()
    console.print(events_table)
    console.print()


def default_printer(user_preferences):

    defaults_table = Table(title="User preferences", box=box.SQUARE)
    defaults_table.add_column("Setting", justify="left", style="magenta")
    defaults_table.add_column("Value", justify="right", style="green")

    for setting in sorted(user_preferences.keys()):
        defaults_table.add_row(setting, str(user_preferences[setting]))

    console = Console()
    console.print()
    console.print(defaults_table)
    console.print()


def summary_printer(calendar_name, calendar_summary, start_date, end_date):

    if start_date is not None and end_date is not None:
        timing = "{} -> {}".format(start_date.strftime("%Y/%m/%d"), end_date.strftime("%Y/%m/%d"))
    else:
        timing = "Full training session"
    summary_table = Table(title="{} - Courses summary ({})".format(calendar_name, timing), box=box.SQUARE)
    summary_table.add_column("Information", justify="left", style="magenta")
    summary_table.add_column("Count", justify="right", style="green")

    for information in sorted(calendar_summary.keys()):
        summary_table.add_row(information, str(calendar_summary[information]))

    console = Console()
    console.print()
    console.print(summary_table)
    console.print()


def templates_printer(templates):
    templates_table = Table(title="Available courses templates", box=box.SQUARE)
    templates_table.add_column("Template", justify="left", style="magenta")
    templates_table.add_column("Title", justify="left", style="green")
    templates_table.add_column("Duration (s)", justify="center", style="green")
    templates_table.add_column("Color", justify="left", style="green")
    templates_table.add_column("Attendees", justify="right", style="green")

    for tpl in sorted(templates.keys()):
        template = templates[tpl]
        templates_table.add_row(tpl, template['title'], str(template['duration']), template['color'], ','.join(template['attendees']))

    console = Console()
    console.print()
    console.print(templates_table)
    console.print()
