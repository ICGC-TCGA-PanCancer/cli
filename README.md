# Overview

The Pancancer CLI is a tool that allows you to provision and manage a fleet of virtual machines in a cloud environment (such as Amazon EC2), and execute Pancancer workflows on them.

<!-- TODO: A little more detail here, and a "how it works" section -->
<!-- This section needs more work.
How the Pancancer CLI can help you:

 - Provision VMs - as many or as few as the user needs.
 - Deploy and execute Pancancer workflows on VMs.
 - Monitor the health and status of VMs and the workflows running on them.
-->

# Bootstrap Install

A user executes this on a Linux VM or host and this gets them setup with Docker, a Launcher container, and the various configurations needed to parameterize the Docker-based launcher.
```
$ wget -qO install_bootstrap https://raw.githubusercontent.com/ICGC-TCGA-PanCancer/cli/develop/scripts/install_bootstrap && bash install_bootstrap
```

# QuickStart guide
The Quick Start guide can be found [here](QuickStart.md).

## Notes for Testing Pre-Release Branches

This feature branch makes changes to the bootstrap script to include:

```
WORKFLOW_LISTING_URL=${workflow_listing_url}
```

In the `~/.pancancer/pancancer.config ` file on the host VM.  This is further
converted to `~/.pancancer/simple_pancancer_config.json` within the launcher.
These files need to be updated in the launcher container to contain the `workflow_listing_url`
parameter.

```
{
    "aws_key": "*****",
    "aws_secret_key": "*****",
    "max_fleet_size": "5",
    "name_of_key": "my-key",
    "path_to_key": "/home/ubuntu/.ssh/my-key.pem",
    "security_group": "launch-wizard-***",
    "workflow_listing_url": "https://raw.githubusercontent.com/ICGC-TCGA-PanCancer/cli/feature/solomon_workflowlist_from_url/config/workflowlist.json"
}
```

You also need to update the `~/arch3/cli` to be whatever branch is currently being used, e.g.:

```
[LAUNCHER 3.1.7] ubuntu@490276e119cf:~/arch3/cli$ git checkout feature/solomon_workflowlist_from_url
Branch feature/solomon_workflowlist_from_url set up to track remote branch feature/solomon_workflowlist_from_url from origin.
Switched to a new branch 'feature/solomon_workflowlist_from_url'
```

# Launcher PanCancer Command

See the specification at the [CLI](https://wiki.oicr.on.ca/display/PANCANCER/PanCancer+Command+Line) wiki page.
