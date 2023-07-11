# General variables
__VERSION = "1.0.1"

PERIODS = {
    "am": "09:00",
    "pm": "13:30"
}

# NEVER CHANGE THIS
SCOPES = ['https://www.googleapis.com/auth/calendar.events', 'https://www.googleapis.com/auth/calendar', 'https://www.googleapis.com/auth/calendar.addons.execute']
DATE_FORMAT = "%Y-%m-%d"
# DATETIME_FORMAT = "%Y-%m-%d %H:%M"
# GCAL_DATE_FORMAT = "%Y-%m-%dT00:00:00+00:00"
# USER_PREFERENCES_FILE = '.gcaltools'
COLORS = {
    'lavender': 1,
    'sage': 2,
    'grape': 3,
    'flamingo': 4,
    'banana': 5,
    'tangerine': 6,
    'peacock': 7,
    'graphite': 8,
    'blueberry': 9,
    'basil': 10,
    'tomato': 11,
}

AVAILABLE_COMMANDS = ['add', 'default', 'help', 'list', 'report', 'summary', 'template', 'quit']