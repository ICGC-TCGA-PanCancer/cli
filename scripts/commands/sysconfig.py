import os
import decimal
import logging
import cliff.command
import configparser
import json
import process_config
import shutil

class SysConfig(cliff.command.Command):
    "This command will setup the pancancer system configuration."
    log = logging.getLogger(__name__)

    def get_parser(self,prog_name):
        parser = super(SysConfig,self).get_parser(prog_name)
        parser.add_argument('--config',dest='config_path',help='The path to your pancancer config file, if it already exists.',required=False)
        parser.add_argument("--force",dest='force_config',required=False, action='store_true')
        # Need to have a "force" option
        return parser

    def _get_config_value(self,prev_user_value,message, alt_condition=None, allow_blank=False, force_once=False):
        "This function will prompt the use with a question and will keep prompting them until a valid value is given."
        user_value=''
        keep_asking = True
        
        if force_once:
            keep_asking = True
        else:
            keep_asking = (alt_condition == None and user_value.strip() == '' and not allow_blank) or (alt_condition != None and not alt_condition(user_value) )
        
        while keep_asking:
        #while (alt_condition == None and user_value.strip() == '') or (alt_condition != None and alt_condition(user_value) and not force_once):
            prev_value_prompt = ''
            if prev_user_value != '':
                prev_value_prompt = '[Press \"ENTER\" to use the previous value: '+str(prev_user_value)+', or type a new value if you want]'
            user_value = input(message + ' ' + prev_value_prompt+'? ')
            user_value = str(user_value).strip() or str(prev_user_value).strip()
            if user_value=='' and not allow_blank:
                self.log.info('This value cannot be blank.')
            elif user_value=='' and allow_blank:
                return user_value
            keep_asking = ((alt_condition == None and user_value.strip() == '' and not allow_blank) or (alt_condition != None and not alt_condition(user_value)))

        return user_value

    def _ask_Azure_questions(self,force_config, config_data, H):

        az_subscription_id = self._ask_question_or_set_to_prev(force_config,  'AZURE_SUBSCRIPTION', H, 'az_subscription_id', config_data, 'What is your Azure subscription ID')
        az_storage_account = self._ask_question_or_set_to_prev(force_config,  'AZURE_STORAGE_ACCOUNT', H, 'az_storage_account', config_data, 'What is your Azure storage account ID')
        az_storage_account_key = self._ask_question_or_set_to_prev(force_config,  'AZURE_STORAGE_ACCOUNT_KEY', H, 'az_storage_account_key', config_data, 'What is your Azure storage account key')
        az_ad_user = self._ask_question_or_set_to_prev(force_config,  'AZURE_AD_USER', H, 'az_ad_user', config_data, 'What is your Azure Active Directory username')
        az_ad_password = self._ask_question_or_set_to_prev(force_config,  'AZURE_AD_PASSWD', H, 'az_ad_password', config_data, 'What is your Azure Active Directory password')
        az_ad_tenant_id = self._ask_question_or_set_to_prev(force_config,  'AZURE_AD_TENANT', H, 'az_ad_tenant_id', config_data, 'What is your Azure Active Directory tenant ID')
        az_ad_client_id = self._ask_question_or_set_to_prev(force_config,  'AZURE_AD_CLIENT', H, 'az_ad_client_id', config_data, 'What is your Azure Active Directory client ID')
        return az_subscription_id, az_storage_account, az_storage_account_key, az_ad_user, az_ad_password, az_ad_tenant_id, az_ad_client_id
    
    def _ask_question_or_set_to_prev(self,force_config, bootstrap_key, bootstrap_config, json_key, json_config, question, alt_condition=None, allow_blank=False):
        """Looks in bootstrap_config[bootstrap_key] and then in json_config[json_key] and if no value is found, the user is asked a question and the answer is returned.
        If force_config is specified, the user will always be asked the question. alt_condition is a lambda that can be used to validate the answer.
        allow_blank allows the user to not answer the question and a blank answer will be accepted (this is False by default)."""
        user_answer=''
        prev_value=''
        if json_key in json_config:
            prev_value = json_config[json_key]
        elif bootstrap_key in bootstrap_config:
            prev_value = bootstrap_config[bootstrap_key]
        
        if force_config:
            user_answer = self._get_config_value(prev_value, question, alt_condition, allow_blank, force_config)
        else:
            user_answer = prev_value
        
        return user_answer

    
    def _ask_OpenStack_questions(self,force_config, config_data, H):
        os_username = self._ask_question_or_set_to_prev(force_config,'OS_USERNAME', H, 'os_username', config_data, 'What is your OpenStack username (formatted as: username:tenant)')
        os_password = self._ask_question_or_set_to_prev(force_config,'OS_PASSWORD', H, 'os_password', config_data, 'What is your OpenStack password')
        os_endpoint = self._ask_question_or_set_to_prev(force_config,'OS_ENDPOINT', H, 'os_endpoint', config_data, 'What is your OpenStack endpoint')
        os_region = self._ask_question_or_set_to_prev(force_config,'OS_REGION', H, 'os_region', config_data, 'What is your OpenStack region')
        os_zone = self._ask_question_or_set_to_prev(force_config,'OS_ZONE', H, 'os_zone', config_data, 'What is your OpenStack zone',allow_blank=True)
        os_network_id = self._ask_question_or_set_to_prev(force_config,'OS_NETWORK_ID', H, 'os_network_id', config_data, 'What is your OpenStack network ID',allow_blank=True)
        security_group = self._ask_for_security_group(force_config, config_data, H)
        return os_username, os_password, security_group, os_endpoint, os_region, os_zone, os_network_id

    def _ask_for_AWS_Keys(self, force_config, aws_config_path, aws_key, aws_secret_key, prev_aws_key, prev_aws_secret_key, aws_config):
        # AWS Key and Secret Key should only be asked for if for some reason they are NOT available (they *should* be, but stuff happens...)
        if force_config or prev_aws_key.strip() == '' or prev_aws_secret_key.strip() == '':
            aws_key = self._get_config_value( prev_aws_key, 'What is your AWS Key')
            aws_secret_key = self._get_config_value( prev_aws_secret_key, 'What is your AWS Secret Key') # If the AWS keys weren't available, ~/.aws/config is either not present or missing values, so re-write it.
            aws_config = configparser.ConfigParser()
            aws_config['default'] = {'aws_access_key_id':aws_key, 'aws_secret_access_key':aws_secret_key}
            with open(aws_config_path, 'w') as aws_configfile:
                aws_config.write(aws_configfile, space_around_delimiters=False)
        else:
            aws_key = prev_aws_key
            aws_secret_key = prev_aws_secret_key
        return aws_secret_key, aws_key


    def _ask_for_security_group(self, force_config, config_data, H):
        prev_security_group=''
        security_group=''
        if 'security_group' in config_data:
            prev_security_group = config_data['security_group']
        elif 'SECURITY_GROUP' in H:
            prev_security_group = H['SECURITY_GROUP']
        if prev_security_group.strip() == '':
            prev_security_group = 'default'
        if force_config:
            security_group = self._get_config_value( prev_security_group, 'What AWS Security Group should the VMs belong to')
        else:
            security_group = prev_security_group
        return security_group


    def _check_for_positive_decimal(self,x):
        "This checks that the input is a positive decimal number"
        try:
            d = decimal.Decimal(x)
            if d>0:
                return True
            else:
                return False
        except:
            return False

    def _ask_for_spot_price(self, force_config, config_data):
        spot_price=''
        prev_spot_price=''
        if 'spot_price' in config_data:
            prev_spot_price = config_data['spot_price']
        if prev_spot_price.strip() == '':
            prev_spot_price = '0.001' # User will only be asked about spot price if they FORCE a sysconfig. Otherwise, Keep It Simple and stick with 0.001 which triggers on-demand instances.
        if force_config:
            spot_price = self._get_config_value( prev_spot_price, 'What spot price would you like to set', alt_condition=lambda x: self._check_for_positive_decimal(x))
        else:
            spot_price = prev_spot_price
        return spot_price


    def _ask_AWS_questions(self, force_config, config_data, aws_config_path, aws_key, aws_secret_key, prev_aws_key, prev_aws_secret_key, aws_config,  H):
        # AWS-only questions.
        security_group = self._ask_for_security_group(force_config, config_data, H)
        spot_price = self._ask_for_spot_price(force_config, config_data)
        aws_secret_key, aws_key = self._ask_for_AWS_Keys(force_config, aws_config_path, aws_key, aws_secret_key, prev_aws_key, prev_aws_secret_key, aws_config)
        return aws_secret_key, aws_key, security_group, spot_price

    def take_action(self, parsed_args):
        self.log.info('Setting up pancancer config files.')
        config_path=vars(parsed_args)['config_path']
        force_config=vars(parsed_args)['force_config']
        self.log.debug('force_config:' + str(force_config))
        if config_path != None:
            # if the user specifies a path to an existing file, they can use that instead of the interactive process.
            self.log.debug('path to config file: ' + config_path)
            process_config.main(config_path)
        else:
            # if the user did not specify a config, ask them questions and then WRITE/update a config!
            pancancer_config_path=os.path.expanduser('~/.pancancer/simple_pancancer_config.json')
            config_data={}
            if os.path.isfile(pancancer_config_path):
                #Read the pancancer_config.json file if it exists
                with open(pancancer_config_path,'r') as pancancer_config_file:
                    config_data = json.load(pancancer_config_file)

            pancancer_config={}


            aws_config_path = os.path.expanduser('~/.aws/config')
            aws_key=''
            aws_secret_key=''
            prev_aws_key=''
            prev_aws_secret_key=''
            if os.path.isfile(aws_config_path):
                # read the file, get the values
                aws_config = configparser.ConfigParser()
                aws_config.read(aws_config_path)
                prev_aws_key = aws_config['default']['aws_access_key_id']
                prev_aws_secret_key = aws_config['default']['aws_secret_access_key']


            # also: get fleet name, PEM key path, and key name from env. If everything went smoothly, these values should be in
            # /opt/from_host/config/pancancer.config
            # Actually, fleet name should be coming from process_config.py, not here, since it's passed into the container as an environment variable.
            # If it's NOT there, we should askt he user for these values.
            bootstrap_config_path='/opt/from_host/config/pancancer.config'
            pem_key_path=''
            prev_pem_key_path=''
            key_name=''
            spot_price = ''
            prev_key_name=''
            security_group = ''
            #prev_fleet_size = ''
            fleet_size=''
            workflow_listing_url=''
            cloud_env=''
            bootstrap_config_exists = False
            if os.path.isfile(bootstrap_config_path):
                self.log.debug('bootstrap config file exists at: '+bootstrap_config_path)
                bootstrap_config_exists = True
                # load simple config file (it should have been generated by install_bootrap) and get values.
                H = dict(line.strip().split('=',maxsplit=1) for line in open(bootstrap_config_path))
                
                #Now, need to strip the leading and trailing double-quotes
                for k in H:
                    H[k] = H[k].lstrip('"').rstrip('"')
                
                cloud_env = self._ask_question_or_set_to_prev(force_config, 'CLOUD_ENV', H, 'cloud_env', config_data, 'What Cloud Environment (must be one of: AWS, Azure, OpenStack) are you working in', alt_condition = lambda x: x.strip() =='AWS' or x.strip() =='Azure' or x.strip() =='OpenStack')
                
                if 'PEM_PATH' in H:
                    prev_pem_key_path = H['PEM_PATH']
                if 'KEY_NAME' in H:
                    prev_key_name = H['KEY_NAME']

                # pull the workflow URL from the config
                if 'WORKFLOW_LISTING_URL' in H:
                    workflow_listing_url = H['WORKFLOW_LISTING_URL']

                fleet_size = self._ask_question_or_set_to_prev(force_config, 'FLEET_SIZE', H, 'max_fleet_size', config_data, 'How many VMs do you want in your fleet', alt_condition = lambda x: x.strip()!='' and x.isdigit() and int(x)>0)

                if prev_pem_key_path.strip() != '':
                    pem_key_path = prev_pem_key_path
                if prev_key_name.strip() != '':
                    key_name = prev_key_name
            
                if cloud_env.upper() == 'AWS':
                    # Ask AWS questions
                    aws_secret_key, aws_key, security_group, spot_price = self._ask_AWS_questions(force_config, config_data, aws_config_path, aws_key, aws_secret_key, prev_aws_key, prev_aws_secret_key, aws_config,  H)
                elif cloud_env.upper() == 'AZURE':
                    # Ask Azure questions
                    az_subscription_id, az_storage_account, az_storage_account_key, az_ad_user, az_ad_password, az_tenant_id, az_client_id = self._ask_Azure_questions(force_config, config_data, H)
                elif cloud_env.upper() == 'OPENSTACK':
                    # Ask OpenStack questions
                    os_username, os_password, security_group, os_endpoint, os_region, os_zone, os_network_id = self._ask_OpenStack_questions(force_config, config_data, H)
                else:
                    print('Unknown cloud environment: \''+cloud_env+'\'')
            
            else:
                self.log.debug('bootstrap config file cannot be found at: '+bootstrap_config_path+' so a new one will be written.')

            # Only ask the use about these if one or the other does not exist (indicates there might be a config value/file problem somewhere)
            if force_config or prev_pem_key_path.strip()=='' or prev_key_name.strip()=='' or not bootstrap_config_exists:
                pem_key_path = self._get_config_value( prev_pem_key_path, 'What is the path to the pem key file that your new VMs to use')
                key_name = self._get_config_value( prev_key_name, 'What is the Name of this key')
                # Now (re)write the bootstrap config file if the user forced sysconfig, OR if the key name or path were missing (because those should never be missing).
                with open(bootstrap_config_path,'w') as bootstrap_config:
                    bootstrap_config.write('PEM_PATH='+pem_key_path+'\n')
                    bootstrap_config.write('KEY_NAME='+key_name+'\n')
                    bootstrap_config.write('FLEET_NAME='+os.environ['FLEET_NAME']+'\n')
                    bootstrap_config.write('WORKFLOW_LISTING_URL='+workflow_listing_url+'\n')
                    bootstrap_config.write('SECURITY_GROUP='+security_group+'\n')
                    if cloud_env.upper() == 'AZURE':
                        bootstrap_config.write('AZURE_SUBSCRIPTION='+az_subscription_id+'\n')
                        bootstrap_config.write('AZURE_STORAGE_ACCOUNT='+az_storage_account+'\n')
                        bootstrap_config.write('AZURE_STORAGE_ACCOUNT_KEY='+az_storage_account_key+'\n')
                        bootstrap_config.write('AZURE_AD_USER='+az_ad_user+'\n')
                        bootstrap_config.write('AZURE_AD_PASSWD='+az_ad_password+'\n')
                        bootstrap_config.write('AZURE_AD_TENANT='+az_tenant_id+'\n')
                        bootstrap_config.write('AZURE_AD_CLIENT='+az_client_id+'\n')
                    elif cloud_env.upper() == 'OPENSTACK':
                        bootstrap_config.write('OS_USERNAME='+os_username+'\n')
                        bootstrap_config.write('OS_PASSWORD='+os_password+'\n')
                        bootstrap_config.write('OS_ENDPOINT='+os_endpoint+'\n')
                        bootstrap_config.write('OS_REGION='+os_region+'\n')
                        bootstrap_config.write('OS_ZONE='+os_zone+'\n')



            # Write the simple JSON config that will be used for the rest of pancancer system.
            # This JSON file will be used as the input to the template file "panancer_config.mustache".
            pancancer_config = { 'max_fleet_size':fleet_size, 'path_to_key': pem_key_path,
                                'name_of_key':key_name, 'security_group': security_group, 'cloud_env':cloud_env,
                                'workflow_listing_url':workflow_listing_url}
            if cloud_env == 'AWS':
                pancancer_config.update( { 'aws_secret_key':aws_secret_key,
                                'aws_key':aws_key,
                                'spot_price': spot_price} )
            elif cloud_env == 'Azure':
                pancancer_config.update( { 'az_subscription_id': az_subscription_id, 'az_storage_account': az_storage_account,
                                'az_storage_account_key': az_storage_account_key, 'az_ad_user': az_ad_user,
                                'az_ad_password': az_ad_password, 'az_ad_tenant_id': az_tenant_id,
                                'az_ad_client_id': az_client_id } )
            elif cloud_env == 'OpenStack':
                pancancer_config.update( {'os_username': os_username, 'os_password': os_password,
                                'os_endpoint': os_endpoint, 'os_region': os_region,
                                'os_zone': os_zone, 'os_network_id': os_network_id } )


            if not os.path.exists(os.path.expanduser('~/.pancancer')):
                os.makedirs(os.path.expanduser('~/.pancancer'))

            with open(pancancer_config_path,'w') as simple_pancancer_config:
                simple_pancancer_config.write(str(json.dumps(pancancer_config,sort_keys=True, indent=4) ))
                self.log.info('Your new pancancer system config file has been written to '+pancancer_config_path)
                self.log.info('The next time you want to run \"pancancer sysconfig\", you can use this file like this: ')
                self.log.info('pancancer sysconfig --config '+pancancer_config_path)

            if cloud_env =='AWS':
                # Copy the AWS config file to ~/.gnos, because some workflows may need it to access S3 and it's just easier to do this automatically
                # then to tell the user to do it. We don't copy to ~/.aws because currently, the ~/.gnos directory and its contents get copied to the 
                # workers and ~/.gnos on the worker will get mounted into the running seqware container. In the future, it may be possible to copy ~/.aws
                # to the workers and have the seqware container look at that as well as ~/.gnos ...
                shutil.copy2(aws_config_path,os.path.expanduser('~/.gnos/config'))

            # Now that a config is written, USE IT!!
            process_config.main(pancancer_config_path)
