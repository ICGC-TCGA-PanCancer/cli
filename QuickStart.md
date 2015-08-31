#Pancancer CLI

This quick-start guide will help you get started using the Pancancer CLI tool.

##What You Need

Before you get started, there are a few items you will need to have available:
 - A valid account on Amazon AWS EC2
 - A valid key file that you can use to log in to your EC2 VMs. Click [here](http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-key-pairs.html) for a document about how to generate these pem keys.
 - Valid GNOS key files.
 - Your AWS Key and Secret Key. If you don't know your Key and Secret Key, [this](http://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSGettingStartedGuide/AWSCredentials.html) document may be able to help you.


##Getting started

1. Launch a new VM in Amazon EC2 (This guide will assume you are using us-east-1 AKA North Virginia). If you are unfamiliar with the process of launching VMs in Amazon EC2, you may want to read [this guide](http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/LaunchingAndUsingInstances.html).
2. Log in to your new VM.
3. You will now need to set up a few files.
  - You will need to set up your AWS credentials on your new VM so that they can be used by the PancancerCLI. Create a directory named `~/.aws` and create a file named `config` in `~/.aws`. Format it as is shown [here](http://docs.aws.amazon.com/cli/latest/userguide/cli-chap-getting-started.html#cli-config-files). Example:
```
$ cat ~/.aws/config
[default]
aws_access_key_id=<YOUR AWS ACCESS KEY>
aws_secret_access_key=<YOUR SECRET KEY>
```
  - You will need to put your AWS pem key on to this machine in `~/.ssh/MyKey.pem`. Also make sure you set the permissions correctly on this file, you can do that with the command:
```
chmod 600 ~/.ssh/MyKey.pem
```
You can do this by editing the files on your VM and copying and pasting from the original files on your workstation, or you can copy the files from your workstation using a tool such as scp. See "Transferring Files to Linux Instances from Linux Using SCP" on [this page](http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/AccessingInstancesLinux.html) for more details about copying files to your VM.
  - You will need to put your GNOS keys on this machine in `~/.gnos/`. You can do this by editing the files on your VM and copying and pasting from the original files on your workstation, or you can copy the files from your workstation using a tool such as scp. See "Transferring Files to Linux Instances from Linux Using SCP" on [this page](http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/AccessingInstancesLinux.html) for more details about copying files to your VM.
4. Download & execute the [bootstrap script](scripts/install_bootstrap)
```
$ wget -qO install_bootstrap https://raw.githubusercontent.com/ICGC-TCGA-PanCancer/cli/develop/scripts/install_bootstrap && bash install_bootstrap
```
This script will install docker, the pancancer_launcher image, and collect some basic configuration info to get the launcher started.

##Inside the Pancancer Launcher.

###Configuration

Once you are in the Pancancer Launcher docker container, you will want to do some basic pancancer system configuration. You can do this using the command:
```
$ pancancer sysconfig
```
You should do this before you run any workflows.


###Running workflows

The Pancancer Launcher can generate a template INI file for workflows (you can see which workflows are available with the command `pancancer workflows list`), but you may want to edit these before executing the workflow.

####Generating an INI file
To generate an INI file:
```
$ pancancer workflows config --workflow BWA
```

A new BWA-specific INI file should be generated in `~/ini-dir`. You will want to edit this file before generating job requests.

####Generating a job request
To generate job requests for a workflow:
```
$ pancancer generator --workflow BWA
```
The generated jobs will use the INI files in `~/ini-dir` so it is important to make any necessary edits before this step!

You can verify that your job request has been enqueued with this command:
```
$ pancancer status queues
```
You should see that some queues have a message in them.

####Running the coordinator and provisioner
Once an INI file has been generated and the job request has been enqueued, you will be ready to start the services which will run the jobs. First, you should start the coordinator service:

```
$ pancancer coordinator start
```
This process will write to a file named `coordinator.out`. More detailed output can also be found in `arch3.log`.

You will also need to start the provisioner service:
```
$ pancancer provisioner start
```
This process will write to a file named `provisioner.out`. More detailed output can also be found in `arch3.log`. Provisioning may take a while. You can watch the progress using this command:
```
$ watch tail -n 30 provisioner.out
```

####Interactive shell
You can also work with the pancancer tool's interactive shell simply by executing the command `pancancer`:
```
$ pancancer
(pancancer) coordinator start
```
In this example, the user has started the interactive shell, as can be seen by the shell prompt, which has changed from `$` to `(pancancer)`.

To get a list of all pancancer commands, you can type `pancancer -h` and the help text will be displayed.
