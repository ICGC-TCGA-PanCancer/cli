# Changes

## L4A_1.0.0
 - Add simple question to install_bootstrap asking if user is OK with tracking/logging usage.
 - New AMI ID for BWA.

## L4A_1.0.0-rc.3
 - Allow user to set spot price via `pancancer sysconfig --force`.
 - Minor bug fixes.
 - Documentation updates.

## L4A_1.0.0-rc.2
 - Update documentation
 - Update mustache template for absolute path for server-tags.json
 - Small improvements for insall_bootstrap, including better error handling.

## L4A_1.0.0-rc.1
 - Update documentation
 - Minor tweaks to bootstrap script

## L4A_1.0.0-rc.0
 - Restrict CLI to only work with BWA on AWS ("L4A" ==> "Launcher for Amazon"). This involved simplifying or changing a number of commands. Documentation has also been updated.
 - New version of consonance: 1.1-rc.1

## 0.0.7
 - Minor documentation updates
 - Added new "--keep_failed" option for generator to prevent failed workers from being reaped (useful for debugging)
 - Fixed some logic bugs in generator related to updating the master config file.
 - Minor updates to install_bootstrap (changed wording of questions, cleaned up some old code).
 - Added version numbers to workflow names in descriptors in workflowlister.py
 - Set reap\_failed\_workers and check\_previous\_job\_hash to null in mustache template - these will be directly set by the generator.
 - A number of smaller bug fixes.

## 0.0.6
 - Updated documentation
 - Added BWA tutorial
 - Code fixes:
  - Fixes for working with workflows that are stored in S3
  - Reset "check\_previous\_job\_hash" back to True
 - Added BWA to workflow lister with new AMI ID
 - Updated consonance version to 1.1-beta.rc.0
 - Set "reap\_failed\_workers" to True in mustache template, so ALL workers will be reaped by default.

## 0.0.5
 - Updated documentation
 - Added "--force" option for generator which will change config/masterConfig.ini:check_previous_job_hash to false
 - Cleaned up some of the code for provisioner/coordinator control
 - Added new "job_results" sub command to "status" command to write jobs results (stdout or stderr) to files.
 - Added a "--force" option to sysconfig
 - update version of consonance (arch3) to 1.1-beta.6
 - Pancancer template: Remove slack_token; fixed "youxia_reaper_parameters"; added "reap_failed_workers"
 - updated workflow lister to only show HelloWorld (with new AMI ID) until other workflows are ready.
