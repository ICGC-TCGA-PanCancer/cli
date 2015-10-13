# Changes

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
