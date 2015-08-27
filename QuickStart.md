#Pancancer CLI

This quick-start guide will help you get started using the Pancancer CLI tool.

##Getting started

1. Launch a new VM in Amazon EC2 (This guide will assume you are using us-east-1 AKA North Virginia).
2. Download the [bootstrap script](scripts/install_bootstrap)
3. Execute the bootstrap script:
```
$ bash install_bootstrap
```
4. This script will install docker, the pancancer_launcher image, and collect some basic configuration info to get the launcher started.

##Inside the Pancancer Launcher.

The main tool for interacting with the Pancancer components is simply named `pancancer`. You can invoke Pancancer commands from the command line like this:
```
$ pancancer coordinator start
```
This example command will start the Pancancer coordinator service.

You can also work with the pancancer tool's interactive shell simply by executing the command `pancancer`:
```
$ pancancer
(pancancer) coordinator start
```
In this example, the user has started the interactive shell, as can be seen by the shell prompt, which has changed from `$` to `(pancancer)`.

To get a list of all pancancer commands, you can type `pancancer -h` and the help text will be displayed.

##Configuration

Once you are in the Pancancer Launcher docker container, you will to do some basic pancancer system configuration. You can do this using the command:
```
$ pancancer sysconfig
```
You should do this before you run any workflows.

##Running workflows

The Pancancer Launcher can generate a template INI file for workflows (you can see which workflows are available with the command `pancancer workflows list`), but you may want to edit these before executing the workflow.

To generate an INI file:
```
$ pancancer workflows config --workflow BWA
```

A new BWA-specific INI file should be generated in `~/ini-dir`. You will want to edit this file before generating job requests.

To generate job requests for a workflow:
```
$ pancancer generator --workflow BWA
```
The generated jobs will use the INI files in `~/ini-dir` so it is important to make any necessary edits before this step!
