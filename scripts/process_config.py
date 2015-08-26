import json
import pystache
import os
import shutil

def makeConfigString(k,v):
    return k+'='+v+'\n'

def processYouxiaSettings(d):
    outstr=''
    outstr+='[youxia]\n'
    aws_str=''
    openstack_str=''
    aws_deployer_str=''
    for k,v in d.items():
        if not (isinstance(v,dict)):
            outstr+=makeConfigString(k,v)
        else:
            # if k=='aws':
            #     # Process AWS-specific variables in the AWS heading
            #     # awsStr+='\n[aws]\n'
            #     aws_settings=d['aws']
            #     for k1,v1 in aws_settings.items():
            #         aws_str+=makeConfigString(k1,str(v1))
            if k=='openstack':
                # Process AWS-specific variables in the AWS heading
                openstack_str+='\n[openstack]\n'
                openstack_settings=d['openstack']
                for k1,v1 in openstack_settings.items():
                    #print(k1+'='+str(v1))
                    openstack_str+=makeConfigString(k1,str(v1))
            elif k=='deployer':
                # Process AWS-specific variables in the AWS heading
                aws_deployer_str+='\n[deployer]\n'
                aws_deployer_settings=d['deployer']
                for k1,v1 in aws_deployer_settings.items():
                    #print(k1+'='+str(v1))
                    aws_deployer_str+=makeConfigString(k1,str(v1))

    outstr+=aws_str
    outstr+=aws_deployer_str
    outstr+=openstack_str
    return outstr

def processParams(d):
    return str(json.dumps(d,sort_keys=True, indent=4) )

def processConsonanceSettings(d):
    outstr=''
    for k,v in d.items():
        outstr+='\n['+k+']\n'
        for k1,v1 in v.items():
            outstr+=makeConfigString(k1,str(v1))
    return outstr


#######################
# Main body of script #
#######################

def main(config_path):
    #TODO: This should take a path to any config file.
    with open(config_path) as simple_config_file:
        simple_config=json.load(simple_config_file)
        # These are not something the user will put into their simple config,
        # so we need to get it from the environment (it will have been set by the start_services_in_container.sh script)
        simple_config['sensu_server_ip_address'] = os.environ['SENSU_SERVER_IP_ADDRESS']
        simple_config['queue_host'] = os.environ['SENSU_SERVER_IP_ADDRESS']

    config_path = os.path.dirname(__file__)
    with open(config_path +'/pancancer_config.mustache') as mustache_template_file:
        mustache_template=mustache_template_file.read()

    renderer=pystache.Renderer()
    parsed=pystache.parse(mustache_template)
    rendered_str=renderer.render(parsed,(simple_config))
    data=json.loads(rendered_str)

    # The master config file should be written to ~/.pancancer/pancancer_config.json
    with open(config_path + '/pancancer_config.json','w') as master_config_file:
        master_config_file.write(str(json.dumps(data,sort_keys=True, indent=4) ))

    # Youxia config should go to ~/.youxia/config
    with open(config_path + '/youxia_config','w') as youxia_file:
        youxia_settings=data['youxia']
        youxia_str=processYouxiaSettings(youxia_settings)
        youxia_file.write(youxia_str)

    # params.json should go to ~/params.json
    with open(config_path + '/params.json','w') as params_json_file:
        params_settings=data['params']
        params_str=processParams(params_settings)
        params_json_file.write(params_str)

    # masterConfig should go to ~/arch3/config/masterConfig.ini
    with open(config_path + '/masterConfig.ini','w') as consonance_file:
        consonance_settings=data['consonance']
        consonance_str=processConsonanceSettings(consonance_settings)
        consonance_file.write(consonance_str)

    shutil.copy2(config_path + '/youxia_config','/home/ubuntu/.youxia/config')
    shutil.copy2(config_path + '/masterConfig.ini','/home/ubuntu/arch3/config/masterConfig.ini')
    shutil.copy2(config_path + '/params.json','/home/ubuntu/params.json')
