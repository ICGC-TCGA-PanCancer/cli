import cliff.command
import subprocess
import logging

class Reports(cliff.command.Command):
    "This will generate reports on the command line."
    log = logging.getLogger(__name__)
    def get_parser(self,prog_name):
        parser = super(Reports,self).get_parser(prog_name)
        subparser = parser.add_subparsers(title='subcommands',help='reporting subcommands: gather, info, jobs, provisioned, status, help',dest='report_subcmd')
        subparser.required=True
        subparser.add_parser('gather',help='gathers the last message sent by each worker and displays the last line of it')
        subparser.add_parser('info',help='retrieves detailed information on provisioned instances')
        subparser.add_parser('jobs',help='retrieves detailed information on jobs')
        subparser.add_parser('provisioned',help='retrieves detailed information on provisioned instances')
        subparser.add_parser('status',help='retrieves configuration and version information on arch3')
        subparser.add_parser('youxia',help='ask youxia for all information on instances known to the cloud APIs that are configured')
        subparser.add_parser('help',help='Prints a help message for the reporting system.')
        return parser

    def take_action(self, parsed_args):
        subcmd = vars(parsed_args)['report_subcmd']
        cmd_str='java -cp reporting.jar info.pancancer.arch3.reportcli.ReportCLI --config /home/ubuntu/arch3/config/masterConfig.ini'
        if subcmd!='help':
            # If you don't pass a reporting subcommand to ReportCLI, it will print the help text by default.
            cmd_str='java -cp reporting.jar info.pancancer.arch3.reportcli.ReportCLI --config /home/ubuntu/arch3/config/masterConfig.ini '+subcmd

        subprocess.call(cmd_str.split(' '))
