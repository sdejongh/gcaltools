import sys
import argparse

from gcaltools.config import AVAILABLE_COMMANDS
from gcaltools.cli_parser import sub_parser_template, sub_parser_show, sub_parser_report, sub_parser_summary, sub_parser_default, sub_parser_add, sub_parser_list
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.completion.nested import NestedCompleter


def get_commandline(text: str):
    temp = ""
    cmdargs = []
    for word in text.split():
        if word[0] == '"':
            temp += word[1:]
        if word[-1] == '"':
            temp += f" {word[:-1]}"
            cmdargs.append(temp)
            temp = ""
        if '"' not in word:
            if len(temp) > 0:
                temp += f" {word}"
            else:
                cmdargs.append(word)
    return cmdargs


class NestedParser(argparse.ArgumentParser):
    def error(self, message: str):
        print(message)
        raise argparse.ArgumentError(None, message)

    def format_help(self):
        formatter = self._get_formatter()
        formatter.add_text("\nAvailable commands")

        # positionals, optionals and user-defined groups
        for action_group in self._action_groups:
            formatter.start_section(action_group.title)
            formatter.add_text(action_group.description)
            formatter.add_arguments(action_group._group_actions)
            formatter.end_section()

        return formatter.format_help()


class Prompter:
    def __init__(self, cli_commands):
        self.__commands = AVAILABLE_COMMANDS
        self.__completer = NestedCompleter(options={cmd: WordCompleter([]) for cmd in self.__commands})
        self.__parser = NestedParser(add_help=False)
        sub_parser = self.__parser.add_subparsers(dest="command")
        sub_parser.add_parser("quit", help="Exits gcaltools interactive prompt")
        sub_parser.add_parser("help", help="Display available commands")
        sub_parser_list(sub_parser, add_help=False)
        sub_parser_add(sub_parser, add_help=False)
        sub_parser_default(sub_parser, add_help=False)
        sub_parser_show(sub_parser, add_help=False)
        sub_parser_report(sub_parser, add_help=False)
        sub_parser_summary(sub_parser, add_help=False)
        sub_parser_template(sub_parser, add_help=False)
        self.__session = PromptSession(completer=self.__completer)
        self.__cli_commands = cli_commands

    def run(self):
        self.__session.output.write("\nWelcome to GCALTOOLS!\n\n")
        while True:
            try:
                text = self.__session.prompt("gcaltools> ")
            except KeyboardInterrupt:
                continue
            except EOFError:
                break

            if not len(text):
                continue

            try:
                args = self.__parser.parse_args(get_commandline(text))
            except argparse.ArgumentError:
                continue

            if args.command == "quit":
                sys.exit(0)
            elif args.command == "help":
                print(self.__parser.format_help())

            else:
                self.__cli_commands.execute_cmd(args.command, args)
