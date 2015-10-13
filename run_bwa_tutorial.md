# Pancancer Launcher CLI - BWA Tutorial
## Running the BWA workflow

This tutorial will walk you through the process of running the BWA workflow on a VM launched by the Pancancer Launcher, in Amazon EC2. It will use Amazon S3 buckets for the upload/download repositories.

This tutorial assumes you have read the [Quick Start](QuickStart.md) guide and are familiar with the basic Pancancer Launcher concepts.

### Setting up the S3 buckets.
Running BWA in S3 assumes you have permission to upload to an S3 bucket and download from and S3 bucket. It also assumes that you can create buckets and directories to download from.

BAM files must be placed in directories which are named with their UUID. For our test example in the `bwa.test.download` bucket, the directory structure looks like this:

```
bwa.test.download /
    4fb18a5a-9504-11e3-8d90-d1f1d69ccc24 /
        analysis.xml
        experiment.xml
        hg19.chr22.5x.normal2.bam
        run.xml
    9c414428-9446-11e3-86c1-ab5c73f0e08b /
        analysis.xml
        experiment.xml
        hg19.chr22.5x.normal.bam
        run.xml
```
 

### Setting up the INI files.
To create an INI file for Worker VMs to use, use the following command:

```
$ pancancer workflows config --workflow BWA
```

You will see that a new INI file has been generated in `~/ini-dir`.

You will need to edit this new INI file to instruct the BWA workflow to use AWS S3. To do this, ensure that this new line is in the INI file:

```
useGNOS=false
```
When `useGNOS` is set to false, the workflow will use S3 for its upload and download functions.

Next, set the download and upload URLs.

The input URLs should be a comma-separated list of URLs that point to the directories which you want to download:
```
input_file_urls=s3://bwa.test.download/4fb18a5a-9504-11e3-8d90-d1f1d69ccc24,s3://bwa.test.download/9c414428-9446-11e3-86c1-ab5c73f0e08b 
```

The workflow will assume that `s3://bwa.test.download/4fb18a5a-9504-11e3-8d90-d1f1d69ccc24` is a path to a _directory_ that contains the BAM files for a given sample. 

The upload URL will determine where the output files go. 
```
output_file_url=s3://bwa.test.download/results/
```
This will tell the workflow to upload files into the `bwa.test.download` bucket, in the `results` directory. When this executes, the directory structure of this bucket will look like:

```
bwa.test.download /
    4fb18a5a-9504-11e3-8d90-d1f1d69ccc24 /
    9c414428-9446-11e3-86c1-ab5c73f0e08b /
    results /
        merged_output.bam
        merged_output.unmapped.bam
```


### Setting up the credentials files.
Ensure that your AWS Key and Secret Key are in `~/.aws/config`. _Copy_ this file to `~/.gnos/config`. On the worker, BWA will look in its `~/.gnos` directory for credentials. We can put the AWS credentials there and BWA will be able to use them to authenticate with S3.

### Running the Generator
You should now be ready to run the Generator to generate the work order. Run this command:
```
$ pancancer generator --workflow BWA
```