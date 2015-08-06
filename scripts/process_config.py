import json

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
                    if k1!='zone':
                        awsStr+=makeConfigString(k1,str(v1))
                    else:
                        awsStr+=makeConfigString(k1,','.join(v1))
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
    d['lvm_device_whitelist']=','.join(d['lvm_device_whitelist'])
    return str(json.dumps(d,sort_keys=True, indent=4) )

def processConsonanceSettings(d):
    outstr=''
    for k,v in d.items():
        outstr+='\n['+k+']\n'
        for k1,v1 in v.items():
            outstr+=makeConfigString(k1,str(v1))
    return outstr


with open('../pancancer_config.json') as data_file:
    data=json.load(data_file)

youxia_file=open('youxia_config','w')
youxia_settings=data['youxia']
youxia_str=processYouxiaSettings(youxia_settings)
youxia_file.write(youxia_str)
youxia_file.close()

params_json_file=open('params.json','w')
params_settings=data['params']
params_str=processParams(params_settings)
params_json_file.write(params_str)
params_json_file.close()

consonance_file=open('masterConfig.ini','w')
consonance_settings=data['consonance']
consonance_str=processConsonanceSettings(consonance_settings)
consonance_file.write(consonance_str)
consonance_file.close()
