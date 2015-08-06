import json

def makeConfigString(k,v):
    return k+'='+v+'\n'

with open('../pancancer_config.json') as data_file:
    data=json.load(data_file)

print('The youxia stuff')
youxia_file=open('youxia_config','w')
youxia_settings=data['youxia']

outstr=''
outstr+='[youxia]\n'
awsStr=''
openstackStr=''

for k,v in youxia_settings.items():
    if not (isinstance(v,dict)):
        outstr+=makeConfigString(k,v)
    else:
        if k=='aws':
            # Process AWS-specific variables in the AWS heading
            awsStr+='\n[aws]\n'
            aws_settings=youxia_settings['aws']
            for k1,v1 in aws_settings.items():
                if k1!='zone':
                    awsStr+=makeConfigString(k1,str(v1))
                else:
                    awsStr+=makeConfigString(k1,','.join(v1))
        elif k=='openstack':
            # Process AWS-specific variables in the AWS heading
            openstackStr+='\n[openstack]\n'
            openstack_settings=youxia_settings['openstack']
            for k1,v1 in openstack_settings.items():
                #print(k1+'='+str(v1))
                openstackStr+=makeConfigString(k1,str(v1))

outstr+=awsStr
outstr+=openstackStr
youxia_file.write(outstr)
youxia_file.close()
