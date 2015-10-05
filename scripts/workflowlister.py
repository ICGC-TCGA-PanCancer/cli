class WorkflowLister:
    "Get a listing of workflows from a source of workflow metadata."
    # Eventually, this data structure should come from some sort of online registry. For now, just define it in code.
    _workflows= {   'HelloWorld':
                    {
                        'full_name':'Workflow_Bundle_HelloWorld_1.0-SNAPSHOT_SeqWare_1.1.1',
                        'http_workflow':
                        {
                            'url':'https://s3.amazonaws.com/oicr.workflow.bundles/released-bundles/Workflow_Bundle_HelloWorld_1.0-SNAPSHOT_SeqWare_1.1.1.zip',
                            'version':'1.0-SNAPSHOT'
                        },
                        'containers':
                        {
                            'seqware_whitestar_pancancer': {
                                'name':'seqware_whitestar_pancancer',
                                'image_name': 'pancancer/seqware_whitestar_pancancer:1.1.1'
                            }
                        },
                        'ami_id':'ami-791c5b1c',
                        'default-ini':'http://something.ini',
                        'instance-type':'m1.xlarge',
                        'lvm_devices':'/dev/xvdb,/dev/xvdc,/dev/xvdd,/dev/xvde',
                        'workflow_uses_gnos':'false',
                        'workflow_uses_s3':'false'
                    }
#                     ,'Sanger':
#                     {
#                         'full_name':'Workflow_Bundle_SangerPancancerCgpCnIndelSnvStr_1.0.8_SeqWare_1.1.0',
#                         'http_workflow':
#                         {
#                             'url':'https://s3.amazonaws.com/oicr.workflow.bundles/released-bundles/Workflow_Bundle_SangerPancancerCgpCnIndelSnvStr_1.0.8_SeqWare_1.1.0.zip',
#                             'version':'1.0.8'
#                         },
#                         'containers':
#                         {
#                             'seqware_whitestar_pancancer': {
#                                 'name':'seqware_whitestar_pancancer',
#                                 'image_name': 'pancancer/seqware_whitestar_pancancer:1.1.1'
#                             }
#                         },
#                         'ami_id':'ami-270cc34c',
#                         'default-ini':'https://raw.githubusercontent.com/ICGC-TCGA-PanCancer/SeqWare-CGP-SomaticCore/1.0.8/workflow/config/CgpCnIndelSnvStrWorkflow.ini',
#                         'instance-type':'m1.xlarge',
#                         'lvm_devices':'/dev/xvdb,/dev/xvdc,/dev/xvdd,/dev/xvde'
#                         'workflow_uses_gnos':'true',
#                         'gnos_keys':['gnos.pem'],
#                         'workflow_uses_s3':'false'
#                     },
#                     'BWA':
#                     {
#                         'full_name':'Workflow_Bundle_BWA_2.6.5_SeqWare_1.1.1',
#                         'http_workflow':
#                         {
#                             'url':'https://s3.amazonaws.com/oicr.workflow.bundles/released-bundles/Workflow_Bundle_BWA_2.6.5_SeqWare_1.1.1.zip',
#                             'version':'2.6.5'
#                         },
#                         'containers':
#                         {
#                             'seqware_whitestar_pancancer': {
#                                 'name':'seqware_whitestar_pancancer',
#                                 'image_name': 'pancancer/seqware_whitestar_pancancer:1.1.1'
#                             }
#                         },
#                         'ami_id':'ami-270cc34c',
#                         'default-ini':'https://raw.githubusercontent.com/ICGC-TCGA-PanCancer/Seqware-BWA-Workflow/2.6.5/workflow/config/workflow.ini',
#                         'instance-type':'m1.xlarge',
#                         'lvm_devices':'/dev/xvdb,/dev/xvdc,/dev/xvdd,/dev/xvde',
#                         'workflow_uses_gnos':'true',
#                         'gnos_keys':['gnos.pem'],
#                         'workflow_uses_s3':'false'
#                     },
#                     'DKFZ_EMBL':
#                     {
#                         'full_name':'Workflow_Bundle_DEWrapperWorkflow_1.0.5_SeqWare_1.1.1',
#                         'http_workflow':
#                         {
#                             'url':'https://s3.amazonaws.com/oicr.workflow.bundles/released-bundles/Workflow_Bundle_DEWrapperWorkflow_1.0.5_SeqWare_1.1.1.zip',
# 
#                             'version':'1.0.5'
#                         },
#                         'containers':
#                         {
#                             'pcawg-delly-workflow': {
#                                 'name':'pcawg-delly-workflow',
#                                 'image_name': 'pancancer/pcawg-delly-workflow:1.0'
#                             },
#                             'seqware_whitestar_pancancer': {
#                                 'name':'seqware_whitestar_pancancer',
#                                 'image_name': 'pancancer/seqware_whitestar_pancancer:1.1.1'
#                             },
#                             'pancancer_upload_download': {
#                                 'name':'pancancer_upload_download',
#                                 'image_name':'pancancer/pancancer_upload_download:1.2'
#                             }
#                         },
#                         's3_containers':
#                         {
#                             'dkfz_dockered_workflows':
#                             {
#                                 'name':'dkfz_dockered_workflows',
#                                 'url':'s3://oicr.docker.private.images/dkfz_dockered_workflows_1.3.tar'
#                             }
#                         },
#                         'ami_id':'ami-270cc34c',
#                         'default-ini':'https://raw.githubusercontent.com/ICGC-TCGA-PanCancer/DEWrapperWorkflow/1.0.6/workflow/config/DEWrapperWorkflow.ini',
#                         'instance-type':'m1.xlarge',
#                         'lvm_devices':'/dev/xvdb,/dev/xvdc,/dev/xvdd,/dev/xvde'
#                         'workflow_uses_gnos':'true',
#                         'gnos_keys':['gnos.pem'],
#                         'workflow_uses_s3':'false'
#                     }
                }

    @staticmethod
    def get_workflow_names():
        keys = ''
        for k in WorkflowLister._workflows:
            keys += k+'\n'
        return keys

    @staticmethod
    def get_workflow_details(workflow_name):
        return WorkflowLister._workflows[workflow_name]
