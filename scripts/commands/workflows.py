import logging
import cliff.command
import workflowlister
import shutil
import urllib.request
import os

class Workflows(cliff.command.Command):
    "This command  can help you configure and select workflows."
    log = logging.getLogger(__name__)

    def get_parser(self,prog_name):
        parser = super(Workflows,self).get_parser(prog_name)
        #parser.add_mutually_exclusive_group()
        workflows_subparser = parser.add_subparsers(title='subcommands',help='workflows subcommands: list and config',dest='subparser_name')
        workflows_subparser.add_parser('list',help='Get a list of workflows')
        workflows_subparser.add_parser('config',help='Generate a default config file for a specific workflow').add_argument('--workflow', dest='workflow_name',help='Name of workflow to configure')
        return parser

    def take_action(self, parsed_args):
        subparser_name=vars(parsed_args)['subparser_name']
        self.log.debug('subparser: %s',subparser_name)
        if subparser_name=='list':
            workflow_list = workflowlister.WorkflowLister.get_workflow_names()
            self.log.info ('Available workflows are:')
            self.log.info(workflow_list)

        elif subparser_name=='config':
            workflow_name=vars(parsed_args)['workflow_name']
            if workflow_name in workflowlister.WorkflowLister.get_workflow_names():
                ini_file_path = os.path.expanduser('~/ini-dir/'+workflow_name+'.ini')
                if workflow_name != 'HelloWorld':
                    workflow_details = workflowlister.WorkflowLister.get_workflow_details(workflow_name)
                    url = workflow_details['default-ini']

                    with urllib.request.urlopen(url) as response, open(ini_file_path,'wb') as ini_file:
                        shutil.copyfileobj(response,ini_file)
                else:
                    with open(ini_file_path,'w') as ini_file:
                        ini_file.write('greeting=Greetings_from_Panancer_CLI')

                self.log.info('generating default INI in /home/ubuntu/ini-dir/'+workflow_name+'.ini for workflow '+workflow_name)
            else:
                self.log.info ('Sorry, but '+workflow_name+' is not a valid workflow name. Please use the command \'workflows list\' to see a list of available workflows.')
        else:
            self.log.info ('The available subcommands are \'list\' and \'config\'.')
