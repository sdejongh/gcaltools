# GCALTOOLS
Google Calendar Python Command Line manager using Google OAuth2 API used to manage training sessions planning.

## Install
### Clone the repository
```bash
git clone https://github.com/sdejongh/gcaltools.git
```

### Enter the project directory
```bash
cd gcaltools
```

### Install requirements
```bash
pip install -r requirements.txt
```

### Install the package
```bash
pip install .
```

## Authenticate
- Copy the client_secrets.json.example to `~/.gcaltools/client_secrets.json`.
- Go to your Google API management : https://console.cloud.google.com/
- Create a new project and create a new OAuth Client ID.
- Copy the Client ID and the SecretKey and the corresponding fields in your `client_secrets.json` file.

Now you can launch gcaltools
```
gcaltools --version
```
A browser should open and ask for authentication for you Google Account.
One authenticated, you can now play with `gcaltools`

## (Optionnal) Create a attendees.yaml 
The file is used for the report feature. This allows gcaltools to replace the email of the attendees by a defined display name.
You can use the provided `attendees.yaml` file as example and put it in `~/.gcaltools/`.
To use it automatically when generating reports, you can set the default attendees catalog using the following command:
```
gcaltools default -a <path to the file>
```

## Running gcaltools
```
usage: gcaltools [-h] [-v] {remoteauth,add,list,show,report,default,summary,template} ...

positional arguments:
  {remoteauth,add,list,show,report,default,summary,template}
    remoteauth          Google API Auth without local webserver.
    add                 Add event to calendar
    list                Lists available calendars
    show                Displays calendar
    report              Generates month occupation reports based on event attendees
    default             Show user's default preferences
    summary             Display events summary for given calendar.
    template            Manage courses templates

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit

````

## Actual state
- [x] Listing available calendars
- [x] Display current week events
- [x] Display current month events
- [x] Display events for given date
- [x] Display events for given period
- [x] Create new event
- [x] Store User preferences in YAML file 
- [ ] Search for events
- [ ] Check for overlapping events based on attendees list
- [x] Add events template for faster creation
- [x] Generate monthly report based on event attendees (XLSX format)
- [ ] Generate monthly report based on event attendees (MarkDown format)
- [x] Display events summary for given calendar (events count, events with attendees, ...)