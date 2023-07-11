import os
import xlsxwriter
import yaml
import calendar
from datetime import datetime, timedelta
from xlsxwriter.utility import xl_rowcol_to_cell


def load_attendees(attendees_catalog):
    if os.path.exists(attendees_catalog):
        with open(attendees_catalog) as file:
            return yaml.load(file, Loader=yaml.FullLoader)
    else:
        return {}


def parse_events(events_list):
    events = {}
    attendees_list = []

    for event in events_list:
        event_attendees = []
        if 'attendees' in event.keys():
            for attendee in event['attendees']:
                event_attendees.append(attendee['email'])
                if attendee['email'] not in attendees_list:
                    attendees_list.append(attendee['email'])
        start = datetime.fromisoformat(event['start']['dateTime'])
        end = datetime.fromisoformat(event['end']['dateTime'])
        event_day = start.strftime("%Y/%m/%d")
        event_duration = (end - start).seconds / 3600

        if event_day not in events.keys():
            events[event_day] = {a: event_duration if a in event_attendees else 0 for a in attendees_list}
        else:
            for a in event_attendees:
                if a in events[event_day]:
                    events[event_day][a] = events[event_day][a] + event_duration
                else:
                    events[event_day][a] = event_duration

    return events, sorted(attendees_list)


def xlsx_report(event_list, filename, year=None, month=None, start_date=None, end_date=None, attendees_catalog=None):

    if attendees_catalog is not None:
        attendees_dict = load_attendees(attendees_catalog)
    else:
        attendees_dict = {}

    events, attendees = parse_events(event_list)

    # HEADER ROW
    rows = [['Date'] + [attendees_dict[a] if a in attendees_dict.keys() else a for a in attendees] + ['Total']]

    # GENERATE ROWS
    if start_date is None and end_date is None:
        # Report for dates on month/year basis
        print('Generating report for {}: {}'.format(str(year) + '/' + str(month), filename))
        for day in range(calendar.monthrange(year, month)[1]):
            row_date = datetime(year=year, month=month, day=day+1).strftime("%Y/%m/%d")
            row = [row_date]
            if row_date in events.keys():
                row += [events[row_date][a] if a in events[row_date].keys() else 0 for a in attendees]
            else:
                row += [0] * len(attendees)
            rows.append(row)
    else:
        # Report for dates from start_date to end_date
        print('Generating report from {} to {}'.format(start_date, end_date))
        actual_date = start_date
        while actual_date <= end_date:
            row_date = actual_date.strftime("%Y/%m/%d")
            row = [row_date]
            if row_date in events.keys():
                row += [events[row_date][a] if a in events[row_date].keys() else 0 for a in attendees]
            else:
                row += [0] * len(attendees)
            rows.append(row)
            actual_date += timedelta(days=1)

    # WRITE FILE
    book = xlsxwriter.Workbook(filename)
    sheet = book.add_worksheet('Rapport')

    row_id = 0
    for row in rows:
        first_cell = xl_rowcol_to_cell(row_id, 1)
        if row_id > 0:
            if len(attendees) > 1:
                last_cell = xl_rowcol_to_cell(row_id, len(attendees))
                row += ['=SUM({}:{})'.format(first_cell, last_cell)]
            else:
                row += ['=SUM({})'.format(first_cell)]
        sheet.write_row(row_id, 0, rows[row_id])
        row_id += 1

    book.close()
    print('Report generation complete.')


# TO DO
# def md_report(event_list, filename, year, month, attendees_catalog=None):
#    pass
