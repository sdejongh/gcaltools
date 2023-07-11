import argparse
import re
from datetime import datetime
from gcaltools.utils import today_date
from gcaltools.config import __VERSION, COLORS, PERIODS

email_pattern = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')


def valid_date(date_string):
    try:
        return datetime.strptime(date_string, "%Y-%m-%d")
    except ValueError:
        msg = "Not a valid date: '{0}'. \nCorrect format is: YYYY-MM-DD".format(date_string)
        raise argparse.ArgumentTypeError(msg)


def valid_time(time_string):
    if time_string in PERIODS:
        return datetime.strptime(PERIODS[time_string], "%H:%M")
    try:
        return datetime.strptime(time_string, "%H:%M")
    except ValueError:
        msg = "Not a valid time: '{0}'. \nCorrect format is: HH:MM".format(time_string)
        raise argparse.ArgumentTypeError(msg)


def valid_attendees(attendees_string):
    msg = "Not a attendees list: '{0}'. \nCorrect format is: user@email.com,user2@email.com".format(attendees_string)
    email_list = attendees_string.split(',')
    try:
        for email in email_list:
            if not email_pattern.match(email):
                raise argparse.ArgumentTypeError(msg)
        return email_list
    except ValueError:
        raise argparse.ArgumentTypeError(msg)


def cli_parser():
    parser = argparse.ArgumentParser()
    sub_parser = parser.add_subparsers(dest='command')
    sub_parser_auth(sub_parser)
    sub_parser_add(sub_parser)
    sub_parser_list(sub_parser)
    sub_parser_show(sub_parser)
    sub_parser_report(sub_parser)
    sub_parser_default(sub_parser)
    sub_parser_summary(sub_parser)
    sub_parser_template(sub_parser)
    parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __VERSION)
    parser.add_argument('-i', '--interactive', action ='store_true')
    return parser


def sub_parser_auth(sub_parser, add_help=True):
    sub_parser.add_parser('remoteauth', help="Google API Auth without local webserver.", add_help=add_help)


def sub_parser_summary(sub_parser, add_help=True):
    summary_parser = sub_parser.add_parser('summary', help="Display events summary for given calendar.", add_help=add_help)
    summary_parser.add_argument('-c', '--calendar', type=str, help="Calendar name")
    summary_parser.add_argument('-s', '--start_date', type=valid_date, help="Summary first day, format: YYYY-MM-DD")
    summary_parser.add_argument('-e', '--end_date', type=valid_date, help="Summary last day, format: YYYY-MM-DD")


def sub_parser_report(sub_parser, add_help=True):
    report_parser = sub_parser.add_parser('report', help="Generates month occupation reports based on event attendees", add_help=add_help)
    report_parser.add_argument('-c', '--calendar', type=str, help="Calendar name")
    report_parser.add_argument('-m', '--month', type=int, help="Month")
    report_parser.add_argument('-y', '--year', type=int, help="Year")
    report_parser.add_argument('-o', '--outputformat', type=int, help="Report output format (not yet implemented)")
    report_parser.add_argument('-f', '--filename', type=str, help="Name for the output file")
    report_parser.add_argument('-a', '--attendees_catalog', type=str, help="Catalog of attendees mapping email with names for report generation")
    report_parser.add_argument('-s', '--start_date', type=valid_date, help="Summary first day, format: YYYY-MM-DD")
    report_parser.add_argument('-e', '--end_date', type=valid_date, help="Summary last day, format: YYYY-MM-DD")


def sub_parser_add(sub_parser, add_help=True):
    add_parser = sub_parser.add_parser('add', help="Add event to calendar", add_help=add_help)
    add_parser.add_argument('-T', '--template', type=str, help="Event template from templates.yaml")
    add_parser.add_argument('-c', '--calendar', type=str, help="Calendar name")
    add_parser.add_argument('-t', '--title', type=str, help="Event title")
    add_parser.add_argument('start_date', type=valid_date, help="Event start time, format: YYYY-MM-DD")
    time_group = add_parser.add_mutually_exclusive_group(required=True)
    time_group.add_argument('-s', '--start', type=valid_time, help="Event start time, format: HH:MM OR am OR pm")
    time_group.add_argument('-f', '--full', action='store_true', help="Generates event for both AM and PM periods")
    add_parser.add_argument('-d', '--duration', type=int, help="Event duration (minutes)")
    add_parser.add_argument('-a', '--attendees', type=valid_attendees, help="List of emails of attendees", required=False)
    add_parser.add_argument('-o', '--override-color', type=str, choices=[c for c in sorted(COLORS.keys())], help="List of emails of attendees", default="")


def sub_parser_list(sub_parser, add_help=True):
    sub_parser.add_parser('list', help="Lists available calendars", add_help=add_help)


def sub_parser_show(sub_parser, add_help=True):
    show_parser = sub_parser.add_parser('show', help="Displays calendar", add_help=add_help)
    display_group = show_parser.add_mutually_exclusive_group()
    display_group.add_argument('-w', action='store_true', help="Displays calendar for current week")
    display_group.add_argument('-m', action='store_true', help="Displays calendar for current month")
    show_parser.add_argument('-c', '--calendar', type=str, help="Calendar name")
    show_parser.add_argument('startDate', type=valid_date, help="First date to search for events", default=today_date(), nargs="?")
    show_parser.add_argument('endDate', type=valid_date, help="Last date to search for events", nargs="?")


def sub_parser_default(sub_parser, add_help=True):
    default_parser = sub_parser.add_parser('default', help="Show user's default preferences", add_help=add_help)
    setting_group = default_parser.add_mutually_exclusive_group()
    setting_group.add_argument('-c', '--calendar', type=str, help="Set default calendar")
    setting_group.add_argument('-d', '--duration', type=int, help="Set default event duration")
    setting_group.add_argument('-r', '--reset', help="Erase .gcaltools file (resets all user preferences)", action="store_true")
    setting_group.add_argument('-t', '--timezone', type=str, help="Set default time zone (IANA format ie: \"Europe/Brussels\")")
    setting_group.add_argument('-a', '--attendees_catalog', type=str, help="Catalog of attendees mapping email with names for report generation")


def sub_parser_template(sub_parser, add_help=True):
    template_parser = sub_parser.add_parser('template', help="Manage courses templates", add_help=add_help)
    template_actions = template_parser.add_subparsers(dest="subcommand")
    template_actions.add_parser('list', help="List available course templates", add_help=add_help)

    tpl_add = template_actions.add_parser('add', help="Create a new course template", add_help=add_help)
    tpl_add.add_argument('name', help="Template name")
    tpl_add.add_argument('title', help="Event title")
    tpl_add.add_argument('-d', '--duration', type=int, help="Event duration (minutes)")
    tpl_add.add_argument('-o', '--override-color', type=str, choices=[c for c in sorted(COLORS.keys())], help="List of emails of attendees", default="")
    tpl_add.add_argument('-a', '--attendees', type=valid_attendees, help="List of emails of attendees", required=False)

    tpl_del = template_actions.add_parser('del', help="Delete existing course template", add_help=add_help)
    tpl_del.add_argument('name', help="Template name")


