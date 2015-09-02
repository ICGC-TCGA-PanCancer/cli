#Pancancer CLI

This quick-start guide will help you get started using the Pancancer CLI tool.

##What You Need

Before you get started, there are a few items you will need to have available:
 - A valid account on Amazon AWS EC2, with access to the "us-east-1" (North Virginia) AWS region.
 - A valid key file that you can use to log in to your EC2 VMs. Click [here](http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-key-pairs.html) for a document about how to generate these pem keys.
 - Valid GNOS key files.
 - Your AWS Key and Secret Key. If you don't know your Key and Secret Key, [this](http://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSGettingStartedGuide/AWSCredentials.html) document may be able to help you.


##Getting started

### Launch a VM
Launch a new VM in Amazon EC2. You **must** use the AWS region "us-east-1" (AKA North Virginia) for this tutorial to work. If you are unfamiliar with the process of launching VMs in Amazon EC2, you may want to read [this guide](http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/LaunchingAndUsingInstances.html).
Once the VM is running, log in to your new VM.
### Set up files
You will now need to set up a few files on your VM.

  - You will need to put your AWS pem key on to this machine in `~/.ssh/MyKey.pem`. Also make sure you set the permissions correctly on this file, you can do that with the command:
```
chmod 600 ~/.ssh/MyKey.pem
```
   You can do this by editing the files on your VM and copying and pasting from the original files on your workstation, or you can copy the files from your workstation using a tool such as scp. See "Transferring Files to Linux Instances from Linux Using SCP" on [this page](http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/AccessingInstancesLinux.html) for more details about copying files to your VM.
  - You will need to put your GNOS keys on this machine in `~/.gnos/`. You can do this by editing the files on your VM and copying and pasting from the original files on your workstation, or you can copy the files from your workstation using a tool such as scp. See "Transferring Files to Linux Instances from Linux Using SCP" on [this page](http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/AccessingInstancesLinux.html) for more details about copying files to your VM.

### Run installer
Download & execute the [bootstrap script](scripts/install_bootstrap) like this:
```
$ wget -qO install_bootstrap https://raw.githubusercontent.com/ICGC-TCGA-PanCancer/cli/develop/scripts/install_bootstrap && bash install_bootstrap
```
This script will install docker, the pancancer_launcher image, and collect some basic configuration info to get the launcher started.

**NOTE:**
Please be aware that if docker has not been installed on your VM before, you *will* need to log out and log in again for user permission changes to take effect (the script will exit automatically at this point to let you do this). This will *only* happen the first time that docker is installed.

After logging out and logging back in, you can resume the setup process by simply typing:

```
bash install_bootstrap
```

When you are asked if you wish to install Docker, you can answer "N" for "no", and continue with the rest of the setup process.

This installer script will ask you some questions about how to get started. It will need to know:
 - The absolute path to your AWS pem key (this should be copied into `~/.ssh` before begining the installer, as per instructions above)
 - The *name* of your AWS key. This is *usually* the same as the name of the key file you download from AWS. For example, an AWS key with the name "MyKey" is normally downloaded and saved as the file "MyKey.pem".
 - Your AWS Key and AWS Secret Key. If you do not know these, [this document](http://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSGettingStartedGuide/AWSCredentials.html) might be able to help you.
 - The name that you would like to give to your fleet. This will make it easier to find your VMs in the AWS EC2 Management Console. If you do not specify a fleet name, a randomly generated name will be used.

##Inside the Pancancer Launcher.

###Configuration

Once you are in the Pancancer Launcher docker container, you will want to do some basic pancancer system configuration. You can do this using the command:
```
$ pancancer sysconfig
```
You should do this before you run any workflows. This configuration tool will ask you questions about:
 - How many VMs you want in your fleet.
 - The name of the AWS Security Group you would like your VMs to be a part of. If you do not specify a security group, the security group name "default" will be used. You may have to configure your Security Group to allow inbound TCP connections from the *public* IP address of the machine on which the pancancer launcher is running. This is **necessary** for provisoning to work. If you are not familiar with working with AWS EC2 Security Groups, you may want to read [this document](http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-network-security.html).

If the tool detects missing values for AWS Key, AWS Secret Key, the path to the pem key, or the key name, it may ask you to fill in these values.

###Running workflows

The Pancancer Launcher can generate a template INI file for workflows (you can see which workflows are available with the command `pancancer workflows list`), but you may want to edit these before executing the workflow.

####Generating an INI file
To generate an INI file:
```
$ pancancer workflows config --workflow HelloWorld
```

A new HelloWorld-specific INI file should be generated in `~/ini-dir`. You will want to edit this file before generating job requests.

####Generating a job request
To generate job requests for a workflow:
```
$ pancancer generator --workflow HelloWorld
```
The generated jobs will use the INI files in `~/ini-dir` so it is important to make any necessary edits before this step!

You can verify that your job request has been enqueued with this command:
```
$ pancancer status queues
```
You should see that some queues have a message in them.

```
queues: 
+-------+-------------------------+---------------------+----------+
| vhost |          name           |        node         | messages |
+-------+-------------------------+---------------------+----------+
| /     | aliveness-test          | rabbit@23aba91e1eaf | 0        |
| /     | pancancer_arch_3_orders | rabbit@23aba91e1eaf | 1        |
+-------+-------------------------+---------------------+----------+
```

As you can see there is one message in the message queue named "pancancer_arch_3_orders". This indicates that the system successfully generated a job order from your INI file in `~/ini-dir`.

####Running the coordinator and provisioner
Once the system has been configured and an INI file has been generated and the job request has been enqueued, you will be ready to start the services which will provision new VMs so that the jobs can be run. First, you should start the coordinator service:

```
$ pancancer coordinator start
```
The coordinator will process job requets into jobs and provisioning requests. This process will write to a file named `coordinator.out`. More detailed output can also be found in `arch3.log`.

You will also need to start the provisioner service:
```
$ pancancer provisioner start
```
The provisioner will provision new VMs. It is these VMs that will execute your jobs. This process will write to a file named `provisioner.out`. More detailed output can also be found in `arch3.log`. Provisioning may take a while. You can watch the progress using this command:
```
$ watch tail -n 30 provisioner.out
```
Type <kbd>Ctrl</kbd>-<kbd>C</kbd> to terminate `watch`.

####Interactive shell
You can also work with the pancancer tool's interactive shell simply by executing the command `pancancer`:
```
$ pancancer
(pancancer) coordinator start
```
In this example, the user has started the interactive shell, as can be seen by the shell prompt, which has changed from `$` to `(pancancer)`.

To get a list of all pancancer commands, you can type `pancancer -h` and the help text will be displayed.

###Troubleshooting

#### The provisioner keeps getting SSH errors!

There are a few things that could cause this to happen, the most common being:
 - An invalid PEM key file
 - Security group configuration issues.

Ensure that your PEM key file is valid and that the path is configured correctly. You can check the path that the system is using in `~/.pancancer/simple_pancancer_config.json`.

Ensure that the security group allows inbound connections on all TCP ports from the *public* IP address of the machine which is acting as the launcher host.

#### I changed my configuration but it doesn't seem to be having any effect.

If the configuration is changed while the provisioner and coordinator are running, they may need to be restarted to use the new configuration. It is best to avoid doing this while a VM is being provisioned. Try stopping these services, updating your configuration, and then starting them again:
```
$ pancancer coordinator stop
$ pancancer provisioner stop
$ pancancer sysconfig
$ pancancer coordinator start
$ pancancer provisioner start
```
