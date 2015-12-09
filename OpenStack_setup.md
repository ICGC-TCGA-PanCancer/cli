# PanCancer CLI on OpenStack

This document will cover some of the differences you may notice when running the launcher on OpenStack

## Initial questions

The installer script will ask OpenStack-specific questions when you run the PanCancer launcher on OpenStack. These questions will ask you about:

 - Your OpenStack username. This should be formatted as `<tenant>:<username>`. For example: `sweng:bob` should be entered if your username is `bob` for the `sweng` tenant.
 - Your OpenStack password.
 - The URL for your OpenStack endpoint. It will probably look something like this:  http://10.5.73.21:5000/v2.0
 - The OpenStack Region in which the launcher should be running.
 - The Security Group for your launcher.
 - The Network ID of the network that the launcher will be running in.
 - The OpenStack Zone. This is optional.
 
## Running the Generator

When you run the generator, you may be prompted to enter the name of an OpenStack workflow configuration name.
This is because it is possible for different OpenStack environments to use different configurations for the same workflow. Variations might be the base imaged ID and flavour. 