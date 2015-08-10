#! /usr/bin/python3

import sys
import logging
from cliff.app import App
from cliff.commandmanager import CommandManager
from cliff.command import Command

class WorkflowLister:
    "Get a listing of workflows from a source of workflow metadata."
    # Eventually, this data structure should come from some sort of online registry. For now, just define it in code.
    _workflows= {   'Sanger':
                    {
                        'full_name':'Workflow_Bundle_SangerPancancerCgpCnIndelSnvStr_1.0.8_SeqWare_1.1.0',
                        'http_workflow':
                        {
                            'url':'https://s3.amazonaws.com/oicr.workflow.bundles/released-bundles/Workflow_Bundle_BWA_2.6.5_SeqWare_1.1.1.zip',
                            'version':'1.0.8'
                        },
                        "containers":
                        {
                            "seqware_whitestar_pancancer": {
                                "name":"seqware_whitestar_pancancer",
                                "image_name": "pancancer/seqware_whitestar_pancancer:1.1.1"
                            }
                        },
                        "ami_id":"ami-12345"
                    },
                    'BWA':
                    {
                        'full_name':'Workflow_Bundle_BWA_2.6.5_SeqWare_1.1.1',
                        'http_workflow':
                        {
                            'url':'https://s3.amazonaws.com/oicr.workflow.bundles/released-bundles/Workflow_Bundle_SangerPancancerCgpCnIndelSnvStr_1.0.8_SeqWare_1.1.0.zip',
                            'version':'2.6.5'
                        },
                        "containers":
                        {
                            "seqware_whitestar_pancancer": {
                                "name":"seqware_whitestar_pancancer",
                                "image_name": "pancancer/seqware_whitestar_pancancer:1.1.1"
                            }
                        },
                        "ami_id":"ami-12345"
                    },
                    'DKFZ/EMBL':
                    {
                        'full_name':'Workflow_Bundle_DEWrapperWorkflow_1.0.5_SeqWare_1.1.1',
                        'http_workflow':
                        {
                            'url':'https://s3.amazonaws.com/oicr.workflow.bundles/released-bundles/Workflow_Bundle_DEWrapperWorkflow_1.0.5_SeqWare_1.1.1.zip',

                            'version':'1.0.5'
                        },
                        "containers":
                        {
                            "pcawg-delly-workflow": {
                                "name":"pcawg-delly-workflow",
                                "image_name": "pancancer/pcawg-delly-workflow:1.0"
                            },
                            "seqware_whitestar_pancancer": {
                                "name":"seqware_whitestar_pancancer",
                                "image_name": "pancancer/seqware_whitestar_pancancer:1.1.1"
                            }
                        },
                        "s3_containers":
                        {
                            "dkfz_dockered_workflows":
                            {
                                "name":"dkfz_dockered_workflows",
                                "url":"https://s3.amazonaws.com/oicr.docker.private.images/dkfz_dockered_workflows_1.3.tar"
                            }
                        },
                        "ami_id":"ami-12345"
                    }
                }

    @staticmethod
    def get_workflow_names():
        keys = ''
        for k in WorkflowLister._workflows:
            keys += k+'\n'
        return keys

    @staticmethod
    def get_workflow_details(workflow_name):
        return WorkflowLister._workflows[workflow_name]


class Workflows(Command):
    "This command  can help you configure and select workflows."
    log = logging.getLogger(__name__)

    def get_parser(self,prog_name):
        parser = super(Workflows,self).get_parser(prog_name)
        workflows_subparser = parser.add_subparsers(title='subcommands',help='workflows subcommands: list and config',dest='subparser_name')
        workflows_subparser.add_parser('list',help='Get a list of workflows')
        workflows_subparser.add_parser('config',help='Generate a default config file for a specific workflow').add_argument('workflow_name',help='Name of workflow to configure')
        return parser

    def take_action(self, parsed_args):
        subparser_name=vars(parsed_args)['subparser_name']
        self.log.info('subparser: %s',subparser_name)
        if subparser_name=='list':
            workflow_list = WorkflowLister.get_workflow_names()
            print ('Available workflows are:')
            print(workflow_list)

        elif subparser_name=='config':
            # TODO: Actually generate the correct INI file!
            print('generating default INI for workflow '+vars(parsed_args)['workflow_name'])


class DaemonCommand(Command):
    "Parent class for commands that start/stop daemons"
    service_name=''
    log = logging.getLogger(__name__)

    def get_parser(self,prog_name):
        parser = super(DaemonCommand,self).get_parser(prog_name)
        subparser = parser.add_subparsers(title='subcommands',help='coordinator subcommands: start, stop, restart',dest='subparser_name')
        subparser.add_parser('start',help='Start the '+self.service_name+' service')
        subparser.add_parser('stop',help='Stop the '+self.service_name+' service')
        subparser.add_parser('restart',help='Stop the '+self.service_name+' service')
        return parser

    def take_action(self, parsed_args):
        subparser_name=vars(parsed_args)['subparser_name']
        self.log.info('subparser: %s',subparser_name)

        #if subparser_name=='start':
            #TODO: Figure out how to properly start/stop services from within python
            # service Coordinator start
        #elif subparser_name=='stop':
            # service Coordinator stop
        #elif subparser_name=='restart':
            # service Coordinator restart


class Coordinator(DaemonCommand):
    "The Coordinator will process existing job orders into requests for VMs and jobs that will be picked up by running VMs."
    log = logging.getLogger(__name__)
    def __init__(self,Coordinator,args):
        self.service_name='Coordinator'


class Provisioner(DaemonCommand):
    "The Provisioner will launcher worker VMs as needed based on the workflow orders sent to the system."
    log = logging.getLogger(__name__)
    def __init__(self,Provisioner,args):
        self.service_name='Provisioner'


class Generator(Command):
    "This Generator will generate new job orders."
    log = logging.getLogger(__name__)
    def get_parser(self,prog_name):
       parser = super(Generator,self).get_parser(prog_name)
       parser.add_argument('--workflow',dest='workflow_name',help='The name of the workflow for which you would like to generate jobs.')
       return parser

    def take_action(self, parsed_args):
        workflow_name=vars(parsed_args)['workflow_name']
        self.log.info('workflow_name: %s',workflow_name)

        if not (workflow_name in WorkflowLister.get_workflow_names()):
            print('Oh, I\'m SO sorry, but '+workflow_name+' is not the name of an available workflow.\nPlease use the command \'workflows list\' to see the list of currently available workflows.')
        else:
            workflow_details = WorkflowLister.get_workflow_details(workflow_name)
            generator_cmd = 'Generator --workflow-name '+workflow_name+' --workflow-version '+workflow_details['http_workflow']['version']+' --workflow-path '+'/workflows/'+workflow_details['full_name']+' --ini-dir '+'/home/ubuntu/ini-dir'
            print(generator_cmd)
            #TODO execute generator_cmd


class Reports(Command):
    "The will generate reports on the command line."
    log = logging.getLogger(__name__)


class PancancerApp(App):
    log = logging.getLogger(__name__)

    def __init__(self):
        commandMgr = CommandManager('pancancer.app')
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
            'coordinator': Coordinator
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
