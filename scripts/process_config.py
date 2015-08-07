import json
import pystache

def makeConfigString(k,v):
    return k+'='+v+'\n'

def processYouxiaSettings(d):
    outstr=''
    outstr+='[youxia]\n'
    awsStr=''
    openstackStr=''
    for k,v in d.items():
        if not (isinstance(v,dict)):
            outstr+=makeConfigString(k,v)
        else:
            if k=='aws':
                # Process AWS-specific variables in the AWS heading
                awsStr+='\n[aws]\n'
                aws_settings=d['aws']
                for k1,v1 in aws_settings.items():
                    awsStr+=makeConfigString(k1,str(v1))
            elif k=='openstack':
                # Process AWS-specific variables in the AWS heading
                openstackStr+='\n[openstack]\n'
                openstack_settings=d['openstack']
                for k1,v1 in openstack_settings.items():
                    #print(k1+'='+str(v1))
                    openstackStr+=makeConfigString(k1,str(v1))

    outstr+=awsStr
    outstr+=openstackStr
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

with open('simple_pancancer_config.json') as simple_config_file:
    simple_config=json.load(simple_config_file)

with open('pancancer_config.mustache') as mustache_template_file:
    mustache_template=mustache_template_file.read()

renderer=pystache.Renderer()
parsed=pystache.parse(mustache_template)
rendered_str=renderer.render(parsed,(simple_config))
#print(rendered_str)
data=json.loads(rendered_str)

with open('youxia_config','w') as youxia_file:
    youxia_settings=data['youxia']
    youxia_str=processYouxiaSettings(youxia_settings)
    youxia_file.write(youxia_str)

with open('params.json','w') as params_json_file:
    params_settings=data['params']
    params_str=processParams(params_settings)
    params_json_file.write(params_str)

with open('masterConfig.ini','w') as consonance_file:
    consonance_settings=data['consonance']
    consonance_str=processConsonanceSettings(consonance_settings)
    consonance_file.write(consonance_str)
