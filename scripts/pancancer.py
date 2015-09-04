#! /usr/bin/python3
import psutil
import json
import configparser
import time
import sys
import os
import subprocess
import logging
import cliff.app
import cliff.commandmanager
import cliff.command
import process_config
import urllib.request
import shutil
import workflowlister
from commands.workflows import Workflows
from commands.sysconfig import SysConfig
###

class DaemonCommand(cliff.command.Command):
    "Parent class for commands that start/stop daemons"
    service_name=''
    log = logging.getLogger(__name__)

    def _do_start(self,start_cmd):
        "Start a process, using flock to ensure that it can't be started multiple times."
        self.log.debug (start_cmd)
        pid_file_path='/tmp/arch3_'+self.service_name+'.pid'
        # set start_new_session=True so that we can kill flock and all it's child processes by killing the process group whose pgid is the same as the flock pid.
        # We don't want to use subprocess.call() or check_call() here because those will wait for the command to complete. Since the child process will run in "endless" mode,
        # we really don't want *this* script to run endlessly - we want to start the child and let it keep running in the background.
        p = subprocess.Popen(start_cmd.split(' '),start_new_session=True)
        # Wait a moment... if we get ANY response, it means that the process did not start, probably because it's already been started.
        time.sleep(2)
        p.poll()

        if p.returncode==1:
            self.log.info('The '+self.service_name+' process might already be running.')
        else:
            self.log.debug('pid: '+str(p.pid))
            self.log.info('The service has been started, check the log files for more detail.')
            # ONLY if the service was started new (and not already running) write a pid file so we will know which processes to kill later.
            with open(pid_file_path,'w') as pidfile:
                pidfile.write(str(p.pid))


    def _do_stop(self,stop_cmd):
        "Stop a process."
        pid = ''
        # Read the pid from the file.
        pid_file_path='/tmp/arch3_'+self.service_name+'.pid'
        if os.path.isfile(pid_file_path):
            with open(pid_file_path,'r') as pidfile:
                pid = pidfile.readline()

            stop_cmd += pid
            self.log.debug (stop_cmd)

            self.log.debug('pid: '+pid)

            if psutil.pid_exists(int(pid)):
                returncode = subprocess.call(stop_cmd.split(' '))
                if returncode == 0:
                    self.log.info ('The '+self.service_name+' process has been stopped.')
                    os.remove(pid_file_path)
            else:
                self.log.info('The '+self.service_name+' process with PID '+pid+' does not appear to be running.')
        else:
            self.log.info('The '+self.service_name+' process does not appear to be running.')

    def get_parser(self,prog_name):
        parser = super(DaemonCommand,self).get_parser(prog_name)
        subparser = parser.add_subparsers(title='subcommands',help='coordinator subcommands: start, stop, restart',dest='service_state')
        subparser.required=True
        subparser.add_parser('start',help='Start the '+self.service_name+' service')
        subparser.add_parser('stop',help='Stop the '+self.service_name+' service')
        subparser.add_parser('restart',help='Stop and then start the '+self.service_name+' service')
        return parser

    def take_action(self, parsed_args):
        subparser_name=vars(parsed_args)['service_state']
        self.log.debug('working on service: '+self.service_name)
        self.log.debug('subparser: %s',subparser_name)
        # Use flock to ensure that multiple instances of the "service" cannot run at the same time.
        start_cmd='flock -n /tmp/arch3_'+self.service_name+'.lock ' +self.service_name+' --config /home/ubuntu/arch3/config/masterConfig.ini --endless'
        # Negate the PID of the process to kill the process group.
        stop_cmd='kill -KILL -'
        if subparser_name=='start':
            self._do_start(start_cmd)
        elif subparser_name=='stop':
            self._do_stop(stop_cmd)
        elif subparser_name=='restart':
            self._do_stop(stop_cmd)
            self._do_start(start_cmd)

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

class Generator(cliff.command.Command):
    "This Generator will generate new job orders."
    log = logging.getLogger(__name__)
    def get_parser(self,prog_name):
       parser = super(Generator,self).get_parser(prog_name)
       parser.add_argument('--workflow',dest='workflow_name',help='The name of the workflow for which you would like to generate jobs.',required=True)
       return parser

    def take_action(self, parsed_args):
        workflow_name=vars(parsed_args)['workflow_name']
        self.log.debug('workflow_name: %s',workflow_name)
        if not (workflow_name in workflowlister.WorkflowLister.get_workflow_names()):
            self.log.info('Oh, I\'m SO sorry, but '+workflow_name+' is not the name of an available workflow.\nPlease use the command \'workflows list\' to see the list of currently available workflows.')
        else:
            workflow_details = workflowlister.WorkflowLister.get_workflow_details(workflow_name)
            generator_cmd = 'Generator --workflow-name '+workflow_name+' --workflow-version '+workflow_details['http_workflow']['version']+' --workflow-path '+'/workflows/'+workflow_details['full_name']+' --ini-dir '+'/home/ubuntu/ini-dir --config /home/ubuntu/arch3/config/masterConfig.ini'
            self.log.debug(generator_cmd)
            # Before generating the job, we have to update params.json with the workflow/container info about the requested workflow.
            paramsData=''
            with open('/home/ubuntu/params.json','r') as params_file:
                paramsData = json.load(params_file)
                if 'http_workflow' in workflow_details:
                    paramsData['http_workflows'] = {}
                    paramsData['http_workflows'][workflow_name] = workflow_details['http_workflow']
                    paramsData['http_workflows'][workflow_name]['name'] = workflow_details['full_name']
                if 's3_workflows' in workflow_details:
                    paramsData['s3_workflows'] = {}
                    paramsData['s3_workflows'][workflow_name] = workflow_details['s3_workflows']
                    paramsData['s3_workflows'][workflow_name]['name'] = workflow_details['full_name']
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
            with open('/home/ubuntu/.youxia/config','w') as youxia_configfile:
                config.write(youxia_configfile,space_around_delimiters=True)

            subprocess.call(generator_cmd.split(' '))
            self.log.info('Job requests have been generated for the '+workflow_name+' using the INIs in ~/ini-dir')
            #TODO: Show the job requests in the queue??

###

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

###

class Status(cliff.command.Command):
    "This will return status information about the launcher."
    log = logging.getLogger(__name__)

    def _do_sql_status(self, sql):
        "Executes a command against the postgres database"
        cmd = 'psql -U queue_user queue_status -c'
        self.log.debug(cmd)
        sql_cmd = cmd.split(' ')
        sql_cmd.append(sql)
        self.log.debug(sql_cmd)
        subprocess.call(sql_cmd)

    def _check_service_with_name(self, service_name):
        "Uses pgrep to check if a process matches the pattern 'java.*<service_name>'"
        # Use pgrep to check if the java process is running.
        cmd = 'pgrep -fla java.*'+service_name
        output=''
        try:
            output = subprocess.check_output(cmd.split(' '),universal_newlines=True)
        except subprocess.CalledProcessError as e:
            # If pgrep returns nothing, then the process is not running.
            self.log.info ('The '+service_name+' process does not appear to be running.')

        if output!='':
            # Print the message with the PID
            self.log.info ('The '+service_name+' appears to be running with PID: '+(output.split(' '))[0])

    def _do_service_checks(self):
        "Check the Coordinator and Provisioner."
        self._check_service_with_name('Coordinator')
        self._check_service_with_name('Provisioner')

    def get_parser(self,prog_name):
        parser = super(Status,self).get_parser(prog_name)
        subparser = parser.add_subparsers(title='subcommands',help='status subcommands: queues, jobs, job_status',dest='status_subcmd')
        subparser.required=True
        subparser.add_parser('queues',help='Prints some basic status information on the RabbitMQ message queues.')
        subparser.add_parser('job_status',help='Prints counts of jobs by status.')
        subparser.add_parser('jobs',help='Prints data from the job table (omits standard error and standard out).')
        subparser.add_parser('services',help='Prints the status of the coordinator and provisioner')
        return parser

    def take_action(self,parsed_args):
        subcmd = vars(parsed_args)['status_subcmd']
        cmd=''
        sql=''
        if subcmd == 'queues':
            # QueueStatus has too much output - Pancancer CLI users will ONLY want to see the queues, so just call rabbitmqadmin directly.
            cmd = 'rabbitmqadmin list queues vhost name node messages'
            subprocess.call(cmd.split(' '))
        elif subcmd == 'job_status':
            sql='select count(*), status from job group by status;'
            self._do_sql_status(sql)
        elif subcmd == 'jobs':
            sql='select status, job_id, job_uuid, workflow, create_timestamp, update_timestamp from job;'
            self._do_sql_status(sql)
        elif subcmd == 'services':
            self._do_service_checks()

###

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
