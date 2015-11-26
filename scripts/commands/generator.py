import subprocess
import logging
import cliff.command
import configparser
import workflowlister
import json
import os
# from commands.daemons import Provisioner
# from commands.sysconfig import SysConfig


class Generator(cliff.command.Command):
    "This Generator will generate new job orders based on the contents of ~/ini-dir. Be aware that it will also rewrite your params.json file and your ~.youxia/config file."
    log = logging.getLogger(__name__)
    def get_parser(self,prog_name):
        parser = super(Generator,self).get_parser(prog_name)
        parser.add_argument('--workflow',dest='workflow_name',help='The name of the workflow for which you would like to generate jobs.',required=True)
        parser.add_argument('--force',dest='force_generate',help='Force the generation of the jobs, even if the system detects that the job has already been generated once before.', required=False, action='store_true')
        parser.add_argument('--keep_failed',dest='keep_failed',help='Keep failed workers in the fleet. Useful for debugging workflows.', required=False, action='store_true')
        #parser.add_argument('--no_config_update',dest='no_config_update',help='Do not update any configuration files.', required=False, action='store_true')
        #parser.add_argument('--uses_gnos', dest='use_gnos',help='Indicates that your worfklow will be using GNOS repositories. --use_gnos and --use_s3 are not mutually exclusive - you could configure your workflow\'s INI file to use both GNOS and AWS S3 repositories.',required=False, default=True, choices=[True,False])
        #parser.add_argument('--uses_s3', dest='use_s3',help='Indicates that your worfklow will be using S3 repositories.  --use_gnos and --use_s3 are not mutually exclusive - you could configure your workflow\'s INI file to use both GNOS and AWS S3 repositories.',required=False, default=False, choices=[True,False])
        return parser

    def take_action(self, parsed_args):
        workflow_name=vars(parsed_args)['workflow_name']
        force_generate=vars(parsed_args)['force_generate']
        keep_failed=vars(parsed_args)['keep_failed']
        self.log.debug('workflow_name: %s',workflow_name)
        self.log.debug('all workflows: '+workflowlister.WorkflowLister.get_workflow_names())
        cloud_env = os.environ['HOST_ENV'].upper()
        
        if workflow_name in workflowlister.WorkflowLister.get_workflow_keys():

            # First thing: if the directory is empty, don't bother going any further.
            if os.listdir(path='/home/ubuntu/ini-dir') != []:
            
                sysconfig_cmd = 'pancancer sysconfig'
                return_code = subprocess.call(sysconfig_cmd.split(' '))
                if return_code != 0:
                    self.log.warn('Attempt to (re)configure system may have encountered an error...')
    
    
                master_config_path = os.path.expanduser('~/arch3/config/masterConfig.ini')
                self.log.debug('setting check_previous_job_hash to false in '+master_config_path)
                master_config = configparser.ConfigParser()
                master_config.optionxform = str
                # We have to update the master config file so that the generator process will allow duplicates.
                master_config.read(master_config_path)
     
                # if --force then do NOT check previous hash
                master_config['generator']['check_previous_job_hash']=str(not force_generate).lower()
                # keep_failed==true -> reap_failed_workers=false
                master_config['provision']['reap_failed_workers']=str(not keep_failed).lower()
    
                with open(master_config_path,'w') as master_config_file:
                    master_config.write(master_config_file,space_around_delimiters=True)
    
                workflow_details = workflowlister.WorkflowLister.get_workflow_details(workflow_name)
                
                if cloud_env == 'AWS' :
                    cloud_specific_details = workflow_details['cloud-specific-details']['aws']
                elif cloud_env == 'OPENSTACK' : 
                    cloud_specific_details = workflow_details['cloud-specific-details']['openstack']
                elif cloud_env == 'AZURE' : 
                    cloud_specific_details = workflow_details['cloud-specific-details']['azure']
                else:
                    self.log.error("Unrecognized cloud environment: "+cloud_env)

                workflow_version = ''            
                if 'http_workflow' in workflow_details:
                    workflow_version = workflow_details['http_workflow']['version']
                else:
                    workflow_version = workflow_details['s3_workflow']['version']
                
                generator_cmd = 'Generator --workflow-name '+workflow_name+' --workflow-version '+workflow_version+' --workflow-path '+'/workflows/'+workflow_details['full_name']+' --ini-dir '+'/home/ubuntu/ini-dir --config /home/ubuntu/arch3/config/masterConfig.ini'
                self.log.debug('generator command will be: '+generator_cmd)
                # Before generating the job, we have to update params.json with the workflow/container info about the requested workflow.
                paramsData=''
                with open('/home/ubuntu/params.json','r') as params_file:
                    paramsData = json.load(params_file)
                    if 'http_workflow' in workflow_details:
                        paramsData['http_workflows'] = {}
                        paramsData['http_workflows'][workflow_name] = workflow_details['http_workflow']
                        paramsData['http_workflows'][workflow_name]['name'] = workflow_details['full_name']
                    if 's3_workflow' in workflow_details:
                        paramsData['s3_workflows'] = {}
                        paramsData['s3_workflows'][workflow_name] = workflow_details['s3_workflows']
                        paramsData['s3_workflows'][workflow_name]['name'] = workflow_details['full_name']
                    if 'containers' in workflow_details:
                        paramsData['containers'] = workflow_details['containers']
                    if 's3_containers' in workflow_details:
                        paramsData['s3_containers'] = workflow_details['s3_containers']
                    if 'http_containers' in workflow_details:
                        paramsData['http_containers'] = workflow_details['http_containers']
                    
                    paramsData['lvm_device_whitelist']=cloud_specific_details['lvm_devices']
                    
                    if paramsData['lvm_device_whitelist'] == "" or paramsData['lvm_device_whitelist'].strip() == "":
                        paramsData['single_node_lvm'] = "false"
                    else:
                        paramsData['single_node_lvm'] = "true"
    
                    # if --force then do NOT check previous hash
                    #paramsData['generator']['check_previous_job_hash']=str(not force_generate)
                    # keep_failed==true -> reap_failed_workers=false
                    #paramsData['provision']['reap_failed_workers']=str(not keep_failed)
                    #
                    paramsData['workflow_name'] = workflow_name
    
                # Now write the params.json file.
                with open('/home/ubuntu/params.json','w+') as params_file:
                    params_file.write(str(json.dumps(paramsData,sort_keys=True, indent=4) ))
    
                # Update the youxia config file with the correct AMI and instance-type
                config = configparser.ConfigParser()
                config.read('/home/ubuntu/.youxia/config')
                if cloud_env == 'AWS':
                    config['deployer']['instance_type']=cloud_specific_details['instance-type']
                    config['deployer']['ami_image']=cloud_specific_details['image']
                elif cloud_env == 'OPENSTACK':
                    config['deployer_openstack']['flavor']=cloud_specific_details['instance-type']
                    config['deployer_openstack']['image_id']=cloud_specific_details['image']
                elif cloud_env == 'AZURE':
                    config['deployer_azure']['flavor']=cloud_specific_details['instance-type']
                    config['deployer_azure']['image_id']=cloud_specific_details['image']
                    
                with open('/home/ubuntu/.youxia/config','w') as youxia_configfile:
                    config.write(youxia_configfile,space_around_delimiters=True)
    
               
                provisioner_cmd = 'pancancer provisioner restart'
                return_code = subprocess.call(provisioner_cmd.split(' '))
                if return_code != 0:
                    self.log.warn('Attempt to restart the provisioner may have encountered an error...')
    
                #sysconfig = SysConfig(SysConfig)
                #parsed_args = sysconfig.get_parser('SysConfig').parse_args('')
                #sysconfig.run()
                #provisioner = Provisioner()
                #provisioner.run(self, provisioner_cmd.split(' '))
                
                return_code = subprocess.call(generator_cmd.split(' '))
                if return_code != 0:
                    self.log.warn('Attempt to generate jobs may have encountered an error...')
                else:
                    self.log.info('Job requests have been generated for the '+workflow_name+' using the INIs in ~/ini-dir')
            else:
                self.log.info('/home/ubuntu/ini-dir is empty. Place your INI files here before attempting to run the generator.')
        else:
            self.log.info(workflow_name+' is not the name of an available workflow.\nPlease use the command \'workflows list\' to see the list of currently available workflows.')   
            
