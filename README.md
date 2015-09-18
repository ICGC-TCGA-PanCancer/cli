# Overview

The Pancancer CLI is a tool that allows you to provision and manage a fleet of virutal machines in a cloud environment (such as Amazon EC2), and execute Pancancer workflows on them.

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

# Launcher PanCancer Command

See the specification at the [CLI](https://wiki.oicr.on.ca/display/PANCANCER/PanCancer+Command+Line) wiki page.
