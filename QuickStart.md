#Pancancer CLI

This quick-start guide will help you get started using the Pancancer CLI tool.

The Pancancer CLI tool is a command-line interface tool that will allow you to interact with the pancancer components. The Pancancer CLI tool can be used to schedule and execute Pancancer workflows (include BWA, Sanger, and DKFZ/EMLB) on a fleet of VMs in a cloud-computing environment.

Diagram showing S3->workflow(s)->S3 out.  People need to realize if they can do this for one they can do it for 500.  We need S3 support in our workflows (inputs and outputs).

##What You Need

Before you get started, there are a few items you will need to have available:
 - A valid account on Amazon AWS EC2, with access to the "us-east-1" (North Virginia) AWS region.
 - A valid key file that you can use to log in to your EC2 VMs. Click [here](http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-key-pairs.html) for a document about how to generate these pem keys.
 - Valid GNOS key files.
 - Your AWS Key and Secret Key. If you don't know your Key and Secret Key, [this](http://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSGettingStartedGuide/AWSCredentials.html) document may be able to help you.


##Getting started

### Launch a VM
Launch a new VM in Amazon EC2. You **must** use the AWS region "us-east-1" (AKA North Virginia) for this tutorial to work. If you are unfamiliar with the process of launching VMs in Amazon EC2, you may want to read [this guide](http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/LaunchingAndUsingInstances.html). When setting up your instance, be sure to include enough storage space to install docker and download docker images. 40 GB should be enough. The instance type normally used for this is m3.large.


Once the VM is running, log in to your new VM over ssh. If you are not sure how to connect to your VM using ssh, right-click on your VM in the AWS EC2 Management Console and click "connect". You will get a detailed information from AWS about how to connect to your VM.


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
$ wget -qO install_bootstrap https://raw.githubusercontent.com/ICGC-TCGA-PanCancer/cli/develop/scripts/install_bootstrap && bash install_bootstrap
```
This script will install docker, the pancancer_launcher image, and collect some basic configuration info to get the launcher started.

**NOTE:**
Please be aware that if docker has not been installed on your VM before, you *will* need to log out and log in again for user permission changes to take effect (the script will exit automatically at this point to let you do this). This will *only* happen the first time that docker is installed.

<!-- TODO: make the printed message all caps in the bootstrap! -->

**After logging out and logging back in to your VM**, you can resume the setup process by simply typing:

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

<!-- TODO: start_services_in_container: less noisy startup process , write to a log file, but not on console. -->

If you follow the directions above you will find yourself dropped into the docker container that has all our launcher tools. The prompt will look something like this (the hostname, "f27e86874dfb" in this case, will be different):

    [LAUNCHER 3.1.3] ubuntu@f27e86874dfb:~/arch3$

###Configuration

Once you are in the Pancancer Launcher docker container, you will want to do some basic pancancer system configuration. You can do this using the command:
```
$ pancancer sysconfig
```
<!-- TODO: Ask these questions in the bootstrap script so there is less to do when they get in -->
You should do this before you run any workflows. This configuration tool will ask you questions about:
 - How many VMs you want in your fleet.
 - The name of the AWS Security Group you would like your VMs to be a part of. If you do not specify a security group, the security group name "default" will be used. You may have to configure your Security Group to allow inbound TCP connections from the *public* IP address of the machine on which the pancancer launcher is running. This is **necessary** for provisoning to work. If you are not familiar with working with AWS EC2 Security Groups, you may want to read [this document](http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-network-security.html).

If the tool detects missing values for AWS Key, AWS Secret Key, the path to the pem key, or the key name, it may ask you to fill in these values.

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

####Generating an INI file
To generate an INI file:
```
$ pancancer workflows config --workflow HelloWorld
```

A new HelloWorld-specific INI file should be generated in `~/ini-dir`.

The generated file has *default* values only. Sometimes, you may need to edit these INI files with your own specific values. For example, for the Sanger workflow, you may need to change the IP address of the tabix server. Other workflows will have other edits that may be necessary. <!-- TODO: Add links to workflows with details about the INI files -->

**You will want to edit this file before generating job requests. Please do this now, before continuing.**

####Generating a job request
To generate job requests for a workflow:
```
$ pancancer generator --workflow HelloWorld
```
<!-- TODO: auto-backup old INI files? -->
The job generator will attempt to generate one job for *each and every* INI file in `~/ini-dir`. It is important to ensure that this directory *only* contains INI files for jobs you wish to run, *and* that you have made any necessary edits to them.

<!-- TODO: need to have some output even if it's OK! -->

<!-- TODO: need better notes on contents of ini-dir, need to move ini out of here once submitted. or not? hash check should prevent duplicates... -->

You can verify that your job request has been enqueued with this command:
```
$ pancancer status queues
```
You should see that some queues have a message in them.
<!-- TODO: Simpler output for 'pancancer status queues' -->
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
The provisioner will provision new VMs. It is these VMs that will execute your jobs. This process will write to a file named `provisioner.out`. More detailed output can also be found in `arch3.log`.

Provisioning may take several minutes. There are a few ways that you can monitor progress. You can watch the progress using this command:
```
$ watch tail -n 30 provisioner.out
```
Type <kbd>Ctrl</kbd>-<kbd>C</kbd> to terminate `watch`.

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

When the job has completed successfully, you should see a result that looks like this:

```
$ pancancer status jobs
 status  | job_id |               job_uuid               |  workflow  |      create_timestamp      |      update_timestamp
---------+--------+--------------------------------------+------------+----------------------------+----------------------------
 SUCCESS |      1 | a3a4da7b-2136-4431-a117-e903590c05d8 | HelloWorld | 2015-09-02 19:45:26.023313 | 2015-09-02 20:04:27.033118
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
$ pancancer sysconfig
$ pancancer coordinator start
$ pancancer provisioner start
```
