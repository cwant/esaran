#!/usr/bin/env python
#
# $Id: wrap_qstat.py 73 2009-03-19 21:40:30Z cwant $
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

def main():
    import sys, os, optparse, subprocess, eSaran

    config = eSaran.get_config()

    if (os.getenv("SSH_AGENT_RESPAWN")):
        # We have been respawned, load pickled options
        options = eSaran.load_program_args()
    else:
        usage = "%prog [options] JOBID.out\n\n" + \
            "JOBID.out is the job identifier file created " + \
            "when the job was submitted"

        parser = optparse.OptionParser(usage=usage)
        add_fetch_options(parser, config)
        eSaran.add_misc_options(parser, config)

        (options_obj, args) = parser.parse_args()
        options = eSaran.obj_to_dict(options_obj)

        (options_obj, args) = parser.parse_args()
        if (len(args) > 1):
            sys.stderr.write("Too many files on the command line!\n")
            sys.exit(1)
        if (len(args) < 1):
            sys.stderr.write("Need a file on the command line!\n")
            sys.exit(1)

        print args[0]
        (options_id, jobid, workdir) = eSaran.read_jobid_file(args[0])
        options = eSaran.obj_to_dict(options_obj)
        eSaran.merge_options(options, None, options_id)

    eSaran.validate_host(config, options, options["host"])

    eSaran.set_up_ssh(config, options)

    print args[0]
    if options['debug']:
        eSaran.job_fetch(options, workdir, False)
    else:
        eSaran.job_fetch(options, workdir, True)
        if options['clean']:
            exitcode = subprocess.call("rm -f %s" % (args[0]),
                                       shell=True)

def add_fetch_options(parser, config):
    import os, optparse

    g = optparse.OptionGroup(parser, "Job Fetch options")

    ### All
    g.add_option("-c", "--clean", action="store_true",
                 dest="clean", default=False,
                 help="Remove job id file after fetching")

    ### Add options ########################
    
    parser.add_option_group(g)

main()

