#AWS Pancancer Workflow Launcher & CLI (L4A)

This guide will help you get started using the Pancancer CLI tool on Amazon's cloud.  **You are responsible for your cloud expenses for this tutorial, be careful to monitor your usage and terminate VMs when you are finished.**

The Pancancer Workflow Launcher and Command Line Tool (CLI) L4A ("Launcher For Amazon") is a system that will allow you to schedule and execute the BWA Pancancer workflow on a fleet of virtual machines in a Amazon's EC2 cloud-computing environment.

![Pancancer CLI Diagram - Overview](/images/Pancancer_CLI_system_diagram.png?raw=true "Click for larger view")

The diagram above shows some detail about how the Pancancer Workflow Launcher and CLI tool are used to manage a fleet of VMs executing pancancer workflows. The details of how this is done can be found in the document below.

##What You Need

Before you get started, there are a few items you will need to have available:
 - A valid account on Amazon AWS EC2, with access to the "us-east-1" (North Virginia) AWS region.
 - A valid key file that you can use to log in to your EC2 VMs. Click [here](http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-key-pairs.html) for a document about how to generate these pem keys.
 - Your AWS Key and Secret Key. If you don't know your Key and Secret Key, [this](http://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSGettingStartedGuide/AWSCredentials.html) document may be able to help you.
 - If you are downloading or uploading data from/to a GNOS respository, you will need a valid GNOS key. If you are only working with S3 then a GNOS key will not be necessary.

