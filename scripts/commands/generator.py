import subprocess
import logging
import cliff.command
import configparser
import workflowlister
import json

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
