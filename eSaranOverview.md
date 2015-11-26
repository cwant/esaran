# eSaran #

The eSaran project strives to make high performance computing (HPC) accessible to researchers who may not have a computational background.

This is achieved in two ways:

1) By providing a series of wrappers for popular HPC programs that the user can run on their local machine to make the network and queuing system more transparent;

2) By providing an API that programmers can use to easily make their own wrappers for submitting jobs.

This wiki aims to document these two parts:

  * [Wrapper Scripts](eSaranWrappers.md)
  * [Programming API](eSaranAPI.md)

# Anatomy of a wrapper #

There are a few approaches to writing wrappers with the eSaran API, but regardless of which way is used, a wrapper will generally do the following:

  * The wrapper is configured, either by loading a configuration file or through API calls, to accept various command line options. Hosts that the wrapper can submit jobs to are specified;
  * The wrapper reads the user's command line options and parses them;
  * Validation of options is performed;
  * The wrapper connects to the remote machine via ssh (preferably through an agent holding keys) and the remote work directory is created;
  * Needed files for the job are transfered to the remote host, including a submission script for the queuing system. This is often done with either rsync or with scp;
  * The job is queued and eventually should run;
  * The user will receive an email stating that the job has completed. If the user had used scp to transfer files, the output will be attached to this email if it is of an agreeable size (if too large, it will be hosted on a web server). If the user is using rsync to transfer files, they can use it to retrieve their output;
  * The remote work directory is cleaned;