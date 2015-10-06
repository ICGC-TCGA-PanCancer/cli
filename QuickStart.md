#Pancancer CLI

This quick-start guide will help you get started using the Pancancer CLI tool.

The Pancancer CLI tool is a command-line interface tool that will allow you to interact with the pancancer components. The Pancancer CLI tool can be used to schedule and execute Pancancer workflows (include BWA, Sanger, and DKFZ/EMBL) on a fleet of virtual machines in a cloud-computing environment.

![Pancancer CLI Diagram - Overview](/images/Pancancer_CLI_system_diagram.png?raw=true "Click for larger view")

The diagram above shows some detail about how the Pancancer CLI tool is used to manage a fleet of VMs executing pancancer workflows. The details of how this is done can be found in the document below.

##What You Need

Before you get started, there are a few items you will need to have available:
 - A valid account on Amazon AWS EC2, with access to the "us-east-1" (North Virginia) AWS region.
 - A valid key file that you can use to log in to your EC2 VMs. Click [here](http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-key-pairs.html) for a document about how to generate these pem keys.
 - Valid GNOS key files.
 - Your AWS Key and Secret Key. If you don't know your Key and Secret Key, [this](http://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSGettingStartedGuide/AWSCredentials.html) document may be able to help you.


##Getting started

### Launch a VM
Launch a new VM in Amazon EC2. You **must** use the AWS region "us-east-1" (AKA North Virginia) for this tutorial to work. If you are unfamiliar with the process of launching VMs in Amazon EC2, you may want to read [this guide](http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/LaunchingAndUsingInstances.html). When setting up your instance, be sure to include enough storage space to install docker and download docker images. 40 GB should be enough. The instance type normally used for this is m3.large. The following screen-shots  illustrate how the VM should be configured.

Choosing an AMI (here, AMI ami-d05e75b8 was used)
![choosing an AMI](/images/1_Choose_AMI.png?raw=true "Click for larger view")

Choosing an m3.large instance type
![choosing an instance type](/images/2_Choose_Instance_Type.png?raw=true "Click for larger view")

Configure your instance. If you want to use [termination protection](http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/terminating-instances.html#Using_ChangingDisableAPITermination), this is the screen where you can enable it.
![Configuring your instance](/images/3_Configure_Instance.png?raw=true "Click for larger view")

Setting up storage. 40 GB should be sufficient.
![Add Storage](/images/4_Add_Storage.png?raw=true "Click for larger view")

Setting tags on your instance. Here, you can set the instance name that your VM will use.
![Tag instance](/images/5_Tag_Instance.png?raw=true "Click for larger view")

Configuring security groups for your instance. You can use an existing group, or let AWS create a new one. *Notice that the rules have been set to allow ssh access from the source "My IP".* It is **very** important to restrict traffic to your VMs to *only* the machines that *need* access. **Avoid** using the "Anywhere" source. If you need to allow access from an IP address that is not "My IP", you can use a Custom IP source.

Make a note of the *name* of the security group that is chosen at this step, you will need it later.
<!--- TODO: note about not putting spaces in the security group name  - actually, this does not appear to be an issue. -->
![Security Groups](/images/6_Security_Group.png?raw=true "Click for larger view")

Once the VM is running, log in to your new VM over ssh. If you are not sure how to connect to your VM using ssh, right-click on your VM in the AWS EC2 Management Console and click "connect". You will get a detailed information from AWS about how to connect to your VM.
![Connect to Instance](/images/AWS_connect_to_VM2.png?raw=true "Click for larger view")

### Set up files
You will now need to set up a few files on your VM.

  - You will need to put your AWS pem key on to this machine in `~/.ssh/FillInYourKeyName.pem`. Also make sure you set the permissions correctly on this file, you can do that with the command:
```
chmod 600 ~/.ssh/FillInYourKeyName.pem
```
   You can do this by editing the files on your VM in an editor such as vi and copying and pasting from the original files on your workstation, or you can transfer the files from your workstation using a tool such as scp. See "Transferring Files to Linux Instances from Linux Using SCP" on [this page](http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/AccessingInstancesLinux.html) for more details about copying files to your VM.
  - You will need to put your GNOS keys (e.g. `gnos.pem`) on this machine in `~/.gnos/`, create this directory if it doesn't exist. You can do this by editing the files on your VM and copying and pasting from the original files on your workstation, or you can copy the files from your workstation using a tool such as scp. See "Transferring Files to Linux Instances from Linux Using SCP" on [this page](http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/AccessingInstancesLinux.html) for more details about copying files to your VM.

### Run installer
Download & execute the [bootstrap script](scripts/install_bootstrap) like this:
```
$ wget -qO install_bootstrap https://github.com/ICGC-TCGA-PanCancer/cli/releases/download/0.0.5/install_bootstrap && bash install_bootstrap
```
This script will install docker (you can skip this step by answering "N" if you already have docker installed), the pancancer_launcher image, and collect some basic configuration info to get the launcher started. 

This installer script will ask you some questions about how to get started. It will need to know:
 - The absolute path to your AWS pem key (this should be copied into `~/.ssh` before begining the installer, as per instructions above)
 - The *name* of your AWS key. This is *usually* the same as the name of the key file you download from AWS. For example, an AWS key with the name "MyKey" is normally downloaded and saved as the file "MyKey.pem".
 - Your AWS Key and AWS Secret Key. If you do not know these, [this document](http://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSGettingStartedGuide/AWSCredentials.html) might be able to help you.
 - The name that you would like to give to your fleet. This will make it easier to find your VMs in the AWS EC2 Management Console. If you do not specify a fleet name, a randomly generated name will be used.
 - The number of VMs you want to have in your fleet (you will be able to change this later, if you want).
 - The name of the security group for your fleet. It needs this so that it can update the permissions of this group so that the VMs in the fleet can communicate properly with each other. 

If for some reason you need to exit this script, you can re-run it simply by executing this command:

```
bash install_bootstrap
```


##Inside the Pancancer Launcher.

<!-- TODO: start_services_in_container: less noisy startup process , write to a log file, but not on console.  can wait... done? needs test -->

If you follow the directions above you will find yourself dropped into the docker container that has all our launcher tools. The prompt will look something like this (the hostname, "f27e86874dfb" in this case, will be different):

    [LAUNCHER 3.1.3] ubuntu@f27e86874dfb:~/arch3$


###Running workflows

The Pancancer Launcher can generate a template INI file for workflows. To see which workflows are available, you can use the command `pancancer workflows list`:

```
$ pancancer workflows list
Available workflows are:
Sanger
HelloWorld
BWA
DKFZ_EMBL
```

For more information about these workflows and how to configure their INI files, see the workflows' home pages:

 - [Sanger](https://github.com/ICGC-TCGA-PanCancer/SeqWare-CGP-SomaticCore)
 - [BWA](https://github.com/ICGC-TCGA-PanCancer/Seqware-BWA-Workflow)
 - [DKFZ/EMBL](https://github.com/ICGC-TCGA-PanCancer/DEWrapperWorkflow)
 - HelloWorld - This is a very simple workflow that is good to use when testing basic setup and infrastructure.

####Generating an INI file
To generate an INI file:
```
$ pancancer workflows config --workflow HelloWorld
```

A new HelloWorld-specific INI file should be generated in `~/ini-dir`.

The generated file has *default* values only. Sometimes, you may need to edit these INI files with your own specific values. For example, for the Sanger workflow, you may need to change the IP address of the tabix server. Other workflows will have other edits that may be necessary.

<!-- TODO: Add links to workflows (done!) with details about the INI files (not yet) -->

**You will want to edit this file before generating job requests. Please make any workflow-specific changes now, before continuing.**

####Generating a work order
A work order is contains information about what work needs to be done, and what kind of VM needs to be provisioned for it.

To generate work order for a workflow:
```
$ pancancer generator --workflow HelloWorld
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

The process that provisiones VMs should detect this request and begin provisioning a new VM. Provisioning may take several minutes. There are a few ways that you can monitor progress. You can watch the progress using this command:
```
$ tail -f provisioner.out
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

At this point, you have successfully installed the Pancancer Launcher, and used it to schedule and execute a workflow!

When looking at your AWS EC2 console, you will notice that when a workflow finishes successfully, the VM it was running on will have been automatically terminated. This is done to save on computing resources. The pancancer workflows write their data to GNOS repositories (AWS S3 support will be coming) before their VM is terminated. The VM that is serving as your launcher will *not* be terminated until you choose to do so.

<!-- TODO: Add section on failed workflow -->

If a workflow fails, you will see that its status is "FAILED". The VM where the failed workflow ran will *not* be terminated. You will need to log in to this VM using ssh to examine the workflow output to determine why it failed, and troubleshoot the problem.

<!-- TODO: Fill in more detail here. currently, the user will have to know to configure the INI for where output goes, but maybe if we just have links to all workflow main pages, we can just reference the section that details where output goes...?
Most workflows will write their results to a GNOS respository or an AWS S3 bucket, so you will want to check there for -->

<!-- TODO: Add section on reporting tool -->


###What's next?
In this guide, we executed a single HelloWorld workflow. Now that you are familiar with some of the capabilities of the Pancancer Launcher, you can understand how it can be used to schedule and execute larger groups of workflows.

<!-- TODO: Should we eventually have a tool that lets the use create n INI files? Might not be that hard, will need to investigate... -->
Your next step, now that you have successfully run one workflow on one VM, could be to create several INI files (you can use `pancancer workflows config --workflow <SOME WORKFLOW NAME>` to create a default INI file and then copy it as many times as you need and edit the copies) and then execute them in a larger fleet.

###Other useful tips

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
$ pancancer sysconfig --force
$ pancancer coordinator start
$ pancancer provisioner start
```
