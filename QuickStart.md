#Pancancer Workflow Launcher & CLI

This quick-start guide will help you get started using the Pancancer CLI tool on Amazon's cloud.  **You are responsible for your cloud expenses for this tutorial, be careful to monitor your usage and terminate VMs when you are finished.**

The Pancancer Workflow Launcher and Command Line Tool (CLI) is a system that will allow you to schedule and execute Pancancer workflows (include BWA, Sanger, and DKFZ/EMBL) on a fleet of virtual machines in a cloud-computing environment.  Currently, these directions focus on Amazon Web Services (AWS) but other environments are supported and will be documented in the future (OpenStack and Azure specifically).

![Pancancer CLI Diagram - Overview](/images/Pancancer_CLI_system_diagram.png?raw=true "Click for larger view")

The diagram above shows some detail about how the Pancancer Workflow Launcher and CLI tool are used to manage a fleet of VMs executing pancancer workflows. The details of how this is done can be found in the document below.

##What You Need

Before you get started, there are a few items you will need to have available:
 - A valid account on Amazon AWS EC2, with access to the "us-east-1" (North Virginia) AWS region.
 - A valid key file that you can use to log in to your EC2 VMs. Click [here](http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-key-pairs.html) for a document about how to generate these pem keys.
 - Your AWS Key and Secret Key. If you don't know your Key and Secret Key, [this](http://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSGettingStartedGuide/AWSCredentials.html) document may be able to help you.
 - If you are downloading or uploading data from/to a GNOS respository, you will need a valid GNOS key. If you are only working with S3 then a GNOS key will not be necessary.


##Getting started

### Launch a VM
Launch a new VM in Amazon EC2. You **must** use the AWS region "us-east-1" (AKA North Virginia) for this tutorial to work. If you are unfamiliar with the process of launching VMs in Amazon EC2, you may want to read [this guide](http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/LaunchingAndUsingInstances.html). When setting up your instance, be sure to include enough storage space to install docker and download docker images. 40 GB should be enough. The instance type normally used for this is m3.large. The following screen-shots  illustrate how the VM should be configured.

#### Choosing an AMI
Choosing an Ubuntu 14.04 AMI (here, AMI ami-d05e75b8 was used)
![choosing an AMI](/images/1_Choose_AMI.png?raw=true "Click for larger view")

#### Choosing an instance type
Choosing an m3.large instance type
![choosing an instance type](/images/2_Choose_Instance_Type.png?raw=true "Click for larger view")

#### Configuring your instance
Configure your instance. If you want to use [termination protection](http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/terminating-instances.html#Using_ChangingDisableAPITermination), this is the screen where you can enable it.
![Configuring your instance](/images/3_Configure_Instance.png?raw=true "Click for larger view")

#### Adding storage
Setting up storage. 40 GB should be sufficient.
![Add Storage](/images/4_Add_Storage.png?raw=true "Click for larger view")

#### Setting tags
Setting tags on your instance. Here, you can set the instance name that your VM will use.
![Tag instance](/images/5_Tag_Instance.png?raw=true "Click for larger view")

#### Configuring security groups
Configuring security groups for your instance. You can use an existing group, or let AWS create a new one. *Notice that the rules have been set to allow ssh access from the source "My IP".* It is **very** important to restrict traffic to your VMs to *only* the machines that *need* access. **Avoid** using the "Anywhere" source. If you need to allow access from an IP address that is not "My IP", you can use a Custom IP source.

When you choose the "MyIP" option, The AWS Console will attempt to determine the IP address that you are using to connect to it. If you are behind a router, it will see the public-facing IP of the router.

**IMPORTANT:** Please make a note of the *name* of the security group that is chosen at this step, you _will_ need it later.

![Security Groups](/images/6_Security_Group.png?raw=true "Click for larger view")

#### Review and Launch
When you have completed configuring Security Groups, you should see a "Review and Launch" button. Clicking on that will bring up a Review page where you can review your instance details:

![Review](/images/Review.png?raw=true "Click for a larger view")

Once you have reviewed your choices, you can click the Launch button to move on the the next step: [Choosing or Generating an SSH key pair](#choosing-or-generating-an-ssh-key-pair).

#### Choosing or generating an SSH key pair
When AWS is ready to launch your VM, it will prompt you to choose an existing SSH key or to create a new one, like this:

![Choose or Create a key](/images/AWS_Create_Key.png?raw=true "Click for a larger view")

Click [here](http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-key-pairs.html#having-ec2-create-your-key-pair) for more information about creating AWS key pairs.

### SSH to VM

Once the VM is running, log in to your new VM over ssh. If you are not sure how to connect to your VM using ssh, right-click on your VM in the AWS EC2 Management Console and click "connect". You will get a detailed information from AWS about how to connect to your VM.
![Connect to Instance](/images/AWS_connect_to_VM2.png?raw=true "Click for larger view")

You will need the key you used in [this step](#choosing-or-generating-an-ssh-key-pair)

### Set up files
You will now need to set up a few files on your VM.

  - You will need to put your AWS pem key on to this machine in `~/.ssh/FillInYourKeyName.pem`. Also make sure you set the permissions correctly on this file, you can do that with the command:
```
chmod 600 ~/.ssh/FillInYourKeyName.pem
```
You can do this by editing the files on your VM in an editor such as vi and copying and pasting from the original files on your workstation, or you can transfer the files from your workstation using a tool such as scp.
   
A call to scp takes the form:
```
$ scp -i <KEY TO AUTHENTICATE WITH> <FILE TO COPY> <USER>@<HOST>:<DESTINATION PATH ON HOST>
```
Transferring your pem key file to your new VM using scp on linux can be done like this:
 
```
$ scp -i <YOUR PEM KEY FILE>.pem <YOUR PEM KEY FILE>.pem ubuntu@<YOUR VM PUBLIC DNS OR IP ADDRESS>:/home/ubuntu/.ssh/<YOUR PEM KEY FILE>.pem
```
   See "Transferring Files to Linux Instances from Linux Using SCP" on [this page](http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/AccessingInstancesLinux.html) for more details about copying files to your VM.

**NOTE:**
  - If you are working with GNOS repositories, which you typically only will be if you are involved in core analysis of PanCancer data through the Technical Working Group, you will need to put your GNOS keys (e.g. `gnos.pem`) on this machine in `~/.gnos/`. Create this directory if it doesn't exist. You can do this by editing the files on your VM and copying and pasting from the original files on your workstation, or you can copy the files from your workstation using a tool such as scp. See "Transferring Files to Linux Instances from Linux Using SCP" on [this page](http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/AccessingInstancesLinux.html) for more details about copying files to your VM.  **Most users will want to analyze their own data from S3 and write the results back to S3, in this scenario GNOS is not used and you can ignore this step.**


### Run Installer
Download & execute the [bootstrap script](scripts/install_bootstrap) like this:
```
$ wget -qO install_bootstrap https://github.com/ICGC-TCGA-PanCancer/cli/releases/download/L4A_1.0.0-rc.3/install_bootstrap && bash install_bootstrap
```
This script will install docker (you can skip this step by answering "N" if you already have docker installed), the pancancer_launcher image, and collect some basic configuration info to get the launcher started. 

This installer script will ask you some questions about how to get started. It will need to know:
 - The absolute path to your AWS pem key (this should be copied into `~/.ssh` before begining the installer, as per instructions above)
 - The *name* of your AWS key. This is *usually* the same as the name of the key file you download from AWS. For example, an AWS key with the name "MyKey" is normally downloaded and saved as the file "MyKey.pem".
 - Your AWS Key and AWS Secret Key. If you do not know these, [this document](http://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSGettingStartedGuide/AWSCredentials.html) might be able to help you.
 - The name that you would like to give to your fleet. This will make it easier to find your VMs in the AWS EC2 Management Console. If you do not specify a fleet name, a randomly generated name will be used.
 - The _maximum_ number of VMs you want to have in your fleet (you will be able to change this later, if you want).
 - The name of the security group for your fleet, which was set in [this step](#configuring-security-groups). It needs this so that it can update the permissions of this group so that the VMs in the fleet can communicate properly with each other. This _must_ be the same as the security group that the launcher is in. If you are not sure about the name of your security group, you can find it in the AWS EC2 console: Find your host VM, and then look for the "Security Group" column. This will show you the name of the security group of your VM.

If for some reason you need to exit this script, you can re-run it simply by executing this command:

```
bash install_bootstrap
```

##Inside the Pancancer Launcher.

If you follow the directions above you will find yourself dropped into the docker container that has all our launcher tools. The prompt will look something like this (the hostname, "f27e86874dfb" in this case, and possibly the version number, will be different):

    [LAUNCHER 3.1.6] ubuntu@f27e86874dfb:~/arch3$


###Running workflows

The Pancancer Launcher can generate a template INI file for workflows. These INI files are used to set workflow-specific parameters, such as which input files to download or where to upload workflow results. To see which workflows are available, you can use the command `pancancer workflows list`:

```
$ pancancer workflows list
Available workflows are:
HelloWorld_1.0-SNAPSHOT
BWA_2.6.7
```

For more information about these workflows and how to configure their INI files, see the workflows' home pages but for now we will walk through using HelloWorld to ensure everything works:

<!-- - [Sanger](https://github.com/ICGC-TCGA-PanCancer/SeqWare-CGP-SomaticCore) -->
<!-- - [DKFZ/EMBL](https://github.com/ICGC-TCGA-PanCancer/DEWrapperWorkflow) -->
 - [BWA](https://github.com/ICGC-TCGA-PanCancer/Seqware-BWA-Workflow)
 - HelloWorld - This is a very simple workflow that does not read or write any data, but it is good to use when testing basic setup and infrastructure.

####Generating an INI file
To generate an INI file:

```
$ pancancer workflows config --workflow HelloWorld_1.0-SNAPSHOT
```

A new HelloWorld-specific INI file should be generated in `~/ini-dir`. 
The generated file has *default* values only. You _will_ need to edit these INI files with your own specific values. For example, for BWA, you will need to specify the upload and download URLs for your BAM files. Other workflows will have other edits that are necessary for the workflow to run correctly.

<!-- TODO: Add links to workflows (done!) with details about the INI files (not yet) -->

**You will want to edit this file before generating job requests. Please make any workflow-specific changes now, before continuing.**

If you would like to generate a batch of INI files, you can do it like this:

```
$ pancancer workflows config --workflow HelloWorld_1.0-SNAPSHOT --num-INI 3
```

And 3 INI files will be created, though you will need to edit them to ensure that they are not identical. The Pancancer Launcher will try to prevent you from generating job requests that reference the same INI file contents, as that is considered running the same job multiple times.

By default, INI files will be moved to a backup-location (`~/ini-backups`) every time you run `pancancer workflows config`, though if you want to turn this behaviour off, you can do so like this:

```
$ pancancer workflows config --workflow HelloWorld_1.0-SNAPSHOT --no-INI-backup
```

Doing this will leave all of the old INI files in `~/ini-dir`.

**NOTE:** The workers launched by the Pancancer Launcher will be _on-demand_ instances, by default. On-demand instances are more reliable and launch faster, but will cost more than spot pricing. If you wish to use spot pricing, read [this section](#setting-a-spot-price) before proceeding.

####Generating a work order
A work order is contains information about what work needs to be done, and what kind of VM needs to be provisioned for it.

To generate work order for a workflow:
```
$ pancancer generator --workflow HelloWorld_1.0-SNAPSHOT
```
<!-- TODO: auto-backup old INI files? can wait... Done, needs test -->

The job generator will attempt to generate one job for *each and every* INI file in `~/ini-dir`. It is important to ensure that this directory *only* contains INI files for jobs you wish to run, *and* that you have made any necessary edits to them. 

<!-- TODO: need better notes on contents of ini-dir, need to move ini out of here once submitted. or not? hash check should prevent duplicates... -->

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

The process that provisiones VMs should detect this request within a couple of minutes and begin provisioning a new VM. Provisioning a new VM may take several minutes (10 minutes is not unreasonable) because we setup various infrastructure on these VMs using Ansible.  The process was designed for the PanCancer workflows which can run for *days* or *weeks* so the startup time of the worker VMs has yet to be optimized.

####Monitoring Progress

There are a few ways that you can monitor progress. You can watch the progress using this command:
```
$ tail -f ~/arch3/logs/provisioner.out
```
Type <kbd>Ctrl</kbd>-<kbd>C</kbd> to terminate `tail`.

You can also monitor progress from the AWS EC2 console. Look for the new instance that is starting up, named `instance_managed_by_<YOUR_FLEET_NAME>`:


Once provisioning is complete, you should see output that looks similar to this (the exact numbers for "ok" and "changed" may vary, but everything is OK as long as "unreachable" and "failed" are 0) in the `provision.out` file:

<pre>
PLAY RECAP ********************************************************************
i-fb797f50                 : ok=125  changed=86   unreachable=0    failed=0

[2015/09/02 18:06:16] | Finishing configuring i-fb797f50
</pre>

At this point, the job should begin executing on the new VM. You can check the status of *all* jobs using the command `pancancer status jobs`

```
$ pancancer status jobs
 status  | job_id |               job_uuid               |  workflow  |      create_timestamp      |      update_timestamp
---------+--------+--------------------------------------+------------+----------------------------+----------------------------
 PENDING |      1 | a3a4da7b-2136-4431-a117-e903590c05d8 | HelloWorld | 2015-09-02 19:45:26.023313 | 2015-09-02 19:45:26.023313
```

When the job has completed successfully, you should see a status result that looks like this:

```
$ pancancer status jobs
 status  | job_id |               job_uuid               |  workflow  |      create_timestamp      |      update_timestamp
---------+--------+--------------------------------------+------------+----------------------------+----------------------------
 SUCCESS |      1 | a3a4da7b-2136-4431-a117-e903590c05d8 | HelloWorld | 2015-09-02 19:45:26.023313 | 2015-09-02 20:04:27.033118
```

To write the full results of a Worker to a file, you can use the `status job_results` command. It has this form:
```
$ cd ~/arch3
$ pancancer status job_results --type stdout  --job_id 1
Job results (stdout) have been written to /home/ubuntu/arch3/job_1.stdout
$ pancancer status job_results --type stderr  --job_id 1
Job results (stderr) have been written to /home/ubuntu/arch3/job_1.stderr
```
Worker VMs report the stdout and stderr from seqware back to your launcher's database. The command above can extract this data and write it to a text file to make it easier to use, if you are interested in seeing the details of the workflow's execution.
The HelloWorld workflow does not do much - it does not read or write data anywhere. It is useful to test your setup and configuration is correct.

At this point, you have successfully installed the Pancancer Launcher, and used it to schedule and execute a workflow!

When looking at your AWS EC2 console, you will notice that when a workflow finishes successfully, the VM it was running on will have been automatically terminated. This is done to save on computing resources. The pancancer workflows write their data to GNOS repositories (AWS S3 support will be coming) before their VM is terminated. The VM that is serving as your launcher will *not* be terminated until you choose to do so.

<!-- TODO: Add section on failed workflow -->

If a workflow fails, you will see that its status is "FAILED". To see the output from the VM, you can use the `pancancer status job_results` command like this:

```
$ pancancer status job_results --job_id <THE JOB_ID OF THE JOB THAT FAILED> --type stdout 
```
This will write data to a file containing the standard output that SeqWare captured while running the workflow. You can also get the standard error messages by running the above command with `stderr` instead of `stdout`. 

If you this is not enough information to properly debug the failure, you can try using the [`--keep_failed` option when running the generator command, as explained in the Troubleshooting section](#My Worker VMs fail and get shut down, but I want them to stay up and running so I can debug problems.).

<!-- TODO: Fill in more detail here. currently, the user will have to know to configure the INI for where output goes, but maybe if we just have links to all workflow main pages, we can just reference the section that details where output goes...?
Most workflows will write their results to a GNOS respository or an AWS S3 bucket, so you will want to check there for -->

<!-- TODO: Add section on reporting tool -->


###What's Next?

In this guide, we executed a single HelloWorld workflow. Now that you are familiar with some of the capabilities of the Pancancer Launcher, you can understand how it can be used to schedule and execute larger groups of different types of workflows.  Over time, the complete set of PanCancer "core" workflows will be available in this launcher.  Each have distinct INI parameters that you need to know how to fill in properly to analyze your data.  See details in the README for each of the project's core workflows, they will provide enough information for you to process your own data using these workflows so you can co-analyze your data with the larger PanCancer dataset:

<!-- - [Sanger](https://github.com/ICGC-TCGA-PanCancer/SeqWare-CGP-SomaticCore) -->
<!-- - [DKFZ/EMBL](https://github.com/ICGC-TCGA-PanCancer/DEWrapperWorkflow) -->
 - [BWA](https://github.com/ICGC-TCGA-PanCancer/Seqware-BWA-Workflow)

<!-- TODO: Should we eventually have a tool that lets the use create n INI files? Might not be that hard, will need to investigate... -->
Your next step, now that you have successfully run one workflow on one VM, could be to create several INI files (you can use `pancancer workflows config --workflow <SOME WORKFLOW NAME>` to create a default INI file and then copy it as many times as you need and edit the copies) and then execute them in a larger fleet.

You can also try running the BWA workflow with your launcher. For more information on this topic, click [here](./run_bwa_tutorial.md).

###Other useful tips

####Setting a spot price.
Amazon spot pricing allows you to specify a maximum price for your EC2 instances, and this can let you save money on running your instances. You can read more about spot pricing [here](https://aws.amazon.com/ec2/spot/pricing/).

To set a spot instance price, run the `pancancer sysconfig --force` command. You will be prompted to answer a number of questions, the answer to which are probably already correct. When you get to the question that asks "What spot price would you like to set?", type your new spot instance price and hit <kbd>Enter</kbd>.

```
$ pancancer sysconfig --force
Setting up pancancer config files.
What is your AWS Key [Press "ENTER" to use the previous value: <PREVIOUS VALUE>, or type a new value if you want]? 
What is your AWS Secret Key [Press "ENTER" to use the previous value: <PREVIOUS VALUE>, or type a new value if you want]? 
How many VMs do you want in your fleet [Press "ENTER" to use the previous value: 1, or type a new value if you want]? 
What AWS Security Group should the VMs belong to [Press "ENTER" to use the previous value: test_security_group, or type a new value if you want]? 
What spot price would you like to set [Press "ENTER" to use the previous value: 0.001, or type a new value if you want]? 0.15
Your new pancancer system config file has been written to /home/ubuntu/.pancancer/simple_pancancer_config.json
The next time you want to run "pancancer sysconfig", you can use this file like this: 
pancancer sysconfig --config /home/ubuntu/.pancancer/simple_pancancer_config.json
```

####Configuration

Configuration should already be complete once you have entered the Pancancer Launcher, but if you need to change or adjust some configuration options (such as fleet size), you can use this command:

```
$ pancancer sysconfig --force
```

####Running the coordinator and provisioner
There are two services that are used to provision new VMs for jobs. They are the Coordinator and Provisioner. The coordinator will process job requests into jobs and provisioning requests. The provisioner will provision new VMs that will execute your jobs, based on the requests generated by the coordinator.

Normally, the Coordinator is started when the Pancancer Launcher is started and the Provisioner will be started when you generate the first INI file. Sometimes, you may want to "pause" or hold the provisioning process, so it is useful to know how to start and stop these services.

```
$ pancancer coordinator start
```
This process will write to a file named `coordinator.out`. More detailed output can also be found in `arch3.log`.

```
$ pancancer coordinator stop
```
This will stop the coordinator. Job requests will not be processed into jobs or provisioning requests until the service is started again. 


```
$ pancancer provisioner start
```
This process will write to a file named `provisioner.out`. More detailed output can also be found in `arch3.log`.


```
$ pancancer provisioner stop
```
This will stop the provisioner. No new VMs will be provisioned until the service is started again. It is not a good idea to stop the provisioner if it is in the middle of provisioning something as it may result in that VM being in a bad state. 


To get the status of these services: 
```
$ pancancer status services
The Coordinator appears to be running with PID: 41193
The Provisioner appears to be running with PID: 42520
```


####Interactive shell
You can also work with the pancancer tool's interactive shell simply by executing the command `pancancer`:
```
$ pancancer
(pancancer) coordinator start
```
In this example, the user has started the interactive shell, as can be seen by the shell prompt, which has changed from `$` to `(pancancer)`.

To get a list of all pancancer commands, you can type `pancancer -h` and the help text will be displayed.

<!-- TODO: what happened?  What did I just do?  Why is it significant?  What do I do now?

* reporting
* how do you get the output of the workflows? e.g. helloworld?
* what do you do next? -->

####Detaching and reattaching with Docker
If you need to do some work on the host machine, it is better to _detach_ from the pancancer\_launcher container than to exit. If you exit, the container should restart automatically, but any processes that are running (such as the provisioning process) may be terminated and that could affect any VMs that are in mid-provision.

To detach safely, press <kbd>Ctrl</kbd>-<kbd>P</kbd> <kbd>Ctrl</kbd>-<kbd>Q</kbd>

To re-attach to your pancancer\_launcher container, issue this command on your host machine:
```
$ sudo docker attach pancancer_launcher
```

Press <kbd>Enter</kbd> if the prompt does not appear right away.

###Troubleshooting

#### The provisioner keeps getting SSH errors!

There are a few things that could cause this to happen, the most common being:
 - An invalid PEM key file
 - Security group configuration issues.

Ensure that your PEM key file is valid and that the path is configured correctly. You can check the path that the system is using in `~/.pancancer/simple_pancancer_config.json`.

Ensure that the security group allows inbound connections on all TCP ports from the *public* IP address of the machine which is acting as the launcher host.

#### I changed my configuration but it doesn't seem to be having any effect.

If the configuration is changed while the Provisioner and Coordinator are running, they may need to be restarted to use the new configuration. It is best to avoid doing this while a VM is being provisioned. Try stopping these services, updating your configuration, and then starting them again:

```
$ pancancer coordinator stop
$ pancancer provisioner stop
$ pancancer sysconfig --force
$ pancancer coordinator start
$ pancancer provisioner start
```

#### My Worker VMs fail and get shut down, but I want them to stay up and running so I can debug problems.

Normally, failed workers are cleaned up automatically. It is sometimes useful to leave failed workers up and running if you are interested in debugging a problematic workflow.

Keeping failed workers must be configured when generating job requests:

```
$ pancancer generator --workflow HelloWorld_1.0-SNAPSHOT --keep_failed
```

The result of this is that if a Worker VM completes its work successfully, it will be automatically removed from the fleet, but if a worker fails, it will be left alone, and you will be able to log in to it and debug whatever caused it fo fail.


#### There is a worker that is stuck in a bad state and I need to get rid of it.

Normally, Worker VM are removed from the fleet when they have finished working. Failed workers are usually cleaned up automatically as well. If it happens that a worker gets stuck in a bad state and cannot be removed automatically, you may need to manually remove it from the fleet.

To remove a Worker VM from the fleet, create a file named `kill-list.json`. This will will contain a _list_ of IP addresses of any Worker VMs that need to be removed:

    [ "0.0.0.1","0.0.0.2"]
 
Then run the Reaper command, passing it the file name containing the list:

```
$ Reaper --kill-list kill-list.json 
[2015/10/13 18:06:59] | Killing {i-346db1a6=i-346db1a6},
[2015/10/13 18:06:59] | Marking instances for death i-346db1a6
```

<!--
##Known Issues

1. the script /home/ubuntu/arch3/cli/scripts/workflowlister.py has a URL for BWA's INI file for a ​_released_​ version of the workflow but this will produce a 404 error if it's not updated to: https://raw.githubusercontent.com/ICGC-TCGA-PanCancer/Seqware-BWA-Workflow/feature/solomon_BWA_use_S3/workflow/config/workflow_s3.ini
Once there is a released version of BWA 2.6.7 in github, this shouldn't be an issue.
2. the INI file needs to be modified. Replace ${version} with 2.6.7. I think this normally happens during the release process...
3. Make sure you put your AWS config file (containing your AWS Key and AWS Secret Key) into .gnos on the launcher host (is this within the host machine or within the launcher docker container?). This is needed so that BWA can talk with S3 for download and upload. This is not pretty but there's no way around it with the current version of Consonance (only `~/.gnos` gets mounted into the running seqware container and aws cli will let you specify an alternate location for the config file but ​_not_​ the credentials file - fortunately, credentials can also go in the config file so `aws s3 cp...` will still work).  The file the workflow looks for is `/home/ubuntu/.gnos/config`
-->
