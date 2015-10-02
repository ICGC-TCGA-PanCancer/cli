import cliff.command
import subprocess
import logging

class Status(cliff.command.Command):
    "This will return status information about the launcher."
    log = logging.getLogger(__name__)

    def _get_job_results(self, job_id, results_type, out_path):
        "Gets the stdout/stderr for a job and writes it to a file."
        cmd = 'psql -U queue_user queue_status -c'
        sql = 'select '+results_type+' from job where job_id = '+job_id;
        cmd = cmd.split(' ')
        cmd.append(sql)
        file_name = out_path+'job_'+job_id+'.'+results_type
        cmd.append('-o')
        cmd.append(file_name)
        self.log.debug(cmd)
        subprocess.call(cmd)
        self.log.info('Job results ('+results_type+') have been written to '+file_name)

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
        job_results_parser = subparser.add_parser('job_results', help='Writes the stdout or stderr for a given job id to a file.')
        job_results_parser.add_argument('--type',help='Can be stderr or stdout', required=True, dest='results_type', choices=['stderr','stdout'])
        job_results_parser.add_argument('--job_id',help='The ID of the job', required=True, dest='job_id')
        job_results_parser.add_argument('--out_path',help='The path to the directory where you want the results file to be written to.', required=False,dest='out_path', default='/home/ubuntu/arch3/')
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
            sql='select status, job_id, job_uuid, workflow, create_timestamp, update_timestamp from job order by job_id asc;'
            self._do_sql_status(sql)
        elif subcmd == 'services':
            self._do_service_checks()
        elif subcmd == 'job_results':
            job_id = vars(parsed_args)['job_id']
            if job_id is None or job_id.strip() == '':
                self.log.info('You must specify a job_id.')
            else:
                results_type = vars(parsed_args)['results_type']
                out_path = vars(parsed_args)['out_path']
                self._get_job_results(job_id, results_type, out_path)
        else:
            self.get_parser('Status').print_help()
