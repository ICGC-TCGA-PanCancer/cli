import os
import subprocess
import logging
import cliff.app
import cliff.commandmanager
import cliff.command
import time
import psutil

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
