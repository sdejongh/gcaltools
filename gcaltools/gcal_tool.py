# Google Calendar Tool
# Based on sample_tool.py from "googleapiclient" package
#
# Modified *.dat file and *.json file location to /home/username/.gcaltools/
#


from __future__ import absolute_import

import argparse
import os

from googleapiclient import discovery
from googleapiclient.http import build_http


def init(
    argv, name, version, doc, filename, scope=None, parents=[], discovery_filename=None
):
    """A common initialization routine for samples.

  Args:
    argv: list of string, the command-line parameters of the application.
    name: string, name of the API.
    version: string, version of the API.
    doc: string, description of the application. Usually set to __doc__.
    file: string, filename of the application. Usually set to __file__.
    parents: list of argparse.ArgumentParser, additional command-line flags.
    scope: string, The OAuth scope used.
    discovery_filename: string, name of local discovery file (JSON). Use when discovery doc not available via URL.

  Returns:
    A tuple of (service, flags), where service is the service object and flags
    is the parsed command-line flags.
  """
    try:
        from oauth2client import client
        from oauth2client import file
        from oauth2client import tools
    except ImportError:
        raise ImportError(
            "googleapiclient.sample_tools requires oauth2client. Please install oauth2client and try again."
        )

    if scope is None:
        scope = "https://www.googleapis.com/auth/" + name

    # Parser command-line arguments.
    parent_parsers = [tools.argparser]
    parent_parsers.extend(parents)
    parser = argparse.ArgumentParser(
        description=doc,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        parents=parent_parsers,
    )
    flags = parser.parse_args(argv[1:])

    # Name of a file containing the OAuth 2.0 information for this
    # application, including client_id and client_secret, which are found
    # on the API Access tab on the Google APIs
    # Console <http://code.google.com/apis/console>.
    client_secrets = os.path.join(os.path.expanduser('~'), ".gcaltools","client_secrets.json")

    # Set up a Flow object to be used if we need to authenticate.
    flow = client.flow_from_clientsecrets(
        client_secrets, scope=scope, message=tools.message_if_missing(client_secrets)
    )

    # Prepare credentials, and authorize HTTP object with them.
    # If the credentials don't exist or are invalid run through the native client
    # flow. The Storage object will ensure that if successful the good
    # credentials will get written back to a file.
    
    dat_file_path = os.path.join(os.path.expanduser('~'),".gcaltools/",name + ".dat")

    storage = file.Storage(dat_file_path)
    credentials = storage.get()
    if credentials is None or credentials.invalid:
        credentials = tools.run_flow(flow, storage, flags)
    http = credentials.authorize(http=build_http())

    if discovery_filename is None:
        # Construct a service object via the discovery service.
        service = discovery.build(name, version, http=http)
    else:
        # Construct a service object using a local discovery document file.
        with open(discovery_filename) as discovery_file:
            service = discovery.build_from_document(
                discovery_file.read(), base="https://www.googleapis.com/", http=http
            )
    return (service, flags)
