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
        workflows_subparser = parser.add_subparsers(title='subcommands', help='workflows subcommands: list and config', dest='subparser_name')
        workflows_subparser.add_parser('list', help='Get a list of workflows')
        config_parser = workflows_subparser.add_parser('config', help='Generate a default config file for a specific workflow')
        config_parser.add_argument('--workflow', dest='workflow_name', help='Name of workflow to configure') 
        config_parser.add_argument('--num-INI', dest='num_INI', help='The number of config files to generate.',required=False,default=1) 
        config_parser.add_argument('--backup-old-INIs', dest='backup_old_INIs', help='Should old INI files be moved to a backup directory?',required=False,default=True)
        return parser
    
    def _do_list(self):
        workflow_list = workflowlister.WorkflowLister.get_workflow_names()
        self.log.info ('Available workflows are:')
        self.log.info(workflow_list)

    def _do_config(self, workflow_name, num_INIs=1, backup_old_INIs=True):
        if workflow_name in workflowlister.WorkflowLister.get_workflow_names():
            backup_dir=os.path.expanduser('~/ini-backups')
            ini_dir=os.path.expanduser('~/ini-dir')
            print(backup_old_INIs)
            # TODO: Add cleanup process to move/back-up old INIs before generating new ones, unless user does not want that. Done. now test... 
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
                if workflow_name != 'HelloWorld':
                    workflow_details = workflowlister.WorkflowLister.get_workflow_details(workflow_name)
                    url = workflow_details['default-ini']
    
                    with urllib.request.urlopen(url) as response, open(ini_file_path, 'wb') as ini_file:
                        shutil.copyfileobj(response, ini_file)
                else:
                    with open(ini_file_path, 'w') as ini_file:
                        ini_file.write('greeting=Greetings_from_Panancer_CLI')
    
                #self.log.info('generating default INI in /home/ubuntu/ini-dir/' + workflow_name + '.ini for workflow ' + workflow_name)
        else:
            self.log.info ('Sorry, but ' + workflow_name + ' is not a valid workflow name. Please use the command \'workflows list\' to see a list of available workflows.')


    def take_action(self, parsed_args):
        subparser_name = vars(parsed_args)['subparser_name']
        self.log.debug('subparser: %s', subparser_name)
        if subparser_name == 'list':
            self._do_list()

        elif subparser_name == 'config':
            workflow_name = vars(parsed_args)['workflow_name']
            num_INIs = vars(parsed_args)['num_INI']
            backup_old_INIs = vars(parsed_args)['backup_old_INIs']
            print(backup_old_INIs)
            self._do_config(workflow_name,int(num_INIs),backup_old_INIs)
#             if workflow_name in workflowlister.WorkflowLister.get_workflow_names():
#                 ini_file_path = os.path.expanduser('~/ini-dir/'+workflow_name+'.ini')
#                 if workflow_name != 'HelloWorld':
#                     workflow_details = workflowlister.WorkflowLister.get_workflow_details(workflow_name)
#                     url = workflow_details['default-ini']
# 
#                     with urllib.request.urlopen(url) as response, open(ini_file_path,'wb') as ini_file:
#                         shutil.copyfileobj(response,ini_file)
#                 else:
#                     with open(ini_file_path,'w') as ini_file:
#                         ini_file.write('greeting=Greetings_from_Panancer_CLI')
# 
#                 self.log.info('generating default INI in /home/ubuntu/ini-dir/'+workflow_name+'.ini for workflow '+workflow_name)
#             else:
#                 self.log.info ('Sorry, but '+workflow_name+' is not a valid workflow name. Please use the command \'workflows list\' to see a list of available workflows.')
        else:
            self.log.info ('The available subcommands are \'list\' and \'config\'.')
