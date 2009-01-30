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

### Main Entry Point
def do_wrapper(name, add_program_options,
               add_gui_controls, get_program_cmdline):
    # add_program_options() add_gui_controls(), and 
    # get_program_cmdline() are callbacks
    import os, optparse

    config = get_config()

    if (os.getenv("SSH_AGENT_RESPAWN")):
        # We have been respawned, load pickled options
        (options, args) = load_program_args()
    else:
        parser = optparse.OptionParser()
        add_program_options(parser)
        add_account_options(parser)
        add_pbs_options(parser)
        add_execution_options(parser)

        parser.seen = dict()
        (options_obj, args) = parser.parse_args()
        options = obj_to_dict(options_obj)
        seen    = parser.seen

        if (options["load_options"]):
            load_merge_options(options, options["load_options"], seen)
        if (options["gui"]):
            make_gui(name, config, options, args, add_gui_controls)

    validate_options(config, options)
    if (options["save_options"]):
        save_options(options, options["save_options"])

    # Set up ssh keys, respawning if needed
    set_up_ssh(options, args)
    executable = get_program_cmdline(options, args)
    submit_job(executable, config, options, args)

### Get Config

def get_config():
    aict_cluster = dict( {
            'mail_host' : "10.0.6.1",
            'sendmail'  : "/usr/sbin/sendmail" } )
    nexus = dict( {
            'mail_host' : None,
            'sendmail'  : "/usr/lib/sendmail" } )

    hosts = dict( {
            'cluster.srv.ualberta.ca' : aict_cluster,
            'nexus.westgrid.ca'       : nexus } )

    config = dict( {\
        'hosts'            : hosts,
        'validators'       : get_validators(),
        'webserver_site'   : "https://sciviz.nic.ualberta.ca/~cwant/hpc_web",
        'webserver_address': "cwant@sciviz.nic.ualberta.ca",
        'webserver_subject': "HPC output download ready" } )

    return config

def obj_to_dict(options_obj):
    options = dict()
    for key, val in vars(options_obj).iteritems():
        options[key] = val
    return options

def load_program_args():
    # Load pickled command line options and positional args
    import pickle, sys

    options = pickle.load(sys.stdin)
    args    = pickle.load(sys.stdin)

    return (options, args)

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

    for key, value in optload.iteritems():
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

def add_account_options(parser):
    import os, optparse

    g = optparse.OptionGroup(parser, "Account options")
    user = os.getenv("USER")

    ### Host
    g.add_option("-H", "--host", action="callback",
                 callback=store_seen, type="string",
                 dest="host", metavar="HOST",
                 default="cluster.srv.ualberta.ca",
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

    ### Key
    g.add_option("-k", "--key", action="callback",
                 callback=store_seen, type="string",
                 dest="key", metavar="KEY",
                 help="Use or specify an ssh key")
    
    parser.add_option_group(g)

def add_pbs_options(parser):
    import os, optparse

    g = optparse.OptionGroup(parser, "Job Scheduling options")
    user = os.getenv("USER")

    ### Email
    if (user):
        g.add_option("-e", "--email", action="callback",
                     callback=store_seen, type="string",
                     dest="email", metavar="USER@EXAMPLE.COM",
                     default=user + "@ualberta.ca",
                     help="The email address for notifications about " + \
                         "errors and job completion " + \
                         "(default: %default)")
    else:
        g.add_option("-e", "--email", action="callback",
                     callback=store_seen, type="string",
                     dest="email", metavar="EMAIL@foo.com",
                     help="The email address for notifications about " + \
                         "errors and job completion")

    ### Notify
    g.add_option("-E", "--notify", action="callback",
                 callback=store_seen, type="string",
                 dest="notify", metavar="[b][e][a]",
                 default="bea",
                 help="Email notifications before (b) the job runs, " + \
                     "or after (a) the job runs, or on errors (e) " + \
                     "(default: %default)")

    ### Job Name
    g.add_option("-N", "--jobname", action="callback",
                 callback=store_seen, type="string",
                 dest="jobname", metavar="JOBNAME", default="job1",
                 help="The name of the job that is submitted to " + \
                     "the HPC resource (default: %default)")

    ### Memory Requirements
    g.add_option("-m", "--pvmem", action="callback",
                 callback=store_seen, type="string",
                 dest="pvmem", metavar="MEMORY", default="512mb",
                 help="The s ze of memory required " + \
                     "(default: %default)")

    ### Nodes
    g.add_option("-n", "--nodes", action="callback",
                 callback=store_seen, type="int",
                 dest="nodes", metavar="NODES", default="1",
                 help="The number of nodes required " + \
                     "(default: %default)")

    ### Processors per node
    g.add_option("-p", "--ppn", action="callback",
                 callback=store_seen, type="int",
                 dest="ppn", metavar="PROCPERNODE", default="1",
                 help="The number of processors per node required" +
                     "(default: %default)")

    ### Wall time
    g.add_option("-w", "--walltime", action="callback",
                 callback=store_seen, type="string",
                 dest="walltime", metavar="WALLTIME", default="24:00:00",
                 help="The maximum time required to run the job " +
                 "(default: %default)")

    ### Work directory
    if (user):
        g.add_option("-d", "--dir", action="callback",
                 callback=store_seen, type="string",
                     dest="dir", metavar="DIRECTORY",
                     default="/scratch/" + user,
                     help="The directory on the HPC resource under which " + \
                         "a temporary work directory will be created " + \
                         "(default: %default)")
    else:
        g.add_option("-d", "--dir", action="callback",
                     callback=store_seen, type="string",
                     dest="dir", metavar="DIRECTORY",
                     help="The directory on the HPC resource under which " + \
                         "a temporary work directory will be created")

    ### Add options ########################
    
    parser.add_option_group(g)


### SSH Routines ###################################

def ssh_keys_loaded():
    import subprocess
    exitcode = subprocess.call("ssh-add -L > /dev/null", shell=True)

    if (exitcode):
        return 0

    return 1

def test_ssh_key(options):
    import subprocess
    exitcode = subprocess.call("ssh -o NumberOfPasswordPrompts=0 " + \
                                   "%s -l %s date" % \
                                   (options["host"],
                                    options["user"]),
                               shell=True)
    if (exitcode):
        return 0

    return 1

def ssh_need_key(options):
    if ( not ssh_keys_loaded() ):
        # Case where there are no keys
        return 1

    # Case where there are keys
    if ( not test_ssh_key(options)):
        return 1

    return 0

def set_up_ssh(options, args):
    import sys, os, pickle, subprocess

    # Check if there is an ssh-agent running -- if not, re-run self in
    # an agent.
    if (options["key"]):
        key = options["key"]
    else:
        key = ""

    ssh_auth = os.getenv("SSH_AUTH_SOCK")
    if (not ssh_auth):
        pipe = subprocess.Popen("SSH_AGENT_RESPAWN=TRUE ssh-agent python %s"
                                % sys.argv[0],
                                stdin=SubProcess.PIPE, shell=True);
        pickle.dump(options, pipe.stdin)
        pickle.dump(args, pipe.stdin)
        pipe.stdin.flush()
        sts = os.waitpid(pipe.pid, 0)
        sys.exit();

    # Check if there are ssh-keys loaded
    if (ssh_need_key(options)):
        # Key needed, so try to add key, note that the variable
        # $key will be empty unless the user used -k
        subprocess.call("ssh-add %s > /dev/null" % (key), shell=True);

        # Try again to see if the key worked
        if ( not test_ssh_key() ):
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
def submit_job(executable, config, options, args):
    import os

    workdir  = "%s/%s_%d.tmp" % (options["dir"], options["jobname"],
                                 os.getpid())
    workfile = "%s_%d.tar.gz" % (options["jobname"], os.getpid())

    make_pbs_script(executable, workdir, config, options, args)
    tar_up_work(workfile, options)
    create_workdir(workdir, options)
    transfer_workfile(workfile, workdir, options)
    queue_pbs_script(workfile, workdir, options)

### Create PBS Script
def make_pbs_script(executable, workdir, config, options, args):
    pbs = open("pbs_script.pbs", "w")

    # create dictionary of strings for heredoc substitutions
    subs = dict()
    subs.update(options)
    subs.update(config)
    subs.update(config['hosts'][options["host"]])
    subs.update(args)
    subs['executable'] = executable
    subs['workdir']    = workdir 

    if (subs['mail_host']):
        # if mail_host is set, ssh to the host to send mail
        subs['mail_command'] = "ssh %s@%s '%s -t'" % \
            (subs['user'], subs['mail_host'], subs['sendmail'])
    else:
        # otherwise, just run sendmail
        subs['mail_command'] = "%s -t" % (subs['sendmail'])

    ### PBS SCRIPT START
    pbs.write("""\
#!/bin/bash -l
#PBS -N %(jobname)s
#PBS -S /bin/bash
#PBS -l pvmem=%(pvmem)s
#PBS -l nodes=%(nodes)d:ppn=%(ppn)d
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

zip -r ${OUTPUT} * > /dev/null
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
EOF_MAIL
) | %(mail_command)s

fi
""" % subs )
    pbs.close()
    ### PBS SCRIPT END

def tar_up_work(workfile, options):
    import subprocess
    exitcode = subprocess.call("tar -czvf %s *" % (workfile),
                               shell=True)

def create_workdir(workdir, options):
    import subprocess
    exitcode = subprocess.call("ssh %s@%s " %
                               (options["user"], options["host"]) +
                               "'mkdir -p %s; chmod o+r %s'" %
                               (workdir, workdir),
                               shell=True)

def transfer_workfile(workfile, workdir, options):
    import subprocess
    exitcode = subprocess.call("scp %s " % (workfile) +
                               "%s@%s:%s" %
                               (options["user"], options["host"], workdir),
                               shell=True)

def queue_pbs_script(workfile, workdir, options):
    import subprocess
    exitcode = subprocess.call("ssh %s@%s " %
                               (options["user"], options["host"]) +
                               "'cd %s; tar -xzvf %s; qsub pbs_script.pbs'" %
                               (workdir, workfile),
                               shell=True)

def run_qstat(options):
    import subprocess
    exitcode = subprocess.call("ssh %s@%s " %
                               (options["user"], options["host"]) +
                               "'qstat'",
                               shell=True)


def add_execution_options(parser):
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

def make_gui(name, config, options, args, add_gui_options):
    import sys
    try:
        import wx
    except:
        return

    app = wx.PySimpleApp()
    frame = OptionsWindow(None, -1, name, 
                          config, options, args, add_gui_options)
    app.MainLoop()

try:
    import wx
except:
    sys.exit(1)

class OptionsWindow(wx.Frame):
    def __init__(self, parent, id, title,
                 config, options, args, app_gui_options):

        wx.Frame.__init__(self, parent, wx.ID_ANY, title)
        self.Bind(wx.EVT_CLOSE, OnCancel)

        self.name    = title
        self.config  = config
        self.options = options
        self.args    = args

        panel = wx.Panel(self, -1)
        sizer = wx.BoxSizer(wx.VERTICAL)

        if (app_gui_options):
            add_options_panel(panel, sizer, options, app_gui_options)

        add_options_panel(panel, sizer, options, pbs_gui_options)

        add_buttons(panel, sizer)

        panel.SetSizerAndFit(sizer)
        panel.SetAutoLayout(True) 
        panel.Fit()
        self.Fit()
        self.Show(1)

def add_buttons(panel, sizer):
    subpanel = wx.Panel(panel, -1)

    buttons_sizer = wx.BoxSizer(wx.HORIZONTAL)
    submit_button = wx.Button(subpanel, label="Submit")
    cancel_button = wx.Button(subpanel, label="Cancel")
    submit_button.Bind(wx.EVT_BUTTON, OnSubmit)
    cancel_button.Bind(wx.EVT_BUTTON, OnCancel)
    buttons_sizer.Add(submit_button,1,wx.EXPAND)
    buttons_sizer.Add(cancel_button,1,wx.EXPAND)
    subpanel.SetSizer(buttons_sizer)

    sizer.Add(subpanel, 0, wx.ALL|wx.EXPAND, border=5)


def OnSubmit(event):
    control = event.GetEventObject()
    optwin =  control.GetTopLevelParent()

    d= wx.MessageDialog( optwin, "Your job has been submitted",
                             "Job submitted!", wx.OK)
    d.ShowModal()
    d.Destroy()

    optwin.Destroy()

def OnCancel(event):
    import sys

    control = event.GetEventObject()
    optwin =  control.GetTopLevelParent()

    optwin.Destroy()
    sys.exit()


def add_options_panel(panel, sizer, options, get_gui_options):
    subpanel = wx.Panel(panel, -1)

    (title, fields) = get_gui_options(subpanel, options)
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

def pbs_gui_options(subpanel, options):
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
                                   "pvmem",
                                   "Memory required:"))
    fields.append(add_spin_control(subpanel,
                                  "nodes",
                                  "Number of nodes:"))
    fields.append(add_spin_control(subpanel,
                                  "ppn",
                                  "Processors per node:"))
    fields.append(add_text_control(subpanel,
                                   "walltime",
                                   "Wall time:"))
    fields.append(add_text_control(subpanel,
                                   "dir",
                                   "Remote work directory:"))

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
    return ([label, ctrl])

### Validators

def get_validators():
    validators = dict( {
            'host' : validate_host
            } )
    return validators


def validate_options(config, options):
    for name, validator in config["validators"].iteritems():
        value = options[name]
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
