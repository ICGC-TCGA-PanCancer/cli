import logging
import cliff.command
import workflowlister
import shutil
import urllib.request
import os
import datetime

class Workflows(cliff.command.Command):
    "This command  can help you configure and select workflows."
    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(Workflows, self).get_parser(prog_name)
        # parser.add_mutually_exclusive_group()
        #workflows_subparser = parser.add_subparsers(title='subcommands', help='workflows subcommands: list and config', dest='subparser_name')
        #workflows_subparser.add_parser('list', help='Get a list of workflows')
        #config_parser = workflows_subparser.add_parser('config', help='Generate a default config file for a specific workflow')
        #config_parser.add_argument('--workflow', dest='workflow_name', help='Name of workflow to configure')
        parser.add_argument('--num-INI', dest='num_INI', help='The number of config files to generate.',required=False,default=1)
        parser.add_argument('--no-INI-backup', dest='backup_old_INIs', help='Do NOT back up INI files to ~/ini-backups', required=False, action='store_false')
        return parser


    def _do_config(self, workflow_name, num_INIs, backup_old_INIs):
        backup_dir=os.path.expanduser('~/ini-backups')
        ini_dir=os.path.expanduser('~/ini-dir')
        self.log.debug("backup old INIS: "+str(backup_old_INIs))
        if backup_old_INIs:
            # do the backup stuff
            # First, check that there is a backup folder and create it if it does not exist.
            if os.path.exists(backup_dir)==False:
                os.mkdir(backup_dir)

            # Move the files to backup_dir
            for ini_file in os.listdir(ini_dir):
                if ini_file != 'backup':
                    self.log.info('backing up file: '+ini_file)
                    shutil.move(ini_dir+'/'+ini_file,backup_dir+'/'+ini_file)


        for i in range(0, num_INIs):
            datestr = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            # INI files will have unique names based on datetime and index in loop
            ini_file_name='~/ini-dir/' + workflow_name + '_' + datestr + '_' + str(i) + '.ini'
            self.log.info('Generating INI file: '+ini_file_name)
            ini_file_path = os.path.expanduser(ini_file_name)
            workflow_details = workflowlister.WorkflowLister.get_workflow_details(workflow_name)
            url = workflow_details['default-ini']

            with urllib.request.urlopen(url) as response, open(ini_file_path, 'wb') as ini_file:
                shutil.copyfileobj(response, ini_file)
                

    def take_action(self, parsed_args):
        subparser_name = vars(parsed_args)['subparser_name']
        self.log.debug('subparser: %s', subparser_name)
        #Workflow name must always be BWA_2.6.6 for Stouffville (L4A - Launcher For Amazon)
        workflow_name = 'BWA_2.6.6'
        num_INIs = vars(parsed_args)['num_INI']
        backup_old_INIs = vars(parsed_args)['backup_old_INIs']
        self.log.debug("backup old INIS: "+str(backup_old_INIs))
        self._do_config(workflow_name,int(num_INIs),backup_old_INIs)
