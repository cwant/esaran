#!/usr/bin/env python
#
# $Id$
#
# Copyright (c) 2009, Chris Want, Research Support Group,
# AICT, University of Alberta. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without 
# modification, are permitted provided that the following conditions are met:
#
# 1) Redistributions of source code must retain the above copyright 
#    notice, this list of conditions and the following disclaimer.
# 2) Redistributions in binary form must reproduce the above copyright 
#    notice, this list of conditions and the following disclaimer in the 
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE 
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE 
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE 
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR 
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF 
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS 
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN 
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) 
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF 
# THE POSSIBILITY OF SUCH DAMAGE.
#
# Contributors: Chris Want (University of Alberta),
#
"""
Helper module for executing PBS jobs remotely.
"""

# Set a few defaults, and ensure that dict entries exist
default_options = {
    'user'     : "",
    'host'     : "cluster.srv.ualberta.ca",
    'dir'      : "",
    'email'    : "",
    'key'      : "",
    'jobname'  : "job1",
    'queue'    : "",
    'pvmem'    : "",
    'mem'      : "",
    'nodes'    : "",
    'ppn'      : "",
    'procs'    : "",
    'walltime' : "24:00:00",
    'notify'   : "bea",
    'input'    : "",
    'output'   : "",
    'rsync'    : False,
    'verbose'  : True,
    'jobid'    : "",
    'debug'    : False
    }

### Main Entry Point
#
# Callback prototypes:
#
#     get_wrapper_cmdline(config, options)
#
#     add_wrapper_options(parser, config)
#
#     wrapper_gui_options(subpanel, config, options)
#
#     add_wrapper_validators(config)
#
def do_wrapper(get_wrapper_cmdline="",
               wrapper_title="",
               add_wrapper_options=None,
               wrapper_gui_options=None,
               add_wrapper_validators=None,
               configfileXML=""):

    config = get_config(get_wrapper_cmdline,
                        wrapper_title,
                        add_wrapper_options,
                        wrapper_gui_options,
                        add_wrapper_validators,
                        configfileXML)

    options = get_options(config)

    validate_options(config, options)
    if (options["save_options"]):
        save_options(options, options["save_options"])

    # Set up ssh keys, respawning if needed
    set_up_ssh(config, options)
    (jobid, workdir) = submit_job(config, options)

    if (options['verbose']):
        print_job_summary(options, jobid, workdir)

    jobid_out = write_jobid_file(options, jobid, workdir)

    return (jobid, workdir)

def print_job_summary(options, jobid, workdir):
    print "Job submission summary:"
    print "  Username: ", options['user']
    print "  Host name: ", options['host']
    print "  Your PBS Job ID is ", jobid
    print "  The remote working directory is ", workdir

def write_jobid_file(options, jobid, workdir):
    import pickle, sys, os

    if (len(options["jobid"])>0):
        file = options["jobid"]
    elif (len(options["jobname"])>0):
        file = "%s_%s_%s.out" % (options["jobname"], jobid, os.getpid())
    else:
        file = "%s_%s.out" % (jobid, os.getpid())

    try:
        f = open(file, "wb")
    except:
        sys.stderr.write("Unable to open file '%s' for saving!\n" % (file))
        sys.exit(1)

    pickle.dump(options, f)
    pickle.dump(jobid, f)
    pickle.dump(workdir, f)
    f.close()

    if options['verbose']:
        print "-----------------------------------"
        print "Wrote job identifier file: %s" % (file)
        print "  To check the status of your job, use:"
        print "     python job_status.py %s" % (file)
        print "  To delete your job, use:"
        print "     python job_delete.py %s" % (file)
        print "  You will recieve an email when your job is finished."
        if (options['rsync']):
            print "  To recieve your output, use:"
            print "     python job_fetch.py %s" % (file)
        else:
            print "  Your output will be attached to the email."
        print "-----------------------------------"
        print "  To remove the remote working directory of your job, use:"
        print "     python job_clean.py %s" % (file)

    return file

def read_jobid_file(file):
    import pickle

    try:
        f = open(file, "rb")
    except:
        sys.stderr.write("Unable to open file for loading!\n")
        sys.exit(1)

    options = pickle.load(f)
    jobid   = pickle.load(f)
    workdir = pickle.load(f)

    f.close()

    return (options, jobid, workdir)

### Get Config
def get_config(get_wrapper_cmdline="",
               wrapper_title="",
               add_wrapper_options=None,
               wrapper_gui_options=None,
               add_wrapper_validators=None,
               configfileXML=""):

    import sys

    hosts = get_hosts_config_XML("hosts.xml")

    config = dict( {\
        'hosts'            : hosts,
        'validators'       : get_validators(),
        'webserver_site'   : "https://sciviz.nic.ualberta.ca/~cwant/hpc_web",
        'webserver_address': "cwant@sciviz.nic.ualberta.ca",
        'webserver_subject': "HPC output download ready" } )

    if (configfileXML):
        add_config_XML(config, configfileXML)
        config["wrapper_title"] = config["wrapper"]["wrapper_title"]
        config["get_wrapper_cmdline"] = get_wrapper_cmdline_XML
        config["add_wrapper_options"] = add_wrapper_options_XML
        config["wrapper_gui_options"] = wrapper_gui_options_XML
    else:
        config["wrapper_title"] = wrapper_title
        config["get_wrapper_cmdline"] = get_wrapper_cmdline
        config["add_wrapper_options"] = add_wrapper_options
        config["wrapper_gui_options"] = wrapper_gui_options

    if (add_wrapper_validators):
        add_wrapper_validators(config)

    #if not config["get_wrapper_cmdline"]:
    #    print("Do not know how to create command line!")
    #    sys.exit(1)

    return config

def get_options(config):
    import os, optparse

    if (os.getenv("SSH_AGENT_RESPAWN")):
        # We have been respawned, load pickled options
        options = load_wrapper_args()
    else:
        parser = optparse.OptionParser()
        if (config["add_wrapper_options"]):
            config["add_wrapper_options"](parser, config)
        add_account_options(parser, config)
        add_file_transfer_options(parser, config)
        add_pbs_options(parser, config)
        add_misc_options(parser, config)
        add_execution_options(parser, config)

        parser.seen = dict()
        (options_obj, args) = parser.parse_args()
        options = obj_to_dict(options_obj)
        options["args"] = args
        seen    = parser.seen

        read_merge_user_defaults(options, seen)
        make_account_defaults(config, options, seen)

        if (options["load_options"]):
            load_merge_options(options, options["load_options"], seen)
        if (options["gui"]):
            make_gui(config, options, config["wrapper_gui_options"])

        options['seen'] = seen

    return options
    
def obj_to_dict(options_obj):
    options = dict()
    for key, val in vars(options_obj).iteritems():
        options[key] = val
    return options

def load_wrapper_args():
    # Load pickled command line options and positional args
    import pickle, sys

    options = pickle.load(sys.stdin)

    return options

def load_merge_options(options, file, seen=None):
    # Load pickled command line options and positional args
    import pickle

    try:
        f = open(file, "rb")
    except:
        sys.stderr.write("Unable to open file for loading!\n")
        sys.exit(1)

    optload = pickle.load(f)
    f.close()

    merge_options(options, seen, optload)

def merge_options(options, seen, optsin):
    # 'options': the regular options dict
    # 'seen'   : records whether the option value in 'options' was set by
    #            the user on the command line (i.e., don't overwrite)
    # 'optsin' : is the dict of options we want to merge into 'options'
    for key, value in optsin.iteritems():
        if seen:
            if not seen.has_key(key):
                options[key] = value
        else:
            options[key] = value

def save_options(options, file):
    import pickle, sys
    try:
        f = open(file, "wb")
    except:
        sys.stderr.write("Unable to open file for saving!\n")
        sys.exit(1)

    pickle.dump(options, f)
    f.close()

def store_seen(option, opt_str, value, parser):
    setattr(parser.values, option.dest, value)
    parser.seen[option.dest] = True

def store_true_seen(option, opt_str, value, parser):
    setattr(parser.values, option.dest, True)
    parser.seen[option.dest] = True

def add_account_options(parser, config):
    import os, optparse

    g = optparse.OptionGroup(parser, "Account options")
    user = os.getenv("USER")

    ### Host
    g.add_option("-H", "--host", action="callback",
                 callback=store_seen, type="string",
                 dest="host", metavar="HOST",
                 default=default_options['host'],
                 help="The name of the host the job will run on " + \
                     "(default: %default)")
    
    ### Username
    if (user):
        g.add_option("-u", "--user", action="callback",
                     callback=store_seen, type="string",
                     dest="user", metavar="USER", default=user,
                     help="The user id used to login to " + \
                         "the HPC resourse (default: %default)")
    else:
        g.add_option("-u", "--user", action="callback",
                     callback=store_seen, type="string",
                     dest="user", metavar="USER",
                     help="The user id used to login to " + \
                         "the HPC resourse")

    ### Work directory
    g.add_option("-D", "--dir", action="callback",
                 callback=store_seen, type="string",
                 dest="dir", metavar="DIRECTORY",
                 default="",
                 help="The directory on the HPC resource under which " + \
                     "a temporary work directory will be created " + \
                     "(default: /scratch/USER or host based location " + \
                     "of scratch space)")

    ### Email
    g.add_option("-e", "--email", action="callback",
                 callback=store_seen, type="string",
                 dest="email", metavar="USER@EXAMPLE.COM",
                 default="",
                 help="The email address for notifications about " + \
                     "errors and job completion " + \
                     "(default: USER@ualberta.ca)")

    ### Key
    g.add_option("-k", "--key", action="callback",
                 callback=store_seen, type="string",
                 dest="key", metavar="KEY",
                 help="Use or specify an ssh key")
    
    parser.add_option_group(g)

def make_account_defaults(config, options, seen):


    if options.has_key("dir") and options["dir"]:
        user = options["user"]
    

    if options["user"]:
        user = options["user"]
        if options["host"] in config["hosts"].keys():
            host = config["hosts"][options["host"]]

        if seen:
            if not seen.has_key("dir") and not options["dir"]:
                dir = host["scratch_base"] + "/" + user
                options["dir"] = dir
            if not seen.has_key("email") and not options["email"]:
                email = user + "@" + host["email_base"]
                options["email"] = email


def add_file_transfer_options(parser, config):
    import os, optparse

    g = optparse.OptionGroup(parser, "File transfer options")

    ### Input
    g.add_option("-i", "--input", action="callback",
                 callback=store_seen, type="string",
                 dest="input", metavar="FILE1 FILE2 ...",
                 default=default_options['input'],
                 help="Files to transfer to remote working directory " + \
                     "(default: send all files in current directory)")
    
    ### Output
    g.add_option("-o", "--output", action="callback",
                 callback=store_seen, type="string",
                 dest="output", metavar="FILE1 FILE2 ...",
                 default=default_options['output'],
                 help="Files to send back to the user on job completion " + \
                     "(default: send all files in remote working directory)")

    ### Rsync
    g.add_option("-r", "--rsync", action="callback",
                 callback=store_true_seen,
                 dest="rsync",
                 default=default_options['rsync'],
                 help="Use rsync to transfer files to the HPC resource " + \
                     "instead of tar/scp")

    ### Add options ########################
    
    parser.add_option_group(g)

def add_pbs_options(parser, config):
    import os, optparse

    g = optparse.OptionGroup(parser, "Job Scheduling options")

    ### Queue
    g.add_option("-Q", "--queue", action="callback",
                 callback=store_seen, type="string",
                 dest="queue", metavar="QUEUE",
                 default=default_options['queue'],
                 help="Queue to submit to (if missing, submit to default " + \
                     "queue for host)")
    
    ### Notify
    g.add_option("-E", "--notify", action="callback",
                 callback=store_seen, type="string",
                 dest="notify", metavar="[b][e][a]",
                 default=default_options['notify'],
                 help="Email notifications before (b) the job runs, " + \
                     "or after (a) the job runs, or on errors (e) " + \
                     "(default: %default)")

    ### Job Name
    g.add_option("-N", "--jobname", action="callback",
                 callback=store_seen, type="string",
                 dest="jobname", metavar="JOBNAME",
                 default=default_options['jobname'],
                 help="The name of the job that is submitted to " + \
                     "the HPC resource (default: %default)")

    ### Memory Requirements
    g.add_option("-M", "--mem", action="callback",
                 callback=store_seen, type="string",
                 dest="mem", metavar="MEM",
                 help="The total amount of memory required")

    ### Per processor Memory Requirements
    g.add_option("-m", "--pvmem", action="callback",
                 callback=store_seen, type="string",
                 dest="pvmem", metavar="MEMORY",
                 help="The amount of per-processor memory required")

    ### Nodes
    g.add_option("-n", "--nodes", action="callback",
                 callback=store_seen, type="int",
                 dest="nodes", metavar="NODES",
                 help="The number of nodes required")

    ### Processors
    g.add_option("-P", "--procs", action="callback",
                 callback=store_seen, type="int",
                 dest="procs", metavar="PROCS",
                 help="The total number of processors required")

    ### Processors per node
    g.add_option("-p", "--ppn", action="callback",
                 callback=store_seen, type="int",
                 dest="ppn", metavar="PROCPERNODE",
                 help="The number of processors per node required")

    ### Wall time
    g.add_option("-w", "--walltime", action="callback",
                 callback=store_seen, type="string",
                 dest="walltime", metavar="WALLTIME",
                 default=default_options['walltime'],
                 help="The maximum time required to run the job " +
                 "(default: %default)")

    ### Job ID
    g.add_option("-j", "--jobid", action="callback",
                 callback=store_seen, type="string",
                 dest="jobid", metavar="FILE",
                 default=default_options['jobid'],
                 help="Write job identifier to specified file " +
                 "(default: automatically generated)")

    ### Add options ########################
    
    parser.add_option_group(g)



def add_misc_options(parser, config):
    import os, optparse

    g = optparse.OptionGroup(parser, "Miscellaneous options")

    ### Verbose
    g.add_option("-v", "--verbose", action="store_true",
                 dest="verbose", default=default_options['verbose'],
                 help="Produce output to terminal")


    ### Quiet
    g.add_option("-q", "--quiet", action="store_false",
                 dest="verbose",
                 help="Silence program output")

    ### Debug
    g.add_option("-d", "--debug", action="store_true",
                 dest="debug", default=default_options['debug'],
                 help="Keep intermediate files around for " +
                 "diagnostic purposes")


    ### Add options ########################
    
    parser.add_option_group(g)


### SSH Routines ###################################

def ssh_keys_loaded():
    import subprocess

    p = subprocess.Popen("ssh-add -L", shell=True,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()
    exitcode = p.wait()

    if (exitcode):
        return False

    return True

def test_ssh_key(options):
    import subprocess
    exitcode = subprocess.call("ssh -o NumberOfPasswordPrompts=0 " + \
                                   "%s -l %s \"date > /dev/null\"" % \
                                   (options["host"],
                                    options["user"]),
                               shell=True)
    if (exitcode):
        return False

    return True

def ssh_need_key(options):
    if ( not ssh_keys_loaded() ):
        # Case where there are no keys
        return True

    # Case where there are keys
    if ( not test_ssh_key(options)):
        return True

    return False

def ssh_run_command(options, command):
    import subprocess

    user = options['user']
    host = options['host']

    ssh_command = "ssh %s@%s \"%s\"" % (user, host, command)

    p = subprocess.Popen(ssh_command, shell=True,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()
    exitcode = p.wait()

    return (exitcode, stdout, stderr)

def set_up_ssh(config, options):
    import sys, os, pickle, subprocess

    # Check if there is an ssh-agent running -- if not, re-run self in
    # an agent.
    try:
        if (options["key"]):
            key = options["key"]
        else:
            key = ""
    except:
        key = ""

    ssh_auth = os.getenv("SSH_AUTH_SOCK")
    if (not ssh_auth):
        os.putenv("SSH_AGENT_RESPAWN", "TRUE")
        pipe = subprocess.Popen("ssh-agent python %s"
                                % sys.argv[0],
                                stdin=subprocess.PIPE, shell=True);
        pickle.dump(options, pipe.stdin)
        pipe.stdin.flush()
        sts = os.waitpid(pipe.pid, 0)
        sys.exit();

    # Check if there are ssh-keys loaded
    if (ssh_need_key(options)):
        # Key needed, so try to add key, note that the variable
        # $key will be empty unless the user used -k

        command = "ssh-add %s" %(key)
        p = subprocess.Popen(command, shell=True,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()
        exitcode = p.wait()

        # Try again to see if the key worked
        if ( not test_ssh_key(options) ):
            # Key didn't work, so educate the user ...
            print("""\
-------------------------------------------------------------------------
To avoid typing your password multiple times, please set up public key
authentication. Please see

  http://www.ualberta.ca/AICT/RESEARCH/LinuxClusters/pka-openssh.html

For assistance, please contact research.support@ualberta.ca
-------------------------------------------------------------------------
""" % locals())

### Job Submission
def submit_job(config, options):
    import os

    executable = config["get_wrapper_cmdline"](config, options)

    workdir  = "%s/%s_%d.tmp" % (options["dir"], options["jobname"],
                                 os.getpid())
    workfile = "%s_%d.tar.gz" % (options["jobname"], os.getpid())

    if options["verbose"]:
        print "Making submission script ..."
    make_pbs_script(executable, workdir, config, options)

    create_workdir(workdir, config, options)

    if options["verbose"]:
        print "Transfering work files..."
    transfer_files(workfile, workdir, config, options)

    if options["verbose"]:
        print "Queueing job ..."
    jobid = queue_pbs_script(workfile, workdir, config, options)

    return (jobid, workdir)

def get_cpu_spec(config, options):
    host = config['hosts'][options['host']]
    cpu_specs = host['pbs_options']['cpu_specs']
    subs = dict()

    # String substitution interprets 'None' as a string, so
    # we need to massage input
    if options['nodes']:
        subs['nodes'] = options['nodes']
    if options['ppn']:
        subs['ppn'] = options['ppn']
    if options['procs']:
        subs['procs'] = options['procs']

    for cpu_spec in cpu_specs:
        # Try to substitute variables from options into the
        # cpu_spec string
        try:
            s = cpu_spec % (subs)
            return s
        except:
            continue
        
    return ""

def get_mem_spec(config, options):
    host = config['hosts'][options['host']]
    mem_specs = host['pbs_options']['mem_specs']
    subs = dict()

    # String substitution interprets 'None' as a string, so
    # we need to massage input
    if options['pvmem']:
        subs['pvmem'] = options['pvmem']
    if options['mem']:
        subs['mem'] = options['mem']
    for mem_spec in mem_specs:
        # Try to substitute variables from options into the
        # mem_spec string
        try:
            s = mem_spec % (subs)
            return s
        except:
            continue
        
    return ""

### Create PBS Script
def make_pbs_script(executable, workdir, config, options):
    import string

    # create dictionary of strings for heredoc substitutions
    subs = dict()
    subs.update(options)
    subs.update(config)
    subs.update(config['hosts'][options["host"]])
    subs['executable'] = executable
    subs['workdir']    = workdir 
    if options["rsync"]:
        rsync_message = """\

Alternatively, you may obtain your output by using:
    rsync -az %(user)s@%(host)s:%(workdir)s/ .

""" % (subs)
    else:
        rsync_message = ""
    subs["rsync_message"] = rsync_message

    if (len(options["output"])>0):
        subs["outfiles"] = options["output"]
    else:
        subs["outfiles"] = "*"

    if (len(options["queue"])>0):
        subs["queue"] = "#PBS -q " + options["queue"]
    else:
        subs["queue"] = ""

    if (subs['mail_host']):
        # if mail_host is set, ssh to the host to send mail
        subs['mail_command'] = "ssh %s@%s '%s -t'" % \
            (subs['user'], subs['mail_host'], subs['sendmail'])
    else:
        # otherwise, just run sendmail
        subs['mail_command'] = "%s -t" % (subs['sendmail'])

    subs['mem_spec'] = get_mem_spec(config, options)
    subs['cpu_spec'] = get_cpu_spec(config, options)

    ### PBS SCRIPT START
    script = """\
#!/bin/bash -l
#PBS -S /bin/bash
#PBS -N %(jobname)s
%(queue)s
%(mem_spec)s
%(cpu_spec)s
#PBS -l walltime=%(walltime)s
#PBS -m %(notify)s
#PBS -M %(email)s

# Run program
cd %(workdir)s
%(executable)s

# Is ${PBS_JOBID} set?
if [ "a${PBS_JOBID}" != "a" ]
then
  OUTPUT="%(user)s_${PBS_JOBID}.zip"
  JOBNAME="PBS job ${PBS_JOBID}"
  SUBJECT="Results from job %(jobname)s (${JOBNAME})"
else
  OUTPUT="%(user)s_%(jobname)s.zip"
  JOBNAME="the job %(jobname)s"
  SUBJECT="Results from job %(jobname)s"
fi

zip -r ${OUTPUT} %(outfiles)s > /dev/null
chmod o+r ${OUTPUT}
ZIPSIZE=`wc -c ${OUTPUT} | cut -d " " -f 1`
if [ ${ZIPSIZE} -lt 5000000 ]
then
# zip file smaller then 5MB, mail to user
(
(cat <<EOF_MAIL
To: %(email)s
Subject: ${SUBJECT}
MIME-Version: 1.0
Content-Type: multipart/mixed; boundary="-q1w2e3r4t5"

---q1w2e3r4t5
Content-Type: text/plain

Here is the output from ${JOBNAME}.
%(rsync_message)s
---q1w2e3r4t5
Content-Type: application; name=${OUTPUT}
Content-Transfer-Encoding: base64
Content-Disposition: attachment; filename="${OUTPUT}"

EOF_MAIL
);
perl -e "
use MIME::Base64 qw(encode_base64);
open(FILE, '%(workdir)s/${OUTPUT}') or die '$!';
while (read(FILE, \$buf, 60*57)) {
	print encode_base64(\$buf);
}";
echo '---q1w2e3r4t5--';
) | %(mail_command)s
else
# zip file too big, signal webserver to pick it up
(cat <<EOF_MAIL
To: %(webserver_address)s
Subject: %(webserver_subject)s
MIME-Version: 1.0
Content-Type: text/plain

Path: %(workdir)s/${OUTPUT}
Host: %(host)s
Username: %(user)s
EOF_MAIL
) | %(mail_command)s
# mail user where to get the file
(cat <<EOF_MAIL
To: %(email)s
Subject: ${SUBJECT}
MIME-Version: 1.0
Content-Type: text/plain

 The output from ${JOBNAME} is too large to mail (${ZIPSIZE} bytes).

 You can obtain your file at:

   %(webserver_site)s

%(rsync_message)s

EOF_MAIL
) | %(mail_command)s

fi
""" % (subs)
    ### PBS SCRIPT END

    # Convert from DOS
    script = string.replace(script, "\r\n", "\n")

    pbs = open("pbs_script.pbs", "wb")
    pbs.write(script)
    pbs.close()

def create_workdir(workdir, config, options):
    import subprocess
    command = "mkdir -p %s; chmod o+r %s" % (workdir, workdir)

    (exitcode, o, e) = ssh_run_command(options, command)

    return exitcode

def transfer_files(workfile, workdir, config, options):
    import subprocess

    if options["verbose"]:
        print "Transfering work ..."

    if options["rsync"]:
        rsync_work(workdir, config, options)
    else:
        tar_up_work(workfile, config, options)
        transfer_workfile(workfile, workdir, config, options)
        # Remove workfile, pbs script
        if not options['debug']:
            exitcode = subprocess.call("rm -f %s" % (workfile),
                                       shell=True)
    if not options['debug']:
        exitcode = subprocess.call("rm -f pbs_script.pbs",
                                   shell=True)

def rsync_work(workdir, config, options):
    import subprocess, sys
    if (len(options["input"])>0):
        files = "pbs_script.pbs " + options["input"]
    else:
        files = "."

    exitcode = subprocess.call("rsync %s " % (files) +
                               "%s@%s:%s" %
                               (options["user"], options["host"], workdir),
                               shell=True)
    if (exitcode):
        sys.stderr.write("Could not rsync files!\n")
        sys.exit(1)

def tar_up_work(workfile, config, options):
    import subprocess

    # always send the pbs script
    if (len(options["input"])>0):
        files = "pbs_script.pbs " + options["input"]
    else:
        files = "*"

    exitcode = subprocess.call("tar -czf %s %s" % (workfile, files),
                               shell=True)

def transfer_workfile(workfile, workdir, config, options):
    import subprocess

    exitcode = subprocess.call("scp -q %s " % (workfile) +
                               "%s@%s:%s" %
                               (options["user"], options["host"], workdir),
                               shell=True)
    return exitcode

def strip_jobid(full_jobid):
    # Full Job ID looks like 90210.opteron-cluster.nic.ualberta.ca
    # We only want the number in the front
    return full_jobid.split(".")[0]

def queue_pbs_script(workfile, workdir, config, options):
    import subprocess
    PIPE = subprocess.PIPE

    if options["rsync"]:
        tar =""
    else:
        tar = config["hosts"][options["host"]]["tar"] + \
            " -xzf %s; rm -f %s; " % (workfile, workfile)

    user = options["user"]
    host =  options["host"]
    command = "cd %s; "  % (workdir) + \
        tar + "qsub pbs_script.pbs; rm -f pbs_script.pbs"
    
    (exitcode, o, e) = ssh_run_command(options, command)

    if exitcode == 0:
        # Return full-qualified job ID
        return o.strip()
    else:
        return None

def job_submit(options_in):
    config = get_config(get_wrapper_cmdline=get_cmdline_dict,
                        wrapper_title="",
                        add_wrapper_options=None,
                        wrapper_gui_options=None,
                        add_wrapper_validators=add_validators_dict,
                        configfileXML="")

    # Record attributes in the dict "options" as seen
    options = dict()
    seen = dict()

    merge_options(options, None, options_in)

    for key, val in options.iteritems():
        seen[key] = True

    merge_options(options, seen, default_options)
    make_account_defaults(config, options, seen)
    read_merge_user_defaults(options, seen)
    validate_options(config, options)
    set_up_ssh(config, options)
    return submit_job(config, options)

def job_delete(options, jobid):
    import subprocess

    command = "qdel %s" % (strip_jobid(jobid))
    (exitcode, o, e) = ssh_run_command(options, command)

    return exitcode

def job_status(options, jobid=None, full=False):
    import subprocess
    command = "qstat"
    if (full):
        command += " -f"
    if (jobid):
        command += " %s" % (strip_jobid(jobid))

    (exitcode, o, e) = ssh_run_command(options, command)

    return exitcode

def job_fetch(options, workdir, clean=False):
    import subprocess
    if not options["rsync"]:
        print "job_fetch needs the rsync option!"
        return 1

    inclexcl = ""
    if (len(options["output"])>0):
        files = options["output"].split()
        for file in files:
            inclexcl += "--include '%s' " % (file)
        inclexcl += "--exclude '/*'"

    command = "rsync -az %s %s@%s:%s/ ." % (inclexcl,
                                            options["user"],
                                            options["host"],
                                            workdir)

    exitcode = subprocess.call(command, shell=True)

    if clean:
        if (exitcode == 0):
            exitcode = job_clean(options, workdir)
        else:
            print "Fetch was not successful, not cleaning!"

    return exitcode

def job_clean(options, workdir):
    import subprocess

    command = "rm -rf %s" % (workdir)

    print "Cleaning remote work directory: %s@%s:%s" % \
        (options["user"], options["host"], workdir)

    (exitcode, o, e) = ssh_run_command(options, command)

    return exitcode
    
def add_execution_options(parser, config):
    import optparse

    g = optparse.OptionGroup(parser, "Execution options")

    ### Key
    g.add_option("-g", "--gui", action="callback",
                 callback=store_true_seen, dest="gui",
                 help="Spawn wxPython GUI", default=False)

    g.add_option("-l", "--load-options", action="callback",
                 callback=store_seen, type="string",
                 dest="load_options", metavar="FILE", default="",
                 help="Load options (except those currently on the " + \
                     "commandline) from a file")

    g.add_option("-s", "--save-options", action="callback",
                 callback=store_seen, type="string",
                 dest="save_options", metavar="FILE", default="",
                 help="Save options to a file")
    
    parser.add_option_group(g)

### GUI ############################################################

def make_gui(config, options, wrapper_gui_options):
    import sys
    try:
        import wx
    except:
        return

    app = wx.PySimpleApp()
    frame = OptionsWindow(None, -1, config["wrapper_title"], 
                          config, options, wrapper_gui_options)
    app.MainLoop()

try:
    import wx
except:
    sys.exit(1)

class OptionsWindow(wx.Frame):
    def __init__(self, parent, id, title,
                 config, options, wrapper_gui_options):

        wx.Frame.__init__(self, parent, wx.ID_ANY, title)
        self.Bind(wx.EVT_CLOSE, OnCancel)

        self.name    = title
        self.config  = config
        self.options = options

        self.text_controls = []
        self.combo_controls = []
        self.spin_controls = []
        self.checkbox_controls = []

        panel = wx.Panel(self, -1)
        sizer = wx.BoxSizer(wx.VERTICAL)

        if (wrapper_gui_options):
            add_options_panel(panel, sizer, config, options,
                              wrapper_gui_options)

        add_options_panel(panel, sizer, config,
                          options, pbs_gui_options)

        add_buttons(panel, sizer)

        panel.SetSizerAndFit(sizer)
        panel.SetAutoLayout(True) 
        panel.Fit()
        self.Fit()
        self.Show(1)

def add_buttons(panel, sizer):
    subpanel = wx.Panel(panel, -1)

    buttons_sizer = wx.BoxSizer(wx.HORIZONTAL)
    load_button   = wx.Button(subpanel, label="Load Options")
    save_button   = wx.Button(subpanel, label="Save Options")
    cancel_button = wx.Button(subpanel, label="Cancel")
    submit_button = wx.Button(subpanel, label="Submit")

    load_button.Bind(wx.EVT_BUTTON, OnLoad)
    save_button.Bind(wx.EVT_BUTTON, OnSave)
    cancel_button.Bind(wx.EVT_BUTTON, OnCancel)
    submit_button.Bind(wx.EVT_BUTTON, OnSubmit)

    buttons_sizer.Add(load_button,1,wx.EXPAND)
    buttons_sizer.Add(save_button,1,wx.EXPAND)
    buttons_sizer.Add(cancel_button,1,wx.EXPAND)
    buttons_sizer.Add(submit_button,1,wx.EXPAND)

    subpanel.SetSizer(buttons_sizer)

    sizer.Add(subpanel, 0, wx.ALL|wx.EXPAND, border=5)

# store the directory name in case of multiple load, save
dirname = ""
filename = ""

def OnSave(event):
    import os
    global dirname, filename

    control = event.GetEventObject()
    optwin =  control.GetTopLevelParent()
    options = optwin.options

    dlg = wx.FileDialog(optwin, "Choose a file", dirname, filename, "*.*",
                        wx.SAVE | wx.OVERWRITE_PROMPT)
    if dlg.ShowModal() == wx.ID_OK:

        filename=dlg.GetFilename()
        dirname=dlg.GetDirectory()
        save_options(options,
                     os.path.join(dirname, filename))

    dlg.Destroy()

def OnLoad(event):
    import os
    global dirname, filename

    control = event.GetEventObject()
    optwin =  control.GetTopLevelParent()
    options = optwin.options

    dlg = wx.FileDialog(optwin, "Choose a file", dirname, filename, "*.*",
                        wx.OPEN)
    if dlg.ShowModal() == wx.ID_OK:

        filename=dlg.GetFilename()
        dirname=dlg.GetDirectory()
        load_merge_options(options,
                           os.path.join(dirname, filename))
        update_controls(optwin)

    dlg.Destroy()

def update_controls(optwin):
    options = optwin.options
    ctrls = optwin.text_controls + optwin.spin_controls + \
        optwin.combo_controls
    for ctrl in ctrls:
        name = ctrl.GetName()
        if (options.has_key(name)):
            ctrl.SetValue(options[name])

def OnCancel(event):
    import sys

    control = event.GetEventObject()
    optwin =  control.GetTopLevelParent()

    optwin.Destroy()
    sys.exit()

def OnSubmit(event):
    control = event.GetEventObject()
    optwin =  control.GetTopLevelParent()

    optwin.Destroy()

def add_options_panel(panel, sizer, config, options, get_gui_options):
    subpanel = wx.Panel(panel, -1)

    (title, fields) = get_gui_options(subpanel, config, options)
    fields_sizer = wx.FlexGridSizer(rows=len(fields), cols=2, 
                                    vgap=10, hgap=10)

    for field in fields:
        fields_sizer.Add(field[0], 2, wx.EXPAND)
        fields_sizer.Add(field[1], 1, wx.EXPAND)

    font = wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD)
    heading = wx.StaticText(subpanel, -1, title, style=wx.ALIGN_CENTRE)
    heading.SetFont(font)

    panel_sizer = wx.BoxSizer(wx.VERTICAL)

    panel_sizer.Add(heading, 0, wx.ALL, border=5)
    panel_sizer.Add(fields_sizer, 0, wx.ALL, border=5)
    subpanel.SetSizer(panel_sizer)

    sizer.Add(subpanel, 0,  wx.ALL, border=5)

def pbs_gui_options(subpanel, config, options):
    title = "PBS Options"
    optwin  =  subpanel.GetTopLevelParent()
    config  = optwin.config
    hosts = config["hosts"].keys()
    fields = []
    fields.append(add_combo_control(subpanel,
                                    "host",
                                    "Host:",
                                    hosts))
    fields.append(add_text_control(subpanel,
                                   "user",
                                   "User:",
                                   width=10))
    fields.append(add_text_control(subpanel,
                                   "email",
                                   "Email:"))
    fields.append(add_text_control(subpanel,
                                   "notify",
                                   "Notify:",
                                   width=5))
    fields.append(add_text_control(subpanel,
                                   "jobname",
                                   "Job name:",
                                   width=30))
    fields.append(add_text_control(subpanel,
                                   "mem",
                                   "Total memory required:"))
    fields.append(add_text_control(subpanel,
                                   "pvmem",
                                   "Per-processor memory required:"))
    fields.append(add_spin_control(subpanel,
                                   "nodes",
                                   "Number of nodes:"))
    fields.append(add_spin_control(subpanel,
                                   "ppn",
                                   "Processors per node:"))
    fields.append(add_spin_control(subpanel,
                                   "procs",
                                   "Total number of processors:"))
    fields.append(add_text_control(subpanel,
                                   "walltime",
                                   "Wall time:"))
    fields.append(add_text_control(subpanel,
                                   "dir",
                                   "Remote work directory:"))
    fields.append(add_text_control(subpanel,
                                   "input",
                                   "Input files:"))
    fields.append(add_text_control(subpanel,
                                   "output",
                                   "Output files:"))
    fields.append(add_checkbox_control(subpanel,
                                       "rsync",
                                       "Rsync:"))

    return (title, fields)

def handle_ctrl(event):
    control = event.GetEventObject()
    optwin  = control.GetTopLevelParent()
    options = optwin.options
    config  = optwin.config
    name    = control.GetName()
    value   = control.GetValue()

    try:
        validator = config["validators"][name]
        optwin.options = validator(config, options, value)
    except:
        optwin.options[name] = value

def add_text_control(panel, name, label, width=None):
    optwin  = panel.GetTopLevelParent()
    options = optwin.options
    config  = optwin.config

    label = wx.StaticText(panel, label=label)
    if (not options[name]):
        options[name] = ""
    ctrl  = wx.TextCtrl(panel, value=options[name], name=name)

    if (width):
        dc=wx.ScreenDC()
        # dc.SetFont(font)
        (x,y) = dc.GetTextExtent("T")
        ctrl.SetMinSize((x * width + 10, -1))
        ctrl.SetMaxSize((x * width + 10, -1))

    ctrl.Bind(wx.EVT_TEXT, handle_ctrl)
    optwin.text_controls.append(ctrl)

    return ([label, ctrl])

def add_combo_control(panel, name, label, choices, width=None):
    optwin  = panel.GetTopLevelParent()
    options = optwin.options
    config  = optwin.config

    label = wx.StaticText(panel, label=label)
    if (not options[name]):
        options[name] = ""
    ctrl  = wx.ComboBox(panel, value=options[name], name=name,
                        choices=choices)

    if (width):
        dc=wx.ScreenDC()
        # dc.SetFont(font)
        (x,y) = dc.GetTextExtent("T")
        ctrl.SetMinSize((x * width + 10, -1))
        ctrl.SetMaxSize((x * width + 10, -1))

    ctrl.Bind(wx.EVT_TEXT, handle_ctrl)
    optwin.combo_controls.append(ctrl)

    return ([label, ctrl])

def add_spin_control(panel, name, label):
    optwin  = panel.GetTopLevelParent()
    options = optwin.options
    config  = optwin.config

    label = wx.StaticText(panel, label=label)
    if (not options[name]):
        options[name] = 0
    ctrl  = wx.SpinCtrl(panel, initial=options[name], name=name)
    
    ctrl.Bind(wx.EVT_TEXT, handle_ctrl)
    optwin.spin_controls.append(ctrl)

    return ([label, ctrl])

def add_checkbox_control(panel, name, label):
    optwin  = panel.GetTopLevelParent()
    options = optwin.options
    config  = optwin.config

    label = wx.StaticText(panel, label=label)
    if (not options[name]):
        options[name] = 0
    ctrl  = wx.CheckBox(panel, name=name)
    ctrl.SetValue(options[name])
    ctrl.Bind(wx.EVT_CHECKBOX, handle_ctrl)
    optwin.checkbox_controls.append(ctrl)

    return ([label, ctrl])

### Validators

def get_validators():
    validators = dict( {
            'host' : validate_host
            } )
    return validators


def validate_options(config, options):
    for name, validator in config["validators"].iteritems():
        if options.has_key(name):
            value = options[name]
        else:
            value = None
        validator(config, options, value)

def validate_host(config, options, value):
    if (value not in config["hosts"].keys()):
        import sys
        print("Bad host name! (%s)" % (value))
        print("Host name must be one of:")
        for host in config["hosts"].keys():
            print("   %s" % (host))
        sys.exit(1)

    return value

### XML based Wrappers

def get_hosts_config_XML(hostsconf):
    import os, sys
    from xml.dom import minidom

    # Read host config from XML file
    confbase = os.path.dirname(__file__)
    if len(confbase)==0:
        confbase = "."

    conf = confbase + "/config/" + hostsconf

    dom = minidom.parse(conf)

    hosts = dict()
    defaults = dict()

    hs = dom.getElementsByTagName("host")
    for h in hs:
        host = dict()

        # defaults?
        type = h.getAttribute("type")
        if (type == "defaults"):
            defaults = host
        else:
            # If not defaults, get hostname
            name = get_text_XML(h, "name")
            if name:
                host["name"] = name
                hosts[name] = host
            else:
                print "Host must have a name!"
                sys.exit(1)

        # Sendmail
        host["sendmail"] = get_text_XML(h, "sendmail")
        # Tar
        host["tar"] = get_text_XML(h, "tar")
        # Mailhost
        host["mail_host"] = get_text_XML(h, "mail_host")
        # scratch_base
        host["scratch_base"] = get_text_XML(h, "scratch_base")
        # email_base
        host["email_base"] = get_text_XML(h, "email_base")
        
        # PBS Options
        pbs = dict()
        p = h.getElementsByTagName("pbs_options")
        queues = []
        mem_specs = []
        cpu_specs = []
        if len(p) > 0:
            # Queues
            qs = p[0].getElementsByTagName("queue")
            for q in qs:
                queue = dict()
                name = get_text_XML(q, "name")
                if name:
                    queue["name"] = name
                else:
                    print "Queue must have a name!"
                    sys.exit(1)
                queues.append(queue)

        
            # mem_spec
            ms = p[0].getElementsByTagName("mem_spec")
            for m in ms:
                mem_spec = get_text_XML(m)
                mem_specs.append(mem_spec)

            # cpu_spec
            cs = p[0].getElementsByTagName("cpu_spec")
            for c in cs:
                cpu_spec = get_text_XML(c)
                cpu_specs.append(cpu_spec)

        pbs["queues"] = queues
        pbs["mem_specs"] = mem_specs
        pbs["cpu_specs"] = cpu_specs
        host["pbs_options"] = pbs
    dom.unlink()

    # Grab missing host attributes from the host called "defaults"
    for key in defaults:
        if defaults[key]:
            for name in hosts:
                if not hosts[name][key]:
                    hosts[name][key] = defaults[key]

    return hosts

def add_config_XML(config, configfileXML):
    import os, sys
    from xml.dom import minidom

    conf = os.path.dirname(__file__) + "/config/" + configfileXML
    dom = minidom.parse(conf)

    wrapper = dict()

    # Get Wrapper Title
    wrapper["wrapper_title"] = get_text_required_XML(dom, "wrapper_title",
                                                     "wrapper")

    # Get Options Title
    wrapper["options_title"] = get_text_required_XML(dom, "options_title",
                                                     "wrapper")

    arguments = dict()
    args = dom.getElementsByTagName("argument")
    for arg in args:
        argument = dict()

        # Get Argument Name
        name  = get_text_required_XML(arg, "name", "argument")
        argument["name"] = name
        # Get Argument Short Form
        argument["short"] = get_text_required_XML(arg, "short", "argument")
        # Get Argument Long Form
        argument["long"] = get_text_required_XML(arg, "long", "argument")
        # Get Argument Help String
        argument["help"] = get_text_required_XML(arg, "help", "argument")
        # Get Argument Default (optional)
        default = get_text_XML(arg, "default")
        if default:
            argument["default"] = default
        # Get GUI title (optional)
        gui_title = get_text_XML(arg, "gui_title")
        if gui_title:
            argument["gui_title"] = gui_title
        # Get GUI width (optional)
        gui_width = get_text_XML(arg, "gui_width")
        if gui_width:
            argument["gui_width"] = gui_width

        arguments[name] = argument

    hosts = dict()
    defaults = dict()

    hs = dom.getElementsByTagName("host")

    # Get Hosts
    for h in hs:
        host = dict()

        type = h.getAttribute("type")
        if (type == "defaults"):
            defaults = host
        else:
            # Get Host Name
            name = get_text_required_XML(h, "name", "host")
            host["name"] = name
            hosts[name] = host

        # Get Command
        host["command"] = get_text_XML(h, "command")

    wrapper["arguments"] = arguments
    wrapper["hosts"] = hosts
    wrapper["defaults"] = defaults

    config["wrapper"] = wrapper

def get_wrapper_cmdline_XML(config, options):

    wrapper = config["wrapper"]

    # Make a dict of options with argument names as key
    args = dict()
    for name in config["wrapper"]["arguments"]:
        args[name] = options[name]

    # Get the command that is appropriate for this host
    # Try getting from defaults first ...
    command = ""
    if "command" in wrapper["defaults"].keys():
        command = wrapper["defaults"]["command"]
    # ... then override by a possible command specific to the host 
    if options["host"] in wrapper["hosts"].keys():
        host = wrapper["hosts"][options["host"]]
        if "command" in host.keys():
            command = host["command"]

    if len(command) > 0:
        # Substitute the args in the command
        return command % (args)
    else:
        print "Command not found!"
        sys.exit(1)

def add_wrapper_options_XML(parser, config):
    import optparse

    wrapper = config["wrapper"]
    if "arguments" in wrapper.keys():
        arguments = wrapper["arguments"]
    else:
        return

    g = optparse.OptionGroup(parser, wrapper["options_title"])

    for key in arguments:
        argument = arguments[key]
        name  = argument["name"]
        short = argument["short"]
        long  = argument["long"]
        if "default" in argument.keys():
            default = argument["default"]
            help = argument["help"] + " (default: %s)" % (default)
            g.add_option(short, long, action="callback",
                         callback=store_seen, type="string",
                         dest=name, metavar="STRING",
                         default=default, help=help)
        else:
            help = argument["help"]
            g.add_option(short, long, action="callback",
                         callback=store_seen, type="string",
                         dest=name, metavar="STRING",
                         help=help)

    parser.add_option_group(g)

def wrapper_gui_options_XML(subpanel, config, options):
    wrapper = config["wrapper"]

    if "arguments" in wrapper.keys():
        arguments = wrapper["arguments"]
    else:
        return

    title = wrapper["options_title"]

    fields = []
    for key in arguments:
        argument = arguments[key]
        if "gui_title" in argument.keys():
            gui_title = argument["gui_title"]
            name      = argument["name"]
            gui_width = 30
            if "gui_width" in argument.keys():
                gui_width = int(argument["gui_width"])

            fields.append(add_text_control(subpanel,
                                           name,
                                           gui_title,
                                           width=gui_width))

    return (title, fields)

# Helper for getting text out of Element nodes
def get_text_XML(element, name=None):
    if not name:
        return str(element.childNodes[0].data)

    node = element.getElementsByTagName(name)
    
    if node:
        return str(node[0].childNodes[0].data)

    return None

def get_text_required_XML(element, name, parent_name):

    text = get_text_XML(element, name)
    if not text:
        print name + " not defined for " + parent_name + "!"
        sys.exit(1)

    return text

def get_boolean_XML(element, name):
    node = element.getElementsByTagName(name)
    
    if node:
        return True

    return False

### User defaults

def read_merge_user_defaults(options, seen=None):
    import os
    from xml.dom import minidom

    optsfile = os.path.expanduser('~/.PBSUtil.xml')
    if not os.path.isfile(optsfile):
        return

    dom = minidom.parse(optsfile)

    useropts = dict()

    d = dom.getElementsByTagName("defaults")
    if len(d) > 0:
        defaults = d[0]
        
    host     = get_text_XML(defaults, "host")
    user     = get_text_XML(defaults, "user")
    email    = get_text_XML(defaults, "email")
    dir      = get_text_XML(defaults, "dir")
    notify   = get_text_XML(defaults, "notify")
    walltime = get_text_XML(defaults, "walltime")
    pvmem    = get_text_XML(defaults, "pvmem")
    rsync    = get_boolean_XML(defaults, "rsync")
    gui      = get_boolean_XML(defaults, "gui")

    if host:
        useropts["host"] = host
    if user:
        useropts["user"] = user
    if email:
        useropts["email"] = email
    if dir:
        useropts["dir"] = dir
    if notify:
        useropts["notify"] = notify
    if walltime:
        useropts["walltime"] = walltime
    if pvmem:
        useropts["pvmem"] = pvmem
    if rsync:
        useropts["rsync"] = rsync
    if gui:
        useropts["gui"] = gui

    merge_options(options, seen, useropts)

    dom.unlink()

def get_cmdline_dict(config, options):
    return options['exe']

def needs_exe(config, options, value):
    if not value:
        error_exit("An 'exe' dictionary item is needed!\n")

def add_validators_dict(config):
    config['validators']['exe'] = needs_exe

def error_exit(message):
    import sys

    sys.stderr.write(message)
    sys.exit(1)

