#! /usr/bin/env python

#  Google Calendar TOOLS
#
#  Google calendar management tool
#  author: dejongh.st@gmail.com
from gcaltools.cli_parser import cli_parser
from gcaltools.gcal_api import GoogleCalendarManager
from gcaltools.cli_command import CliCommand
from gcaltools.prompter import Prompter


def main():
    # Configure command line argument parser
    parser = cli_parser()

    args = parser.parse_args()
    remote_auth = (args.command == 'remoteauth')

    # Create Google Calendar Manager
    calendar_manager = GoogleCalendarManager(remote_auth=remote_auth)

    # Create CLI Commands Manager
    cli_commands = CliCommand(calendar_manager)

    if args.interactive:
        cli_prompt = Prompter(cli_commands)
        cli_prompt.run()
    else:
        # Execute function for args.command
        cli_commands.execute_cmd(args.command, args)
