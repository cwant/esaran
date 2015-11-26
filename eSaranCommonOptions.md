

# eSaran Common Options #

Options that specify the username and host are examples of options that are frequently needed in eSaran wrappers. We will discuss these options below from both a end user perspective, and from a programming perspective.

In the discussion below, **`parser`** is a Parser object from the Optparse module. The Optparse parser outputs an object with options as attributes, and **`options`** is the dict that has been converted from this object (attributes become dictionary items).


---


## Account Options ##

These options are added to a wrapper by using the function
```
eSaran.add_account_options(parser)
```

This function will add a group of options to the parser with the heading **'Account options'**. The options added are:

### -H / --host ###

The string included with this option will be stored in **`options["host"]`** after parsing.

This will be the remote host where the compute job will be queued.

### -u / --user ###

The string included with this option will be stored in **`options["user"]`** after parsing.

This will be the username of the account on the remote host where the compute job will be queued. If this is not supplied, the wrapper will try to guess a value based on the username on the local machine.

### -D / --dir ###

The string included with this option will be stored in **`options["dir"]`** after parsing.

This is the directory on the remote machine under which a temporary working directory will be created. If not specified, the wrapper will try to guess a value based on the location of the scratch space of the remote machine.

### -e / --email ###

The string included with this option will be stored in **`options["email"]`** after parsing.

This is the email address where the user will receive information about the compute job. If the user does not supply a value for this, a value will be guessed based on the username.

### -k / --key ###

The string included with this option will be stored in **`options["key"]`** after parsing.

This option is used to specify a specific ssh key to be used to submit the job. By default, the wrapper will try to use the default key used by ssh/scp, if it exists.


---


## File Transfer Options ##

These options are added to a wrapper by using the function
```
eSaran.add_file_transfer_options(parser)
```

This function will add a group of options to the parser with the heading **'File transfer options'**. The options added are:

### -i / --input ###

The string included with this option will be stored in **`options["input"]`** after parsing.

This option is used to specify a (space separated) list of files to transfer over to the remote computing resource. Wild cards may be used. If this option is not specified, the program will send over all files (and subdirectories) in the current directory.

### -o / --output ###

The string included with this option will be stored in **`options["output"]`** after parsing.

This option is used to specify a (space separated) list of files to transfer from the remote computing resource to the local machine, one the job has completed. Wild cards may be used. If this option is not specified, the program will send all files (and subdirectories) in the remote working directory.

### -r / --rsync ###

This flag will cause a **`True`** value to be stored in **`options["rsync"]`** after parsing (default is **`False`**).

Adding this flag will cause rsync to be used to transfer files, instead of scp.


---


## PBS Options ##

These options are added to a wrapper by using the function
```
eSaran.add_pbs_options(parser)
```

This function will add a group of options to the parser with the heading **'Job Scheduling options'**. The options added are:

### -Q / --queue ###

The string included with this option will be stored in **`options["queue"]`** after parsing.

This option indicated the remote PBS queue to submit the compute job to. If this option is excluded, the default PBS queue will be used.

### -E / --notify ###

The string included with this option will be stored in **`options["notify"]`** after parsing.

This string is used to tell PBS when to email notifications about the user's compute job. The options, which may be used together are:

  * **b**: before the job runs
  * **a**: after the job runs
  * **e**: on errors.

The default for this is **"bea"**.

### -N / --jobname ###

The string included with this option will be stored in **`options["jobname"]`** after parsing.

This sets the PBS job name. Default is "job1".

### -M / --mem ###

The string included with this option will be stored in **`options["mem"]`** after parsing.

This sets the total memory required by the job. E.g., "512mb". Default is left up to the PBS installation. Note: this option may not be available on all systems.

### -m / --pvmem ###

The string included with this option will be stored in **`options["pvmem"]`** after parsing.

This sets the per-processor virtual memory for the job. E.g., "512mb". Default is left up to the PBS installation. Note: this option may not be available on all systems.

### -n / --nodes ###

The string included with this option will be stored in **`options["nodes"]`** after parsing.

This sets the number of nodes needed to run the job. Default is left up to the PBS installation. Note: this option may not be available on all systems.

### -P / --procs ###

The string included with this option will be stored in **`options["procs"]`** after parsing.

This sets the number of processors needed to run the job. Default is left up to the PBS installation. Note: this option may not be available on all systems.

### -p / --ppn ###

The string included with this option will be stored in **`options["ppn"]`** after parsing.

This sets the processors-per-node required for the job. Default is left up to the PBS installation. Note: this option may not be available on all systems.

### -w / --walltime ###

The string included with this option will be stored in **`options["walltime"]`** after parsing.

This sets the amount of walltime required for the job. Format is "HH:MM:SS". Default is "24:00:00".

### -j / --jobid ###

The string included with this option will be stored in **`options["jobid"]`** after parsing.

This sets the name of the job identifier file associated for the job. If not specified, the file name is automatically generated.

### -t / --test ###

This flag will cause a **`True`** value to be stored in **`options["test"]`** after parsing (default is **`False`**).

This flag will cause the wrapper to generate a submission script without actually transferring files and submitting the job.


---


## Miscellaneous Options ##

These options are added to a wrapper by using the function
```
eSaran.add_misc_options(parser)
```

This function will add a group of options to the parser with the heading **'Miscellaneous options'**. The options added are:

### -v / --verbose ###

This flag will cause a **`True`** value to be stored in **`options["verbose"]`** after parsing. This flag is redundant, since the default value is **`True`**.

This is the opposite of the **`--quiet'** flag below.

### -q / --quiet ###

This flag will cause a **`False`** value to be stored in **`options["verbose"]`** after parsing.

This flag suppresses most of the output of the wrapper.

### -d / --debug ###

This flag will cause a **`True`** value to be stored in **`options["debug"]`** after parsing (default is **`False`**).

This flag will keep intermediate files around after the job is run, which can be helpful for diagnosing problems.


---


## Execution Options ##

These options are added to a wrapper by using the function
```
eSaran.add_execution_options(parser)
```

This function will add a group of options to the parser with the heading **'Execution options'**. The options added are:

### -g / --gui ###

This flag will cause a **`True`** value to be stored in **`options["gui"]`** after parsing (default is **`False`**).

Using this option will cause a wxPython GUI to appear with most of the options available to edit.

### -l / --load-options ###

The string included with this option will be stored in **`options["load_options"]`** after parsing.

This option is used to specify a file to read the current set of options from. The data read from the file is the **`options`** dict, read using the standard python Pickle module. The options read from file will not overwrite any other options that are specified using command line arguments.

### -s / --save-options ###

The string included with this option will be stored in **`options["save_options"]`** after parsing.

This option is used to specify a file to write the current set of options to. The data written to the file is the **`options`** dict , written using the standard python Pickle module.