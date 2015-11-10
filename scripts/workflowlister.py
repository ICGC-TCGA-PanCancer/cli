import urllib, json
import os
class WorkflowLister:
    "Get a listing of workflows from a source of workflow metadata."
    _workflows = {}

    @staticmethod
    def get_workflow_names():
        WorkflowLister.read_workflow_details()
        keys = ''
        for k in WorkflowLister._workflows:
            keys += k+'\n'
        return keys

    @staticmethod
    def get_workflow_keys():
        WorkflowLister.read_workflow_details()
        return WorkflowLister._workflows.keys()

    @staticmethod
    def get_workflow_details(workflow_name):
        WorkflowLister.read_workflow_details()
        return WorkflowLister._workflows[workflow_name]
    @staticmethod
    def read_workflow_details():
        pancancer_config_path=os.path.expanduser('~/.pancancer/simple_pancancer_config.json')
        config_data={}
        if os.path.isfile(pancancer_config_path):
            #Read the pancancer_config.json file if it exists
            with open(pancancer_config_path,'r') as pancancer_config_file:
                config_data = json.load(pancancer_config_file)
        
        if 'workflow_listing_url' not in config_data or config_data['workflow_listing_url'] == '':
            config_data['workflow_listing_url'] = 'https://raw.githubusercontent.com/ICGC-TCGA-PanCancer/cli/L4A/config/workflowlist.json'
            
        response = urllib.request.urlopen(config_data['workflow_listing_url'])
        WorkflowLister._workflows = json.loads(response.read().decode('utf-8'))
