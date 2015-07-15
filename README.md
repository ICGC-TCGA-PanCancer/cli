# Overview

This is a common pancancer command line interface that does two major things:

* includes an `install_bootstrap` script that installs Docker and the PanCancer launcher
* within the launcher, a `pancancer` script that simply wraps the tools clouds shepherds use behind a common command line

# Bootstrap Install

A user executes this on a Linux VM or host and this gets them setup with Docker, a Launcher container, and the various configurations needed to parameterize the Docker-based launcher.

    wget -qO- https://get.pancancer.info/ | sh

# Launcher PanCancer Command

See the specification at the [CLI](https://wiki.oicr.on.ca/display/PANCANCER/PanCancer+Command+Line) wiki page.
