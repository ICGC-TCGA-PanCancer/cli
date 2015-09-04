import os
import logging
import json
import cliff.app
import cliff.commandmanager
import cliff.command
import configparser
import json

class SysConfig(cliff.command.Command):
    "This command will setup the pancancer system configuration."
    log = logging.getLogger(__name__)

    def get_parser(self,prog_name):
        parser = super(SysConfig,self).get_parser(prog_name)
        sysconf_subparser = parser.add_argument('--config',dest='config_path',help='The path to your pancancer config file, if it already exists.',required=False)
        return parser

    def _get_config_value(self,user_value,prev_user_value,message, alt_condition=None):
        "This function will prompt the use with a question and will keep prompting them until a valid value is given."
        while (alt_condition == None and user_value.strip() == '') or (alt_condition != None and alt_condition(user_value)):
            prev_value_prompt = ''
            if prev_user_value != '':
                prev_value_prompt = '[Press \"ENTER\" to use the previous value: '+prev_user_value+', or type a new value if you want]'
            user_value = input(message + ' ' + prev_value_prompt+'? ')
            user_value = user_value.strip() or prev_user_value.strip()
            if user_value=='':
                self.log.info('This value cannot be blank.')

        return user_value

    def take_action(self, parsed_args):
        self.log.info('Setting up pancancer config files.')
        config_path=vars(parsed_args)['config_path']

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

            # TODO: This value could also come from bootstrap config file...
            prev_fleet_size = ''
            fleet_size=''
            if 'max_fleet_size' in config_data:
                prev_fleet_size = config_data['max_fleet_size']
            fleet_size = self._get_config_value(fleet_size, prev_fleet_size, 'How many VMs do you want in your fleet', alt_condition = lambda x: x.strip()=='' or x.isdigit() == False or int(x)<=0 )

            # TODO: This value could also come from bootstrap config file...
            prev_security_group = ''
            security_group = ''
            if 'security_group' in config_data:
                prev_security_group = config_data['security_group']
            if prev_security_group.strip() == '':
                prev_security_group = 'default'
            security_group = self._get_config_value(security_group, prev_security_group,'What AWS Security Group should the VMs belong to')

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

            # AWS Key and Secret Key should only be asked for if for some reason they are NOT available (they *should* be, but stuff happens...)
            if prev_aws_key.strip() == '' or prev_aws_secret_key.strip() == '':
                aws_key = self._get_config_value(aws_key,prev_aws_key,'What is your AWS Key')
                aws_secret_key = self._get_config_value(aws_secret_key,prev_aws_secret_key,'What is your AWS Secret Key')
                # If the AWS keys weren't available, ~/.aws/config is either not present or missing values, so re-write it.
                aws_config = configparser.ConfigParser()
                aws_config['default'] = {'aws_access_key_id':aws_key, 'aws_secret_access_key':aws_secret_key}
                with open(aws_config_path,'w') as aws_configfile:
                    aws_config.write(aws_configfile,space_around_delimiters=False)
            else:
                aws_key = prev_aws_key
                aws_secret_key = prev_aws_secret_key

            # also: get fleet name, PEM key path, and key name from env. If everything went smoothly, these values should be in
            # /opt/from_host/config/pancancer.config
            # Actually, fleet name should be coming from process_config.py, not here, since it's passed into the container as an environment variable.
            # If it's NOT there, we should askt he user for these values.
            bootstrap_config_path='/opt/from_host/config/pancancer.config'
            pem_key_path=''
            prev_pem_key_path=''
            key_name=''
            prev_key_name=''
            if os.path.isfile(bootstrap_config_path):
                self.log.debug('bootstrap config file exists at: '+bootstrap_config_path)
                # load simple config file (it should have been generated by install_bootrap) and get values.
                H = dict(line.strip().split('=') for line in open(bootstrap_config_path))
                if 'PEM_PATH' in H:
                    prev_pem_key_path = H['PEM_PATH']
                if 'KEY_NAME' in H:
                    prev_key_name = H['KEY_NAME']

                if prev_pem_key_path.strip() != '':
                    pem_key_path = prev_pem_key_path
                if prev_key_name.strip() != '':
                    key_name = prev_key_name
            else:
                self.log.debug('bootstrap config file cannot be found at: '+bootstrap_config_path+' so a new one will be written.')

            # Only ask the use about these if one or the other does not exist (indicates there might be a config value/file problem somewhere)
            if prev_pem_key_path.strip()=='' or prev_key_name.strip()=='':
                pem_key_path = self._get_config_value(pem_key_path, prev_pem_key_path, 'What is the path to the AWS pem key file that your new VMs to use')
                key_name = self._get_config_value(key_name, prev_key_name, 'What is the Name of this key in AWS')
                #Now write the bootstrap config file, but only if we had to ask the user for help filling in the details.
                with open(bootstrap_config_path,'w') as bootstrap_config:
                    bootstrap_config.write('PEM_PATH='+pem_key_path+'\n')
                    bootstrap_config.write('KEY_NAME='+key_name+'\n')
                    bootstrap_config.write('FLEET_NAME='+os.environ['FLEET_NAME']+'\n')

            # Now, write the simple JSON config that will be used for the rest of pancancer system.
            pancancer_config = { 'max_fleet_size':fleet_size, 'path_to_key': pem_key_path,
                                'name_of_key':key_name, 'aws_secret_key':aws_secret_key,
                                'security_group': security_group, 'aws_key':aws_key }

            if not os.path.exists(os.path.expanduser('~/.pancancer')):
                os.makedirs(os.path.expanduser('~/.pancancer'))

            with open(pancancer_config_path,'w') as simple_pancancer_config:
                simple_pancancer_config.write(str(json.dumps(pancancer_config,sort_keys=True, indent=4) ))
                self.log.info('Your new pancancer system config file has been written to '+pancancer_config_path)
                self.log.info('The next time you want to run \"pancancer sysconfig\", you can use this file like this: ')
                self.log.info('pancancer sysconfig --config '+pancancer_config_path)

            # Now that a config is written, USE IT!!
            process_config.main(pancancer_config_path)
