#! /usr/bin/python3
# import psutil
# import json
# import configparser
# import time
import sys
# import os
# import subprocess
import logging
import cliff.app
import cliff.commandmanager
import cliff.command
import process_config
# import urllib.request
# import shutil
import workflowlister
from commands.workflows import Workflows
from commands.sysconfig import SysConfig
from commands.daemons import DaemonCommand
from commands.daemons import Coordinator
from commands.daemons import Provisioner
from commands.generator import Generator
from commands.reports import Reports
from commands.status import Status

class PancancerApp(cliff.app.App):
    log = logging.getLogger(__name__)

    def __init__(self):
        commandMgr = cliff.commandmanager.CommandManager('pancancer.app')
        super(PancancerApp, self).__init__(
            description='Pancancer CLI',
            version='1.0',
            command_manager=commandMgr,
        )
        commands = {
            'workflows': Workflows,
            'generator': Generator,
            'reports': Reports,
            'provisioner': Provisioner,
            'coordinator': Coordinator,
            'status': Status,
            'sysconfig': SysConfig
        }
        for k, v in commands.items():
            commandMgr.add_command(k, v)


    def initialize_app(self, argv):
        self.log.debug('initialize_app')

    def prepare_to_run_command(self, cmd):
        self.log.debug('prepare_to_run_command %s', cmd.__class__.__name__)

    def clean_up(self, cmd, result, err):
        self.log.debug('clean_up %s', cmd.__class__.__name__)
        if err:
            self.log.debug('got an error: %s', err)


def main(argv=sys.argv[1:]):
    app = PancancerApp()
    return app.run(argv)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
