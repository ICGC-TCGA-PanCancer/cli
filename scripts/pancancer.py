#! /usr/bin/python3
import json
import configparser
import time
import sys
import subprocess
import logging
from cliff.app import App
from cliff.commandmanager import CommandManager
from cliff.command import Command

class WorkflowLister:
    "Get a listing of workflows from a source of workflow metadata."
    # Eventually, this data structure should come from some sort of online registry. For now, just define it in code.
    _workflows= {   'HelloWorld':
                    {
                        'full_name':'Workflow_Bundle_HelloWorld_1.0-SNAPSHOT_SeqWare_1.1.1',
                        'http_workflow':
                        {
                            'url':'https://s3.amazonaws.com/oicr.workflow.bundles/released-bundles/Workflow_Bundle_HelloWorld_1.0-SNAPSHOT_SeqWare_1.1.1.zip',
                            'version':'1.0-SNAPSHOT'
                        },
                        'containers':
                        {
                            'seqware_whitestar_pancancer': {
                                'name':'seqware_whitestar_pancancer',
                                'image_name': 'pancancer/seqware_whitestar_pancancer:1.1.1'
                            }
                        },
                        'ami_id':'ami-12345',
                        'default-ini':'http://something.ini',
                        'instance-type':'m3.medium',
                        'lvm_devices':'/dev/xvdb,/dev/xvdc,/dev/xvdd,/dev/xvde'
                    },
                    'Sanger':
                    {
                        'full_name':'Workflow_Bundle_SangerPancancerCgpCnIndelSnvStr_1.0.8_SeqWare_1.1.0',
                        'http_workflow':
                        {
                            'url':'https://s3.amazonaws.com/oicr.workflow.bundles/released-bundles/Workflow_Bundle_SangerPancancerCgpCnIndelSnvStr_1.0.8_SeqWare_1.1.0.zip',
                            'version':'1.0.8'
                        },
                        'containers':
                        {
                            'seqware_whitestar_pancancer': {
                                'name':'seqware_whitestar_pancancer',
                                'image_name': 'pancancer/seqware_whitestar_pancancer:1.1.1'
                            }
                        },
                        'ami_id':'ami-12345',
                        'default-ini':'http://something.ini',
                        'instance-type':'m3.medium',
                        'lvm_devices':'/dev/xvdb,/dev/xvdc,/dev/xvdd,/dev/xvde'
                    },
                    'BWA':
                    {
                        'full_name':'Workflow_Bundle_BWA_2.6.5_SeqWare_1.1.1',
                        'http_workflow':
                        {
                            'url':'https://s3.amazonaws.com/oicr.workflow.bundles/released-bundles/Workflow_Bundle_BWA_2.6.5_SeqWare_1.1.1.zip',
                            'version':'2.6.5'
                        },
                        'containers':
                        {
                            'seqware_whitestar_pancancer': {
                                'name':'seqware_whitestar_pancancer',
                                'image_name': 'pancancer/seqware_whitestar_pancancer:1.1.1'
                            }
                        },
                        'ami_id':'ami-12345',
                        'default-ini':'http://something.ini',
                        'instance-type':'m3.medium',
                        'lvm_devices':'/dev/xvdb,/dev/xvdc,/dev/xvdd,/dev/xvde'
                    },
                    'DKFZ_EMBL':
                    {
                        'full_name':'Workflow_Bundle_DEWrapperWorkflow_1.0.5_SeqWare_1.1.1',
                        'http_workflow':
                        {
                            'url':'https://s3.amazonaws.com/oicr.workflow.bundles/released-bundles/Workflow_Bundle_DEWrapperWorkflow_1.0.5_SeqWare_1.1.1.zip',

                            'version':'1.0.5'
                        },
                        'containers':
                        {
                            'pcawg-delly-workflow': {
                                'name':'pcawg-delly-workflow',
                                'image_name': 'pancancer/pcawg-delly-workflow:1.0'
                            },
                            'seqware_whitestar_pancancer': {
                                'name':'seqware_whitestar_pancancer',
                                'image_name': 'pancancer/seqware_whitestar_pancancer:1.1.1'
                            }
                        },
                        's3_containers':
                        {
                            'dkfz_dockered_workflows':
                            {
                                'name':'dkfz_dockered_workflows',
                                'url':'https://s3.amazonaws.com/oicr.docker.private.images/dkfz_dockered_workflows_1.3.tar'
                            }
                        },
                        'ami_id':'ami-12345',
                        'default-ini':'http://something.ini',
                        'instance-type':'m3.medium',
                        'lvm_devices':'/dev/xvdb,/dev/xvdc,/dev/xvdd,/dev/xvde'
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

###

class Workflows(Command):
    "This command  can help you configure and select workflows."
    log = logging.getLogger(__name__)

    def get_parser(self,prog_name):
        parser = super(Workflows,self).get_parser(prog_name)
        #parser.add_mutually_exclusive_group()
        workflows_subparser = parser.add_subparsers(title='subcommands',help='workflows subcommands: list and config',dest='subparser_name')
        workflows_subparser.add_parser('list',help='Get a list of workflows')
        workflows_subparser.add_parser('config',help='Generate a default config file for a specific workflow').add_argument('workflow_name',help='Name of workflow to configure')
        return parser

    def take_action(self, parsed_args):
        subparser_name=vars(parsed_args)['subparser_name']
        self.log.debug('subparser: %s',subparser_name)
        if subparser_name=='list':
            workflow_list = WorkflowLister.get_workflow_names()
            print ('Available workflows are:')
            print(workflow_list)

        elif subparser_name=='config':
            workflow_name=vars(parsed_args)['workflow_name']
            if workflow_name in WorkflowLister.get_workflow_names():
                # TODO: Actually generate the correct INI file!
                print('generating default INI in /home/ubuntu/ini-dir/'+workflow_name+'.ini for workflow '+workflow_name)
            else:
                print ('Sorry, but '+workflow_name+' is not a valid workflow name. Please use the command \'workflows list\' to see a list of available workflows.')
        else:
            print ('The available subcommands are \'list\' and \'config\'.')

###

class DaemonCommand(Command):
    "Parent class for commands that start/stop daemons"
    service_name=''
    log = logging.getLogger(__name__)

    def _do_start(self,start_cmd):
        self.log.debug (start_cmd)
        p = subprocess.Popen(start_cmd.split(' '))
        # Wait a moment... if we get ANY response, it means that the process did not start, probably because it's already been started.
        time.sleep(2)
        p.poll()
        if p.returncode==1:
            print('The '+self.service_name+' process might already be running.')
        else:
            print('The service has been started, check the log files for more detail.')

    def _do_stop(self,stop_cmd):
        self.log.debug (stop_cmd)
        p = subprocess.Popen(stop_cmd.split(' '))
        # wait a moment to get the result of the kill command.
        time.sleep(2)
        p.poll()
        if p.returncode==0:
            print('The '+self.service_name+' process has been stopped.')
        elif p.returncode==1:
            print('The '+self.service_name+' process does not appear to have been running, nothing has been stopped.')

    def get_parser(self,prog_name):
        parser = super(DaemonCommand,self).get_parser(prog_name)
        subparser = parser.add_subparsers(title='subcommands',help='coordinator subcommands: start, stop, restart',dest='service_state')
        subparser.required=True
        subparser.add_parser('start',help='Start the '+self.service_name+' service')
        subparser.add_parser('stop',help='Stop the '+self.service_name+' service')
        subparser.add_parser('restart',help='Stop the '+self.service_name+' service')
        return parser

    def take_action(self, parsed_args):
        subparser_name=vars(parsed_args)['service_state']
        self.log.debug('working on service: '+self.service_name)
        self.log.debug('subparser: %s',subparser_name)
        start_cmd='flock -n /tmp/arch3_'+self.service_name+'.pid ' +self.service_name+' --config /home/ubuntu/arch3/config/masterConfig.ini --endless'
        stop_cmd='pkill -f '+self.service_name
        if subparser_name=='start':
            self._do_start(start_cmd)
        elif subparser_name=='stop':
            self._do_stop(stop_cmd)
        elif subparser_name=='restart':
            self._do_stop(start_cmd)
            self._do_start(stop_cmd)

###

class Coordinator(DaemonCommand):
    "The Coordinator will process existing job orders into requests for VMs and jobs that will be picked up by running VMs."
    log = logging.getLogger(__name__)
    def __init__(self,Coordinator,args):
        self.service_name='Coordinator'

###

class Provisioner(DaemonCommand):
    "The Provisioner will launcher worker VMs as needed based on the workflow orders sent to the system."
    log = logging.getLogger(__name__)
    def __init__(self,Provisioner,args):
        self.service_name='Provisioner'

###

class Generator(Command):
    "This Generator will generate new job orders."
    log = logging.getLogger(__name__)
    def get_parser(self,prog_name):
       parser = super(Generator,self).get_parser(prog_name)
       parser.add_argument('--workflow',dest='workflow_name',help='The name of the workflow for which you would like to generate jobs.',required=True)
       return parser

    def take_action(self, parsed_args):
        workflow_name=vars(parsed_args)['workflow_name']
        self.log.debug('workflow_name: %s',workflow_name)
        if not (workflow_name in WorkflowLister.get_workflow_names()):
            print('Oh, I\'m SO sorry, but '+workflow_name+' is not the name of an available workflow.\nPlease use the command \'workflows list\' to see the list of currently available workflows.')
        else:
            workflow_details = WorkflowLister.get_workflow_details(workflow_name)
            generator_cmd = 'Generator --workflow-name '+workflow_name+' --workflow-version '+workflow_details['http_workflow']['version']+' --workflow-path '+'/workflows/'+workflow_details['full_name']+' --ini-dir '+'/home/ubuntu/ini-dir --config /home/ubuntu/arch3/config/masterConfig.ini'
            self.log.debug(generator_cmd)
            # Before generating the job, we have to update params.json with the workflow/container info about the requested workflow.
            paramsData=''
            with open('/home/ubuntu/params.json','r') as params_file:
                paramsData = json.load(params_file)
                if 'http_workflow' in workflow_details:
                    paramsData['http_workflows'] = workflow_details['http_workflow']
                if 's3_workflows' in workflow_details:
                    paramsData['s3_workflows'] = workflow_details['s3_workflows']
                if 'containers' in workflow_details:
                    paramsData['containers'] = workflow_details['containers']
                if 's3_containers' in workflow_details:
                    paramsData['s3_containers'] = workflow_details['s3_containers']
                if 'http_containers' in workflow_details:
                    paramsData['http_containers'] = workflow_details['http_containers']

                paramsData['lvm_device_whitelist'] = workflow_details['lvm_devices']
                paramsData['workflow_name'] = workflow_name

            # Now write the params.json file.
            with open('/home/ubuntu/params.json','w+') as params_file:
                params_file.write(str(json.dumps(paramsData,sort_keys=True, indent=4) ))

            # Update the youxia config file with the correct AMI and instance-type
            config = configparser.ConfigParser()
            config.read('/home/ubuntu/.youxia/config')
            config['deployer']['instance_type']=workflow_details['instance-type']
            config['deployer']['ami_image']=workflow_details['ami_id']
            with open('/home/ubuntu/.youxia/config','r+') as youxia_configfile:
                config.write(youxia_configfile,space_around_delimiters=True)

            subprocess.check_call(generator_cmd.split(' '))

###

class Reports(Command):
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
        cmd_str=''
        if subcmd!='help':
            # TODO: The path to the config file should probably be configurable, or at least in a more standard location than /home/ubuntu/...
            cmd_str='java -cp reporting.jar info.pancancer.arch3.reportcli.ReportCLI --config /home/ubuntu/arch3/config/masterConfig.ini '+subcmd
        elif subcmd=='help':
            cmd_str='java -cp reporting.jar info.pancancer.arch3.reportcli.ReportCLI --config /home/ubuntu/arch3/config/masterConfig.ini'
        subprocess.call(cmd_str.split(' '))

###

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
